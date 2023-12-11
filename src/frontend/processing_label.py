# processing_label.py

import tkinter as tk
import random

class ProcessingLabel:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.label = tk.Label(root, text="Processing...", font=("Arial", 24))
        self.label_id = canvas.create_window(896, 512, anchor=tk.CENTER, window=self.label)
        canvas.itemconfigure(self.label_id, state='hidden')  # Hide the label initially

        # List of whimsical loading messages the processing label can use
        self.loading_messages = [
            "The scroll is weaving your fate...",
            "Ink is flowing, magic is brewing...",
            "The parchment is whispering secrets...",
            "Ancient runes are taking shape...",
            "The quill dances across the parchment...",
            "Enchantments are being scribed...",
            "Your adventure is being penned...",
            "Mystic quill at work...",
            "Scribing the unseen, wait a brief spell...",
            "Unfolding tales take time, patience..."
            # ... (add all phrases here) ...
        ]

    def show(self):
        message = random.choice(self.loading_messages)
        self.label.config(text=message)  # Update the label text
        self.canvas.itemconfigure(self.label_id, state='normal')  # Show the label
        self.root.update_idletasks()  # Update the GUI to show the label immediately

    def hide(self):
        self.canvas.itemconfigure(self.label_id, state='hidden')  # Hide the label

    def update_text(self, text):
        self.label.config(text=text)
