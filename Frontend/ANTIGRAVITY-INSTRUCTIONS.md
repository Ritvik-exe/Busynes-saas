# Antigravity System Specification: Busynes SaaS (v1.0.0)

## 1. Core Objective
Assemble, unify, and polish the provided HTML page mockups into a cohesive, responsive multi-page web application. Ensure all components adhere strictly to the "Emerald Growth" design system tokens. Implement dynamic data-fetching from our live AWS serverless API Gateway.

## 2. Global Style & Token Constraints
Adhere strictly to these design specifications across all generated pages:
- **Brand Personality:** Corporate, authoritative, crisp, modern. Low-contrast outlines over heavy shadows.
- **Color Palette:**
  - Primary (Action): `#1B7A16` (Emerald Green)
  - Secondary (Stability): `#515F74` (Professional Slate)
  - Surface Base: `#FFFFFF`
  - Border Accents: `border-outline-variant/30` or `border-outline/20`
- **Typography:**
  - Headlines: 'Hanken Grotesk' (Tight letter-spacing for large sizes).
  - UI & Body: 'Inter' (Optimized for small text readability).
  - Code/Data Strings: 'JetBrains Mono' (For financial metrics, currency, and IDs).
- **Rounding:** Soft corners. Base small components use `rounded` (0.25rem / 4px). Containers/Cards use `rounded-lg` (0.5rem / 8px).

## 3. Global Routing & Navigation Map
Ensure all static links and navigation bars are configured to route between pages logically:
- **Home/Landing Page** -> CTA routes to **Sign-up (Get Started)**.
- **Sign-up/Register Page** -> Successful form submission routes to **Onboarding (Sarah's Welcome Page)**.
- **Onboarding Page** -> CTA routes to **Main Dashboard**.
- **Sidebar Navigation (Dashboard / Invoice Vault / Innovation Lab):** 
  - Ensure the sidebar is present and identical on all dashboard-level views.
  - Active links must use the `bg-secondary-container text-on-secondary-container` selection states.
  - Inactive links must hover gracefully.

## 4. API Integration Specifications (The V1.0.0 Bridge)
The Main Dashboard must dynamically fetch metrics from our public API Gateway instead of displaying static dummy numbers. 

### API Endpoint Configuration:
Define your API endpoint in a centralized configuration variable at the top of the dashboard's JavaScript:
`const API_BASE_URL = "https://aqwkzc2r0d.execute-api.eu-west-2.amazonaws.com/";`

### Fetching Logic:
1. When the dashboard page loads, perform an HTTP `GET` request to your API URL.
2. Dynamically pass the active user's identity as a query parameter (defaulting to `client_777` for our testing phase):
   `fetch(`${API_BASE_URL}?client_id=client_777`)`
3. Parse the returning JSON response [1, 2]:
   - Expected Payload Format: `{"ClientID": "...", "This_Month_Total": ..., "Today_Total": ...}`
4. **DOM Updates:** Update the dashboard metric text fields dynamically:
   - Identify your dashboard container elements (like the KPI card text).
   - Dynamically replace the text values on the UI with the parsed `Today_Total` and `This_Month_Total` values returned from the database [1].
   - If the request fails, default grace-fully to `£0.00` and output the error to the console.

## 5. Deployment Readiness
Keep all HTML files self-contained. Utilize Tailwind CSS via the CDN script with the customized inline config script blocks provided. Output optimized, semantic HTML5 structure with vanilla JavaScript for dynamic interactions.