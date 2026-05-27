# Product Availability Tracker

A full-stack web application that allows users to log in, add public product URLs with desired sizes, and receive email notifications when products become available in their desired size.

## Architecture

- **Frontend**: React (Azure Static Web Apps)
- **Backend**: Python (Azure Functions)
- **Database**: Azure Cosmos DB (NoSQL)
- **Authentication**: Azure Entra ID (MSAL)
- **Email**: Azure Communication Services
- **Scraping/AI**: Azure Functions + BeautifulSoup / Azure AI Content Understanding
![arch](./architecture/Azure-Basic-Template-serverless.svg)

## Project Structure

```
product-availability-tracker/
├── frontend/          # React SPA
├── backend/           # Python Azure Functions
├── docs/              # Step-by-step Azure Portal guide (Markdown)
└── architecture/      # Architecture diagram (draw.io XML)
```

## Quick Start

See `docs/azure-portal-guide.md` for full step-by-step deployment instructions.
