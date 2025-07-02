from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime, timezone
import logging
now_utc = datetime.now(timezone.utc)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# --- Set up structured logging ---
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Dummy user database (in-memory)
users = {
    'admin@example.com': {'password': 'admin123', 'user_id': 1},
    'john.doe@example.com': {'password': 'johnpass', 'user_id': 2},
    'jane.smith@example.com': {'password': 'janepass', 'user_id': 3}
}

# --- Home Page ---
@app.route('/')
def home():
    if 'user_id' in session:
        return f'''
        <h2>Welcome to app7, {session["email"]}!</h2>
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
        data = request.get_json() if request.is_json else request.form

        email = data.get('email')
        password = data.get('password')
        user = users.get(email)

        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['email'] = email

            app.logger.info(
                f"Login | user_id={user['user_id']} | email={email} | time={datetime.now(timezone.utc)}"
            )
            return redirect(url_for('home'))

        app.logger.warning(
            f"Failed login attempt | email={email} | time={datetime.now(timezone.utc)} | IP={request.remote_addr}"
        )
        return 'Invalid credentials', 401

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
    user_email = session.get('email')
    session.clear()
    app.logger.info(
        f"Logout | email={user_email} | time={datetime.now(timezone.utc)} | IP={request.remote_addr}"
    )
    return redirect('/login')

# --- Protected Route ---
@app.route('/protected')
def protected():
    if 'user_id' in session:
        current_time = datetime.now(timezone.utc)
        app.logger.info(
            f"Accessed /protected | user_id={session['user_id']} | email={session['email']} | time={current_time}"
        )
        return f'''
        <h2>Protected Content</h2>
        <p>Hello {session["email"]}, this is a protected page.</p>
        <p>Current UTC time: {current_time}</p>
        <a href="/">Go back home</a>
        '''
    
    app.logger.warning(
        f"Unauthorized access attempt to /protected | IP={request.remote_addr} | time={datetime.now(timezone.utc)}"
    )
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
