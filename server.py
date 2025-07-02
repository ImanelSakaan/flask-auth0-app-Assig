import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode

app = Flask(__name__)
# app.secret_key = os.environ.get("APP_SECRET_KEY")
app.secret_key = "-rLzPQyhJ1wp2XviyCeiYUG-wDnhnYVNTpEnu0N3uxw"
app.debug = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# OAuth setup
oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid_configuration',
    client_kwargs={
        "scope": "openid profile email",
    },
)

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'))

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = auth0.authorize_access_token()
    session["user"] = token
    
    # Log successful login
    user_info = token.get('userinfo', {})
    user_id = user_info.get('sub', 'unknown')
    email = user_info.get('email', 'unknown')
    
    app.logger.info(json.dumps({
        "event": "user_login",
        "user_id": user_id,
        "email": email,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'unknown')
    }))
    
    return redirect("/")

@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    # Log logout
    if 'user' in session:
        user_info = session['user'].get('userinfo', {})
        user_id = user_info.get('sub', 'unknown')
        email = user_info.get('email', 'unknown')
        
        app.logger.info(json.dumps({
            "event": "user_logout",
            "user_id": user_id,
            "email": email,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": request.remote_addr
        }))
    
    session.clear()
    return redirect(
        "https://" + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/protected")
def protected():
    # Check if user is authenticated
    if 'user' not in session:
        # Log unauthorized attempt
        app.logger.warning(json.dumps({
            "event": "unauthorized_access_attempt",
            "route": "/protected",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'unknown')
        }))
        return redirect("/login")
    
    # Log authorized access to protected route
    user_info = session['user'].get('userinfo', {})
    user_id = user_info.get('sub', 'unknown')
    email = user_info.get('email', 'unknown')
    
    app.logger.info(json.dumps({
        "event": "protected_route_access",
        "user_id": user_id,
        "email": email,
        "route": "/protected",
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'unknown')
    }))
    
    return render_template("protected.html", user=session.get('user'))

@app.errorhandler(404)
def not_found(error):
    app.logger.warning(json.dumps({
        "event": "404_error",
        "route": request.path,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'unknown')
    }))
    return "Page not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000), debug=False)