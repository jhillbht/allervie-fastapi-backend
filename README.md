# Allervie Analytics FastAPI Backend

This is a modernized FastAPI backend for the Allervie Analytics Dashboard, replacing the previous Flask implementation.

## Features

- **Modern FastAPI Framework**: Leveraging the latest features of FastAPI for improved performance and developer experience.
- **Automatic OpenAPI Documentation**: Detailed API documentation available at `/api/docs`.
- **Type Hints and Validation**: Built-in request and response validation with Pydantic.
- **Dependency Injection**: Clean, modular code structure with dependency injection.
- **Google OAuth Integration**: Authentication via Google OAuth 2.0.
- **Google Ads API Integration**: Connect to the Google Ads API to retrieve real ad performance data.
- **Mock Data Support**: Development with mock data when real API credentials aren't available.

## Getting Started

### Prerequisites

- Python 3.9+
- Google OAuth 2.0 credentials
- Google Ads API credentials

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   # Create a .env file with the following variables
   ENVIRONMENT=development
   USE_REAL_ADS_CLIENT=true
   ALLOW_MOCK_DATA=true
   ALLOW_MOCK_AUTH=true
   FRONTEND_URL=http://localhost:3000
   REDIRECT_URI=http://localhost:5002/api/auth/callback
   SECRET_KEY=your-secret-key
   CLIENT_CUSTOMER_ID=your-google-ads-customer-id
   ```

5. Set up Google OAuth and Ads API credentials:
   - Place your `client_secret.json` in the `credentials` directory
   - Place your `google-ads.yaml` in the `credentials` directory

### Running the Server

```bash
python main.py
```

The server will start on http://localhost:5002 by default.

## API Documentation

- Swagger UI: http://localhost:5002/api/docs
- ReDoc: http://localhost:5002/api/redoc

## Project Structure

```
allervie-fastapi-backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── dashboard.py    # Dashboard data endpoints
│   │   │   ├── google_ads.py   # Google Ads API endpoints
│   │   │   └── diagnostics.py  # Diagnostic endpoints
│   │   └── routers.py          # API router configuration
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   └── logging.py          # Logging configuration
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── auth.py             # Authentication services
│   │   └── google_ads_client.py # Google Ads API client
│   └── templates/              # HTML templates
├── credentials/                # OAuth and API credentials
├── logs/                       # Application logs
├── main.py                     # Application entry point
└── requirements.txt            # Project dependencies
```

## Key Differences from Flask Implementation

- **Automatic OpenAPI Documentation**: Interactive API documentation.
- **Type Hints**: Comprehensive type checking for request/response data.
- **Dependency Injection**: Clean handling of dependencies like authentication.
- **Modern Async Support**: Built-in async/await support.
- **Improved Performance**: FastAPI is significantly faster than Flask.
- **Modern Error Handling**: Standardized error responses.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | development |
| `USE_REAL_ADS_CLIENT` | Whether to use real Google Ads API | true |
| `ALLOW_MOCK_DATA` | Allow mock data when real data unavailable | true |
| `ALLOW_MOCK_AUTH` | Allow mock authentication | true |
| `FRONTEND_URL` | URL of the frontend application | http://localhost:3000 |
| `REDIRECT_URI` | OAuth redirect URI | http://localhost:5002/api/auth/callback |
| `SECRET_KEY` | Secret key for JWT tokens | allervie-dashboard-secret-key |
| `CLIENT_CUSTOMER_ID` | Google Ads customer ID | 8127539892 |
| `PORT` | Port to run the server on | 5002 |
| `HOST` | Host to bind to | 0.0.0.0 |

## License

Proprietary - All rights reserved
