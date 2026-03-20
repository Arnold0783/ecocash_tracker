from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import Counter
import pandas as pd
import io
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey2026"

# --- DATABASE ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), default="ZWL")
    category = db.Column(db.String(50))
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- LOGIN REQUIRED DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# --- FETCH LIVE USD/ZWL RATE ---
def get_usd_rate():
    try:
        res = requests.get("https://www.floatrates.com/daily/zwl.json", timeout=5)
        rate = res.json()['usd']['rate']
        return round(rate, 2)
    except:
        return 32  # fallback realistic rate

def convert_to_zwl(amount, currency):
    return amount * get_usd_rate() if currency == "USD" else amount

# --- REGISTER ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        surname = request.form["surname"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        # Check username
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register"))

        # Check password match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        new_user = User(name=name, surname=surname, phone=phone, address=address,
                        username=username, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DASHBOARD ---
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    usd_rate = get_usd_rate()

    if request.method == "POST":
        t = Transaction(
            user_id=user_id,
            type=request.form["type"],
            amount=float(request.form["amount"]),
            currency=request.form.get("currency", "ZWL"),
            category=request.form["category"],
            description=request.form["description"]
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("index"))

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    # Totals
    income = sum(convert_to_zwl(t.amount, t.currency) for t in transactions if t.type=="income")
    expense = sum(convert_to_zwl(t.amount, t.currency) for t in transactions if t.type=="expense")
    balance = income - expense

    # Category totals and monthly data
    category_totals = {}
    monthly_data = {}
    for t in transactions:
        amt = convert_to_zwl(t.amount, t.currency)
        if t.type == "expense":
            cat = (t.category or "Other").lower()
            category_totals[cat] = category_totals.get(cat,0) + amt
        month = t.date.strftime("%Y-%m")
        monthly_data[month] = monthly_data.get(month,0) + amt

    return render_template("index.html",
                           transactions=transactions,
                           income=round(income,2),
                           expense=round(expense,2),
                           balance=round(balance,2),
                           category_totals=category_totals,
                           monthly_data=monthly_data,
                           usd_rate=usd_rate)

# --- LIVE RATE ENDPOINT ---
@app.route("/rate")
@login_required
def rate():
    return jsonify({"rate": get_usd_rate()})

# --- INSIGHTS ---
@app.route("/insights")
@login_required
def insights():
    user_id = session["user_id"]
    transactions = Transaction.query.filter_by(user_id=user_id).all()

    total_expense = 0
    categories = []

    for t in transactions:
        if t.type == "expense":
            amt = convert_to_zwl(t.amount, t.currency)
            total_expense += amt
            categories.append(t.category)

    top_category = Counter(categories).most_common(1)[0][0] if categories else "N/A"
    avg_expense = total_expense / (len(categories) or 1)

    warning = "⚠️ High spending!" if total_expense > 50000 else ""
    message = f"Total expenses: ZWL {total_expense:.2f}. Top category: {top_category}. Avg: ZWL {avg_expense:.2f}. {warning}"
    return jsonify({"insight": message})

# --- EXPORT CSV ---
@app.route("/export")
@login_required
def export_csv():
    user_id = session["user_id"]
    transactions = Transaction.query.filter_by(user_id=user_id).all()

    data = [{
        "Type": t.type,
        "Amount": t.amount,
        "Currency": t.currency,
        "Category": t.category,
        "Description": t.description,
        "Date": t.date.strftime("%Y-%m-%d")
    } for t in transactions]

    df = pd.DataFrame(data)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(io.BytesIO(buffer.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=f"{session['username']}_transactions.csv")

# --- SMART CATEGORY ---
@app.route("/suggest", methods=["POST"])
@login_required
def suggest():
    description = request.json.get("description","").lower()
    category = "Other"
    if "food" in description or "meal" in description: category = "Food"
    if "airtime" in description or "mtn" in description: category = "Airtime"
    if "bill" in description or "electric" in description: category = "Bills"
    if "fuel" in description or "transport" in description: category = "Transport"
    return jsonify({"suggested_category": category})

if __name__ == "__main__":
    app.run()