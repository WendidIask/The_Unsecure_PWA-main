from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from datetime import timedelta

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, generate_csrf
from urllib.parse import urlparse
from flask_talisman import Talisman

import user_management as dbHandler

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=5)
Talisman(app)
app.secret_key = 'iUK#Kc!E3vFgqz$T@oP6eJ9HbLWm^NAR'
csrf = CSRFProtect(app)
app.jinja_env.auto_reload = True
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.before_request
def ensure_csrf_token():
    if request.method == "GET":
        csrf_token = generate_csrf()
        from flask import g
        g.csrf_token = csrf_token

@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if "username" not in session: 
        return redirect("/")
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if urlparse(url).netloc or urlparse(url).scheme:
            url = "/"
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
    dbHandler.listFeedback()
    return render_template("success.html", state=True, value="Back")
    
@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if urlparse(url).netloc or urlparse(url).scheme:
            url = "/"
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        if dbHandler.userExists(username):
            return render_template("signup.html", error="User already exists!")
        dbHandler.insertUser(username, password, DoB)
        session.permanent = True
        session["username"] = username
        dbHandler.listFeedback()
        return render_template("success.html", value=username, state=True)
    if "username" in session: 
        return render_template("loggedin.html", state=True)
    else:
        return render_template("signup.html")
    
@app.route("/logout", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if urlparse(url).netloc or urlparse(url).scheme:
            url = "/"
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            session.permanent = True
            session["username"] = username
            dbHandler.listFeedback()
            return render_template("success.html", value=username, state=True)
        else:
            return render_template("index.html", error="Incorrect username or password.")
    if "username" in session: 
        return render_template("loggedin.html", state=True)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)