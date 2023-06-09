from flask import Flask, render_template, request, redirect, flash, session, jsonify
from functools import wraps
from datetime import datetime
import psycopg2

app = Flask(__name__)
app.secret_key = "abcd"  # replace abcd with your secret key 

conn = psycopg2.connect(
    
    # Replace abcd with your respective database values...

    host="abcd",
    database="abcd",
    user="abcd",
    password="abcd"
)

mail = ''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    global mail
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE (username = %s AND password = %s) or (email = %s AND password = %s)",
            (username, password, username, password)
        )
        user = cursor.fetchone()
        cursor.close()

        if user: 
            mail = str(user[2])
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid username or password!', 'credentialError')
            return render_template('login.html', error_message='Invalid username or password')

    response = app.make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/logout')
def logout():
    session.clear()
    response = app.make_response(redirect('/'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password == confirm_password:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already exists!', 'mailError')
                return render_template('register.html', error_message='Email already exists')
            else:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
                conn.commit()
                cursor.close()
                print("success")
                flash('Resgistration Successful!', 'success')

                return render_template('login.html', error_message='success')

        else:
            flash('Passwords do not match!', 'passwordError')
            return render_template('register.html', error_message='Passwords do not match')

    response = app.make_response(render_template('register.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions where email = %s ORDER BY date", (mail,))
    transactions = cursor.fetchall()
    cursor.close()
    return render_template('dashboard.html', transactions=transactions)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    transaction = request.get_json()
    text = transaction.get('text')
    amount = transaction.get('amount')
    date = transaction.get('date')

    if not text or not amount or not date:
        return jsonify({'error': 'Invalid transaction data'})

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (text, amount, date, email) VALUES (%s, %s, %s, %s)",
                       (text, amount, date, mail))
        conn.commit()
        cursor.close()
    except psycopg2.Error:
        return jsonify({'error': 'Failed to insert transaction into the database'})

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE text = %s AND amount = %s AND date = %s AND email = %s",
                       (text, amount, date, mail))
        new_transaction = cursor.fetchone()
        cursor.close()
    except psycopg2.Error as e:
        return jsonify({'error': 'Failed to retrieve the newly created transaction'})

    new_transaction_dict = {
        'transaction_id': new_transaction[0],
        'text': new_transaction[1],
        'amount': new_transaction[2],
        'date': new_transaction[3],
        'email': new_transaction[4]
    }

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions where email = %s", (mail,))
        transactions = cursor.fetchall()
        cursor.close()
    except psycopg2.Error as e:
        return jsonify({'error': 'Failed to retrieve transactions from the database'})

    transactions_list = []
    for transaction in transactions:
        transaction_dict = {
            'transaction_id': transaction[0],
            'text': transaction[1],
            'amount': transaction[2],
            'date': transaction[3],
            'email': transaction[4]
        }
        transactions_list.append(transaction_dict)

    return jsonify({'transaction': new_transaction_dict, 'transactions': transactions_list})

@app.route('/delete_transaction/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        conn.commit()
        cursor.close()
    except psycopg2.Error:
        return jsonify({'error': 'Failed to delete transaction from the database'})

    return jsonify({'message': 'Transaction deleted successfully'})

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    try:
        start_date = request.args.get('start-date')
        end_date = request.args.get('end-date')

        cursor = conn.cursor()

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            cursor.execute(
                "SELECT * FROM transactions WHERE email = %s AND date >= %s AND date <= %s",
                (mail, start_date, end_date)
            )
        else:
            cursor.execute("SELECT * FROM transactions WHERE email = %s", (mail,))

        transactions = cursor.fetchall()
        cursor.close()

        transactions_list = []
        for transaction in transactions:
            transaction_dict = {
                'transaction_id': transaction[0],
                'text': transaction[1],
                'amount': transaction[2],
                'date': transaction[3],
                'email': transaction[4]
            }
            transactions_list.append(transaction_dict)

        return jsonify({'transactions': transactions_list})
    except psycopg2.Error as e:
        return jsonify({'error': 'Failed to retrieve transactions from the database'})

@app.after_request
def add_cache_control_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

if __name__ == '__main__':
    app.run(debug=True)
