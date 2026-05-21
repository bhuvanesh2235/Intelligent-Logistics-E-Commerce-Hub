# Logistics Hub Selenium UI Automation Suite

This directory contains automated End-to-End UI tests for the **Intelligent Logistics & E-Commerce Hub** admin portal.

## Technology Stack & Requirements

- **Java Version**: 21
- **Testing Framework**: JUnit 5
- **Automation Tool**: Selenium WebDriver 4
- **Driver Management**: WebDriverManager (Automated download and setup of ChromeDriver)
- **Design Pattern**: Page Object Model (POM)

## Test Coverage

The suite automates the complete administrator flow:
1. **Admin Login**: Signs in securely using administrator credentials.
2. **Sidebar Navigation**: Verifies page routing links.
3. **Product Creation**: Automates filling the multi-section form to create products.
4. **AI Forecast Dashboard Verification**: Validates rendering of forecasted metrics.
5. **Damage Detection Dashboard Verification**: Confirms MobileNetV2 damage analyzer elements load correctly.

## Project Structure

```text
selenium-tests/
├── pom.xml
├── README.md
└── src/
    └── test/
        └── java/
            └── com/
                └── logistics/
                    ├── BaseTest.java            # Browser setup/teardown & Configuration
                    ├── AdminUiFlowTest.java     # E2E Test Scenarios
                    └── pages/                   # Page Object Model Layer
                        ├── LoginPage.java
                        ├── DashboardPage.java
                        └── ProductPage.java
```

## Setup & Running the Tests

### Prerequisites
1. Ensure the web application frontend is running locally on `http://localhost:3000`.
2. Ensure you have Chrome Browser installed.

### Command to Run Tests
From this directory (`selenium-tests/`), execute:
```bash
mvn clean test
```

*Note: The tests run in **headless** mode by default (`--headless=new`) for maximum speed, compatibility, and execution stability in background scripts and CI pipelines.*

### Run via Docker Compose
Requires the core services to be running (`docker-compose up -d`) first:
```bash
docker-compose run selenium-tests
```
> This builds a Docker image with Google Chrome pre-installed, executes the full test suite, and exits.

