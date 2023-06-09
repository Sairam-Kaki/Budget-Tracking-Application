# Budget Tracking Application
This is a simple web application built with Flask that allows users to manage their expenses. Users can register, log in, add transactions, view their transaction history, filter them, and delete transactions.

## Features
- View Transactions: Users can view their transactions history which includes details such as description, date and amount.
- Add Transaction: users can addd new transaction by providing necessary data.
- Delete Transaction: Users can delete a specific transacion from their transaction history.
- Filter Transacions: Users can filter their transacion history based on a specified date range.
- Balance, Income & Expense: Users can view updated balance, total income and total expense he made.
- User Friendly UI: The user can find the website which is responsive and eyes friendly colors and design as attractive.

## Installation
1. Clone the repository using the command:
  `git clone https://github.com/Sairam-Kaki/Budget-Tracking-Application.git`
2. Install the required dependencies such as Flask, Libraries etc.
3. Set up the database:
   - Make sure you have PostgreSQL installed and running.
   - Create a new database named 'postgres' and configure the database details in the Flask app's 'conn' variable.
   - Create the database schema ( use the following code to create ):
     ```SQL
     CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     username VARCHAR(50) NOT NULL,
     email VARCHAR(100) NOT NULL,
     password VARCHAR(100) NOT NULL
     );

     CREATE TABLE transactions (
     transaction_id SERIAL PRIMARY KEY,
     text VARCHAR(100) NOT NULL,
     amount NUMERIC(10, 2) NOT NULL,
     date DATE NOT NULL,
     email VARCHAR(100) NOT NULL,
     FOREIGN KEY (email) REFERENCES users (email)
     );
     ```
4. Run the "app.py" file.
5. Open your web browser and access the aplication at http://localhost:5000


## Contributing
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.
