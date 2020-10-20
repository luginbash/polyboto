FROM python:alpine
WORKDIR /tmp
COPY ./requirements.txt /tmp
RUN apk add --no-cache -t .build-dep build-base libffi-dev openssl-dev \
    && pip install -r ./requirements.txt \
    && apk del .build-dep \
    && rm -rf /tmp


FROM scratch
COPY --from=0 / /
