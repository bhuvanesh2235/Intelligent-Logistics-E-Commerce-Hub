# Logistics Hub Playwright E2E Automation Suite

This directory contains automated End-to-End E2E test suites for the customer checkout and order tracking flow of the **Intelligent Logistics & E-Commerce Hub**.

## Technology Stack & Requirements

- **Runtime**: Node.js (v18+)
- **Testing Framework**: Playwright Test
- **Browsers**: Chromium (Default)
- **Design Pattern**: Page Object Model (POM)

## Test Coverage

The suite automates the complete customer checkout lifecycle:
1. **User Login**: Logs in using customer account credentials.
2. **Product Browsing**: Navigates to the product listings catalog.
3. **Cart Addition**: Selects and adds products to the shopping cart.
4. **Checkout Processing**: Fills out the delivery address, order notes, and places the order.
5. **Order Verification**: Confirms order creation on the orders page and extracts the tracking identifier.
6. **Shipment Tracking**: Searches for the package using the tracking page and verifies delivery stage progress.

## Project Structure

```text
playwright-tests/
├── playwright.config.js
├── package.json
├── README.md
├── pages/                       # Page Object Model Layer
│   ├── LoginPage.js
│   ├── ProductCatalogPage.js
│   ├── CartPage.js
│   ├── CheckoutPage.js
│   └── OrderTrackingPage.js
└── tests/                       # Test Specification Layer
    └── checkout.spec.js
```

## Setup & Running the Tests

### Prerequisites
1. Ensure the web application frontend is running locally on `http://localhost:3000`.

### Install Dependencies
Run the following command from the `playwright-tests/` directory:
```bash
npm install
npx playwright install chromium
```

### Run E2E Tests
To execute the tests in headless mode:
```bash
npm test
```

To run the tests with the visual headed browser:
```bash
npm run test:headed
```

To view HTML test results and execution traces:
```bash
npm run show-report
```

### Run via Docker Compose
Requires the core services to be running (`docker-compose up -d`) first:
```bash
docker-compose run playwright-tests
```
> This uses the official `mcr.microsoft.com/playwright:v1.44.0-jammy` image with Chromium pre-installed and runs in headless mode.

