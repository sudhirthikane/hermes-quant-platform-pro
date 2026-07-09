# 🏦 TaxMaximizer Wizard - Indian Income Tax SaaS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red)

**TaxMaximizer Wizard** is an enterprise-grade, highly secure software-as-a-service (SaaS) application designed to automate Indian Income Tax calculations (AY 2025-26). It features a robust mathematical engine that dynamically compares the Old vs. New tax regimes, supports complex capital gains and business income filings, and generates exact Income Tax Department (ITD) compliant JSON payloads.

---

## ✨ Enterprise Features

### 🧮 Advanced Tax Engine
- **Full ITR Suite Support:** Modules for **ITR-1** (Salary), **ITR-2** (Capital Gains), **ITR-3** (Business/F&O), **ITR-4** (Sugam), and **ITR-5** (Partnership Firms).
- **Dynamic Regime Comparison:** Real-time dual calculation of Old vs. New Tax Regimes, including dynamic marginal relief, Section 87A rebates, and 4% Health & Education cess.
- **Section 40(b) Automation:** Automatically enforces strict remuneration limits for Partnership Firms and LLPs.

### 🔐 Bank-Grade Security (DPDP Act Compliant)
- **Bcrypt Authentication:** Zero-knowledge proof login system where raw passwords are mathematically salted and hashed.
- **AES-256 Field-Level Encryption:** Sensitive user data (like PAN numbers) and financial state dictionaries are scrambled using the `cryptography` Fernet library before ever touching the database.
- **Strict Route Protection:** Unauthenticated users are instantly intercepted and blocked from accessing financial endpoints.

### ☁️ Multi-Tenant Cloud Architecture
- **Persistent Workspaces:** Users can click **"Cloud Save"** to serialize their active frontend state and push it to the encrypted backend database, allowing them to log out and restore their session identically days later.
- **State Segregation:** Every session is cryptographically bound to the authenticated `USER_ID`.

### 💳 SaaS Monetization & Paywall
- **Tiered Checkout Interceptor:** The final JSON download is blocked by a highly realistic mock payment gateway.
- **Multi-Gateway UI:** Beautifully tabbed UI supporting Credit/Debit Cards, UPI, and Net Banking simulations (Stripe/Razorpay styling).

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TaxMaximizer.git
cd TaxMaximizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Ensure you have `streamlit`, `bcrypt`, `cryptography`, `pypdf`, `plotly`, and `pytesseract` installed).*

### 3. Initialize the Application
```bash
streamlit run Home.py
```

### 4. Test Credentials
The application requires authentication. Upon booting, you can click **"Register"** on the Login portal to create a secure test account, or use your pre-configured demo credentials.

---

## 📂 Project Structure

```text
📦 TaxMaximizer
 ┣ 📂 pages/
 ┃ ┣ 📜 0_Login.py             # Bcrypt Authentication Portal
 ┃ ┣ 📜 1_ITR_1_Salary.py      # Salary & Standard Deductions
 ┃ ┣ 📜 2_ITR_2_CapGains.py    # Stocks, Crypto, & Real Estate
 ┃ ┣ 📜 3_ITR_3_Business.py    # Proprietary Business & F&O
 ┃ ┣ 📜 4_ITR_4_Sugam.py       # Presumptive Taxation (44AD/ADA)
 ┃ ┣ 📜 5_ITR_5_Firms.py       # Partnership & LLP Tax Engine
 ┃ ┗ 📜 6_Checkout.py          # Secure Payment Gateway Simulator
 ┣ 📂 utils/
 ┃ ┣ 📜 db_manager.py          # SQLite Multi-Tenant Connection Pool
 ┃ ┣ 📜 security.py            # AES-256 Fernet Encryption Engine
 ┃ ┣ 📜 tax_calculators.py     # Core Mathematical Tax Logic
 ┃ ┣ 📜 json_generators.py     # Official ITD Schema Sync
 ┃ ┣ 📜 ocr_engine.py          # PDF Parsing (Form 16/Broker P&L)
 ┃ ┗ 📜 theme.py               # Global UI Components & Styling
 ┣ 📜 Home.py                  # Secure Application Dashboard
 ┗ 📜 requirements.txt         # Dependency tree
```

---

## ⚠️ Disclaimer & Legal
This application is designed as an **architectural prototype and educational resource** for Fintech development. It currently utilizes a local mock database and a Sandbox Payment Gateway.

**DO NOT** use the generated JSON files to file official taxes with the Government of India without first securing an **e-Return Intermediary (ERI)** license, replacing the Sandbox gateway with Live API keys, and deploying the system to a compliant cloud infrastructure (AWS/GCP).

---
*Built with ❤️ using Python & Streamlit.*
