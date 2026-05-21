package com.logistics.cli;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * InventoryManager — core business logic layer.
 * OOP: single responsibility, depends on FileStorage abstraction.
 */
public class InventoryManager {

    private final FileStorage storage;
    private List<Product> products;
    private long nextId;

    public InventoryManager(FileStorage storage) {
        this.storage  = storage;
        this.products = storage.loadAll();
        this.nextId   = products.stream()
                .mapToLong(p -> p.getId() != null ? p.getId() : 0L)
                .max().orElse(0L) + 1;
    }

    // ── Add ─────────────────────────────────────────────────────
    public Product add(String name, String sku, String category,
                       double price, int stockQty, String description) {
        if (findBySku(sku).isPresent())
            throw new IllegalArgumentException("SKU already exists: " + sku.toUpperCase());
        Product p = new Product(nextId++, name, sku, category, price, stockQty, description);
        products.add(p);
        storage.saveAll(products);
        return p;
    }

    // ── View all ─────────────────────────────────────────────────
    public List<Product> findAll() {
        return products.stream()
                .sorted(Comparator.comparing(Product::getId))
                .collect(Collectors.toList());
    }

    // ── Find by ID ───────────────────────────────────────────────
    public Optional<Product> findById(long id) {
        return products.stream().filter(p -> p.getId() == id).findFirst();
    }

    // ── Find by SKU ──────────────────────────────────────────────
    public Optional<Product> findBySku(String sku) {
        return products.stream()
                .filter(p -> p.getSku().equalsIgnoreCase(sku))
                .findFirst();
    }

    // ── Search ───────────────────────────────────────────────────
    public List<Product> search(String keyword) {
        String kw = keyword.toLowerCase();
        return products.stream()
                .filter(p -> p.getName().toLowerCase().contains(kw)
                          || p.getSku().toLowerCase().contains(kw)
                          || p.getCategory().toLowerCase().contains(kw)
                          || (p.getDescription() != null && p.getDescription().toLowerCase().contains(kw)))
                .collect(Collectors.toList());
    }

    // ── Update stock ─────────────────────────────────────────────
    public Product updateStock(long id, int newStock) {
        Product p = findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Product not found: id=" + id));
        p.setStockQuantity(newStock);
        p.touchUpdatedAt();
        storage.saveAll(products);
        return p;
    }

    // ── Delete ───────────────────────────────────────────────────
    public boolean delete(long id) {
        Optional<Product> found = findById(id);
        if (found.isEmpty()) return false;
        products.remove(found.get());
        storage.saveAll(products);
        return true;
    }

    public int count() { return products.size(); }
}
