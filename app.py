from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transactions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo de Transação
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'Receita' ou 'Despesa'

# Inicializar o banco de dados
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.type == "Receita")
    total_expense = sum(t.amount for t in transactions if t.type == "Despesa")
    balance = total_income - total_expense
    return render_template("index.html", transactions=transactions, balance=balance)

@app.route("/add", methods=["POST"])
def add_transaction():
    description = request.form.get("description", "")
    category = request.form.get("category", "")
    date = datetime.strptime(request.form.get("date", ""), "%Y-%m-%d")
    amount = float(request.form.get("amount", 0))
    transaction_type = request.form.get("type", "Receita")
    new_transaction = Transaction(
        description=description,
        category=category,
        date=date,
        amount=amount,
        type=transaction_type,
    )
    db.session.add(new_transaction)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if request.method == "POST":
        transaction.description = request.form.get("description", "")
        transaction.category = request.form.get("category", "")
        transaction.date = datetime.strptime(request.form.get("date", ""), "%Y-%m-%d")
        transaction.amount = float(request.form.get("amount", 0))
        transaction.type = request.form.get("type", "Receita")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", transaction=transaction)

@app.route("/delete/<int:id>")
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)


