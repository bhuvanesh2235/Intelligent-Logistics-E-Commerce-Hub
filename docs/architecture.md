```
╔══════════════════════════════════════════════════════════════════════════════════╗
║          INTELLIGENT LOGISTICS & E-COMMERCE HUB — SYSTEM ARCHITECTURE          ║
╚══════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────── USER BROWSER ────────────────────────────────────┐
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                    REACT SPA (Vite + Redux Toolkit)                       │  │
│   │                                                                          │  │
│   │  ┌──────────────┐  ┌────────────────┐  ┌───────────────────────────┐   │  │
│   │  │  Auth Pages  │  │  E-Commerce    │  │    Admin AI Dashboard     │   │  │
│   │  │  Login       │  │  Home/Products │  │  ┌──────────────────────┐ │   │  │
│   │  │  Register    │  │  Cart/Checkout │  │  │  📈 Forecast Charts  │ │   │  │
│   │  └──────────────┘  │  Orders/Track  │  │  │  🔍 Damage Detection │ │   │  │
│   │                    └────────────────┘  │  │  📊 KPI Dashboard    │ │   │  │
│   │                                        │  └──────────────────────┘ │   │  │
│   │                                        └───────────────────────────┘   │  │
│   │                                                                          │  │
│   │  ┌────────────────────────────────────────────────────────────────────┐ │  │
│   │  │  Axios API Client (JWT interceptor — auto-attach Bearer token)     │ │  │
│   │  └────────────────────────────────────────────────────────────────────┘ │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                          │                    │              │
                    REST /api             REST /api/v2   REST /api/v3
                    (JWT Auth)           (Forecasting)  (CNN Detect)
                          │                    │              │
┌─────────────────────────┼────────────────────┼──────────────┼──────────────────┐
│                   DOCKER COMPOSE NETWORK (logistics_network)                    │
│                                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐  │
│  │  SPRING BOOT BACKEND │  │  FLASK FORECASTING   │  │  FLASK CNN API      │  │
│  │  Port: 8080          │  │  (Module 2)          │  │  (Module 3)         │  │
│  │                      │  │  Port: 5001          │  │  Port: 5002         │  │
│  │  • JWT Auth (RBAC)   │  │                      │  │                     │  │
│  │  • REST Controllers  │  │  GET  /health        │  │  GET  /health       │  │
│  │  • JPA/Hibernate     │  │  GET  /api/v2/info   │  │  POST /api/v3/      │  │
│  │  • Spring Security   │  │  POST /api/v2/       │  │       detect-damage │  │
│  │  • CORS config       │  │    forecast/sales    │  │                     │  │
│  └──────────┬───────────┘  │  POST /api/v2/       │  │  MobileNetV2 CNN   │  │
│             │              │    forecast/shipments │  │  (best_model.keras) │  │
│             │              │                      │  └─────────────────────┘  │
│             │              │  LSTM Model          │                           │
│             │              │  (lstm_sales.keras)  │  ┌─────────────────────┐  │
│  ┌──────────▼───────────┐  └──────────────────────┘  │  ML PREPROCESSING   │  │
│  │  MYSQL DATABASE      │                            │  (Module 1 support) │  │
│  │  Port: 3306          │  ┌──────────────────────┐  │  Kaggle dataset ETL │  │
│  │                      │  │  NGINX (Frontend)    │  │  Feature engineering│  │
│  │  • users             │  │  Port: 3000 → 80     │  └─────────────────────┘  │
│  │  • products          │  │  Reverse proxy →     │                           │
│  │  • orders            │  │  /api/* → backend    │                           │
│  │  • shipments         │  │  /* → React SPA      │                           │
│  │  • order_items       │  └──────────────────────┘                           │
│  └──────────────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

══════════════════════════════════════════════════════════════════════════════════

AUTHENTICATION FLOW (JWT):

  User → POST /api/auth/login → {token}
  User → GET  /api/v2/*      → Authorization: Bearer {token} → 200/401
  User → POST /api/v3/*      → Authorization: Bearer {token} → 200/401

══════════════════════════════════════════════════════════════════════════════════

DATA FLOW:

  Kaggle CSV (50K records)
    └──▶ ml-preprocessing/preprocessing.py
           └──▶ cleaned_dataset.csv (49,844 rows, 20 features)
                  └──▶ ml-forecasting/preprocessing.py
                         └──▶ daily_sales.csv (1,461 days)
                                └──▶ LSTM training → lstm_sales.keras
                                       └──▶ Flask API → /api/v2/forecast/sales

  Kaggle Image Dataset (800 images: 400 damaged + 400 intact)
    └──▶ ml-damage-detection/preprocessing.py
           └──▶ data/train/ + data/val/ + data/test/
                  └──▶ MobileNetV2 fine-tuning → best_model.keras
                         └──▶ Flask API → /api/v3/detect-damage

══════════════════════════════════════════════════════════════════════════════════

TECH STACK SUMMARY:

  Layer           Technology
  ─────────────── ──────────────────────────────────────────────
  Frontend        React 18, Vite, Redux Toolkit, Recharts
  Backend         Spring Boot 3, Spring Security, JPA, JWT
  Database        MySQL 8.2
  ML — Forecast   Python 3.11, TensorFlow/Keras LSTM, Flask
  ML — Vision     Python 3.11, TensorFlow/Keras MobileNetV2, Flask
  Preprocessing   pandas, scikit-learn, numpy, kagglehub
  DevOps          Docker, Docker Compose, Nginx
  Auth            JWT RS256, RBAC (USER / ADMIN)

══════════════════════════════════════════════════════════════════════════════════
```
