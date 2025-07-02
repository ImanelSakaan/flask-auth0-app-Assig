from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# --- Set up logging ---
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Dummy user database (in-memory)
users = {
    'admin@example.com': {
        'password': 'admin123',
        'user_id': 1
    },
    'john.doe@example.com': {
        'password': 'johnpass',
        'user_id': 2
    },
    'jane.smith@example.com': {
        'password': 'janepass',
        'user_id': 3
    }
}


# --- Home Page ---
@app.route('/')
def home():
    if 'user_id' in session:
        return f'''
        <h2>Welcome, {session["email"]}!</h2>
        <p><a href="/protected">Go to protected page</a></p>
        <form method="post" action="/logout">
            <button type="submit">Logout</button>
        </form>
        '''
    return redirect('/login')

# --- Login Page and Handler ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle JSON or form
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
            return redirect(url_for('home'))  # ✅ Redirect after login

        logging.warning(f'Failed login attempt | email={email}')
        return 'Invalid credentials', 401

    # If GET, show login form
    return '''
    <h2>Login</h2>
    <form method="post" action="/login">
        <input type="text" name="email" placeholder="Email" required />
        <input type="password" name="password" placeholder="Password" required />
        <button type="submit">Login</button>
    </form>
    '''

# --- Logout Route ---
@app.route('/logout', methods=['POST'])
def logout():
    user = session.get('email')
    session.clear()
    logging.info(f'User logged out | email={user}')
    return redirect('/login')

# --- Protected Route ---
@app.route('/protected')
def protected():
    if 'user_id' in session:
        logging.info(f'Accessed /protected | user_id={session["user_id"]} | email={session["email"]}')
        return f'''
        <h2>Protected Content</h2>
        <p>Hello {session["email"]}, this is a protected page.</p>
        <a href="/">Go back home</a>
        '''
    logging.warning(f'Unauthorized access attempt to /protected | IP={request.remote_addr}')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
