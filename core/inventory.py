# core/inventory.py
# This file contains the game logic for items and player inventories (bags).
# It does NOT handle Discord commands, only the underlying mechanics.

from data.items import ITEMS  # We import our item data from the data layer


class Item:
    """Represents a single instance of an item."""

    def __init__(self, item_id: str, quantity: int = 1):
        # Look up the base item data from our ITEMS dictionary
        item_data = ITEMS.get(item_id)
        if not item_data:
            raise ValueError(f"Item with ID '{item_id}' not found in data/items.py")

        self.item_id = item_id
        self.quantity = quantity

        # Assign all attributes from the data file to this object
        self.name = item_data.get('name', 'Unknown Item')
        self.description = item_data.get('description', '')
        self.category = item_data.get('category', 'Misc')
        self.price = item_data.get('price')
        self.slot = item_data.get('slot')
        self.effect = item_data.get('effect')
        # Add any other item attributes here in the future

    def __repr__(self):
        return f"Item(id='{self.item_id}', name='{self.name}', quantity={self.quantity})"


class Bag:
    """Represents a player's bag, managing a collection of items."""

    def __init__(self, owner_id: int, items_data: list = None):
        """
        Initializes the Bag.
        'items_data' should be a list of dicts, e.g., [{'item_id': 'potion', 'quantity': 5}]
        """
        self.owner_id = owner_id
        self.items = {}  # We'll use a dictionary for faster lookups: {item_id: Item_object}

        if items_data:
            for item_info in items_data:
                self.add_item(item_info['item_id'], item_info['quantity'])

    def add_item(self, item_id: str, quantity: int = 1):
        """Adds an item to the bag or increases its quantity."""
        if quantity <= 0:
            return

        if item_id in self.items:
            # If item already exists, just increase the quantity
            self.items[item_id].quantity += quantity
        else:
            # If it's a new item, create an Item object and add it
            try:
                self.items[item_id] = Item(item_id, quantity)
            except ValueError as e:
                print(f"Warning: Could not add item. {e}")

    def remove_item(self, item_id: str, quantity: int = 1):
        """Removes an item from the bag or decreases its quantity."""
        if quantity <= 0:
            return

        if item_id in self.items:
            self.items[item_id].quantity -= quantity
            # If the quantity drops to 0 or below, remove the item entirely
            if self.items[item_id].quantity <= 0:
                del self.items[item_id]

    def get_item(self, item_id: str) -> Item | None:
        """Retrieves a specific item object from the bag."""
        return self.items.get(item_id)

    def get_all_items(self) -> list[Item]:
        """Returns a list of all item objects in the bag."""
        return list(self.items.values())

    def to_dict_for_saving(self) -> list[dict]:
        """Converts the bag's contents to a simple list of dicts for saving to the DB."""
        return [
            {'item_id': item.item_id, 'quantity': item.quantity}
            for item in self.items.values()
        ]