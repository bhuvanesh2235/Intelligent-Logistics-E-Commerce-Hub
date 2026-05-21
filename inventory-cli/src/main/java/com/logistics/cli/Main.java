package com.logistics.cli;

import java.util.List;
import java.util.Optional;
import java.util.Scanner;

/**
 * Main — console menu UI entry point.
 * Demonstrates OOP, exception handling, input validation.
 */
public class Main {

    private static final String DATA_FILE = "data/inventory.json";
    private static InventoryManager manager;
    private static Scanner scanner;

    public static void main(String[] args) {
        System.out.println("\n╔══════════════════════════════════════════════╗");
        System.out.println("║   🏭  Intelligent Logistics — Inventory CLI  ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        FileStorage storage = new FileStorage(DATA_FILE);
        manager  = new InventoryManager(storage);
        scanner  = new Scanner(System.in);

        boolean running = true;
        while (running) {
            printMenu();
            String choice = scanner.nextLine().trim();
            switch (choice) {
                case "1" -> addProduct();
                case "2" -> viewInventory();
                case "3" -> updateStock();
                case "4" -> deleteProduct();
                case "5" -> searchProduct();
                case "6" -> { System.out.println("\n👋 Goodbye!\n"); running = false; }
                default  -> System.out.println("⚠  Invalid option. Please enter 1–6.\n");
            }
        }
        scanner.close();
    }

    // ── Menu ─────────────────────────────────────────────────────
    private static void printMenu() {
        System.out.println("┌──────────────────────────────────┐");
        System.out.println("│            MAIN MENU             │");
        System.out.println("├──────────────────────────────────┤");
        System.out.println("│  1. Add Product                  │");
        System.out.println("│  2. View Inventory               │");
        System.out.println("│  3. Update Stock                 │");
        System.out.println("│  4. Delete Product               │");
        System.out.println("│  5. Search Product               │");
        System.out.println("│  6. Exit                         │");
        System.out.println("└──────────────────────────────────┘");
        System.out.print("  Enter choice: ");
    }

    // ── 1. Add ───────────────────────────────────────────────────
    private static void addProduct() {
        System.out.println("\n── Add New Product ──────────────────");
        try {
            String name     = prompt("Product Name      : ");
            String sku      = prompt("SKU               : ");
            String category = prompt("Category          : ");
            double price    = promptDouble("Price (₹)         : ");
            int    stock    = promptInt("Stock Quantity    : ");
            String desc     = promptOptional("Description (opt) : ");

            Product p = manager.add(name, sku, category, price, stock, desc);
            System.out.println("\n✅ Product added successfully!");
            printProductDetail(p);
        } catch (IllegalArgumentException e) {
            System.out.println("❌ Error: " + e.getMessage());
        }
        System.out.println();
    }

    // ── 2. View ──────────────────────────────────────────────────
    private static void viewInventory() {
        List<Product> list = manager.findAll();
        System.out.println("\n── Inventory (" + list.size() + " products) ──────────────");
        if (list.isEmpty()) {
            System.out.println("  (No products in inventory)\n");
            return;
        }
        printTableHeader();
        list.forEach(p -> System.out.println(p));
        printTableFooter();
        System.out.println();
    }

    // ── 3. Update Stock ──────────────────────────────────────────
    private static void updateStock() {
        System.out.println("\n── Update Stock ─────────────────────");
        try {
            long id    = promptLong("Product ID  : ");
            int  stock = promptInt("New Stock   : ");
            Product p  = manager.updateStock(id, stock);
            System.out.println("✅ Stock updated → " + p.getName() + " = " + stock + " units\n");
        } catch (IllegalArgumentException e) {
            System.out.println("❌ Error: " + e.getMessage() + "\n");
        }
    }

    // ── 4. Delete ────────────────────────────────────────────────
    private static void deleteProduct() {
        System.out.println("\n── Delete Product ───────────────────");
        try {
            long id = promptLong("Product ID to delete: ");
            Optional<Product> found = manager.findById(id);
            if (found.isEmpty()) {
                System.out.println("❌ No product found with ID " + id + "\n");
                return;
            }
            System.out.print("⚠  Delete \"" + found.get().getName() + "\"? (yes/no): ");
            String confirm = scanner.nextLine().trim();
            if ("yes".equalsIgnoreCase(confirm)) {
                manager.delete(id);
                System.out.println("✅ Product deleted.\n");
            } else {
                System.out.println("Cancelled.\n");
            }
        } catch (IllegalArgumentException e) {
            System.out.println("❌ Error: " + e.getMessage() + "\n");
        }
    }

    // ── 5. Search ────────────────────────────────────────────────
    private static void searchProduct() {
        System.out.println("\n── Search Products ──────────────────");
        String keyword = prompt("Enter keyword (name/SKU/category): ");
        List<Product> results = manager.search(keyword);
        System.out.println("Found " + results.size() + " result(s):");
        if (results.isEmpty()) {
            System.out.println("  (No matches)\n");
            return;
        }
        printTableHeader();
        results.forEach(System.out::println);
        printTableFooter();
        System.out.println();
    }

    // ── Table formatting ─────────────────────────────────────────
    private static void printTableHeader() {
        System.out.println("┌──────┬──────────────────────┬──────────────┬─────────────────┬──────────┬───────┐");
        System.out.println("│ ID   │ Name                 │ SKU          │ Category        │    Price │ Stock │");
        System.out.println("├──────┼──────────────────────┼──────────────┼─────────────────┼──────────┼───────┤");
    }
    private static void printTableFooter() {
        System.out.println("└──────┴──────────────────────┴──────────────┴─────────────────┴──────────┴───────┘");
    }
    private static void printProductDetail(Product p) {
        System.out.println("  ID       : " + p.getId());
        System.out.println("  Name     : " + p.getName());
        System.out.println("  SKU      : " + p.getSku());
        System.out.println("  Category : " + p.getCategory());
        System.out.println("  Price    : ₹" + String.format("%.2f", p.getPrice()));
        System.out.println("  Stock    : " + p.getStockQuantity());
    }

    // ── Input helpers ────────────────────────────────────────────
    private static String prompt(String msg) {
        System.out.print(msg);
        String val = scanner.nextLine().trim();
        if (val.isBlank()) throw new IllegalArgumentException("Input cannot be empty.");
        return val;
    }
    private static String promptOptional(String msg) {
        System.out.print(msg);
        return scanner.nextLine().trim();
    }
    private static double promptDouble(String msg) {
        try { return Double.parseDouble(prompt(msg)); }
        catch (NumberFormatException e) { throw new IllegalArgumentException("Invalid number for price."); }
    }
    private static int promptInt(String msg) {
        try { return Integer.parseInt(prompt(msg)); }
        catch (NumberFormatException e) { throw new IllegalArgumentException("Invalid integer value."); }
    }
    private static long promptLong(String msg) {
        try { return Long.parseLong(prompt(msg)); }
        catch (NumberFormatException e) { throw new IllegalArgumentException("Invalid ID value."); }
    }
}
