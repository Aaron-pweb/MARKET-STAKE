from flask import Flask, request, render_template, redirect, url_for, session, flash
from market_service import MarketStackService

app = Flask(__name__)
app.config.from_prefixed_env()
API_KEY = app.config.get("API_KEY")
app.secret_key = "app.config.get('API_KEY')"
app.config["SECRETE_KEY"] = "THIS NIS TEH SECRETE KEY YEAH"

users = {}

@app.route("/")
def home():
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
	
	try:
		service = MarketStackService(api_key=API_KEY)
		stock_data = service.get_stock_data()
	except Exception as e:
		print(f"Error getting stock data: {e}")
		stock_data = []
		flash("Error retrieving stock data", "danger")

	return render_template("dashboard.html", user=user, stock_data=stock_data)


@app.route("/sign-out")
def sign_out():
	session.pop("user", None)
	flash("Signed out", "info")
	return redirect(url_for("home"))


if __name__ == "__main__":
	app.run(debug=True)