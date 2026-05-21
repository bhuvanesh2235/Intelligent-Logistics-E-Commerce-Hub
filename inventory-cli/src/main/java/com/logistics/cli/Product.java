package com.logistics.cli;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Represents a product in the inventory.
 * OOP design: encapsulated fields with validation.
 */
public class Product {

    private Long id;
    private String name;
    private String sku;
    private String category;
    private double price;
    private int stockQuantity;
    private String description;
    private String createdAt;
    private String updatedAt;

    // Required for Jackson deserialization
    public Product() {}

    public Product(Long id, String name, String sku, String category,
                   double price, int stockQuantity, String description) {
        this.id            = id;
        this.name          = validate(name, "Name");
        this.sku           = validate(sku, "SKU").toUpperCase();
        this.category      = validate(category, "Category");
        this.price         = validatePrice(price);
        this.stockQuantity = validateQty(stockQuantity);
        this.description   = description;
        String now         = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        this.createdAt     = now;
        this.updatedAt     = now;
    }

    // ── Validation helpers ───────────────────────────────────────
    private static String validate(String value, String field) {
        if (value == null || value.isBlank())
            throw new IllegalArgumentException(field + " cannot be blank.");
        return value.trim();
    }
    private static double validatePrice(double price) {
        if (price < 0) throw new IllegalArgumentException("Price cannot be negative.");
        return price;
    }
    private static int validateQty(int qty) {
        if (qty < 0) throw new IllegalArgumentException("Stock quantity cannot be negative.");
        return qty;
    }

    // ── Getters & Setters ────────────────────────────────────────
    public Long getId()                  { return id; }
    public void setId(Long id)           { this.id = id; }

    public String getName()              { return name; }
    public void setName(String name)     { this.name = validate(name, "Name"); }

    public String getSku()               { return sku; }
    public void setSku(String sku)       { this.sku = validate(sku, "SKU").toUpperCase(); }

    public String getCategory()          { return category; }
    public void setCategory(String cat)  { this.category = validate(cat, "Category"); }

    public double getPrice()             { return price; }
    public void setPrice(double price)   { this.price = validatePrice(price); }

    public int getStockQuantity()               { return stockQuantity; }
    public void setStockQuantity(int stockQuantity) {
        this.stockQuantity = validateQty(stockQuantity);
    }

    public String getDescription()                   { return description; }
    public void setDescription(String description)   { this.description = description; }

    public String getCreatedAt()                     { return createdAt; }
    public void setCreatedAt(String createdAt)       { this.createdAt = createdAt; }

    public String getUpdatedAt()                     { return updatedAt; }
    public void setUpdatedAt(String updatedAt)       { this.updatedAt = updatedAt; }

    public void touchUpdatedAt() {
        this.updatedAt = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
    }

    @Override
    public String toString() {
        return String.format(
            "│ %-4d │ %-20s │ %-12s │ %-15s │ %8.2f │ %5d │",
            id, truncate(name, 20), truncate(sku, 12), truncate(category, 15), price, stockQuantity);
    }

    private String truncate(String s, int max) {
        if (s == null) return "";
        return s.length() <= max ? s : s.substring(0, max - 1) + "…";
    }
}
