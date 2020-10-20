create table quizes
(
    quiz_id      blob
        constraint quizes_pk
            primary key,
    quiz_enabled int,
    quiz_deleted int
);

create table questions
(
    question_id         blob not null
        constraint questions_pk
            primary key,
    question_collection blob not null,
    question_deleted    int,
    question_audited    int,
    question            text not null,
    quiz_id             int  not null
        references quizes
            on update cascade on delete cascade
);

create table answers
(
    answer_id      blob not null
        constraint answers_pk
            primary key,
    option         text not null,
    option_enabled int,
    question_id    int
        references questions
            on update cascade on delete cascade
);

create unique index answers_answer_id_uindex
    on answers (answer_id);

create unique index questions_question_id_uindex
    on questions (question_id);

create unique index quizes_quiz_id_uindex
    on quizes (quiz_id);


