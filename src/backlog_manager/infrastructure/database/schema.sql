-- Schema: EP-001 Fundacao e Persistencia + EP-045 Planning CRUD
-- Versao: 002
-- Data: 2026-04-08

PRAGMA foreign_keys = ON;

-- Tabela Developer
CREATE TABLE IF NOT EXISTS Developer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
);

-- Tabela Feature
CREATE TABLE IF NOT EXISTS Feature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    wave INTEGER NOT NULL UNIQUE CHECK (wave > 0)
);

-- Tabela Planning
CREATE TABLE IF NOT EXISTS Planning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
    updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_planning_name ON Planning(name);

-- Tabela Story
CREATE TABLE IF NOT EXISTS Story (
    planning_id INTEGER NOT NULL REFERENCES Planning(id) ON DELETE CASCADE,
    id VARCHAR(20) NOT NULL,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL,
    PRIMARY KEY (planning_id, id)
);

CREATE INDEX IF NOT EXISTS idx_story_planning ON Story(planning_id);
CREATE INDEX IF NOT EXISTS idx_story_status ON Story(planning_id, status);
CREATE INDEX IF NOT EXISTS idx_story_developer ON Story(planning_id, developer_id);
CREATE INDEX IF NOT EXISTS idx_story_feature ON Story(planning_id, feature_id);
CREATE INDEX IF NOT EXISTS idx_story_priority ON Story(planning_id, priority);

-- Tabela Story_Dependency
CREATE TABLE IF NOT EXISTS Story_Dependency (
    planning_id INTEGER NOT NULL,
    story_id VARCHAR(20) NOT NULL,
    depends_on_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (planning_id, story_id, depends_on_id),
    FOREIGN KEY (planning_id, story_id) REFERENCES Story(planning_id, id) ON DELETE CASCADE,
    FOREIGN KEY (planning_id, depends_on_id) REFERENCES Story(planning_id, id) ON DELETE CASCADE,
    CHECK (story_id != depends_on_id)
);
