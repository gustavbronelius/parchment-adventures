# File: game_state_manager.py

from openai import AsyncOpenAI
import json
import os
import tiktoken
from backend.history_manager import HistoryManager
from backend.shared_timestamp import SharedTimestamp
from datetime import datetime


class GameStateManager:
    def __init__(self, history_manager):
        self.history_manager = history_manager
        self.game_state = self.load_game_state()
        self.data_dir = '../data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.conversation_history = self.load_past_conversation()
        self.initialize_openai_context()  # Initialize OpenAI context during the object creation
        self.api_key = self.get_api_key()  # Get the API key
        self.client = AsyncOpenAI(api_key=self.api_key)     

    def get_api_key(self, file_path='../openai.api_key.txt'):
        # Check if the file exists
        if not os.path.exists(file_path):
            # If the file doesn't exist, prompt the user to enter their API key
            api_key = input("Enter your OpenAI API key: ")
            # Write the API key to the file
            with open(file_path, 'w') as file:
                file.write(api_key)
        else:
            # If the file exists, read the API key from the file
            with open(file_path, 'r') as file:
                api_key = file.read().strip()
        return api_key

    def load_game_state(self):
        game_state_dir = '../data'
        game_state_files = [f for f in os.listdir(game_state_dir) if f.startswith('game_state_')]
        if not game_state_files:  # if the list is empty, fall back to the default game_state.txt
            game_state_file_path = os.path.join('..', 'config', 'game_state.txt')  # Updated path to ../config
        else:
            latest_game_state_file = max(game_state_files, key=lambda f: os.path.getmtime(os.path.join(game_state_dir, f)))
            game_state_file_path = os.path.join(game_state_dir, latest_game_state_file)

        with open(game_state_file_path, 'r') as file:
            game_state = file.read()  # Read the contents of the file as a string
        
        return game_state
    
    def initialize_openai_context(self):
        self.conversation_history = self.load_past_conversation()
        if not self.conversation_history:
            task_description_file_path = '../config/game_state_manager_task_description.txt'
            if os.path.exists(task_description_file_path):
                with open(task_description_file_path, 'r') as file:
                    task_description = file.read()
                system_message = {"role": "system", "content": task_description}
                self.conversation_history = [system_message]
                self.save_conversation(self.conversation_history)  # Save the initial conversation
                print("[GameStateManager] Initialized OpenAI context with task description.")
            else:
                print(f"[GameStateManager] Error: Task description file not found at {task_description_file_path}")
        else:
            print("[GameStateManager] OpenAI context already initialized.")

    def create_prompt_string(self):
        print("[GameStateManager] Creating prompt string with the narrative")
        
        # Extract the latest narrative entries using the HistoryManager
        latest_narrative_entries = self.history_manager.extract_latest_narrative_entries()
        
        # Check if the method returned None (due to an error) before proceeding
        if latest_narrative_entries is None:
            print("[GameStateManager] Could not retrieve the latest narrative entries.")
            return None  # Or handle this error in another way
        
        # Combine the formatted strings into the final prompt string.
        prompt_string = (
            "====Conversation====\n" +
            latest_narrative_entries + "\n\n" +  # Updated this line
            "====Game State====\n" +
            self.game_state
        )
        return prompt_string
    
    async def process_command(self):
        print("[GameStateManager] Processing command asynchronously with streaming")
        prompt_string = self.create_prompt_string()

        if not prompt_string:
            print("[GameStateManager] Invalid prompt string.")
            return None

        try:
            print("[GameStateManager] OpenAI is being called to process asynchronously with streaming")

            # Append the prompt string to the conversation history
            self.conversation_history.append({"role": "user", "content": prompt_string})

            client = AsyncOpenAI(api_key=self.api_key)
            response_stream = await client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=self.conversation_history,
                temperature=0.2,
                max_tokens=500,
                stream=True
            )

            full_response = ""
            print("[GameStateManager] Awaiting streaming responses...")
            async for response in response_stream:
                if hasattr(response, 'choices') and response.choices and response.choices[0].delta:
                    chunk = response.choices[0].delta.content if response.choices[0].delta.content else ''
                    full_response += chunk

                if hasattr(response.choices[0], 'finish_reason') and response.choices[0].finish_reason == 'stop':
                    break

            self.save_response(full_response)
            self.conversation_history.append({"role": "assistant", "content": full_response})
            self.save_conversation(self.conversation_history)

            print("[GameStateManager] OpenAI has asynchronously processed command with streaming")
            return full_response

        except Exception as e:
            print(f"[GameStateManager] Error processing command asynchronously with streaming: {e}")
            return None


    def save_response(self, response):
        if response is None:
            print("[GameStateManager] No response to save.")
            return  # Exit the method if there's no response

        # Get a timestamp for creating a unique file name
        timestamp = SharedTimestamp.get_timestamp()
        response_file = f'../data/game_state_{timestamp}.txt'
    
        # Save the response string to a file
        with open(response_file, 'w') as file:
            file.write(response)

    def load_past_conversation(self):
        os.makedirs(self.data_dir, exist_ok=True)
        conversation_files = [f for f in os.listdir(self.data_dir) if f.startswith('gsm_conversation_history_') and f.endswith('.json')]
        if not conversation_files:
            print("[GameStateManager] No conversation history files found.")
            return []
        sorted_files = sorted(conversation_files, key=lambda x: datetime.strptime('_'.join(x.split('_')[3:]).split('.')[0], '%Y%m%d_%H%M%S'), reverse=True)
        latest_file = sorted_files[0]
        latest_file_path = os.path.join(self.data_dir, latest_file)
        with open(latest_file_path, 'r') as file:
            conversation_history = json.load(file)
        return conversation_history

    def save_conversation(self, conversation):
        MAX_TOKENS = 5000  # Maximum number of tokens to keep
        SYSTEM_MESSAGE_INDEX = 0  # Assuming system message is always the first in the list

        # Initialize the tokenizer with the specified encoder
        tokenizer = tiktoken.get_encoding("cl100k_base")

        # Function to count tokens
        def count_tokens(text, encoder):
            return len(encoder.encode(text))

        # Separate the system message
        system_message = conversation[SYSTEM_MESSAGE_INDEX]

        # Calculate total tokens and trim conversation if necessary
        total_tokens = sum(count_tokens(msg['content'], tokenizer) for msg in conversation)
        trimmed_conversation = conversation[1:]  # Excluding the system message

        # Remove old messages until the token limit is met
        while total_tokens > MAX_TOKENS and len(trimmed_conversation) > 1:
            removed_message = trimmed_conversation.pop(0)  # Remove the oldest message
            total_tokens -= count_tokens(removed_message['content'], tokenizer)

        # Reconstruct the conversation with the system message
        self.conversation_history = [system_message] + trimmed_conversation

        # Save the updated conversation history to a file
        timestamp = SharedTimestamp.get_timestamp()
        filename = os.path.join(self.data_dir, f'gsm_conversation_history_{timestamp}.json')
        with open(filename, 'w') as file:
            json.dump(self.conversation_history, file, indent=4)

        print("[GameStateManager] Conversation saved. Current token count:", total_tokens)

    def reload_data(self):
        # Reload game state
        self.game_state = self.load_game_state()

        # Reload conversation history
        self.conversation_history = self.load_past_conversation()

        # Reinitialize OpenAI context if needed
        if not self.conversation_history:
            self.initialize_openai_context()
        else:
            print("[GameStateManager] OpenAI context already initialized with the latest data.")
        
        # Reload narrative history if it's relevant
        if self.history_manager:
            self.history_manager.reload_data()

        print("[GameStateManager] Data has been reloaded.")