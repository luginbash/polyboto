#!/usr/bin/env python3
import os
import logging
import datetime
import argparse
import signal
#import sentry_sdk
#SENTRY_API = os.environ.get('SENTRY_API')
#sentry_sdk.init(SENTRY_API)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from typing import NewType
import telegram
import json


TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '8000'))
HOST = os.environ.get('HOST', '')
LISTEN_ADDR = os.environ.get('LISTEN_ADDR', '0.0.0.0')

PERM_NO_NOTHING = telegram.ChatPermissions(
        can_send_messages=False
        , can_send_media_messages=False
        , can_send_polls=False
        , can_send_other_messages=False
        , can_add_web_page_previews=False
        , can_invite_users=False
        , can_pin_messages=False
        , can_change_info=False
    )

class DbMan(object):
    def __init__(self,dbname):
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.conn.create_function('uuidgen',1,uuid.uuid4())
        self.cur = self.conn.cursor()

    def query(self, arg:str):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def __del__(self):
        self.conn.close()

class BotCmd(object):
    def __init__(self):
        self._dict = {}

    def __call__(self, func):
        self._dict[func.__name__] = func
        return func

    def register_onto(self, dispatcher):
        for n, f in self._dict.items():
            dispatcher.add_handler(CommandHandler(n, f))

class botGroupMsg(object):
    def __init__(self):
        self._dict = {}

    def __call__(self, func):
        self._dict[func.__name__] = func
        return func

    def register_onto(self, dispatcher):
        for n, f in self._dict.items():
            dispatcher.add_handler(MessageHandler(Filters.group, f))


botcmd = BotCmd()
groupMsg = botGroupMsg()


import sqlite3
import uuid

@botcmd
def start(bot, update):
    txt = "You have just pressed start, but nothing happened."
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=txt,
                    reply_to_message_id=update.message.message_id)

@botcmd
def ping(bot, update):
    t0 = datetime.datetime.now()
    message = bot.sendMessage(
        chat_id=update.message.chat_id,
        text="Pong!",
        reply_to_message_id=update.message.message_id,
        parse_mode="Markdown")
    dt = datetime.datetime.now() - t0
    message.edit_text(
        parse_mode="Markdown", text="Pong!\n**`%.3f`**" % dt.total_seconds())

@groupMsg
def welcome(update: telegram.Update, ctx: telegram.ext.CallbackContext):
    if update.message.new_chat_members:
        for usr in update.message.new_chat_members:
            ctx.bot.restrict_chat_member(
                update.message.chat_id
                , user_id=usr.id
                , permissions=PERM_NO_NOTHING
            )
            ctx.bot.sendMessage(
                chat_id=update.message.chat_id
                , reply_to_message_id=update.message.message_id
                , text='Prove that you\'re not a degenerate bot.'
            )
            kickJob = ctx.job_queue.run_once(callbackKick,
                                   18,
                                   [update.message.chat_id
                                       ,usr.id])




def callbackKick(ctx:telegram.ext.CallbackContext):
    ctx.bot.kick_chat_member(chat_id=ctx.job.context[0]
                             , user_id=ctx.job.context[1])


def main(token: str, listen_addr: str, port: int, hostname: str, useNgork: bool) -> None:
    db = DbMan('quizes.db')
    updater = Updater(token, use_context=True)
    j = updater.job_queue

    botcmd.register_onto(updater.dispatcher)
    groupMsg.register_onto(updater.dispatcher)

    if useNgork:
      from pyngrok import ngrok
      webhook_url = ngrok.connect(port=port)
      hostname = webhook_url.replace('http://','',1)

      webhook_url = f"https://{hostname}/{token}"

    # todo(lug): load config in __main__
    with open('../config.json') as f:
        conf = json.load(f)

    # print(webhook_url)
    updater.start_webhook(
        listen=listen_addr,
        port=port,
        url_path=token,
        webhook_url=webhook_url)
    updater.bot.set_webhook(webhook_url)
    #import IPython; IPython.embed()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(description='Doorman bot is a naïve telegram anti-spam bot.')
    parser.add_argument('--token', dest='TOKEN')
    parser.add_argument('--host', dest='HOST')
    parser.add_argument('--port', dest='PORT', type=int, default='8000')
    parser.add_argument('--listen', dest='LISTEN_ADDR', default='127.0.0.1')
    parser.add_argument('--with-ngrok', dest='USE_NGROK', default=True)
    args = parser.parse_args()

    main(token=args.TOKEN, listen_addr=args.LISTEN_ADDR, port=args.PORT, hostname=args.HOST, useNgork=args.USE_NGROK)

