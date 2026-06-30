-- Nemory schema. Designed so future features (photos, tags, attachments) can be
-- added in new tables/columns without breaking existing data.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activities (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id           INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    title              TEXT    NOT NULL,
    description        TEXT    NOT NULL DEFAULT '',
    activity_date      TEXT    NOT NULL,                 -- ISO date: YYYY-MM-DD
    reminder_interval  INTEGER,                          -- NULL = no reminder
    reminder_unit      TEXT,                             -- 'days' | 'months' | 'years'
    next_reminder_date TEXT,                             -- ISO date, computed
    created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Most queries filter activities by asset or order by reminder/date.
CREATE INDEX IF NOT EXISTS idx_activities_asset       ON activities(asset_id);
CREATE INDEX IF NOT EXISTS idx_activities_next_remind ON activities(next_reminder_date);
CREATE INDEX IF NOT EXISTS idx_activities_date        ON activities(activity_date);
