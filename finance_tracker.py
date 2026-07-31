"""
Personal Finance Tracking Program
CIS-30A Course Project - Option 2

This program allows users to track income, expenses, and savings goals.
It provides functionality to add, modify, delete, and view financial data.

Author: Elsa Ledesma Saucedo
Date: July 31st, 2026
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


# ============================================================
# Custom Module: Data Validators
# ============================================================

class DataValidators:
    """Custom module containing validation functions for financial data."""
    
    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate that amount is a positive number."""
        return isinstance(amount, (int, float)) and amount >= 0
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format YYYY-MM-DD."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_category(category: str, categories: List[str]) -> bool:
        """Validate that category exists in the allowed list."""
        return category.lower() in [c.lower() for c in categories]
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency string."""
        return f"${amount:.2f}"


# ============================================================
# Class 1: Transaction
# ============================================================

class Transaction:
    """
    Represents a single financial transaction (income or expense).
    
    Attributes:
        amount (float): Transaction amount
        category (str): Category of the transaction
        date (str): Date of transaction (YYYY-MM-DD)
        description (str): Description of the transaction
        transaction_type (str): 'income' or 'expense'
    """
    
    def __init__(self, amount: float, category: str, date: str = None, 
                 description: str = "", transaction_type: str = "expense"):
        """
        Initialize a Transaction object.
        
        Args:
            amount: Transaction amount
            category: Category of transaction
            date: Date of transaction (defaults to today)
            description: Description of transaction
            transaction_type: 'income' or 'expense'
        """
        self.amount = amount
        self.category = category
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.description = description
        self.transaction_type = transaction_type
        self.id = id(self)  # Unique identifier
    
    def __str__(self) -> str:
        """String representation of the transaction."""
        type_symbol = "+" if self.transaction_type == "income" else "-"
        return (f"[{self.date}] {self.transaction_type.title()}: "
                f"{self.category} - {type_symbol}{DataValidators.format_currency(self.amount)} "
                f"({self.description})")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization."""
        return {
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
            "type": self.transaction_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction from dictionary data."""
        return cls(
            amount=data["amount"],
            category=data["category"],
            date=data["date"],
            description=data["description"],
            transaction_type=data["type"]
        )


# ============================================================
# Class 2: Budget
# ============================================================

class Budget:
    """
    Manages budget limits for different categories.
    
    Attributes:
        monthly_budget (dict): Monthly budget limits by category
        weekly_budget (dict): Weekly budget limits by category
    """
    
    def __init__(self):
        """Initialize a Budget object."""
        self.monthly_budget: Dict[str, float] = {}
        self.weekly_budget: Dict[str, float] = {}
    
    def set_monthly_budget(self, category: str, amount: float):
        """Set monthly budget for a category."""
        if DataValidators.validate_amount(amount):
            self.monthly_budget[category] = amount
            return True
        return False
    
    def set_weekly_budget(self, category: str, amount: float):
        """Set weekly budget for a category."""
        if DataValidators.validate_amount(amount):
            self.weekly_budget[category] = amount
            return True
        return False
    
    def check_budget(self, category: str, amount: float, period: str = "monthly") -> bool:
        """
        Check if spending amount is within budget.
        
        Args:
            category: Category to check
            amount: Amount to check
            period: 'monthly' or 'weekly'
        
        Returns:
            True if within budget, False if over budget
        """
        budget = self.monthly_budget if period == "monthly" else self.weekly_budget
        if category in budget:
            return amount <= budget[category]
        return True  # No budget set
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert budget to dictionary."""
        return {
            "monthly": self.monthly_budget,
            "weekly": self.weekly_budget
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """Create Budget from dictionary data."""
        budget = cls()
        budget.monthly_budget = data.get("monthly", {})
        budget.weekly_budget = data.get("weekly", {})
        return budget


# ============================================================
# Subclass: FinanceTracker (extends Budget functionality)
# ============================================================

class FinanceTracker(Budget):
    """
    Main finance tracking system. Inherits from Budget.
    
    Attributes:
        income_list (List[Transaction]): List of income transactions
        expense_list (List[Transaction]): List of expense transactions
        savings_goal (float): User's savings goal
        categories (List[str]): Available transaction categories
    """
    
    def __init__(self):
        """Initialize FinanceTracker object."""
        super().__init__()  # Call parent class constructor
        self.income_list: List[Transaction] = []
        self.expense_list: List[Transaction] = []
        self.savings_goal: float = 0.0
        self.categories = [
            "Salary", "Business", "Investment", "Gift",
            "Housing", "Food", "Transportation", "Utilities",
            "Entertainment", "Healthcare", "Education", "Shopping",
            "Insurance", "Other"
        ]
    
    # ====== Income Methods ======
    
    def add_income(self, amount: float, category: str, date: str = None, 
                   description: str = "") -> bool:
        """
        Add an income transaction.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not DataValidators.validate_amount(amount):
            return False
        
        if category not in self.categories:
            return False
        
        transaction = Transaction(amount, category, date, description, "income")
        self.income_list.append(transaction)
        return True
    
    def get_total_income(self) -> float:
        """Calculate total income."""
        return sum(t.amount for t in self.income_list)
    
    def get_income_by_category(self) -> Dict[str, float]:
        """Get income totals by category."""
        income_by_cat = {}
        for t in self.income_list:
            income_by_cat[t.category] = income_by_cat.get(t.category, 0) + t.amount
        return income_by_cat
    
    # ====== Expense Methods ======
    
    def add_expense(self, amount: float, category: str, date: str = None,
                    description: str = "") -> bool:
        """
        Add an expense transaction.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not DataValidators.validate_amount(amount):
            return False
        
        if category not in self.categories:
            return False
        
        # Check budget
        if not self.check_budget(category, amount + self.get_expense_by_category().get(category, 0)):
            print(f"Warning: This expense exceeds your monthly budget for {category}")
        
        transaction = Transaction(amount, category, date, description, "expense")
        self.expense_list.append(transaction)
        return True
    
    def get_total_expenses(self) -> float:
        """Calculate total expenses."""
        return sum(t.amount for t in self.expense_list)
    
    def get_expense_by_category(self) -> Dict[str, float]:
        """Get expense totals by category."""
        expense_by_cat = {}
        for t in self.expense_list:
            expense_by_cat[t.category] = expense_by_cat.get(t.category, 0) + t.amount
        return expense_by_cat
    
    # ====== Savings Methods ======
    
    def set_savings_goal(self, amount: float) -> bool:
        """Set a savings goal."""
        if DataValidators.validate_amount(amount):
            self.savings_goal = amount
            return True
        return False
    
    def get_savings_balance(self) -> float:
        """Calculate current savings balance (income - expenses)."""
        return self.get_total_income() - self.get_total_expenses()
    
    def get_savings_progress(self) -> float:
        """Calculate progress towards savings goal as percentage."""
        if self.savings_goal == 0:
            return 0
        balance = self.get_savings_balance()
        return (balance / self.savings_goal) * 100
    
    # ====== Modification Methods ======
    
    def modify_transaction(self, transaction_id: int, new_amount: float = None,
                          new_category: str = None, new_description: str = None) -> bool:
        """
        Modify an existing transaction by its ID.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Search in both income and expense lists
        all_transactions = self.income_list + self.expense_list
        target = None
        
        for t in all_transactions:
            if id(t) == transaction_id:
                target = t
                break
        
        if target is None:
            return False
        
        if new_amount is not None and DataValidators.validate_amount(new_amount):
            target.amount = new_amount
        
        if new_category is not None and new_category in self.categories:
            target.category = new_category
        
        if new_description is not None:
            target.description = new_description
        
        return True
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction by its ID.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check income list
        for i, t in enumerate(self.income_list):
            if id(t) == transaction_id:
                del self.income_list[i]
                return True
        
        # Check expense list
        for i, t in enumerate(self.expense_list):
            if id(t) == transaction_id:
                del self.expense_list[i]
                return True
        
        return False
    
    # ====== Summary Methods ======
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all financial data."""
        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()
        savings_balance = total_income - total_expenses
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings_balance": savings_balance,
            "savings_goal": self.savings_goal,
            "savings_progress": self.get_savings_progress(),
            "income_by_category": self.get_income_by_category(),
            "expense_by_category": self.get_expense_by_category(),
            "income_count": len(self.income_list),
            "expense_count": len(self.expense_list)
        }
    
    def display_summary(self):
        """Print a formatted summary to the console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("               FINANCIAL SUMMARY")
        print("="*60)
        
        print(f"\nOVERVIEW")
        print(f"  Total Income:   {DataValidators.format_currency(summary['total_income'])}")
        print(f"  Total Expenses: {DataValidators.format_currency(summary['total_expenses'])}")
        print(f"  Net Savings:    {DataValidators.format_currency(summary['savings_balance'])}")
        
        if summary['savings_goal'] > 0:
            print(f"  Savings Goal:   {DataValidators.format_currency(summary['savings_goal'])}")
            print(f"  Progress:       {summary['savings_progress']:.1f}%")
        
        print(f"\nINCOME BY CATEGORY")
        if summary['income_by_category']:
            for cat, amount in summary['income_by_category'].items():
                print(f"  {cat}: {DataValidators.format_currency(amount)}")
        else:
            print("  No income recorded")
        
        print(f"\nEXPENSES BY CATEGORY")
        if summary['expense_by_category']:
            for cat, amount in summary['expense_by_category'].items():
                print(f"  {cat}: {DataValidators.format_currency(amount)}")
        else:
            print("  No expenses recorded")
        
        print(f"\nTRANSACTIONS")
        print(f"  Income transactions: {summary['income_count']}")
        print(f"  Expense transactions: {summary['expense_count']}")
        print("="*60)
    
    # ====== File Operations ======
    
    def save_to_json(self, filename: str = "finance_data.json") -> bool:
        """Save all data to a JSON file."""
        try:
            data = {
                "income": [t.to_dict() for t in self.income_list],
                "expenses": [t.to_dict() for t in self.expense_list],
                "savings_goal": self.savings_goal,
                "budget": self.to_dict(),
                "categories": self.categories
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def load_from_json(self, filename: str = "finance_data.json") -> bool:
        """Load data from a JSON file."""
        try:
            if not os.path.exists(filename):
                print(f"File {filename} does not exist.")
                return False
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Reset data
            self.income_list = [Transaction.from_dict(t) for t in data.get("income", [])]
            self.expense_list = [Transaction.from_dict(t) for t in data.get("expenses", [])]
            self.savings_goal = data.get("savings_goal", 0)
            
            # Load budget data
            budget_data = data.get("budget", {})
            self.monthly_budget = budget_data.get("monthly", {})
            self.weekly_budget = budget_data.get("weekly", {})
            
            self.categories = data.get("categories", self.categories)
            return True
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False
    
    def export_to_csv(self, filename: str = "finance_report.csv") -> bool:
        """Export all transactions to a CSV file."""
        try:
            all_transactions = []
            for t in self.income_list:
                all_transactions.append([t.date, t.transaction_type, t.category, 
                                        t.amount, t.description])
            for t in self.expense_list:
                all_transactions.append([t.date, t.transaction_type, t.category, 
                                        t.amount, t.description])
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
                writer.writerows(all_transactions)
            
            print(f"Data exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def generate_text_report(self, filename: str = "finance_report.txt") -> bool:
        """Generate a detailed text report."""
        try:
            summary = self.get_summary()
            
            with open(filename, 'w') as f:
                f.write("="*60 + "\n")
                f.write("         PERSONAL FINANCE REPORT\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("SUMMARY\n")
                f.write("-"*40 + "\n")
                f.write(f"Total Income:   {DataValidators.format_currency(summary['total_income'])}\n")
                f.write(f"Total Expenses: {DataValidators.format_currency(summary['total_expenses'])}\n")
                f.write(f"Net Savings:    {DataValidators.format_currency(summary['savings_balance'])}\n")
                if summary['savings_goal'] > 0:
                    f.write(f"Savings Goal:   {DataValidators.format_currency(summary['savings_goal'])}\n")
                    f.write(f"Progress:       {summary['savings_progress']:.1f}%\n")
                
                f.write("\nINCOME TRANSACTIONS\n")
                f.write("-"*40 + "\n")
                for t in self.income_list:
                    f.write(f"  {t}\n")
                
                f.write("\nEXPENSE TRANSACTIONS\n")
                f.write("-"*40 + "\n")
                for t in self.expense_list:
                    f.write(f"  {t}\n")
                
                f.write("\nBUDGET STATUS\n")
                f.write("-"*40 + "\n")
                for category, limit in self.monthly_budget.items():
                    spent = summary['expense_by_category'].get(category, 0)
                    remaining = limit - spent
                    f.write(f"  {category}: Budget {DataValidators.format_currency(limit)}, "
                           f"Spent {DataValidators.format_currency(spent)}, "
                           f"Remaining {DataValidators.format_currency(remaining)}\n")
            
            print(f"Text report generated: {filename}")
            return True
        except Exception as e:
            print(f"Error generating report: {e}")
            return False


# ============================================================
# Main Program Functions
# ============================================================

def get_valid_number(prompt: str, allow_zero: bool = True) -> float:
    """
    Get a valid numeric input from the user.
    
    Args:
        prompt: Prompt to display
        allow_zero: Whether to allow zero value
    
    Returns:
        float: Validated number
    
    Raises:
        ValueError: If input cannot be converted to float
    """
    while True:
        try:
            user_input = input(prompt)
            if user_input == "":
                return 0.0
            number = float(user_input)
            if number < 0:
                print("Amount cannot be negative. Please try again.")
                continue
            if not allow_zero and number == 0:
                print("Amount cannot be zero. Please try again.")
                continue
            return number
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_valid_category(categories: List[str], prompt: str = "Enter category: ") -> str:
    """Get a valid category from the user."""
    while True:
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        print("  0. Add custom category")
        
        try:
            choice = input(prompt)
            if choice == "0":
                custom = input("Enter custom category name: ").strip()
                if custom:
                    categories.append(custom)
                    return custom
                continue
            
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            print("Invalid choice. Please select a valid category.")
        except ValueError:
            print("Please enter a number.")


def get_valid_date(prompt: str = "Enter date (YYYY-MM-DD) or press Enter for today: ") -> str:
    """Get a valid date from the user."""
    while True:
        date_input = input(prompt)
        if date_input == "":
            return datetime.now().strftime("%Y-%m-%d")
        if DataValidators.validate_date(date_input):
            return date_input
        print("Invalid date format. Please use YYYY-MM-DD.")


def display_menu() -> int:
    """Display the main menu and get user choice."""
    print("\n" + "="*50)
    print("       PERSONAL FINANCE TRACKER")
    print("="*50)
    print(" 1.  Add Income")
    print(" 2.  Add Expense")
    print(" 3.  Set Savings Goal")
    print(" 4.  View Summary")
    print(" 5.  Modify Transaction")
    print(" 6.  Delete Transaction")
    print(" 7.  Save Data")
    print(" 8.  Load Data")
    print(" 9.  Export Report")
    print(" 10. Set Budget")
    print(" 0.  Exit")
    print("="*50)
    
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 0 <= choice <= 10:
                return choice
            print("Please enter a number between 0 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def add_income_menu(finance: FinanceTracker):
    """Handle adding income."""
    print("\nADD INCOME")
    print("-"*30)
    
    amount = get_valid_number("Amount: ")
    if amount == 0:
        print("Amount must be greater than zero.")
        return
    
    category = get_valid_category(finance.categories, "Select category: ")
    date = get_valid_date()
    description = input("Description (optional): ").strip()
    
    if finance.add_income(amount, category, date, description):
        print(f"Income added: {DataValidators.format_currency(amount)} - {category}")
    else:
        print("Failed to add income. Please check your input.")


def add_expense_menu(finance: FinanceTracker):
    """Handle adding expense."""
    print("\nADD EXPENSE")
    print("-"*30)
    
    amount = get_valid_number("Amount: ")
    if amount == 0:
        print("Amount must be greater than zero.")
        return
    
    category = get_valid_category(finance.categories, "Select category: ")
    date = get_valid_date()
    description = input("Description (optional): ").strip()
    
    if finance.add_expense(amount, category, date, description):
        print(f"Expense added: {DataValidators.format_currency(amount)} - {category}")
    else:
        print("Failed to add expense. Please check your input.")


def set_savings_goal_menu(finance: FinanceTracker):
    """Handle setting savings goal."""
    print("\nSET SAVINGS GOAL")
    print("-"*30)
    
    print(f"Current savings balance: {DataValidators.format_currency(finance.get_savings_balance())}")
    
    amount = get_valid_number("Enter savings goal (0 to clear): ")
    
    if amount == 0:
        finance.savings_goal = 0
        print("Savings goal cleared.")
    elif finance.set_savings_goal(amount):
        print(f"Savings goal set to {DataValidators.format_currency(amount)}")
    else:
        print("Invalid savings goal.")


def set_budget_menu(finance: FinanceTracker):
    """Handle setting budget."""
    print("\nSET BUDGET")
    print("-"*30)
    
    period = input("Enter period (monthly/weekly): ").lower()
    if period not in ["monthly", "weekly"]:
        print("Invalid period. Please enter 'monthly' or 'weekly'.")
        return
    
    category = get_valid_category(finance.categories, "Select category: ")
    amount = get_valid_number("Budget limit: ")
    
    if period == "monthly":
        if finance.set_monthly_budget(category, amount):
            print(f"Monthly budget set for {category}: {DataValidators.format_currency(amount)}")
        else:
            print("Failed to set budget.")
    else:
        if finance.set_weekly_budget(category, amount):
            print(f"Weekly budget set for {category}: {DataValidators.format_currency(amount)}")
        else:
            print("Failed to set budget.")


def modify_transaction_menu(finance: FinanceTracker):
    """Handle modifying a transaction."""
    print("\nMODIFY TRANSACTION")
    print("-"*30)
    
    # Show all transactions
    all_transactions = finance.income_list + finance.expense_list
    if not all_transactions:
        print("No transactions to modify.")
        return
    
    print("\nCurrent transactions:")
    for i, t in enumerate(all_transactions, 1):
        print(f"  {i}. {t}")
    
    try:
        idx = int(input("Select transaction number to modify (0 to cancel): "))
        if idx == 0:
            return
        if idx < 1 or idx > len(all_transactions):
            print("Invalid selection.")
            return
        
        target = all_transactions[idx - 1]
        target_id = id(target)
        
        print(f"\nModifying: {target}")
        print("Leave blank to keep current value.")
        
        new_amount = get_valid_number("New amount (or 0 to keep): ")
        if new_amount > 0:
            new_amount = None if new_amount == 0 else new_amount
        else:
            new_amount = None
        
        new_category = input(f"New category (current: {target.category}): ").strip()
        if new_category and new_category not in finance.categories:
            finance.categories.append(new_category)
        
        new_description = input(f"New description (current: {target.description}): ").strip()
        new_description = new_description if new_description else None
        
        if finance.modify_transaction(target_id, new_amount, new_category, new_description):
            print("Transaction modified successfully.")
        else:
            print("Failed to modify transaction.")
            
    except ValueError:
        print(" Invalid input.")


def delete_transaction_menu(finance: FinanceTracker):
    """Handle deleting a transaction."""
    print("\n  DELETE TRANSACTION")
    print("-"*30)
    
    all_transactions = finance.income_list + finance.expense_list
    if not all_transactions:
        print("No transactions to delete.")
        return
    
    print("\nCurrent transactions:")
    for i, t in enumerate(all_transactions, 1):
        print(f"  {i}. {t}")
    
    try:
        idx = int(input("Select transaction number to delete (0 to cancel): "))
        if idx == 0:
            return
        if idx < 1 or idx > len(all_transactions):
            print("Invalid selection.")
            return
        
        target = all_transactions[idx - 1]
        confirm = input(f"Are you sure you want to delete: {target}? (y/n): ").lower()
        
        if confirm == 'y':
            if finance.delete_transaction(id(target)):
                print("Transaction deleted successfully.")
            else:
                print("Failed to delete transaction.")
        else:
            print("Deletion cancelled.")
            
    except ValueError:
        print("Invalid input.")


def save_data_menu(finance: FinanceTracker):
    """Handle saving data."""
    print("\nSAVE DATA")
    print("-"*30)
    
    filename = input("Enter filename (default: finance_data.json): ").strip()
    if not filename:
        filename = "finance_data.json"
    
    if finance.save_to_json(filename):
        print(f"Data saved to {filename}")
    else:
        print("Failed to save data.")


def load_data_menu(finance: FinanceTracker):
    """Handle loading data."""
    print("\nLOAD DATA")
    print("-"*30)
    
    filename = input("Enter filename (default: finance_data.json): ").strip()
    if not filename:
        filename = "finance_data.json"
    
    if finance.load_from_json(filename):
        print(f"Data loaded from {filename}")
    else:
        print("Failed to load data.")


def export_report_menu(finance: FinanceTracker):
    """Handle exporting reports."""
    print("\nEXPORT REPORT")
    print("-"*30)
    
    print("1. Export to CSV")
    print("2. Generate Text Report")
    print("3. Both")
    
    choice = input("Select option: ").strip()
    
    if choice == "1":
        filename = input("Enter CSV filename (default: finance_report.csv): ").strip()
        filename = filename if filename else "finance_report.csv"
        finance.export_to_csv(filename)
    elif choice == "2":
        filename = input("Enter text filename (default: finance_report.txt): ").strip()
        filename = filename if filename else "finance_report.txt"
        finance.generate_text_report(filename)
    elif choice == "3":
        finance.export_to_csv()
        finance.generate_text_report()
    else:
        print("Invalid option.")


# ============================================================
# Main Function
# ============================================================

def main():
    """
    Main program loop with error handling.
    """
    print("\n" + "="*60)
    print("    WELCOME TO PERSONAL FINANCE TRACKER")
    print("    by Elsa Ledesma Saucedo")
    print("="*60)
    
    # Create finance tracker instance
    tracker = FinanceTracker()
    
    # Try to load existing data
    if os.path.exists("finance_data.json"):
        load = input("\nFound existing data file. Load it? (y/n): ").lower()
        if load == 'y':
            tracker.load_from_json("finance_data.json")
    
    # Main program loop
    while True:
        try:
            choice = display_menu()
            
            if choice == 0:
                # Exit with save prompt
                save = input("\nSave data before exiting? (y/n): ").lower()
                if save == 'y':
                    tracker.save_to_json()
                print("\nThank you for using Personal Finance Tracker!")
                break
            
            elif choice == 1:
                add_income_menu(tracker)
            
            elif choice == 2:
                add_expense_menu(tracker)
            
            elif choice == 3:
                set_savings_goal_menu(tracker)
            
            elif choice == 4:
                tracker.display_summary()
            
            elif choice == 5:
                modify_transaction_menu(tracker)
            
            elif choice == 6:
                delete_transaction_menu(tracker)
            
            elif choice == 7:
                save_data_menu(tracker)
            
            elif choice == 8:
                load_data_menu(tracker)
            
            elif choice == 9:
                export_report_menu(tracker)
            
            elif choice == 10:
                set_budget_menu(tracker)
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("   Please try again or contact support.")


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    main()
