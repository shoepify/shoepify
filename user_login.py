from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data
users = {
    "admin": "password123"
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials, please try again."

@app.route('/dashboard')
def dashboard():
    return "Welcome to the dashboard!"

if __name__ == '__main__':
    app.run(debug=True)