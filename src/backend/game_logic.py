# game_logic.py

import asyncio
from backend.game_state_parser import parse_game_state

class GameLogic:
    def __init__(self, history_manager, narrator, game_state_manager, items_gui, quests_gui, game_gui):
        self.history_manager = history_manager
        self.narrator = narrator
        self.game_state_manager = game_state_manager
        self.items_gui = items_gui
        self.quests_gui = quests_gui
        self.game_gui = game_gui
        self.accept_command = True 

    async def process_command_streaming(self, command):
        self.game_gui.set_processing_command(True)
        self.game_gui.set_streaming_narrative(True)
        print("[GameLogic] Starting process_command_streaming")
        await self.narrator.process_command_streaming(command)
        print("[GameLogic] Finished process_command_streaming")
        
        full_response = self.narrator.get_full_response()
        # Append the command and the full response to the narrative history
        self.history_manager.append_latest_narrative(command, full_response)
        self.history_manager.save_narrative_history()

        self.game_gui.set_streaming_narrative(False)

    async def update_quests_and_items(self, command):
        print("[GameLogic] Starting update_quests_and_items")

        # Await the asynchronous process_command method of GameStateManager
        await self.game_state_manager.process_command()

        # Update GUI
        items, quests = parse_game_state()
        self.items_gui.update_items(items)
        self.quests_gui.update_quests(quests)

        print("[GameLogic] Finished update_quests_and_items")

        # TODO Reset the is_processing_command flag to False. Move this to another place so that it works with the summary.
        self.game_gui.set_processing_command(False)
    
    def initialize_game_state(self):
        # Parse the game state
        items, quests = parse_game_state()
        # Update GUI components
        self.items_gui.update_items(items)
        self.quests_gui.update_quests(quests)