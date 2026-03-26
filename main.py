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