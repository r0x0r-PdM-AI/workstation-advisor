PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS scale_tier_products;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS scale_tiers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS workloads;
DROP TABLE IF EXISTS verticals;
DROP TABLE IF EXISTS industries;
DROP TABLE IF EXISTS archetypes;

CREATE TABLE archetypes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_mobile_primary INTEGER DEFAULT 0
);

CREATE TABLE industries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archetype_id INTEGER NOT NULL REFERENCES archetypes(id),
    name TEXT NOT NULL
);

CREATE TABLE verticals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_id INTEGER NOT NULL REFERENCES industries(id),
    name TEXT NOT NULL
);

CREATE TABLE workloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertical_id INTEGER NOT NULL REFERENCES verticals(id),
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE scale_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_id INTEGER NOT NULL REFERENCES workloads(id),
    scale_level INTEGER NOT NULL CHECK (scale_level IN (1, 2, 3)),
    scale_label TEXT NOT NULL CHECK (scale_label IN ('Light', 'Standard', 'Heavy')),
    threshold_unit TEXT,
    threshold_min REAL,
    threshold_max REAL,
    description TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    brand TEXT NOT NULL,
    form_factor TEXT NOT NULL,
    max_cpu_cores INTEGER,
    max_cpu_tdp_watts INTEGER,
    max_ram_gb INTEGER,
    ram_slots INTEGER,
    max_gpu_vram_gb INTEGER,
    gpu_vram_range TEXT,
    supports_dual_gpu INTEGER DEFAULT 0,
    max_storage_nvme_tb REAL,
    max_psu_watts INTEGER,
    isv_certified INTEGER DEFAULT 1,
    ecc_memory INTEGER DEFAULT 1,
    os_support TEXT,
    recommended_scale_min INTEGER CHECK (recommended_scale_min IN (1, 2, 3)),
    recommended_scale_max INTEGER CHECK (recommended_scale_max IN (1, 2, 3)),
    notes TEXT
);

CREATE TABLE scale_tier_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scale_tier_id INTEGER NOT NULL REFERENCES scale_tiers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    rank INTEGER NOT NULL DEFAULT 1,
    UNIQUE (scale_tier_id, product_id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
