# Auth0 Flask Demo

## Setup

1. Create a free account at https://auth0.com/
2. Create an application (Regular Web App)
3. Set the following in your Auth0 app settings:
   - **Allowed Callback URLs**: `http://localhost:5000/callback`
   - **Allowed Logout URLs**: `http://localhost:5000`

4. Copy `.env.example` to `.env` and fill in your values.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000) to test.

## Features

- Login with Auth0
- View user session on `/dashboard`
- Logout and redirect to home
