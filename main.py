from flask import Flask, request, render_template, redirect, url_for, session, flash
# import os


app = Flask(__name__)
app.config.from_prefixed_env()
API_KEY = app.config.get("API_KEY")
app.secret_key = app.config.get('API_KEY')
users = {}


@app.route("/")
def home():
	print(API_KEY)
	print(users)
	"""Home page. Shows sign in / sign up links or dashboard link when signed in."""
	user = session.get("user")
	return render_template("home.html", user=user)


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		user = users.get(username)
		if user and user.get("password") == password:
			session["user"] = username
			flash("Signed in successfully", "success")
			return redirect(url_for("dashboard"))
		flash("Invalid credentials", "danger")
	return render_template("sign_in.html")


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		if not username or not password:
			flash("Provide a username and password", "warning")
		elif username in users:
			flash("Username already exists", "warning")
		else:
			users[username] = {"password": password}
			session["user"] = username
			flash("Account created", "success")
			return redirect(url_for("dashboard"))
	return render_template("sign_up.html")


@app.route("/dashboard")
def dashboard():
	"""Protected-ish dashboard page. Redirects to sign-in if not signed in."""
	user = session.get("user")
	if not user:
		flash("Please sign in first", "info")
		return redirect(url_for("sign_in"))
	return render_template("dashboard.html", user=user)


@app.route("/sign-out")
def sign_out():
	session.pop("user", None)
	flash("Signed out", "info")
	return redirect(url_for("home"))


# Suggested additional routes (implement as needed):
# - /profile : view / edit user profile
# - /reset-password : password reset flow (email + token)
# - /api/... : JSON endpoints for app data
# - /static/... : serve assets (Flask serves /static by default)


if __name__ == "__main__":
	# Run in debug for local development only
	app.run(debug=True)
