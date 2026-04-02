PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS scale_tier_products;
DROP TABLE IF EXISTS saved_profiles;
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
    archetype_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (archetype_id) REFERENCES archetypes(id)
);

CREATE TABLE verticals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (industry_id) REFERENCES industries(id)
);

CREATE TABLE workloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertical_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (vertical_id) REFERENCES verticals(id)
);

CREATE TABLE scale_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_id INTEGER NOT NULL,
    scale_level INTEGER NOT NULL CHECK (scale_level IN (1, 2, 3)),
    scale_label TEXT NOT NULL CHECK (scale_label IN ('Light', 'Standard', 'Heavy')),
    threshold_unit TEXT,
    threshold_min REAL,
    threshold_max REAL,
    description TEXT,
    FOREIGN KEY (workload_id) REFERENCES workloads(id)
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
    scale_tier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    rank INTEGER NOT NULL DEFAULT 1,
    UNIQUE (scale_tier_id, product_id),
    FOREIGN KEY (scale_tier_id) REFERENCES scale_tiers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    workload_id INTEGER NOT NULL,
    scale_level INTEGER NOT NULL CHECK (scale_level IN (1, 2, 3)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workload_id) REFERENCES workloads(id)
);
