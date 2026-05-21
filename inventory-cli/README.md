# Java CLI Inventory Tool

A standalone, interactive Java 21 console application for managing products and warehouse stock levels using JSON file persistence.

## Features

1. **Add Product**: Create a new product specifying SKU, name, price, stock, category, and description. Handles input validations (positive prices, unique SKUs).
2. **View Inventory**: Print all active products in a formatted console table.
3. **Update Stock**: Modify stock quantities by product ID.
4. **Delete Product**: Perform hard/soft deletion of products.
5. **Search Product**: Perform substring-match queries across SKU, name, category, and descriptions.
6. **Exit**: Gracefully exit the loop and close scanning sessions.

## Project Structure

```text
inventory-cli/
├── pom.xml
├── README.md
├── Dockerfile
└── src/main/java/com/logistics/cli/
    ├── Main.java              # Console menu loop & input parser
    ├── model/
    │   └── Product.java       # Data model with validation guards
    ├── service/
    │   └── InventoryManager.java # CRUD operations & filtering logic
    └── storage/
        └── FileStorage.java   # JSON serialization to data/inventory.json
```

## How to Build & Run

### Prerequisites
- Java 17+ SDK
- Apache Maven

### Commands

1. **Navigate to the CLI directory**:
   ```bash
   cd inventory-cli
   ```

2. **Build the fat JAR (with dependencies)**:
   ```bash
   mvn clean package
   ```

3. **Run the application**:
   ```bash
   java -jar target/inventory-cli-1.0.0.jar
   ```

### Run via Docker Compose (Interactive mode)
```bash
docker-compose run inventory-cli
```
> The container starts with `stdin_open: true` and `tty: true` to support the interactive menu loop.

## Persistence Data Location
The inventory database is saved as a structured JSON file at:
`inventory-cli/data/inventory.json`
