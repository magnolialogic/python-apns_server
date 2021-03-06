/* DB initialization for https://github.com/magnolialogic/python-apns_server */

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS bundle;
DROP TABLE IF EXISTS token;
DROP TABLE IF EXISTS session;
DROP TABLE IF EXISTS session_relationship;

CREATE TABLE user (
	id TEXT PRIMARY KEY
);

CREATE TABLE bundle (
	id TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE token (
	id TEXT NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	bundle_id TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(id),
	FOREIGN KEY (bundle_id) REFERENCES bundle(id)
);

CREATE TABLE session (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	active INTEGER DEFAULT 0 NOT NULL CHECK(active >= 0 AND active <= 1)
);

CREATE TABLE session_relationship (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	session_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(id),
	FOREIGN KEY (session_id) REFERENCES session(id)
);
