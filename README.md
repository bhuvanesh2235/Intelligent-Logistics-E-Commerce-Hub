# Intelligent Logistics & E-Commerce Hub

> **Capstone Internship Project** | Enterprise-grade AI-powered logistics platform integrating full-stack web, machine learning forecasting, and computer vision.

![Status](https://img.shields.io/badge/Status-Production--Oriented-success?style=flat-square)
![Modules](https://img.shields.io/badge/Modules-3%20Complete-6c63ff?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-React%20%7C%20Spring%20Boot%20%7C%20TensorFlow%20%7C%20Flask-00d4aa?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose%20Orchestrated-blue?style=flat-square)

---

## Project Overview

The **Intelligent Logistics & E-Commerce Hub** is an enterprise-grade, AI-powered logistics platform built as a capstone internship project. It demonstrates the integration of:

- A complete **React + Spring Boot** e-commerce platform with JWT authentication
- An **LSTM neural network** for time-series sales and shipment demand forecasting
- A **MobileNetV2 CNN** for automated parcel damage detection
- A **containerized microservices architecture** using Docker Compose

This project demonstrates enterprise software engineering, AI integration, MLOps workflows, secure API development, automated testing, and microservices deployment in a unified logistics ecosystem.

---

## System Architecture

```
React SPA ──► Spring Boot API ──► MySQL
     │              │
     │         JWT Auth (RBAC)
     │
     ├──► Flask API (Module 2: LSTM Forecasting)  :5001
     └──► Flask API (Module 3: CNN Damage Detect) :5002

All services orchestrated via Docker Compose
```

See [`docs/architecture.md`](docs/architecture.md) for the full ASCII architecture diagram.

---

## Key Achievements

- **5-Service Microservices Architecture**: Fully containerized and orchestrated using Docker Compose (MySQL, Spring Boot, React, and twin Flask ML APIs).
- **Full-Stack Integration**: Integrated a React frontend with a secure Spring Boot API and twin Flask ML serving pipelines.
- **Robust Security & RBAC**: Implemented secure stateless JWT authentication with strict Role-Based Access Control (RBAC) at both API and frontend levels.
- **LSTM Forecasting Engine**: Developed an LSTM recurrent neural network for time-series sales and shipment demand prediction.
- **Computer Vision Pipeline**: Built a CNN-based parcel damage detection classifier using transfer learning.
- **Automated Testing Suite**: Programmed 39 unit tests (JUnit 5 + Mockito), E2E user checkout testing (Playwright), and administrator flow automation (Selenium WebDriver).
- **Interactive AI Workflows**: Created end-to-end data pipelines connecting user order placements to automated shipping tracking, demand forecasting, and cargo validation.

---

## Core Features

- **AI-Powered Logistics Analytics**: Centralized dashboards rendering real-time KPI metrics.
- **Sales Demand Forecasting**: Interactive charting displaying 7/14/30-day forecasted volumes.
- **Shipment Demand Prediction**: Recursive multi-step forecasts for supply chain resource allocation.
- **Parcel Damage Detection**: Visual upload portal classifying cargo state with confidence scoring.
- **Role-Based Admin Dashboard**: Restricted access screens for managing catalog inventory and AI predictions.
- **Secure JWT Auth**: State-backed security utilizing secure cookies, request interception, and automatic session revocation.
- **Dockerized Deployment**: Fully self-contained builds running with standardized environment variables.
- **Multi-Level Automated Testing**: End-to-end validation covering services, user flows, and control interfaces.
- **Responsive Dark-Theme UI**: Premium user interface using vanilla CSS variables, transitions, and hover interactions.

---

## Performance Metrics

| Component | Metric | Result |
|---|---|---|
| LSTM Forecasting | MAE | 4.21 |
| LSTM Forecasting | RMSE | 5.41 |
| CNN Detection | Accuracy | 72.5% |
| CNN Detection | ROC-AUC | 0.80 |
| Backend Tests | Passing | 39/39 |
| API Response Time | Avg | ~38 ms |

> **Note:** CNN accuracy is constrained by the relatively small dataset size (800 images).

---

## Modules

### Module 1 — Full-Stack E-Commerce Platform ✅
| Feature | Technology |
|---|---|
| Single-page React app | React 18, Vite, Redux Toolkit |
| REST API | Spring Boot 3, Spring MVC |
| Authentication | JWT + Spring Security (RBAC) |
| Database | MySQL 8.2 + JPA/Hibernate |
| UI | Recharts, custom dark-theme CSS |

### Module 2 — LSTM Sales Forecasting ✅
| Feature | Value |
|---|---|
| Dataset | 50,000 e-commerce orders (1,461 daily rows) |
| Model | 2-layer LSTM (128→64 units) |
| Engineered features | 10 (rolling MA, lag, seasonality) |
| Forecast horizons | 7 / 14 / 30 days |
| API | Flask REST `/api/v2/forecast/sales` |

### Module 3 — CNN Damage Detection ✅
| Feature | Value |
|---|---|
| Dataset | 800 package images (400 damaged + 400 intact) |
| Model | Transfer Learning using MobileNetV2 (ImageNet pretrained) |
| Accuracy | 72.5% (improved using enhanced v2 pipeline) |
| ROC-AUC | 0.80 |
| API | Flask REST `/api/v3/detect-damage` |

---

## Quick Start

### Prerequisites
- Docker Desktop
- Node.js 18+
- Python 3.11+
- Java 21 LTS
- Maven 3.9+

### Option A — Docker Compose (Recommended)
```bash
# Clone
git clone https://github.com/your-username/logistics-hub.git
cd logistics-hub

# Configure
cp .env.example .env
# Edit .env with your DB_PASSWORD and JWT_SECRET

# Build & run all 5 services
docker-compose up --build

# Access
# Frontend   → http://localhost:3000
# Backend    → http://localhost:8080
# Forecasting→ http://localhost:5001
# CNN API    → http://localhost:5002
```

### Option B — Local Development
```bash
# 1. Backend
cd backend && mvn spring-boot:run

# 2. Frontend
cd frontend && npm install && npm run dev

# 3. ML Preprocessing (one-time)
cd ml-preprocessing && pip install -r requirements.txt && python preprocessing.py

# 4. Forecasting API
cd ml-forecasting
pip install -r requirements.txt
python preprocessing.py   # generate time-series data
python train_lstm.py      # train LSTM models
python app.py             # start Flask API :5001

# 5. CNN API
cd ml-damage-detection
pip install -r requirements.txt
python preprocessing.py   # download & split images
python train_cnn.py       # train MobileNetV2
python app.py             # start Flask API :5002
```

### Default Admin Credentials
```
Username: admin
Password: Admin@123
```
> ⚠️ Change these in production!

---

## API Reference

### Spring Boot Backend `:8080`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | — | Login → JWT |
| POST | `/api/auth/register` | — | Register user |
| GET | `/api/products` | JWT | List products |
| POST | `/api/orders` | JWT | Place order |
| GET | `/api/admin/dashboard` | ADMIN | Dashboard stats |

### Forecasting API `:5001`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v2/forecast/sales/quick?horizon=7` | Quick 7-day sales forecast |
| GET | `/api/v2/forecast/shipments/quick?horizon=7` | Quick 7-day shipment forecast |
| POST | `/api/v2/forecast/sales` | Custom horizon forecast |
| POST | `/api/v2/forecast/shipment-demand` | Shipment demand forecast |

### CNN Damage Detection API `:5002`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v3/detect-damage` | Upload image → damage prediction |

**Example response:**
```json
{
  "prediction": "Damaged",
  "confidence": 0.97,
  "damage_prob": 0.97,
  "class_index": 1,
  "response_time_ms": 38
}
```

---

## ML Pipeline

```
Raw Data (Kaggle)
  │
  ├─► ml-preprocessing/preprocessing.py
  │     50,000 orders → 49,844 clean rows → 20 features
  │
  ├─► ml-forecasting/
  │     daily_sales.csv (1,461 days)
  │     train_lstm.py → lstm_sales.keras + lstm_shipments.keras
  │     app.py → Flask API :5001
  │
  └─► ml-damage-detection/
        800 images → 560 train / 120 val / 120 test
        train_cnn.py → MobileNetV2 fine-tuned → best_model.keras
        app.py → Flask API :5002
```

---

## Project Structure

```
logistics-hub/
├── frontend/               # React SPA (Vite + Redux)
│   └── src/
│       ├── pages/          # 12 pages including AI dashboards
│       ├── store/slices/   # authSlice, mlSlice, orderSlice...
│       └── components/     # Sidebar, Navbar, Layout
│
├── backend/                # Spring Boot REST API
│   └── src/main/java/com/logistics/hub/
│       ├── controller/     # REST endpoints
│       ├── service/        # Business logic
│       ├── repository/     # JPA repositories
│       └── security/       # JWT filter, SecurityConfig
│
├── inventory-cli/          # Java Console CLI Inventory Reorder Tool
│   ├── src/main/java/com/logistics/cli/
│   │   ├── InventoryCliApp.java  # Interactive Console Loop Application
│   │   └── service/
│   │       └── InventoryService.java # Business Logic for Inventory Checks & Reorders
│   ├── pom.xml             # Maven dependencies
│   └── README.md           # Tool usage instructions
│
├── selenium-tests/         # Headless Chrome Selenium Admin UI Tests (JUnit 5 + POM)
│   ├── src/test/java/com/logistics/
│   │   ├── BaseTest.java        # Browser driver lifecycle setup
│   │   ├── AdminUiFlowTest.java # Admin E2E flow test cases
│   │   └── pages/               # Page Object Model components
│   │       ├── LoginPage.java
│   │       ├── DashboardPage.java
│   │       └── ProductPage.java
│   ├── pom.xml             # Selenium & WebDriverManager dependencies
│   └── README.md           # Setup and run instructions
│
├── playwright-tests/       # E2E Playwright Customer Checkout Tests (Node.js + POM)
│   ├── pages/              # Page Object Model components
│   │   ├── LoginPage.js
│   │   ├── ProductCatalogPage.js
│   │   ├── CartPage.js
│   │   ├── CheckoutPage.js
│   │   └── OrderTrackingPage.js
│   ├── tests/
│   │   └── checkout.spec.js # Checkout E2E test cases
│   ├── playwright.config.js # Test runner configuration
│   ├── package.json        # Playwright dependencies
│   └── README.md           # Run instructions
│
├── database/               # schema.sql
│
├── ml-preprocessing/       # Module 1 data pipeline
│   ├── preprocessing.py    # ETL + feature engineering
│   └── data/processed/     # cleaned_dataset.csv
│
├── ml-forecasting/         # Module 2 LSTM
│   ├── train_lstm.py       # LSTM architecture + training
│   ├── predict.py          # Recursive multi-step forecast
│   ├── app.py              # Flask API :5001
│   └── models/             # lstm_sales.keras, scalers
│
├── ml-damage-detection/    # Module 3 CNN
│   ├── train_cnn.py        # MobileNetV2 transfer learning
│   ├── predict.py          # Single/batch inference
│   ├── app.py              # Flask API :5002
│   └── models/             # best_model.keras
│
├── docs/
│   └── architecture.md     # Full system architecture diagram
│
├── docker-compose.yml      # 5-service orchestration
├── .env.example            # Environment variable template
└── README.md
```

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | React + Vite | 18 / 5 |
| State | Redux Toolkit | 2.x |
| Charts | Recharts | 2.x |
| Backend | Spring Boot | 3.x |
| Auth | Spring Security + JWT | — |
| Database | MySQL | 8.2 |
| ML Forecast | TensorFlow/Keras LSTM | 2.15 |
| ML Vision | TensorFlow/Keras MobileNetV2 | 2.15 |
| ML Serving | Flask + Flask-CORS | 3.x |
| Backend Testing | JUnit 5 + Mockito | 5.x |
| UI Automation | Selenium WebDriver | 4.x |
| E2E Testing | Playwright | 1.x |
| Data | pandas, scikit-learn, kagglehub | — |
| DevOps | Docker + Docker Compose + Nginx | — |

---

## Testing & Validation Suite

The platform includes a comprehensive, multi-layered testing and validation suite:

### 1. JUnit & Mockito Backend Tests
A suite of 39 backend tests covers validation logic, services, auth controller endpoints, and token generation utility correctness.
```bash
cd backend
mvn test
```

**Alternatively, run via Docker Compose:**
```bash
docker-compose run backend-tests
```

### 2. Selenium Admin UI Automation
Automates admin login, catalog navigation, unique product insertion flow, and forecast/damage detection dashboards checking in headless Chrome.
```bash
cd selenium-tests
mvn test
```
*Requires Google Chrome to be installed. See [`selenium-tests/README.md`](selenium-tests/README.md) for configurations.*

**Alternatively, run via Docker Compose:**
```bash
docker-compose run selenium-tests
```

### 3. Playwright Customer E2E Checkout Tests
Automates standard user flow: Login -> Browse -> Add to Cart -> Checkout Form Submission -> Order Placement -> Track Shipment verification.
```bash
cd playwright-tests
npm install
npx playwright install chromium
npm test
```
*See [`playwright-tests/README.md`](playwright-tests/README.md) for configurations.*

**Alternatively, run via Docker Compose:**
```bash
docker-compose run playwright-tests
```

---

## Java CLI Inventory Tool

A standalone console application for warehouse managers to view products, check low-stock thresholds, and reorder.
```bash
cd inventory-cli
mvn clean package
java -jar target/inventory-cli-1.0-SNAPSHOT.jar
```
*See [`inventory-cli/README.md`](inventory-cli/README.md) for full interactive loop features.*

**Alternatively, run via Docker Compose (Interactive console mode):**
```bash
docker-compose run inventory-cli
```

---

## Screenshots

> Screenshots are saved to `screenshots/` after first run.

| Screen | Description |
|---|---|
| `login.png` | JWT login page |
| `admin_dashboard.png` | KPI cards + Recharts analytics |
| `forecast_dashboard.png` | LSTM 7/30-day forecast charts |
| `damage_detection.png` | CNN upload + prediction result |
| `products.png` | E-commerce product catalog |

---

## Security

- **JWT Authentication** — all API routes require Bearer token
- **RBAC** — USER and ADMIN roles enforced in Spring Security
- **Admin routes** — `/admin`, `/forecast`, `/damage` require ADMIN role
- **Axios interceptor** — auto-attaches token; auto-logout on 401
- **CORS** — configured per service; restricted in production

---

## Future Improvements

- [ ] Module 4: Real-time WebSocket order tracking
- [ ] Attention-mechanism LSTM for better forecasting accuracy
- [ ] Probabilistic CNN uncertainty (MC Dropout)
- [ ] Multi-GPU training support
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline (GitHub Actions)

---

## Author

Bhuvanesh K — Internship Capstone Project  
*Intelligent Logistics & E-Commerce Hub*  
BCT Internship Program, 2026

---

## License

MIT License © 2026 Bhuvanesh K
