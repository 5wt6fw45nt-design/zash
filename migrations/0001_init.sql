-- Zash: usuarios, alertas, kv y cola de envíos. Sin pagos: Zash es gratis.
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  created_at INTEGER NOT NULL,
  blocked INTEGER NOT NULL DEFAULT 0,
  country TEXT,
  tz TEXT NOT NULL DEFAULT 'Europe/Madrid',
  source TEXT,
  daily INTEGER NOT NULL DEFAULT 1,
  lesson INTEGER NOT NULL DEFAULT 0,
  uses_date TEXT,
  uses INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  asset TEXT NOT NULL,
  op TEXT NOT NULL CHECK (op IN ('>', '<')),
  price REAL NOT NULL,
  currency TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS alerts_user ON alerts (user_id);
CREATE TABLE IF NOT EXISTS outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);
