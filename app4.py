from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import logging
import os

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Required for session
app.secret_key = os.getenv("APP_SECRET_KEY")

# --- Set up logging ---
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Dummy users database
users = {
    'admin@example.com': {'password': 'admin123', 'user_id': 1}
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login (JSON or form data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        email = data.get('email')
        password = data.get('password')

        user = users.get(email)
        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['email'] = email
            logging.info(f'Login successful | user_id={user["user_id"]} | email={email}')
            return jsonify({'message': 'Login successful'})

        logging.warning(f'Failed login attempt | email={email}')
        return jsonify({'message': 'Invalid credentials'}), 401

    # If GET, return a simple HTML form to test from browser
    return '''
    <form method="post" action="/login">
        <input type="text" name="email" placeholder="Email" />
        <input type="password" name="password" placeholder="Password" />
        <button type="submit">Login</button>
    </form>
    '''


# --- Protected Route ---
@app.route('/protected')
def protected():
    if 'user_id' in session:
        # ✅ Log access to protected route
        logging.info(f'Accessed /protected | user_id={session["user_id"]} | email={session["email"]}')
        return jsonify({'message': 'Welcome to the protected route'})
    
    # ❌ Log unauthorized attempt
    logging.warning(f'Unauthorized access attempt to /protected | IP={request.remote_addr}')
    return jsonify({'message': 'Unauthorized'}), 401

# --- Logout Route ---
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

# --- Example route to test login form ---
@app.route('/')
def home():
    return '''
    <form action="/login" method="post" enctype="application/json">
        <input name="email" placeholder="email" />
        <input name="password" placeholder="password" type="password" />
        <input type="submit" />
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
