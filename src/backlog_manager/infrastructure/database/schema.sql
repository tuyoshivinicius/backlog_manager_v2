-- Schema: EP-001 Fundacao e Persistencia
-- Versao: 001
-- Data: 2026-02-28

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

-- Tabela Story
CREATE TABLE IF NOT EXISTS Story (
    id VARCHAR(20) PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL
);

-- Tabela Story_Dependency
CREATE TABLE IF NOT EXISTS Story_Dependency (
    story_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    depends_on_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    PRIMARY KEY (story_id, depends_on_id),
    CHECK (story_id != depends_on_id)
);

-- Indices para performance
CREATE INDEX IF NOT EXISTS idx_story_status ON Story(status);
CREATE INDEX IF NOT EXISTS idx_story_developer ON Story(developer_id);
CREATE INDEX IF NOT EXISTS idx_story_feature ON Story(feature_id);
CREATE INDEX IF NOT EXISTS idx_story_priority ON Story(priority);
