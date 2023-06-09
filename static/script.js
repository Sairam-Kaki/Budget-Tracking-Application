const balance = document.getElementById('balance');
const money_plus = document.getElementById('money-plus');
const money_minus = document.getElementById('money-minus');
const list = document.getElementById('list');
const form = document.getElementById('form');
const text = document.getElementById('text');
const category = document.getElementById('category');
const amount = document.getElementById('amount');
const date = document.getElementById('date');
const type = document.getElementById('type');
const addIncomeBtn = document.getElementById('add-income-btn');
const addExpenseBtn = document.getElementById('add-expense-btn');
const noHistory = document.getElementById('no-history');
const toast = document.getElementById('toast');

let transactions = [];

// Show or hide income/expense buttons based on selection
function handleTransactionType() {
  const selectedType = type.value;
  category.style.display = selectedType === 'expense' ? 'block' : 'none';
  text.style.display = selectedType === 'income' ? 'block' : 'none';

  addIncomeBtn.style.display = selectedType === 'income' ? 'block' : 'none';
  addExpenseBtn.style.display = selectedType === 'expense' ? 'block' : 'none';
}

// Add transaction
function addTransaction(e, isIncome) {
  e.preventDefault();

  if (!(isIncome) && (category.value === '' || amount.value.trim() === '' || date.value === '')) {
    alert('Please provide category, amount and date!');
    return;
  }else if (isIncome && (text.value.trim() === '' || amount.value.trim() === '' || date.value === '')) {
    alert('Please provide Description, Amount, and Date!');
    return;
  }

  var bal = parseInt(balance.innerHTML.slice(1));

  if (!isIncome && (bal - amount.value < 0)){
    alert("Insufficent Balance!");
    return;
  }

  const transaction = {
    text: isIncome ? text.value : category.value,
    amount: isIncome ? parseFloat(amount.value) : -parseFloat(amount.value),
    date: date.value,
  };

  fetch('/add_transaction', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(transaction),
  })
    .then(response => response.json())
    .then(data => {
      addTransactionDOM(data.transaction);
      updateValues(data.transactions);
      text.value = '';
      amount.value = '';
      date.value = '';

      noHistory.style.display = 'none';

      addIncomeBtn.style.display = 'none';
      addExpenseBtn.style.display = 'none';
      text.style.display='none';
      category.style.display='none';

      category.value = '';
      type.value = '';

      showToast("Transaction added!", "add");
    })
    .catch(error => console.log('Error:', error));
}

// Add transactions to DOM list
function addTransactionDOM(transaction) {
  const { text, amount, date, transaction_id } = transaction;
  const sign = amount < 0 ? '-' : '+';
  const existingTransaction = transactions.find(t => t.transaction_id === transaction.transaction_id);

  if (!existingTransaction) {
    transactions.push(transaction);
  }

  const item = document.createElement('li');
  item.classList.add(amount < 0 ? 'minus' : 'plus');
  const dt = new Date(date).toLocaleDateString('en-GB');

  item.innerHTML = `
    ${text}
    <span class="date">${dt}</span>
    <span>${sign}${Math.abs(amount)}</span>
    <button class="delete-btn" onclick="removeTransaction(${transaction_id})">x</button>
  `;

  list.appendChild(item);
}

// Remove transaction by ID
function removeTransaction(transactionId) {
  fetch(`/delete_transaction/${transactionId}`, {
    method: 'DELETE',
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        throw new Error(data.error);
      }
      updateValues(data.transactions);
      showToast("Transaction removed!", "del");
      init();
    })
    .catch(error => {
      console.log('An error occurred while removing the transaction:', error);
    });
}

// Update the balance, income, and expense
function updateValues() {
  const amounts = transactions.map(transaction => parseFloat(transaction.amount));
  const total = amounts.reduce((acc, item) => (acc += item), 0).toFixed(2);
  const income = amounts
    .filter(item => item > 0)
    .reduce((acc, item) => (acc += item), 0)
    .toFixed(2);
  const expense = (
    amounts.filter(item => item < 0).reduce((acc, item) => (acc += item), 0) * -1
  ).toFixed(2);

  balance.innerHTML = `&#8377;${total}`;
  money_plus.innerHTML = `&#8377;${income}`;
  money_minus.innerHTML = `&#8377;${expense}`;
}


// Filters the transactions 
function filterTransactions() {
  const startDate = document.getElementById('start-date').value;
  const endDate = document.getElementById('end-date').value;

  fetch(`/get_transactions?start-date=${startDate}&end-date=${endDate}`)
    .then(response => response.json())
    .then(data => {
      list.innerHTML = '';

      if (data.transactions.length === 0) {
        noHistory.style.display = 'block';
      } else {
        noHistory.style.display = 'none';
        data.transactions.forEach(addTransactionDOM);
      }

      updateValues();
    })
    .catch(error => console.error('Error retrieving transactions:', error));
}

// To remove the filters and hide the options
function resetFilters() {
  document.getElementById('start-date').value = '';
  document.getElementById('end-date').value = '';
  document.getElementById('filter-form').style.display='none';
  init();
}

// shows filter options
function showFilterForm(){
  document.getElementById('filter-form').style.display='flex';
}

// Notification toast to inform when a transaction is added/removed
function showToast(message, type) {
  toast.textContent = message;
  toast.className = `toast ${type}`;

  toast.style.opacity = '1';

  setTimeout(() => {
    toast.style.opacity = '0';
  }, 1500);
}

// Bind event listeners
type.addEventListener('change', handleTransactionType);
addIncomeBtn.addEventListener('click', e => addTransaction(e, true));
addExpenseBtn.addEventListener('click', e => addTransaction(e, false));

function init() {
  list.innerHTML = '';
  fetch('/get_transactions')
    .then(response => response.json())
    .then(data => {
      transactions = data.transactions;

      if (transactions.length === 0) {
        noHistory.style.display = 'block';
      } else {
        noHistory.style.display = 'none';
        transactions.forEach(addTransactionDOM);
      }

      updateValues();
    })
    .catch(error => console.error('Error retrieving transactions:', error));
}

form.addEventListener('submit', e => {
  e.preventDefault();
});

init();