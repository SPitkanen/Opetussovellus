CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT, password TEXT, role TEXT);
CREATE TABLE courses (id SERIAL PRIMARY KEY, name TEXT, teacher_id INTEGER REFERENCES users(id), visible INTEGER);
CREATE TABLE tasks (id SERIAL PRIMARY KEY, course_id INTEGER REFERENCES courses(id), name TEXT, description TEXT, visible INTEGER, typ INTEGER);
CREATE TABLE choices (id SERIAL PRIMARY KEY, task_id INTEGER REFERENCES tasks(id), text TEXT, boolea INTEGER, typ INTEGER, visible INTEGER);
CREATE TABLE solved (id SERIAL PRIMARY KEY, task_id INTEGER REFERENCES tasks(id), user_id INTEGER REFERENCES users(id), sent TIMESTAMP);
CREATE TABLE content (id SERIAL PRIMARY KEY, course_id INTEGER REFERENCES courses(id), content TEXT, visible INTEGER);
CREATE TABLE participants (id SERIAL PRIMARY KEY, course_id INTEGER REFERENCES courses(id), user_id INTEGER REFERENCES users(id), attend INTEGER);
