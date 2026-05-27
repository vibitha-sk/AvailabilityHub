# Step-by-Step Azure Portal Deployment Guide
## Product Availability Tracker

---

## Prerequisites

- An active Azure subscription
- Access to Azure Portal: https://portal.azure.com
- A domain verified in Azure Communication Services (for sending emails)
- Node.js 18+ and Python 3.11+ installed locally for testing

---

## Step 1 — Create a Resource Group

1. Go to **Azure Portal** > search **Resource Groups** > click **+ Create**
2. Fill in:
   - **Subscription**: your subscription
   - **Resource group name**: `rg-product-tracker`
   - **Region**: `Canada Central` (or your preferred region)
3. Click **Review + Create** > **Create**

---

## Step 2 — Register the Application in Azure Entra ID

### 2a. Create the App Registration

1. Go to **Azure Entra ID** > **App registrations** > **+ New registration**
2. Fill in:
   - **Name**: `product-tracker-app`
   - **Supported account types**: *Accounts in this organizational directory only*
   - **Redirect URI**: Select **Single-page application (SPA)** and enter `http://localhost:3000`
3. Click **Register**
4. Note the **Application (client) ID** and **Directory (tenant) ID** — you will need these.

### 2b. Expose an API Scope

1. In your app registration, go to **Expose an API**
2. Click **+ Add a scope**
3. Accept the default Application ID URI (e.g. `api://<client-id>`)
4. Fill in:
   - **Scope name**: `access_as_user`
   - **Who can consent**: Admins and users
   - **Admin consent display name**: Access Product Tracker API
5. Click **Add scope**

### 2c. Add the Production Redirect URI

After deploying the Static Web App (Step 5), come back here and add the production URL:
1. Go to **Authentication** > under **Single-page application** click **+ Add URI**
2. Add: `https://your-static-web-app.azurestaticapps.net`

---

## Step 3 — Create Azure Cosmos DB (NoSQL)

1. Go to **Azure Portal** > search **Azure Cosmos DB** > **+ Create**
2. Select **Azure Cosmos DB for NoSQL** > **Create**
3. Fill in:
   - **Resource group**: `rg-product-tracker`
   - **Account name**: `cosmos-product-tracker` (must be globally unique)
   - **Location**: `Canada Central`
   - **Capacity mode**: **Serverless** (cost-effective for low traffic)
4. Click **Review + Create** > **Create** (takes ~5 minutes)
5. Once created, go to the resource > **Keys** and note:
   - **URI** (COSMOS_ENDPOINT)
   - **PRIMARY KEY** (COSMOS_KEY)

### 3a. Create Database and Container

1. Go to your Cosmos DB account > **Data Explorer** > **+ New Database**
   - **Database id**: `ProductTracker`
2. Click **+ New Container**:
   - **Database id**: `ProductTracker`
   - **Container id**: `Products`
   - **Partition key**: `/user_id`
3. Click **OK**

---

## Step 4 — Create Azure Communication Services

1. Go to **Azure Portal** > search **Communication Services** > **+ Create**
2. Fill in:
   - **Resource group**: `rg-product-tracker`
   - **Resource name**: `acs-product-tracker`
3. Click **Review + Create** > **Create**
4. Once created, go to the resource > **Keys** and note the **Connection string**

### 4a. Set Up Email Domain

1. In your ACS resource, go to **Email** > **Domains** > **+ Add domain**
2. Choose **Azure managed domain** for a quick start (e.g. `azurecomm.net`)
3. Note the sender address (e.g. `DoNotReply@xxxxxxxx.azurecomm.net`)

---

## Step 5 — Create Azure Function App (Backend)

1. Go to **Azure Portal** > search **Function App** > **+ Create**
2. Fill in:
   - **Resource group**: `rg-product-tracker`
   - **Function App name**: `func-product-tracker` (globally unique)
   - **Runtime stack**: **Python**
   - **Version**: **3.11**
   - **Region**: `Canada Central`
   - **Hosting plan**: **Consumption (Serverless)**
3. Click **Review + Create** > **Create**

### 5a. Configure Application Settings

1. Go to your Function App > **Configuration** > **Application settings** > **+ New application setting**
2. Add each of the following:

| Name | Value |
|------|-------|
| `COSMOS_ENDPOINT` | Your Cosmos DB URI |
| `COSMOS_KEY` | Your Cosmos DB primary key |
| `COSMOS_DATABASE` | `ProductTracker` |
| `COSMOS_CONTAINER` | `Products` |
| `ACS_CONNECTION_STRING` | Your ACS connection string |
| `EMAIL_SENDER` | Your ACS sender address |
| `AZURE_TENANT_ID` | Your Entra ID tenant ID |
| `AZURE_CLIENT_ID` | Your app registration client ID |

3. Click **Save**

### 5b. Deploy the Backend Code

**Option A — Azure CLI (recommended):**
```bash
cd product-availability-tracker/backend
func azure functionapp publish func-product-tracker
```

**Option B — VS Code:**
1. Install the **Azure Functions** VS Code extension
2. Right-click the `backend` folder > **Deploy to Function App**
3. Select `func-product-tracker`

### 5c. Enable CORS on the Function App

1. Go to your Function App > **CORS**
2. Add your Static Web App URL (e.g. `https://your-app.azurestaticapps.net`)
3. Also add `http://localhost:3000` for local development
4. Click **Save**

---

## Step 6 — Create Azure Static Web App (Frontend)

1. Go to **Azure Portal** > search **Static Web Apps** > **+ Create**
2. Fill in:
   - **Resource group**: `rg-product-tracker`
   - **Name**: `swa-product-tracker`
   - **Plan type**: **Free**
   - **Region**: `East US 2` (Static Web Apps have limited regions)
   - **Source**: **Other** (we will deploy manually)
3. Click **Review + Create** > **Create**
4. Once created, go to the resource > **Manage deployment token** and copy the token

### 6a. Build and Deploy the Frontend

1. Create a `.env` file in `frontend/` based on `.env.example` and fill in your values
2. Build the app:
```bash
cd product-availability-tracker/frontend
npm install
npm run build
```
3. Deploy using the SWA CLI:
```bash
npm install -g @azure/static-web-apps-cli
swa deploy ./build --deployment-token <your-token> --env production
```

---

## Step 7 — Verify the Deployment

1. Open your Static Web App URL in a browser
2. Click **Sign in with Microsoft** — you should be redirected to Microsoft login
3. After login, you should see the dashboard
4. Add a product URL and size
5. Wait up to 1 minute for the availability checker to run
6. Check Azure Function logs: **Function App** > **Functions** > `availability_checker` > **Monitor**

---

## Step 8 — (Optional) Custom Domain

1. Go to your Static Web App > **Custom domains** > **+ Add**
2. Follow the DNS verification steps for your domain registrar
3. Update the Entra ID redirect URI with your custom domain

---

## Cost Estimate (Monthly)

| Service | Tier | Estimated Cost |
|---------|------|----------------|
| Azure Cosmos DB | Serverless | ~$0-5 |
| Azure Functions | Consumption | ~$0-2 |
| Azure Static Web Apps | Free | $0 |
| Azure Communication Services | Pay-as-you-go | ~$0.0025/email |
| **Total** | | **~$0-10/month** |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login redirect loop | Verify redirect URI in Entra ID matches exactly |
| 401 Unauthorized from API | Check `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` in Function App settings |
| Emails not sending | Verify ACS domain is verified and sender address is correct |
| Cosmos DB connection error | Check `COSMOS_ENDPOINT` and `COSMOS_KEY` in Function App settings |
| Scraper returns false always | Some sites block scrapers; try a different product URL for testing |
