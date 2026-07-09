# TaxMaximizer Pro Enterprise: Technical Walkthrough

The application has been successfully scaled from a single-file prototype into a full-fledged **Streamlit Multi-Page Application (MPA)**. The architecture now seamlessly supports multiple distinct Income Tax Returns with localized domain logic.

## 1. Modular Architecture
The monolithic `app.py` has been completely decoupled:
*   `Home.py`: The beautiful, centralized dashboard where users can navigate to different tax forms.
*   `pages/`: Contains the isolated UI and workflow for each specific tax form (e.g., `1_ITR_1_Salary.py`, `2_ITR_2_CapGains.py`, etc.).
*   `utils/ocr_engine.py`: A unified library containing the Tesseract PDF parser and all Regular Expression extraction engines (for both Form 16s and Broker P&L statements).
*   `utils/tax_calculators.py`: The centralized mathematical engine supporting Standard Slabs, Special Capital Gains Rates (STCG/LTCG), and Presumptive Business Income calculations.

## 2. Advanced Form Capabilities

### 🟢 ITR-1 (Sahaj - Salary & House Property)
The legacy app was perfectly ported into the new architecture. It retains the powerful OCR fallback mechanism and the official ITD JSON payload generator for direct e-Filing.

### 🟡 ITR-2 (Capital Gains Module)
*   **Broker Statement OCR:** Automatically extracts STCG and LTCG from standard Brokerage P&L statements (Zerodha, Groww, Upstox).
*   **Special Rate Calculator:** Natively calculates tax at 20% (STCG) and 12.5% over ₹1.25L (LTCG) in accordance with the latest FY 2024-25 budget updates.
*   **Safety Guardrails:** Automatically detects if the user traded F&O or Intraday, throwing an error instructing them to switch to ITR-3.

### 🔵 ITR-4 (Sugam - Presumptive Taxation)
*   **Automated Profit Logic:** Dynamically calculates minimum mandatory profit for Professionals under Section 44ADA (50%) and Businesses under Section 44AD (6% for digital / 8% for cash).
*   **Limit Enforcement:** Strictly enforces the new turnover limits (₹75 Lakhs for Professionals, ₹3 Crores for Businesses) to prevent illegal filings.

### 🔴 ITR-3 (Business & F&O)
*   **Financial Grids:** Interactive grids for full Profit & Loss statements and Balance Sheets.
*   **F&O Turnover & Tax Audit:** Automatically calculates absolute F&O turnover (sum of positive and negative trades) to determine if a Section 44AB Tax Audit is mandatory (Turnover > ₹10 Crores).
*   **Balance Sheet Tally Check:** Actively monitors the Assets vs Liabilities inputs, throwing a red mismatch error if the balance sheet doesn't tally perfectly.

### 🟣 ITR-5 (Firms & LLPs)
*   **Corporate Taxation Engine:** Built a completely separate tax engine applying the mandatory 30% flat tax rate exclusively for Partnership Firms, LLPs, AOPs, and BOIs.
*   **Section 40(b) Remuneration Guardian:** Automatically calculates Book Profit and enforces the strict Section 40(b) mathematical limits (90% on first ₹3L, 60% on balance) on partner remuneration. It instantly throws a disallowance alert if the firm tries to overpay its partners!

## 3. Database State Persistence (SQLite)
> [!IMPORTANT]
> **Data Loss Prevention:** Complex forms like ITR-3 require users to enter dozens of financial fields. If the browser refreshes, Streamlit's native `session_state` gets wiped instantly. 
> 
> To solve this, a lightweight **SQLite Database (`utils/db_manager.py`)** was integrated. 
* Users can now click **"💾 Save Draft to Database"** at any time. This serializes their entire active session and safely stores it locally. 
* When returning, they click **"🔄 Load Draft"** to instantly restore their P&L and Balance Sheet exactly as they left it!

## 4. Phase 6: SaaS Enterprise Architecture
The application has been successfully elevated from a simple prototype into a secure, monetized consumer SaaS platform.

### 🔐 Multi-Tenant Authentication (`pages/0_Login.py`)
*   **Bcrypt Hashing:** User passwords are automatically salted and hashed via the `bcrypt` standard. Raw passwords are never stored.
*   **Universal Route Protection:** A strict global interceptor locks down `Home.py` and all ITR forms, instantly redirecting unauthenticated users to the Login portal to prevent URL bypasses.

### 🛡️ AES-256 Data Encryption (`utils/security.py`)
*   **DPDP Act Compliance:** The application uses the `cryptography` (Fernet) library to implement strict Field-Level Encryption. 
*   **Database Interceptor:** When users save forms (like ITR-3), sensitive fields (PAN) and financial JSON payloads are scrambled into an AES-256 cipher before being written to SQLite. They are dynamically decrypted in-memory during session load.

### 💳 Payment Gateway Paywall (`pages/6_Checkout.py`)
*   **Tiered Monetization:** The final step of the tax generation process is blocked. The "Download JSON" button is intercepted and replaced with a "Pay to File" button (e.g., ₹499 for ITR-1).
*   **Mock Stripe Checkout:** Simulates a professional credit card checkout environment. Upon successful mock payment, the `payment_status` is flipped to True, permanently unlocking the certified JSON download for that session.
