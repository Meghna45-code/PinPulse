-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop tables if they exist
DROP TABLE IF EXISTS checkout_velocity;
DROP TABLE IF EXISTS outfit_completer;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS regional_boutique_trends;
DROP TABLE IF EXISTS creators;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS products;

-- Create products table
CREATE TABLE products (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    product_url TEXT,
    tags TEXT[] NOT NULL DEFAULT '{}',
    zip_codes TEXT[] NOT NULL DEFAULT '{}', -- Localized availability (empty means global)
    embedding vector(512) -- 512-dimensional vector for CLIP embeddings
);

-- Create calendar table
CREATE TABLE calendar (
    zip_code TEXT NOT NULL,
    date DATE NOT NULL,
    event_name TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'festival', -- 'festival', 'pre_wedding', 'wedding_day', 'post_wedding'
    attire_tags TEXT[] NOT NULL DEFAULT '{}',
    is_festive BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (zip_code, date)
);

-- Create checkout_velocity table
CREATE TABLE checkout_velocity (
    product_id BIGINT NOT NULL,
    zip_code TEXT NOT NULL,
    velocity_score FLOAT NOT NULL DEFAULT 0.0, -- 0.0 to 1.0 normalized
    units_last_hour INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (product_id, zip_code),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Create outfit_completer table
CREATE TABLE outfit_completer (
    primary_item_id BIGINT NOT NULL,
    suggested_accessory_id BIGINT,
    suggested_footwear_id BIGINT,
    occasion_tag TEXT NOT NULL,
    PRIMARY KEY (primary_item_id, occasion_tag),
    FOREIGN KEY (primary_item_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Create regional_boutique_trends table
CREATE TABLE regional_boutique_trends (
    store_id VARCHAR(50) PRIMARY KEY,
    zip_code VARCHAR(10),
    locality VARCHAR(100),
    store_name VARCHAR(100),
    social_signal_source VARCHAR(50),
    simulated_engagement INT,
    extracted_visual_trend VARCHAR(50),
    style_vibe_cluster VARCHAR(50)
);

-- Create creators table
CREATE TABLE creators (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    youtube_url TEXT,
    demographic TEXT NOT NULL, -- 'millennial', 'gen-z'
    subscriber_weight FLOAT NOT NULL DEFAULT 1.0,
    embedding vector(512),
    confidence_score FLOAT NOT NULL DEFAULT 1.0,
    zip_code TEXT NOT NULL
);

-- Create stores table
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    rating FLOAT NOT NULL DEFAULT 3.0,
    review_count INT NOT NULL DEFAULT 0,
    estimated_cost INT NOT NULL DEFAULT 0,
    embedding vector(512),
    zip_code TEXT NOT NULL
);
