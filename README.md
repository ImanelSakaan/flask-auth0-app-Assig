# Assignment 1: Securing and Monitoring an Authenticated Flask App
---
🎥 Demo Video

YouTube Demo Link - 5 Minute Walkthrough
https://youtu.be/WROOqldlzZM


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

<img src="https://github.com/user-attachments/assets/224d887a-bde6-42f3-9d8b-723da3be7a8e" width="50%" />

<img src="https://github.com/user-attachments/assets/a94c093b-f89f-47ea-8803-85dc7e41980b)" width="50%" />

<img src="https://github.com/user-attachments/assets/bea4393a-a454-40a7-afc4-46aa497d2d84" width="50%" />


<img src="https://github.com/user-attachments/assets/29f38b1c-d42c-4834-b5bd-c286b5367bfc" width="50%" />

---


## 2. Deploy to Azure App Service

### 2.1 Reuse Azure setup from Lab 2

#### 1. In VS Code terminal:

```bash
az login
az group create --name flask-lab-rg --location canadacentral
az appservice plan create --name flaskPlan --resource-group flask-lab-rg --sku FREE
az webapp create --resource-group flask-lab-rg --plan flaskPlan --name flask-lab-iman123 --runtime "PYTHON|3.10" --deployment-local-git
````

This created a **Git URL** like:
```
https://flask-lab-iman123.scm.azurewebsites.net:443/flask-lab-iman123.git
https://flask-lab-iman123.scm.azurewebsites.net/
```

### 2. Set deployment remote and push:

#### 1. Add remote:

```bash
git remote add azure https://iman@flask-lab-iman123.scm.azurewebsites.net/flask-lab-iman123.git
```

This tells Git:
> “Add a new remote repository called `azure` pointing to the Azure Web App Git URL.”

---
#### 2. Push code to Azure:

```bash
git push azure master
```

This tells Git:
> “Push my local code (from the `master` branch) to the `azure` remote.”

---

### 🔗 Your app becomes live at:
```
https://flask-lab-iman123.scm.azurewebsites.net/
```
![image](https://github.com/user-attachments/assets/2288d79d-fd48-4986-939a-0af8334f2433)

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
<img width="587" alt="image" src="https://github.com/user-attachments/assets/f7d3ef4b-45c1-4866-99cc-76993762ff52" />

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
   * 
<img width="1133" alt="image" src="https://github.com/user-attachments/assets/94b20d3a-dee9-4a24-9f4d-6017c647198a" />
```


