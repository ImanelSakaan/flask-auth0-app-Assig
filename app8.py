from flask import Flask, request, session, redirect, url_for, jsonify
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging
import os

load_dotenv()

now_utc = datetime.now(timezone.utc)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')  # Required for session

# --- Logging Setup ---
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Auth0 Setup ---
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CALLBACK_URL = os.environ["AUTH0_CALLBACK_URL"]
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")  # Optional

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
)

# --- Home ---
@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        current_time = datetime.now(timezone.utc)
        return f'''
        <h2 style="color: green; font-weight: bold; font-size: 22px">Welcome to Assignment 1: Securing and Monitoring an Authenticated Flask App</h2>
        <h2 style="color: blue; font-weight: bold; font-size: 20px">Active User Email: {user["email"]}</h2>
        <h2 style="color: blue; font-weight: bold; font-size: 20px">Current UTC time: {current_time}</h2>
        <p style="color: red; font-size: 24px"><a href="/protected">Go to protected page</a></p>
        <form method="post" action="/logout"><button type="submit">Logout</button></form>
        <p><a href="/force-relogin">Force Re-login via Auth0</a></p>
        '''
    return redirect('/login')

# --- Auth0 Login ---
@app.route('/login')
def login():
    return auth0.authorize_redirect(
        redirect_uri=AUTH0_CALLBACK_URL,
        audience=AUTH0_AUDIENCE
    )

# --- Force Re-login ---
@app.route('/force-relogin')
def force_relogin():
    return auth0.authorize_redirect(
        redirect_uri=AUTH0_CALLBACK_URL,
        audience=AUTH0_AUDIENCE,
        prompt='login'  # 👈 Force re-login
    )

# --- Auth0 Callback ---
@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = token.get('userinfo')
    session['user'] = {
        'email': userinfo['email'],
        'name': userinfo.get('name'),
        'sub': userinfo.get('sub')
    }
    app.logger.info(f"Login | email={userinfo['email']} | time={datetime.now(timezone.utc)}")
    return redirect('/')

# --- Logout ---
@app.route('/logout', methods=['POST'])
def logout():
    user = session.pop('user', None)
    if user:
        app.logger.info(f"Logout | email={user['email']} | time={datetime.now(timezone.utc)} | IP={request.remote_addr}")
    session.clear()
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout?' + urlencode({
            'returnTo': url_for('home', _external=True),
            'client_id': AUTH0_CLIENT_ID,
        })
    )

# --- Protected Route ---
@app.route('/protected')
def protected():
    user = session.get('user')
    if user:
        current_time = datetime.now(timezone.utc)
        app.logger.info(f"Accessed /protected | email={user['email']} | time={current_time}")
        return f'''
        <h2 style="color: green; font-size: 32px">Protected Content</h2>
        <p style="color: blue; font-weight: bold; font-size: 20px">Hello {user["email"]}, this is a protected page.</p>
        <p style="color: blue; font-size: 18px">Current UTC time: {current_time}</p>
        <a href="/">Go back home</a>
        '''
    
    app.logger.warning(f"Unauthorized access to /protected | IP={request.remote_addr} | time={datetime.now(timezone.utc)}")
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
