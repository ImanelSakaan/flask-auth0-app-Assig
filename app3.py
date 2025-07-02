import os
from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()


app = Flask(__name__)
# app.secret_key = os.getenv("-rLzPQyhJ1wp2XviyCeiYUG-wDnhnYVNTpEnu0N3uxw")
# app.secret_key = "-rLzPQyhJ1wp2XviyCeiYUG-wDnhnYVNTpEnu0N3uxw"
app.secret_key = os.getenv("APP_SECRET_KEY")

app.config['SESSION_COOKIE_NAME'] = 'auth0_session'

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=f"https://{os.getenv('AUTH0_DOMAIN')}",
    access_token_url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    client_kwargs={'scope': 'openid profile email'},
)


@app.route('/')
def home():
      return 'Welcome! <a href="/login">Login</a>'
    # return render_template("home.html", session=session.get('user'))

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = token['userinfo']
    session['user'] = {
        'user_id': userinfo['sub'],
        'email': userinfo['email'],
        'name': userinfo['name'],
        'timestamp': datetime.utcnow().isoformat()
    }

    # Log the successful login
    app.logger.info("User logged in", extra={
        "user_id": userinfo['sub'],
        "email": userinfo['email'],
        "timestamp": session['user']['timestamp']
    })

    return redirect('/dashboard')

@app.route('/protected')
def protected():
    user = session.get('user')
    if not user:
        app.logger.warning("Unauthorized access attempt to /protected", extra={
            "timestamp": datetime.utcnow().isoformat()
        })
        return redirect('/login')

    app.logger.info("Accessed /protected route", extra={
        "user_id": user['user_id'],
        "email": user['email'],
        "timestamp": datetime.utcnow().isoformat()
    })
    return render_template('protected.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect('/')
    return f"Logged in as {user['email']}<br><a href='/logout'>Logout</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo=http://localhost:5000"
    )

if __name__ == "__main__":
    app.run(debug=True)
