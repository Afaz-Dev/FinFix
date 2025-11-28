FINFIX – PERSONAL FINANCE / BUDGET TRACKER
------------------------------------------------------------
Description
FinFix is a lightweight, offline, command-line Python application designed to help students monitor and
manage personal finances. It provides tools to record income and expenses, set monthly category
budgets, and generate clear, auditable financial summaries using simple CSV and TXT files. The
system prioritises privacy, transparency, and compliance with academic requirements.
Program Objectives
• Enable students to track income and monthly spending behaviour.
• Support monthly budgeting through category-based limits.
• Reduce manual recording errors commonly found in spreadsheets.
• Provide clear summaries for self-review or consultation with campus advisors.
• Improve financial self-discipline through structured tracking.
• Maintain full privacy through local, offline data storage.
• Allow simple export of financial summaries for academic or personal use.
Core Features
• Runs on standard Python 3.10+
• No external libraries required
• Simple and clean CLI menu system
• Automatic validation of inputs
• Autosave after every transaction
• Modular structure: input handling, processing, reporting, and storage
• Human-readable TXT/CSV output files
Data Files Used
1. transactions.csv – Stores all income and expense entries (date, amount, category, merchant, notes)
2. budgets.csv – Stores monthly budget limits per category
3. categories.csv – Maintains the master list of available spending categories
How to Use the Program
1. Run the application using:
python main.py
2. Navigate through the menu, which includes:
• Record a transaction
• Manage budgets
• Generate reports
• Export summaries
• Exit
3. Enter details as prompted. All data is validated and stored automatically.
4. Generate monthly summaries or category breakdowns when needed. Reports are saved as TXT or
CSV files for clarity and portability.
Program Workflow (Summary)
• load_data()
• display main menu
• process user selection
• record_transaction(), manage_budgets(), generate_reports(), or export_files()
• save_and_exit() on program termination
Source and Context
The program was designed for Swinburne Sarawak Student Affairs (Financial Wellbeing) to support
student budgeting practices. It provides auditable financial tracking tools suited for academic reporting,
financial advising, and student self-monitoring.
Primary Users
• Swinburne Sarawak students
Stakeholders
• Student Affairs (Financial Wellbeing), as part of financial literacy and wellbeing initiatives.
Team Members
• Ahmad Firdaus Bin Ahmad Zaki – 104408954
• Adem Jian Kai Ngieng – 104410878
• You Han Liu – 105805954
• Muhammad – 104402477
