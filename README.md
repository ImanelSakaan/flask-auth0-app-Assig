# Assignment 1: Securing and Monitoring an Authenticated Flask App
---

## Part 1: App Enhancements & Deployment

### 1. Enhance Flask App with Logging
## 📋 Prerequisites

- Python 3.7+
- Git
- Auth0 account (free)

---

**File: app7.py**`  
Add these enhancements to my existing Lab 1 code:

```python
# Add these imports
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
        current_time = datetime.now(timezone.utc)
        return f'''
        <h2 style="color: green; font-weight: bold; font-size: 22px">Welcome to Assignment 1: Securing and Monitoring an Authenticated Flask App</h2>
        <h2 style="color: blue; font-weight: bold; font-size: 20px"> Active User ID:   {session["user_id"]}</h2>
        <h2 style="color: blue; font-weight: bold; font-size: 20px"> Active User Email:   {session["email"]}</h2>
        <h2 style="color: blue; font-weight: bold; font-size: 20px"> Current UTC time: {current_time}</h2>
        <p style="color: red; font-size: 24px"><a href="/protected">Go to protected page</a></p>
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
        #return 'Invalid credentials', 401
        return (
            '<h2 style="color: red; font-weight: bold; font-size: 28px">Invalid credentials</h2>',
            401,
)

    return '''
    <h2 style="color: blue; font-weight: bold; font-size: 28px">Login</h2>
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
        <h2 style="color: green; font-size: 32px">Protected Content</h2>
        <p style="color: blue; font-weight: bold; font-size: 20px">Hello {session["email"]}, this is a protected page.</p>
        <p style="color: blue; font-size: 18px">Current UTC time: {current_time}</p>
        <a href="/">Go back home</a>
        '''
    
    app.logger.warning(
        f"Unauthorized access attempt to /protected | IP={request.remote_addr} | time={datetime.now(timezone.utc)}"
    )
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

````
## Run the Application

```bash
python app7.py
```
![image](https://github.com/user-attachments/assets/224d887a-bde6-42f3-9d8b-723da3be7a8e)

![image](https://github.com/user-attachments/assets/a94c093b-f89f-47ea-8803-85dc7e41980b)

![image](https://github.com/user-attachments/assets/bea4393a-a454-40a7-afc4-46aa497d2d84)

![image](https://github.com/user-attachments/assets/29f38b1c-d42c-4834-b5bd-c286b5367bfc)

---

### 2. Deploy to Azure App Service

1. Reuse Azure setup from Lab 2
2. **Enable logging**:

In **Azure Portal** → Your App Service → **Monitoring** → **Diagnostic settings**:

* Enable `AppServiceConsoleLogs`
* Send to **Log Analytics workspace**

3. **Configure environment variables** in Azure:

In **Application Settings** → Add the following:

```
AUTH0_CLIENT_ID
AUTH0_DOMAIN
AUTH0_CLIENT_SECRET
SECRET_KEY
```

---

## Part 2: Monitoring & Detection

### 1. Simulate Traffic

Use this `test-app.http` file (for VS Code REST Client extension):

```http
### Valid login
GET http://localhost:5000/login

### Access protected route (valid)
GET http://localhost:5000/protected

### Invalid access (no session)
GET http://localhost:5000/protected
```

---

### 2. KQL Query for Log Analytics

```kusto
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where LogMessage contains "Protected access"
| parse LogMessage with * "user_id=" user_id "," * "timestamp=" timestamp
| summarize AccessCount = count() by user_id, bin(TimeGenerated, 15m)
| where AccessCount > 10
| project user_id, TimeGenerated, AccessCount
```

---

### 3. Create Azure Alert

1. **In Azure Portal**:

   * Go to Log Analytics → **New alert rule**
   * **Condition**: Custom log search
   * Paste the KQL query above
   * **Set threshold**: > 0 results

2. **Configure actions**:

   * Create **action group** with email notifications
   * Set alert severity: `3 (Low)`

3. **Alert logic**:

   * **Evaluation frequency**: 5 minutes
   * **Lookback period**: 15 minutes

```

Let me know if you want me to save this to a `.md` file or upload it to your repo automatically.
```
