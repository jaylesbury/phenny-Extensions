CREATE TABLE genres(id INTEGER PRIMARY KEY, name VARCHAR(50));
CREATE TABLE recommendations(id INTEGER PRIMARY KEY, artist VARCHAR(500), album VARCHAR(500), url VARCHAR(40), genre_id INTEGER, user_id INTEGER);
CREATE TABLE users(id INTEGER PRIMARY KEY, name VARCHAR(15));
