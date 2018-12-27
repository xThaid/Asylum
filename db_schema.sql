BEGIN TRANSACTION;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS energy;
DROP TABLE IF EXISTS blinds_task;
DROP TABLE IF EXISTS blinds_task_history;
DROP TABLE IF EXISTS blinds_schedule;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE user_mac_address(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mac_address TEXT UNIQUE NOT NULL,
  user_id INTEGER DEFAULT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE energy(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  production INTEGER NOT NULL,
  import INTEGER NOT NULL,
  export INTEGER NOT NULL,
  power_production INTEGER NOT NULL,
  power_import INTEGER NOT NULL,
  power_export INTEGER NOT NULL,

  CONSTRAINT time_unique UNIQUE (time)
);

CREATE TABLE blinds_task(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  device INTEGER NOT NULL,
  action INTEGER NOT NULL,
  user_id INTEGER DEFAULT NULL,
  schedule_id INTEGER DEFAULT NULL,
  timeout INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(user_id) REFERENCES user(id)
  FOREIGN KEY(schedule_id) REFERENCES blinds_schedule(id)
);

CREATE TABLE blinds_task_history(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  device INTEGER NOT NULL,
  action INTEGER NOT NULL,
  user_id INTEGER DEFAULT NULL,
  schedule_id INTEGER DEFAULT NULL,
  status INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE blinds_schedule(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  device INTEGER NOT NULL,
  action INTEGER NOT NULL,
  hour_type INTEGER NOT NULL,
  time_offset INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE energy_daily(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day_ordinal INTEGER NOT NULL,
  production INTEGER NOT NULL,
  import INTEGER NOT NULL,
  export INTEGER NOT NULL,
  production_offset INTEGER NOT NULL,
  import_offset INTEGER NOT NULL,
  export_offset INTEGER NOT NULL,
  max_power_production INTEGER NOT NULL,
  max_power_import INTEGER NOT NULL,
  max_power_export INTEGER NOT NULL,
  max_power_consumption INTEGER NOT NULL,
  max_power_use INTEGER NOT NULL,
  max_power_store INTEGER NOT NULL
);

COMMIT;
