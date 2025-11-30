# FINFIX – PERSONAL FINANCE / BUDGET TRACKER

## Description
FinFix is a lightweight, offline, Python-based application designed to help students monitor and manage personal finances. It provides tools to record income, expenses, and savings, set monthly category budgets, and generate clear, auditable financial summaries. The system prioritizes privacy, transparency, and compliance with academic requirements. The program features a modern GUI built using **PyQt5**, offering an intuitive and interactive user experience.

Github Link : https://github.com/Afaz-Dev/FinFix

---

## Program Objectives
* Enable students to track income, expenses, and savings with detailed transaction records.
* Support monthly budgeting through category-based limits and progress tracking.
* Provide visual insights into financial behavior with charts and summaries.
* Reduce manual recording errors commonly found in spreadsheets.
* Maintain full privacy through local, offline data storage.
* Allow exporting of financial summaries in **CSV, PNG, and PDF** formats for academic or personal use.

---

## Core Features
* **Modern GUI**: Built with PyQt5, featuring a clean and interactive interface.
* **Transaction Management**: Add, edit, duplicate, or delete income, expenses, and savings transactions.
* **Budget Tracking**: Set monthly budgets per category and monitor spending progress.
* **Visual Insights**: Generate savings charts, expense pie charts, and daily spending sparklines.
* **Currency Conversion**: Convert MYR to other currencies using live exchange rates (when online).
* **Undo Functionality**: Undo the last transaction for error correction.
* **Data Validation**: Automatic validation of inputs to ensure data integrity.
* **Autosave**: All changes are saved automatically to local CSV files.
* **Export Options**: Export monthly summaries as CSV, PNG, or PDF files.
* **Dark/Light Mode**: Toggle between dark and light themes for better usability.
* **Offline Storage**: All data is stored locally, ensuring privacy and security.

---

## Technologies Used
* **Programming Language**: Python 3.10+
* **IDE**: Visual Studio Code
* **GUI Framework**: PyQt5
* **Data Storage**: CSV files for transactions and budgets, JSON for currency rates.

---

## Python Modules Used
The following Python modules and libraries are used in the project:
* **PyQt5**: For building the graphical user interface.
* **requests**: For getting and posting http requests to an external api.
* **os**: For file system operations.
* **datetime**: For handling dates in transactions and summaries.
* **matplotlib**: For generating charts and visualizations.

---

## Data Files Used
1. **`transactions.csv`** – Stores all income, expense, and savings entries (transaction ID, date, type, category, amount, description).
2. **`budgets.csv`** – Stores monthly budget limits per category.
3. **`rates.json`** – Stores cached currency exchange rates for offline use.

---

## How to Use the Program

### 1. Run the Application
Ensure you have **Python 3.10+** installed. Run the program using:
```bash
python main.py
```

or download and run FinFix.exe file

### 2. Main Features
* **Log Transactions**: Add income, expenses, or savings with categories and descriptions.
* **Manage Budgets**: Set or edit monthly budgets for specific categories.
* **Generate Reports**: View monthly summaries, savings charts, and expense distributions.
* **Currency Conversion**: Convert MYR to other currencies using live exchange rates.
* **Export Data**: Save financial summaries as CSV, PNG, or PDF files.

### 3. Input Handling
* **Transaction Types**: Choose between "Income", "Expense", or "Savings".
* **Categories**: Assign transactions to predefined or custom categories.
* **Validation**: All inputs (e.g., amounts, dates) are validated to ensure accuracy.

### 4. Reports and Visualizations
* **Monthly Summary**: View income, expenses, savings, and net position for the selected month.
* **Savings Chart**: Visualize cumulative savings per category as battery-style charts.
* **Expense Pie Chart**: Analyze expense distribution across categories.
* **Daily Spending Sparkline**: Track daily spending trends for the selected month.

### 5. Export Options
* **CSV**: Export transaction data for the selected month.
* **PNG**: Save a snapshot of the monthly summary.
* **PDF**: Generate a detailed PDF report of the monthly summary.

---

## Program Workflow (Summary)

1. **Initialization**:
   * Load existing data from `transactions.csv` and `budgets.csv`.
   * Migrate legacy data formats if necessary.
   * Cache currency exchange rates for offline use.
2. **User Interaction**:
   * Display the main menu with options for transactions, budgets, reports, and exports.
   * Handle user inputs through the GUI.
3. **Data Processing**:
   * Validate and save transactions or budgets.
   * Update summaries, charts, and progress bars dynamically.
4. **Export and Save**:
   * Save data automatically after every transaction.
   * Allow users to export summaries in various formats.
5. **Exit**:
   * Ensure all data is saved before closing the application.

---

## Primary Users & Stakeholders

* **Primary Users**: Swinburne Sarawak students.
* **Stakeholders**:
  * Student Affairs (Financial Wellbeing)
  * Financial literacy & wellbeing initiatives

---

## Team Members

* Ahmad Firdaus Bin Ahmad Zaki (Leader) – 104408954
* Adem Jian Kai Ngieng – 104410878
* You Han Liu – 105805954
* Muhammad – 104402477