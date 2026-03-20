# 💳 Smart EcoCash Tracker

Hey! This is my money tracker app. It helps you track **income** and **expenses** in ZWL and USD. You can see live USD/ZWL rates, charts, smart insights, budgets, and even export your transactions. Simple and clean.

---

## 🚀 Features

- Sign up and login securely
- Dashboard with total income, expenses, and balance
- Live USD/ZWL rate
- Monthly and category spending charts
- Budget bars for Food, Airtime, Bills
- Smart insights: top spending, warnings, averages
- Export transactions to CSV
- Smart category suggestions based on description

---

## 💻 How to Run Locally

1. Clone this repo:

   git clone https://github.com/Arnold/ecocash_tracker.git
   cd ecocash_tracker

2. Create a virtual environment and activate:

   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate

3. Install dependencies:

   pip install -r requirements.txt

4. Run the app:

   python app.py

5. Open in your browser:

   http://127.0.0.1:5000

---

## 🗄️ Database

- **SQLite** (`transactions.db`)
- Stores users (username & hashed password)
- Stores transactions (type, amount, currency, category, description, date)

> Easy to switch to PostgreSQL for bigger apps

---

## ⚡ Tech Stack

- Python 3 + Flask backend
- TailwindCSS for frontend
- Chart.js for charts
- Requests for live USD/ZWL rate
- SQLite database

---

## 📁 Folder Structure

.
├── app.py             # Main app
├── templates/         # HTML templates
│   ├── index.html
│   ├── login.html
│   └── register.html
├── static/            # JS and CSS
│   └── main.js
├── transactions.db    # Database
├── requirements.txt
└── README.md

---

## 📝 License

MIT License

---

Made by me. Simple, clean, and ready to help you track your money. Check my GitHub [here](https://github.com/Arnold0783)