CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    topic_id INT REFERENCES topics(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL
);

CREATE TABLE choices (
    id SERIAL PRIMARY KEY,
    question_id INT REFERENCES questions(id) ON DELETE CASCADE,
    choice_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL
);