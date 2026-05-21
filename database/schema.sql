-- =============================================================
-- Intelligent Logistics & E-Commerce Hub — Module 1
-- MySQL Schema
-- =============================================================

CREATE DATABASE IF NOT EXISTS logistics_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE logistics_hub;

-- =============================================================
-- 1. USERS
-- =============================================================
CREATE TABLE users (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('ADMIN','CUSTOMER') NOT NULL DEFAULT 'CUSTOMER',
    full_name     VARCHAR(100),
    phone         VARCHAR(20),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role  (role)
);

-- =============================================================
-- 2. CATEGORIES
-- =============================================================
CREATE TABLE categories (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 3. WAREHOUSES
-- =============================================================
CREATE TABLE warehouses (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    block_code   VARCHAR(1)   NOT NULL UNIQUE,
    name         VARCHAR(100) NOT NULL,
    location     VARCHAR(200),
    capacity     INT          NOT NULL DEFAULT 1000,
    current_load INT          NOT NULL DEFAULT 0,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_warehouse_block (block_code)
);

-- =============================================================
-- 4. PRODUCTS
-- =============================================================
CREATE TABLE products (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku              VARCHAR(50)    NOT NULL UNIQUE,
    name             VARCHAR(200)   NOT NULL,
    description      TEXT,
    category_id      BIGINT         NOT NULL,
    cost             DECIMAL(10,2)  NOT NULL,
    price            DECIMAL(10,2)  NOT NULL,
    weight_grams     INT            NOT NULL DEFAULT 0,
    importance       ENUM('LOW','MEDIUM','HIGH') NOT NULL DEFAULT 'MEDIUM',
    stock_quantity   INT            NOT NULL DEFAULT 0,
    warehouse_id     BIGINT,
    is_active        BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id)  REFERENCES categories(id)  ON DELETE RESTRICT,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)  ON DELETE SET NULL,
    INDEX idx_products_sku      (sku),
    INDEX idx_products_category (category_id)
);

-- =============================================================
-- 5. INVENTORY
-- =============================================================
CREATE TABLE inventory (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id   BIGINT    NOT NULL UNIQUE,
    quantity     INT       NOT NULL DEFAULT 0,
    reorder_level INT      NOT NULL DEFAULT 10,
    last_restocked TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- =============================================================
-- 6. ORDERS
-- =============================================================
CREATE TABLE orders (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number     VARCHAR(50) NOT NULL UNIQUE,
    customer_id      BIGINT      NOT NULL,
    status           ENUM('PENDING','CONFIRMED','PROCESSING','SHIPPED','DELIVERED','CANCELLED')
                         NOT NULL DEFAULT 'PENDING',
    total_amount     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount  DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    shipping_address TEXT         NOT NULL,
    notes            TEXT,
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status   (status),
    INDEX idx_orders_number   (order_number)
);

-- =============================================================
-- 7. ORDER ITEMS
-- =============================================================
CREATE TABLE order_items (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id    BIGINT        NOT NULL,
    product_id  BIGINT        NOT NULL,
    quantity    INT           NOT NULL,
    unit_price  DECIMAL(10,2) NOT NULL,
    subtotal    DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_order_items_order (order_id)
);

-- =============================================================
-- 8. SHIPMENTS
-- =============================================================
CREATE TABLE shipments (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    tracking_number  VARCHAR(50)  NOT NULL UNIQUE,
    order_id         BIGINT       NOT NULL UNIQUE,
    warehouse_id     BIGINT,
    mode             ENUM('Ship','Flight','Road') NOT NULL DEFAULT 'Road',
    status           ENUM('PREPARING','IN_TRANSIT','OUT_FOR_DELIVERY','DELIVERED','FAILED')
                         NOT NULL DEFAULT 'PREPARING',
    carrier          VARCHAR(100),
    weight_grams     INT          NOT NULL DEFAULT 0,
    customer_care_calls INT       NOT NULL DEFAULT 0,
    customer_rating  INT          CHECK (customer_rating BETWEEN 1 AND 5),
    discount_offered DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    delivered_on_time BOOLEAN,
    estimated_delivery DATE,
    actual_delivery   DATE,
    created_at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id)     REFERENCES orders(id)     ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE SET NULL,
    INDEX idx_shipments_tracking (tracking_number),
    INDEX idx_shipments_status   (status)
);

-- =============================================================
-- SEED DATA
-- =============================================================

-- Categories
INSERT INTO categories (name, description) VALUES
  ('Electronics',    'Mobile, laptops, accessories'),
  ('Clothing',       'Men, women, kids apparel'),
  ('Home & Kitchen', 'Furniture, cookware, decor'),
  ('Books',          'Textbooks, novels, guides'),
  ('Sports',         'Fitness, outdoor, gear');

-- Warehouses (A–E from Kaggle dataset)
INSERT INTO warehouses (block_code, name, location, capacity) VALUES
  ('A', 'Alpha Warehouse',   'Mumbai, MH',  2000),
  ('B', 'Bravo Warehouse',   'Delhi, DL',   1800),
  ('C', 'Charlie Warehouse', 'Bangalore, KA', 2200),
  ('D', 'Delta Warehouse',   'Chennai, TN', 1500),
  ('F', 'Foxtrot Warehouse', 'Hyderabad, TS', 1700);

-- Admin user (password: Admin@123 — BCrypt hash)
INSERT INTO users (username, email, password_hash, role, full_name) VALUES
  ('admin', 'admin@logisticshub.com',
   '$2b$12$nFSVNRkQr8d1NZaP6Hxj9OyauB4R4Qry9.UIwIJxnfW9r2UvzqZZ6',
   'ADMIN', 'System Administrator');

-- Sample customer
INSERT INTO users (username, email, password_hash, role, full_name, phone) VALUES
  ('john_doe', 'john@example.com',
   '$2b$12$nFSVNRkQr8d1NZaP6Hxj9OyauB4R4Qry9.UIwIJxnfW9r2UvzqZZ6',
   'CUSTOMER', 'John Doe', '+91-9876543210');

-- Sample products
INSERT INTO products (sku, name, category_id, cost, price, weight_grams, importance, stock_quantity, warehouse_id) VALUES
  ('ELEC-001', 'Wireless Headphones',  1, 1500.00, 2499.00, 350,  'MEDIUM', 100, 1),
  ('ELEC-002', 'Smartphone Pro X',     1, 18000.00,24999.00, 185, 'HIGH',   50,  2),
  ('CLTH-001', 'Cotton T-Shirt',       2, 200.00,  599.00,   250,  'LOW',   300, 3),
  ('HOME-001', 'Non-stick Cookware Set',3, 800.00, 1899.00, 2100, 'MEDIUM', 80,  4),
  ('BOOK-001', 'Data Structures Guide',4, 250.00,  499.00,   450,  'LOW',   200, 5);

-- Inventory
INSERT INTO inventory (product_id, quantity, reorder_level) VALUES
  (1, 100, 15), (2, 50, 5), (3, 300, 30), (4, 80, 10), (5, 200, 20);
