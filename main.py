import json
import os
from datetime import date

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