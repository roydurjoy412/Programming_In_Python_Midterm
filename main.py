import json
import os
from datetime import date, datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class Entry:
    def __init__(self, entry_id, entry_type, amount, category, note, entry_date=None):
        self.id = entry_id
        self.type = entry_type
        self.amount = float(amount)
        self.category = category
        self.note = note
        self.date = entry_date if entry_date else str(date.today())

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount,
            "category": self.category,
            "note": self.note,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"], 
            data["type"], 
            data["amount"], 
            data["category"], 
            data["note"], 
            data["date"]
        )
    
class Storage:
    def __init__(self, filename="budget_data.json"):
        self.filename = filename

    def save_data(self, entries):
        with open(self.filename, 'w') as file:
            json.dump([e.to_dict() for e in entries], file, indent=4)

    def load_data(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return [Entry.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError, ValueError):
            return []
        
class BudgetManager:
    def __init__(self, storage):
        self.storage = storage
        self.entries = self.storage.load_data()

    def add_entry(self, entry_type, amount, category, note, entry_date):
        new_id = max((e.id for e in self.entries), default=0) + 1
        new_entry = Entry(new_id, entry_type, amount, category, note, entry_date)
        self.entries.append(new_entry)
        self.storage.save_data(self.entries)
        return new_id

    def get_all_entries(self):
        return self.entries

    def find_entry(self, entry_id):
        for e in self.entries:
            if e.id == int(entry_id):
                return e
        return None

    def update_entry(self, entry_id, new_amount=None, new_category=None, new_note=None):
        entry = self.find_entry(entry_id)
        if entry is None:
            return False
        
        if new_amount is not None:
            entry.amount = float(new_amount)
        if new_category is not None:
            entry.category = new_category.strip()
        if new_note is not None:
            entry.note = new_note.strip()
            
        self.storage.save_data(self.entries)
        return True

    def delete_entry(self, entry_id):
        entry_id = int(entry_id)
        original_count = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        
        if len(self.entries) < original_count:
            self.storage.save_data(self.entries)
            return True
        return False
    
    def search_by_category(self, search_term):
        results = []
        for e in self.entries:
            if search_term.lower() in e.category.lower():
                results.append(e)
        return results

    def sort_entries(self, by="date", reverse=True):
        if by == "amount":
            return sorted(self.entries, key=lambda x: x.amount, reverse=reverse)
        return sorted(self.entries, key=lambda x: x.date, reverse=reverse)
    
    def get_monthly_summary(self, year, month):
        total_income = 0
        total_expense = 0
        category_totals = {}

        for e in self.entries:
            try: 
                entry_year, entry_month, _ = e.date.split("-")
                
                if int(entry_year) == year and int(entry_month) == month:
                    if e.type == "income":
                        total_income += e.amount
                    else:
                        total_expense += e.amount
                        if e.category not in category_totals:
                            category_totals[e.category] = 0
                        category_totals[e.category] += e.amount
            except ValueError:
                continue 

        balance = total_income - total_expense

        warning = None
        if total_income > 0:
            if total_expense / total_income >= 0.8:
                warning = "Warning: You have spent 80% or more of your income this month!"

        top_category = None
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)

        return {
            "income": total_income,
            "expense": total_expense,
            "balance": balance,
            "top_category": top_category,
            "warning": warning
        }
    
class BudgetCLI:
    
    def __init__(self, manager):
        self.manager = manager
        self.console = Console() 

    def show_menu(self):
        self.console.print("\n[bold magenta]--- Menu ---[/bold magenta]")
        self.console.print("[bold yellow]1.[/bold yellow] Add new entry")
        self.console.print("[bold yellow]2.[/bold yellow] View all entries")
        self.console.print("[bold yellow]3.[/bold yellow] Edit an entry")
        self.console.print("[bold yellow]4.[/bold yellow] Delete an entry")
        self.console.print("[bold yellow]5.[/bold yellow] Search by category")
        self.console.print("[bold yellow]6.[/bold yellow] Sort entries")
        self.console.print("[bold yellow]7.[/bold yellow] Monthly summary report")
        self.console.print("[bold red]8.[/bold red] Exit")
        self.console.print("[bold magenta]-----------------------------[/bold magenta]")

    def run(self):
       
        self.console.print(Panel("Welcome to Student Budget Tracker", style="bold green"))
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()

            if choice == "1":
                self.handle_add()
            elif choice == "2":
                self.handle_view()
            elif choice == "3":
                self.handle_edit()
            elif choice == "4":
                self.handle_delete()
            elif choice == "5":
                self.handle_search()
            elif choice == "6":
                self.handle_sort()
            elif choice == "7":
                self.handle_monthly_report()
            elif choice == "8":
                self.console.print("\n[bold green]Thanks for using Budget Tracker! Keep tracking your money.[/bold green]\n")
                break
            else:
                self.console.print("[bold red]Invalid choice. Please enter a number between 1 and 8.[/bold red]")

    def handle_add(self):
        self.console.print("\n[bold cyan]--- Add New Entry ---[/bold cyan]")

        while True:
            entry_type = input("Type (income/expense): ").strip().lower()
            if entry_type in ["income", "expense"]:
                break
            self.console.print("Invalid type! Please enter 'income' or 'expense'.", style="bold red")

        while True:
            try:
                amount = float(input("Amount (৳): ").strip())
                if amount > 0:
                    break
                self.console.print("Amount must be greater than 0.", style="bold red")
            except ValueError:
                self.console.print("Invalid amount! Please enter a valid number.", style="bold red")

        if entry_type == "income":
            self.console.print("Hint: allowance, tuition, gift, freelance, etc.", style="dim")
        else:
            self.console.print("Hint: food, transport, photocopy, recharge, etc.", style="dim")

        while True:
            category = input("Category: ").strip().lower()
            if category:
                break
            self.console.print("Category cannot be empty.", style="bold red")

        note = input("Note (optional): ").strip()

        while True:
            date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            if not date_input:
                entry_date = None
                break
            
            parts = date_input.split("-")
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    entry_date = date_input
                    break
                except ValueError:
                    self.console.print("Invalid date! Please enter a real calendar date.", style="bold red")
            else:
                self.console.print("Invalid format! Please use YYYY-MM-DD (e.g., 2026-03-28).", style="bold red")

        new_id = self.manager.add_entry(entry_type, amount, category, note, entry_date)
        self.console.print(f"\n Entry added successfully! ID: {new_id}", style="bold green")

    def handle_view(self):
        self.console.print("\n[bold cyan]--- All Entries ---[/bold cyan]")
        
        entries = self.manager.get_all_entries()
        
        if not entries:
            self.console.print("No entries found. Add some entries first.", style="bold yellow")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", width=5, justify="right")
        table.add_column("Type", width=10, justify="center")
        table.add_column("Amount (৳)", width=12, justify="right")
        table.add_column("Category", width=15)
        table.add_column("Note", width=20)
        table.add_column("Date", width=12, justify="center")
        
        for e in entries:
            if e.type == "income":
                type_color = "[bold green]Income[/bold green]"
                amount_color = f"[bold green]+{e.amount:.2f}[/bold green]"
            else:
                type_color = "[bold red]Expense[/bold red]"
                amount_color = f"[bold red]-{e.amount:.2f}[/bold red]"
            
            table.add_row(
                str(e.id),
                type_color,
                amount_color,
                e.category.title(),
                e.note if e.note else "-",
                e.date
            )
        
        self.console.print(table)
        self.console.print(f"Total entries: {len(entries)}", style="dim")
        input("\nPress any key to return to the main menu...")

    def handle_edit(self):
        self.console.print("\n[bold cyan]--- Edit Entry ---[/bold cyan]")
        
        if not self.manager.get_all_entries():
            self.console.print("No entries found.", style="bold yellow")
            return
            
        self.handle_view()
        
        while True:
            id_input = input("\nEnter the ID to edit (or 'back' to cancel): ").strip()
            if id_input.lower() == "back":
                return
            try:
                entry_id = int(id_input)
                entry = self.manager.find_entry(entry_id)
                if entry:
                    break
                self.console.print(f"No entry found with ID {entry_id}.", style="bold red")
            except ValueError:
                self.console.print("Invalid ID. Please enter a number.", style="bold red")
                
        self.console.print(f"\nCurrent details:", style="dim")
        self.console.print(f"  Amount: ৳{entry.amount:.2f}", style="dim")
        self.console.print(f"  Category: {entry.category}", style="dim")
        self.console.print(f"  Note: {entry.note if entry.note else '-'}", style="dim")
        self.console.print("(Press Enter to keep current value)", style="dim")
        
        new_amount = None
        while True:
            amount_input = input("New amount (৳): ").strip()
            if not amount_input:
                break
            try:
                new_amount = float(amount_input)
                if new_amount > 0:
                    break
                self.console.print("Amount must be greater than 0.", style="bold red")
            except ValueError:
                self.console.print("Invalid amount. Please enter a valid number.", style="bold red")
                
        category_input = input("New category: ").strip().lower()
        new_category = category_input if category_input else None
        
        note_input = input("New note: ").strip()
        new_note = note_input if note_input else None
        
        self.manager.update_entry(entry_id, new_amount, new_category, new_note)
        self.console.print("\nEntry updated successfully!", style="bold green")

    def handle_delete(self):
        self.console.print("\n[bold cyan]--- Delete Entry ---[/bold cyan]")
        
        if not self.manager.get_all_entries():
            self.console.print("No entries found.", style="bold yellow")
            return
            
        self.handle_view()
        
        while True:
            id_input = input("\nEnter the ID to delete (or 'back' to cancel): ").strip()
            if id_input.lower() == "back":
                return
            try:
                entry_id = int(id_input)
                entry = self.manager.find_entry(entry_id)
                if entry:
                    break
                self.console.print(f"No entry found with ID {entry_id}.", style="bold red")
            except ValueError:
                self.console.print("Invalid ID. Please enter a number.", style="bold red")
                
        confirm = input(f"Are you sure you want to delete entry {entry_id}? (y/n): ").strip().lower()
        if confirm == 'y':
            self.manager.delete_entry(entry_id)
            self.console.print("\nEntry deleted successfully!", style="bold green")
        else:
            self.console.print("\nDeletion cancelled.", style="bold yellow")

    def handle_search(self):
        
        self.console.print("\n[bold cyan]--- Search by Category ---[/bold cyan]")
        
        if not self.manager.get_all_entries():
            self.console.print("No entries found.", style="bold yellow")
            return
        
        search_term = input("Enter category to search (or press Enter to cancel): ").strip().lower()
        if not search_term:
            return
        
        results = self.manager.search_by_category(search_term)
        
        if not results:
            self.console.print(f"No entries found for '{search_term}'.", style="bold yellow")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", width=5, justify="right")
        table.add_column("Type", width=10, justify="center")
        table.add_column("Amount (৳)", width=12, justify="right")
        table.add_column("Category", width=15)
        table.add_column("Note", width=20)
        table.add_column("Date", width=12, justify="center")
        
        for e in results:
            if e.type == "income":
                type_color = "[bold green]Income[/bold green]"
                amount_color = f"[bold green]+{e.amount:.2f}[/bold green]"
            else:
                type_color = "[bold red]Expense[/bold red]"
                amount_color = f"[bold red]-{e.amount:.2f}[/bold red]"
            
            table.add_row(
                str(e.id),
                type_color,
                amount_color,
                e.category.title(),
                e.note if e.note else "-",
                e.date
            )
        
        self.console.print(table)
        self.console.print(f"Found {len(results)} result(s) for '{search_term}'.", style="dim")
    
    
def handle_sort(self):
        self.console.print("\n[bold cyan]--- Sort Entries ---[/bold cyan]")
        
        if not self.manager.get_all_entries():
            self.console.print("No entries found.", style="bold yellow")
            return
        
        self.console.print("[bold yellow]1.[/bold yellow] Sort by amount (high to low)")
        self.console.print("[bold yellow]2.[/bold yellow] Sort by amount (low to high)")
        self.console.print("[bold yellow]3.[/bold yellow] Sort by date (newest first)")
        self.console.print("[bold yellow]4.[/bold yellow] Sort by date (oldest first)")
        
        choice = input("\nEnter your choice (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        if choice == "1":
            sorted_entries = self.manager.sort_entries(by="amount", reverse=True)
            label = "Amount (High to Low)"
        elif choice == "2":
            sorted_entries = self.manager.sort_entries(by="amount", reverse=False)
            label = "Amount (Low to High)"
        elif choice == "3":
            sorted_entries = self.manager.sort_entries(by="date", reverse=True)
            label = "Date (Newest First)"
        elif choice == "4":
            sorted_entries = self.manager.sort_entries(by="date", reverse=False)
            label = "Date (Oldest First)"
        else:
            self.console.print("Invalid choice.", style="bold red")
            return
        
        self.console.print(f"\n[bold cyan]Sorted by: {label}[/bold cyan]")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", width=5, justify="right")
        table.add_column("Type", width=10, justify="center")
        table.add_column("Amount (৳)", width=12, justify="right")
        table.add_column("Category", width=15)
        table.add_column("Note", width=20)
        table.add_column("Date", width=12, justify="center")
        
        for e in sorted_entries:
            if e.type == "income":
                type_color = "[bold green]Income[/bold green]"
                amount_color = f"[bold green]+{e.amount:.2f}[/bold green]"
            else:
                type_color = "[bold red]Expense[/bold red]"
                amount_color = f"[bold red]-{e.amount:.2f}[/bold red]"
            
            table.add_row(
                str(e.id),
                type_color,
                amount_color,
                e.category.title(),
                e.note if e.note else "-",
                e.date
            )
        
        self.console.print(table)



if __name__ == "__main__":
    storage = Storage("budget_data.json")
    manager = BudgetManager(storage)
    app = BudgetCLI(manager)
    app.run()