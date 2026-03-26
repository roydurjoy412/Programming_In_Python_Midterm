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
        except (json.JSONDecodeError, KeyError):
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
            entry.category = new_category
        if new_note is not None:
            entry.note = new_note
            
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