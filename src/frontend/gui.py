# gui.py

import tkinter as tk
import asyncio
import os

from backend.game_logic import GameLogic
from backend.narrator import Narrator
from backend.history_manager import HistoryManager
from backend.game_state_manager import GameStateManager
from backend.config_manager import ConfigManager
from backend.lexi import Lexi
from backend.shared_timestamp import SharedTimestamp

from frontend.console_widget import ConsoleWidget
from frontend.items_widget import ItemsWidget
from frontend.quests_widget import QuestsWidget
from frontend.word_widget import WordWidget
from frontend.config_ui import ConfigUI
from frontend.themes import themes_list

class GameGUI:
    def __init__(self):
        SharedTimestamp.set_timestamp()
        self.root = tk.Tk()
        self.root.title("Parchment Adventures")
        self.initialize_window()
        self.create_widgets()
        self.bind_events()
        self.game_logic = self.create_game_logic()
        self.display_initial_history()
        self.game_logic.initialize_game_state()
        self.root.update()
        self.update_gui_positions()
        self.is_processing_command = False
        self.is_streaming_narrative = False

    def set_processing_command(self, is_processing):
        self.is_processing_command = is_processing
        # Used for preventing commands being sent

    def set_streaming_narrative(self, is_typing):
        self.is_streaming_narrative = is_typing
        # Used for preventing typing during streams

    def initialize_window(self):
        self.config_manager = ConfigManager()
        window_width = int(self.config_manager.get_config("window_width") or "1792")
        window_height = int(self.config_manager.get_config("window_height") or "1080")
        current_theme_index = int(self.config_manager.get_config("theme_index") or 0)
        current_theme = themes_list[current_theme_index]
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas = tk.Canvas(self.root, width=window_width, height=window_height, bg=current_theme.console_bg_color)
        self.canvas.pack(fill="both", expand=True)

    def create_widgets(self):
        self.console_widget = ConsoleWidget(self.canvas, self)
        self.items_gui = ItemsWidget(self.canvas)
        self.quests_gui = QuestsWidget(self.canvas)
        self.word_list_gui = WordWidget(self.canvas)

        # Placement of console_widget, items and quests
        self.console_window = self.canvas.create_window(696, 200, anchor=tk.NW, window=self.console_widget, width=400, height=600)
        self.items_window_window = self.canvas.create_window(1592, 540, anchor=tk.CENTER, window=self.items_gui, width=200, height=600)
        self.quests_window_window = self.canvas.create_window(200, 540, anchor=tk.CENTER, window=self.quests_gui, width=200, height=600)
        self.word_list_window = self.canvas.create_window(200, 540, anchor=tk.CENTER, window=self.word_list_gui, width=200, height=600)
        self.canvas.itemconfigure(self.word_list_window, state='hidden')  # Initially hide the word list

        # Initialize the necessary managers for ConfigUI
        lexi = Lexi()
        history_manager = HistoryManager()
        game_state_manager = GameStateManager(history_manager)
        narrator = Narrator(self, history_manager, lexi)

        # Instantiate ConfigUI with all required arguments
        self.config_ui = ConfigUI(
            self.root, 
            self.canvas, 
            self.console_widget, 
            self.items_gui, 
            self.quests_gui, 
            self.word_list_gui,
            self.config_manager, 
            history_manager, 
            game_state_manager, 
            narrator,
            self  # Pass the GameGUI instance
        )
        
        # Force an update of the GUI layout to calculate widget dimensions
        self.root.update_idletasks()
        self.update_gui_positions()        

    def toggle_word_list_view(self):
        # Check which widget is currently visible and toggle
        if self.canvas.itemcget(self.word_list_window, 'state') == 'hidden':
            self.canvas.itemconfigure(self.word_list_window, state='normal')
            self.canvas.itemconfigure(self.quests_window_window, state='hidden')
        else:
            self.canvas.itemconfigure(self.word_list_window, state='hidden')
            self.canvas.itemconfigure(self.quests_window_window, state='normal')

        self.canvas.update_idletasks()
        self.update_gui_positions()

    def bind_events(self):
        self.console_widget.bind('<Return>', self.handle_command)
        self.root.bind('<Configure>', self.on_window_resize)

    def create_game_logic(self):
        history_manager = HistoryManager()
        lexi = Lexi()  # Create an instance of Lexi
        self.narrator = Narrator(self, history_manager, lexi)  # Pass the Lexi instance to Narrator
        game_state_manager = GameStateManager(history_manager)
        return GameLogic(history_manager, self.narrator, game_state_manager, self.items_gui, self.quests_gui, self, lexi, self.word_list_gui)  # Pass Lexi to GameLogic


    def display_initial_history(self):
        print("[GameGUI] Display initial history called")
        initial_narrative_text = self.game_logic.history_manager.narrative_history
        initial_narrative_text = initial_narrative_text.rstrip('\n')

        # Load the summary
        summary = self.game_logic.history_manager.load_latest_summary()

        # Determine the text to display
        if initial_narrative_text:
            text_to_display = initial_narrative_text + "\n\n" + summary
        else:
            welcome_text = "Greetings, valiant traveler! Your epic saga unfolds from this very moment. Within the mystic realms of parchment and ink, your path awaits. Should you wish to tailor your initial quests and arsenal, the ancient scrolls within the config folder hold the key to your destiny. Embark now, for adventure beckons!"
            text_to_display = welcome_text + "\n\n" + summary

        self.console_widget.append_text(text_to_display + '\n\n')

    def update_gui_positions(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate new dimensions for the console_widget
        console_widget_new_width = int(canvas_width * 0.5)  # Adjust as needed
        console_widget_x = (canvas_width - console_widget_new_width) // 2
        console_widget_y = canvas_height / 2 - self.console_widget.winfo_height() / 2

        # Adjust the size of the window within the canvas that holds the console_widget
        self.canvas.itemconfig(self.console_window, width=console_widget_new_width)
        self.canvas.coords(self.console_window, console_widget_x, console_widget_y)

        # Update positions of items_gui and quests_gui
        items_gui_x = canvas_width - (self.items_gui.winfo_width() / 2 + 50)
        quests_gui_x = 50 + (self.quests_gui.winfo_width() / 2)
        world_list_gui_x = 50 + (self.word_list_gui.winfo_width() / 2)
        self.canvas.coords(self.items_window_window, items_gui_x, canvas_height / 2)
        self.canvas.coords(self.quests_window_window, quests_gui_x, canvas_height / 2)
        self.canvas.coords(self.word_list_window, world_list_gui_x, canvas_height / 2)

        # Update the position of the background image if it exists
        if hasattr(self.config_ui, 'background_image_id'):
            new_x = canvas_width // 2
            new_y = canvas_height // 2
            self.canvas.coords(self.config_ui.background_image_id, new_x, new_y)

        # Update the positions of the buttons
        if hasattr(self, 'config_ui') and self.config_ui:
            self.config_ui.update_button_positions()

    def on_window_resize(self, event):
        current_width = event.width
        current_height = event.height
        if current_width > 800 and current_height > 600:
            self.config_manager.update_config("window_width", current_width)
            self.config_manager.update_config("window_height", current_height)
            self.config_manager.save_config()
            self.update_gui_positions(event)

    def start_async_loop(self, loop):
        print("[GameGUI] Starting asyncio event loop")
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def handle_command(self, event):
        # Creates a new timestamp
        SharedTimestamp.set_timestamp()

        if self.is_processing_command:
            print("[GameGUI] Still processing the previous command. Please wait.")
            return  # Exit the method if a command is already being processed

        self.is_processing_command = True  # Set the flag to True as processing starts
        command = self.console_widget.get_command()
        print(f"[GameGUI] Command received: {command}")
        self.console_widget.append_text("\n")

        word_list = self.narrator.lexi.get_content(self.word_list_gui)
        self.narrator.lexi.save_word_list(word_list)
        
        self.start_streaming_command_processing(command)

    def start_streaming_command_processing(self, command):
        print("[GameGUI] Starting streaming command processing")
        loop = asyncio.get_event_loop()
        print(f"[GameGUI] Is event loop running: {loop.is_running()}")
        loop.create_task(self.handle_streaming_command(command))

    async def handle_streaming_command(self, command):
        print(f"[GameGUI] About to process streaming command: {command}")

        # Start the process_command_streaming task
        process_task = asyncio.create_task(self.game_logic.process_command_streaming(command))

        # Wait for the process_command_streaming task to complete
        await process_task

        # Retrieve the narrative history
        narrative_history = self.game_logic.history_manager.narrative_history

        # Start the update_quests_and_items task and create_summary task concurrently
        update_quests_and_items_task = asyncio.create_task(self.game_logic.update_quests_and_items(command))
        create_summary_task = asyncio.create_task(self.game_logic.history_manager.create_summary())

        # Wait for both tasks to complete
        await asyncio.gather(update_quests_and_items_task, create_summary_task)

    def run_pending_async_tasks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(0))  # Run pending tasks and return
        self.root.after(100, self.run_pending_async_tasks)  # Schedule next check

    def start(self):
        # Set up the async loop
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

        # Schedule the periodic check for asyncio tasks
        self.root.after(100, self.run_pending_async_tasks)

        # Start the Tkinter main loop
        self.root.mainloop()

if __name__ == "__main__":
    game_gui = GameGUI()
    game_gui.start()