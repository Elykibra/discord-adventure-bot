class Bag:
    def __init__(self, slots=10):
        self.slots = slots
        self.items = []

    def add_item(self, item):
        if len(self.items) >= self.slots:
            return False
        self.items.append(item)
        return True

    def expand(self, extra_slots):
        self.slots += extra_slots

    def to_dict(self):
        return {"slots": self.slots, "items": self.items}

    @classmethod
    def from_dict(cls, data):
        bag = cls(slots=data.get("slots", 10))
        bag.items = data.get("items", [])
        return bag
