# config_ui.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import re
from datetime import datetime
from backend.game_state_parser import parse_game_state
from backend.history_manager import HistoryManager
from backend.narrator import Narrator
from backend.game_state_manager import GameStateManager
from frontend.themes import themes_list

class ConfigUI:
    def __init__(self, root, canvas, console_widget, items_gui, quests_gui, config_manager, history_manager, game_state_manager, narrator):
        self.root = root
        self.canvas = canvas
        self.console_widget = console_widget
        self.items_gui = items_gui
        self.quests_gui = quests_gui
        self.config_manager = config_manager
        self.history_manager = history_manager
        self.game_state_manager = game_state_manager
        self.narrator = narrator
        
        # Load the current theme index from the config manager
        self.current_theme_index = int(self.config_manager.get_config("theme_index") or 0)
        self.current_theme = themes_list[self.current_theme_index]
        self.create_cycle_theme_button()

        # Store button IDs for later reference
        self.font_size_button_id = None
        self.font_type_button_id = None

        # Create UI elements
        self.create_font_size_button()
        self.create_font_type_button()
        self.create_delete_latest_save_button()

        # Bind the Configure event to the update_button_positions method
        self.root.bind('<Configure>', lambda event: self.update_button_positions())
        
        # Predefined font sizes and fonts
        self.font_sizes = [10, 12, 14, 16, 18, 20]
        self.fonts = ["Arial", "Courier", "Helvetica", "Times New Roman"]

        self.set_initial_background()
        
        # Get initial config values
        self.current_font_size_index = self.font_sizes.index(self.config_manager.get_config("font_size"))
        self.current_font_index = self.fonts.index(self.config_manager.get_config("font"))

        self.apply_initial_font_type()
        self.apply_initial_font_size()
        self.update_ui_with_theme(self.current_theme)

    def remove_latest_save(self):
        data_dir = '../data'  # Update this to your data directory
        files = os.listdir(data_dir)
        timestamp_regex = re.compile(r'\d{8}_\d{6}')
        timestamps = []
        for file in files:
            match = timestamp_regex.search(file)
            if match:
                timestamps.append(datetime.strptime(match.group(), '%Y%m%d_%H%M%S'))
        
        if timestamps:
            latest_timestamp = max(timestamps)
            for file in files:
                if datetime.strptime(timestamp_regex.search(file).group(), '%Y%m%d_%H%M%S') == latest_timestamp:
                    os.remove(os.path.join(data_dir, file))
                    print(f"Deleted: {file}")

        self.reload_all_components()

    def confirm_latest_save_removal(self):
        # Ask for confirmation before deleting
        response = messagebox.askyesno("Confirm", "Are you sure you want to delete the latest save?")
        if response:
            self.remove_latest_save()

    def create_delete_latest_save_button(self):
        # Create the button for deleting the latest save and place it on the canvas
        delete_latest_save_button = tk.Button(self.root, text="Delete Latest Save", command=self.confirm_latest_save_removal)
        # Create the window once and store its ID
        self.delete_latest_save_button_id = self.canvas.create_window(896, 150, anchor=tk.CENTER, window=delete_latest_save_button)

    def create_font_size_button(self):
        # Create the button for changing font size and place it on the canvas
        font_size_button = tk.Button(self.root, text="Size", command=self.cycle_font_size)
        # Create the window once and store its ID
        self.font_size_button_id = self.canvas.create_window(896, 50, anchor=tk.CENTER, window=font_size_button)

    def create_font_type_button(self):
        # Create the button for changing font type and place it on the canvas
        font_type_button = tk.Button(self.root, text="Font", command=self.cycle_font_type)
        # Create the window once and store its ID
        self.font_type_button_id = self.canvas.create_window(896, 100, anchor=tk.CENTER, window=font_type_button)

    def cycle_font_size(self):
        # Cycle through font sizes
        self.current_font_size_index = (self.current_font_size_index + 1) % len(self.font_sizes)
        new_font_size = self.font_sizes[self.current_font_size_index]
        new_font_name = self.config_manager.get_config("font")
        self.console_widget.config(font=(new_font_name, new_font_size))
        self.items_gui.update_font(new_font_name, new_font_size)  # Update the font in items_gui
        self.quests_gui.update_font(new_font_name, new_font_size)  # Update the font in quests_gui
        self.config_manager.update_config("font_size", new_font_size)
        self.config_manager.save_config()

    def apply_initial_font_size(self):
        new_font_size = self.font_sizes[self.current_font_size_index]
        new_font_name = self.config_manager.get_config("font")
        # Set the font size for all relevant widgets
        self.console_widget.config(font=(new_font_name, new_font_size))
        self.items_gui.update_font(new_font_name, new_font_size)
        self.quests_gui.update_font(new_font_name, new_font_size)

    def cycle_font_type(self):
        # Cycle through fonts
        self.current_font_index = (self.current_font_index + 1) % len(self.fonts)
        new_font = self.fonts[self.current_font_index]
        new_font_size = self.config_manager.get_config("font_size")
        self.console_widget.config(font=(new_font, new_font_size))
        self.items_gui.update_font(new_font, new_font_size)  # Update the font in items_gui
        self.quests_gui.update_font(new_font, new_font_size)  # Update the font in quests_gui
        self.config_manager.update_config("font", new_font)
        self.config_manager.save_config()

    def apply_initial_font_type(self):
        new_font = self.fonts[self.current_font_index]
        new_font_size = self.config_manager.get_config("font_size")
        # Set the font type for all relevant widgets
        self.console_widget.config(font=(new_font, new_font_size))
        self.items_gui.update_font(new_font, new_font_size)
        self.quests_gui.update_font(new_font, new_font_size)


    def update_button_positions(self):
        # Get the current canvas width and height
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        padding_x = 30  # Horizontal padding from the right edge
        padding_y = 30  # Vertical padding from the bottom edge
        button_spacing = 10  # Space between buttons

        # Y coordinate for all buttons
        buttons_y = canvas_height - padding_y

        # Start positioning buttons from the right
        # Calculate X coordinate for the rightmost button (Size)
        size_button_width = self.canvas.bbox(self.font_size_button_id)[2] - self.canvas.bbox(self.font_size_button_id)[0]
        size_button_x = canvas_width - padding_x - size_button_width / 2

        # Calculate X coordinate for the Font button
        font_button_width = self.canvas.bbox(self.font_type_button_id)[2] - self.canvas.bbox(self.font_type_button_id)[0]
        font_button_x = size_button_x - size_button_width / 2 - font_button_width / 2 - button_spacing

        # Calculate X coordinate for the Theme button
        theme_button_width = self.canvas.bbox(self.cycle_theme_button_id)[2] - self.canvas.bbox(self.cycle_theme_button_id)[0]
        theme_button_x = font_button_x - font_button_width / 2 - theme_button_width / 2 - button_spacing

        # Calculate X coordinate for the Delete Latest Save button
        delete_save_button_width = self.canvas.bbox(self.delete_latest_save_button_id)[2] - self.canvas.bbox(self.delete_latest_save_button_id)[0]
        delete_save_button_x = theme_button_x - theme_button_width / 2 - delete_save_button_width / 2 - button_spacing

        # Move the buttons to the new positions
        self.canvas.coords(self.font_size_button_id, size_button_x, buttons_y)
        self.canvas.coords(self.font_type_button_id, font_button_x, buttons_y)
        self.canvas.coords(self.cycle_theme_button_id, theme_button_x, buttons_y)
        self.canvas.coords(self.delete_latest_save_button_id, delete_save_button_x, buttons_y)


    def reload_all_components(self):
        # Reload the narrative history, game state, narrator, etc.
        self.history_manager.reload_data()
        self.game_state_manager.reload_data()
        self.narrator.reload_data()

        # Clear the existing content in the console widget
        self.console_widget.clear_text()
        
        # Fetch the updated narrative history using the correct method name
        updated_narrative_text = self.history_manager.load_narrative_history()
        
        # Append the updated narrative history to the console widget
        self.console_widget.append_text(updated_narrative_text)
        
        # Parse the updated game state and update the GUI
        items, quests = parse_game_state()
        self.items_gui.update_items(items)
        self.quests_gui.update_quests(quests)

        #print("[ConfigUI] All components have been reloaded.")

    def cycle_theme(self):
        # Cycle to the next theme
        self.current_theme_index = (self.current_theme_index + 1) % len(themes_list)
        new_theme = themes_list[self.current_theme_index]
        self.update_ui_with_theme(new_theme)

        # Update the current theme index in the config manager
        self.config_manager.update_config("theme_index", self.current_theme_index)
        self.config_manager.save_config()  # Don't forget to save the updated configuration

        # Set the new theme as the current theme
        self.current_theme = new_theme

        # Update the UI elements with the new theme
        self.update_ui_with_theme(new_theme)

        # Update the background image
        self.set_initial_background()

    def create_cycle_theme_button(self):
        # Create the button for cycling themes and place it on the canvas
        cycle_theme_button = tk.Button(self.root, text="Theme", command=self.cycle_theme)
        # Create the window once and store its ID
        self.cycle_theme_button_id = self.canvas.create_window(896, 200, anchor=tk.CENTER, window=cycle_theme_button)

    def update_ui_with_theme(self, theme):
        #print(f"[ConfigUI] Updating UI with theme: {theme.name}")

        # Get the current canvas width and height
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Clear any existing background image
        if hasattr(self, 'background_image_id'):
            self.canvas.delete(self.background_image_id)
            delattr(self, 'background_image_id')
            #print("[ConfigUI] Cleared existing background image")

        # Try to load the new background image if it exists
        if hasattr(theme, 'background_image') and theme.background_image:
            try:
                new_background_image = Image.open(theme.background_image)
                new_background_image_tk = ImageTk.PhotoImage(new_background_image)
                self.background_image_id = self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=new_background_image_tk, tags="background")
                self.canvas.lower(self.background_image_id)  # Ensure the image is behind other canvas items
                self.background_image = new_background_image_tk  # Update reference to prevent garbage collection
                #print("[ConfigUI] Set new background image")
                
                # Force the canvas to redraw itself
                self.canvas.update()
                
            except FileNotFoundError:
                #print(f"[ConfigUI] Background image not found for theme '{theme.name}'. Using solid color fallback.")
                self.canvas.config(bg=theme.console_bg_color)  # Use console background color as fallback
                #print("[ConfigUI] Set solid color background")
        else:
            # If the theme doesn't have a background image attribute or it's set to None
            self.canvas.config(bg=theme.console_bg_color)
            #print("[ConfigUI] Set solid color background")

        # Update the text color in console widget and other text widgets
        self.console_widget.config(fg=theme.text_color)
        self.items_gui.update_text_color(theme.text_color)  # Update the text color in items GUI
        self.quests_gui.update_text_color(theme.text_color)  # Update the text color in quests GUI

        # Update console background color
        self.console_widget.config(bg=theme.console_bg_color)
        self.items_gui.update_bg_color(theme.console_bg_color)  # Update the background color in items GUI
        self.quests_gui.update_bg_color(theme.console_bg_color)  # Update the background color in quests GUI

        # Another call to force the canvas to redraw
        self.canvas.update()

        #print("[ConfigUI] Updated UI with theme")


    def set_initial_background(self):
        # Load the background image from the default theme
        try:
            initial_background_image = Image.open(self.current_theme.background_image)
            initial_background_image_tk = ImageTk.PhotoImage(initial_background_image)

            # Get the current canvas width and height
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Create the background image and keep a reference to avoid garbage collection
            # Anchor the center of the image to the center of the window
            self.background_image_id = self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=initial_background_image_tk)
            self.canvas.lower(self.background_image_id)  # Ensure the image is behind other canvas items
            self.background_image = initial_background_image_tk

        except FileNotFoundError:
            # If the image file is not found, use a solid color background
            #print(f"[ConfigUI] Background image not found for theme '{self.current_theme.name}'. Using solid color fallback.")
            self.canvas.config(bg=self.current_theme.console_bg_color)
