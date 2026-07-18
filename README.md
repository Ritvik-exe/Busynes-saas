# Busynes 🚀

Busynes is a B2B serverless SaaS platform built to automate invoice processing, ledger reconciliation, and daily financial operations for businesses. By replacing manual data entry with cloud-native automation, Busynes helps business owners and back-office teams reclaim their time.

## 🛠 Architecture Overview

The platform is designed around a fully automated, event-driven, serverless architecture on AWS and Stripe, managed via Infrastructure as Code (Terraform) and deployed with zero-password GitHub Actions.

```text
┌──────────────────────┐
│   Cloudflare Pages   │ (Frontend: Vite + Tailwind CSS)
└──────────┬───────────┘
           │ (Public HTTPS)
           ▼
┌──────────────────────┐
│  AWS API Gateway v2  │ (HTTP API Router)
└──────────┬───────────┘
           │
  ┌────────┴────────────────┐
  ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ Cognito Author  │       │  Python Lambda  │ (Single Handler Backend)
│ (JWT Validation)│       │  (Python 3.12)  │
└─────────────────┘       └────────┬────────┘
                                   │
    ┌────────────────┬─────────────┼─────────────┐
    ▼                ▼             ▼             ▼
┌────────────┐   ┌────────────┐   ┌──────────┐   ┌──────────┐
│ DynamoDB   │   │ S3 Bucket  │   │ AWS SES  │   │ Rekognition
│ (Ledger)   │   │ (Invoices) │   │ (Emails) │   │ (OCR API)│
└────────────┘   └────────────┘   └──────────┘   └──────────┘
```

## 📦 Release History

### v1.0.0 (Production Release — Live)
Our initial launch establishes a secure, compliant, and robust base infrastructure alongside our first core tool: the **Automated Invoice Calculator**.

#### Key Features
*   **Cognito Auth & Session Verification**: Fully secure sign-up, email verification, and login workflows. A lightweight JavaScript Route Guard instantly parses and verifies Cognito ID Tokens in `sessionStorage` before permitting application access.
*   **Invoice Calculator & S3 Ingestion**: Standard users can upload up to 10 invoices per month (with unlimited processing for Pro users). The system uses AWS Rekognition OCR to extract transaction totals and line items, writing them directly to a DynamoDB ledger.
*   **HMRC-Compliant Lifecycle Policy**: Invoices uploaded to S3 are stored securely under standard storage, automatically transitioning to Standard-IA after 90 days, Glacier Instant Retrieval after 180 days, and permanently expiring after 6 years to satisfy statutory HMRC requirements.
*   **Stripe Billing Integrations**: Direct Stripe Checkout integration for subscription upgrades. A cryptographically verified public Stripe Webhook automatically upgrades users to Pro inside DynamoDB upon successful subscription payment, or downgrades accounts to Free upon invoice failures after a 3-day grace period.
*   **Integrated Bug and Support Engine**: Unauthenticated public `/support` routes allow visitors to request callbacks or file bug reports. Bug reports allow users to upload diagnostic screenshots directly to S3 before dispatching responsive, brand-aligned email alerts to `support@busynes.com` via AWS SES.

#### Deployment & Infrastructure
*   **Terraform IaC**: Complete backend infrastructure mapped out declaratively with variables managing configuration parameters securely.
*   **OIDC CI/CD Pipeline**: GitHub Actions automatically assumes a secure AWS IAM execution role via OpenID Connect (OIDC), packaging third-party Python dependencies (like Stripe) dynamically, archiving the backend, and deploying the Lambda function.

### v1.1.0 (Upcoming Roadmap)
Our next roadmap sprint focuses on scaling environment isolation, visual analytics, and user experience.

*   **Environment Isolation (Staging vs. Production)**: Refactoring the Terraform configurations to maintain isolated development environments using dedicated DynamoDB tables, S3 buckets, and Stripe Test keys.
*   **Multi-Currency Processing**: Enhancing the OCR parser and database to compute, convert, and format multi-currency invoices for international business operations.
*   **Social Sign-In**: Integrating Google and Microsoft Federation directly into the Cognito identity pipeline.
*   **Busynes AI Chat**: Structuring a serverless assistant component to query transaction trends directly through conversational natural language.

## 🔒 Security & Compliance

*   **ICO Registered**: Officially registered with the UK Information Commissioner's Office (ICO) as a data controller.
*   **Data Protection & Liability**: Live, compliant Legal policies (Terms and Privacy) updated on the frontend, enforcing statutory B2B liability caps and secure storage standards.
*   **S3 Public Access Block**: Direct public access to the primary invoice bucket is strictly blocked. Users retrieve objects securely using short-lived S3 Presigned URLs generated dynamically by the Lambda backend.

## ⚙️ Development Setup

To inspect or collaborate on the development of Busynes:

1.  **Clone the monorepo**:
    ```bash
    git clone https://github.com/Ritvik-exe/Busynes-saas.git
    ```

2.  **Navigate to `/Frontend` to run the Vite dev server**:
    ```bash
    cd Frontend
    npm install
    npm run dev
    ```

3.  **To view the infrastructure blueprints**:
    ```bash
    cd ../Terraform
    terraform init
    terraform plan
    ```