# File: narrator.py

from openai import AsyncOpenAI
import os
import json
import tiktoken
from datetime import datetime
from backend.shared_timestamp import SharedTimestamp

class Narrator:
    def __init__(self, game_gui, history_manager, lexi):
        self.data_dir = '../data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.conversation_history = self.load_past_conversation()
        self.initialize_openai_context()
        self.game_gui = game_gui
        self.history_manager = history_manager
        self.lexi = lexi
        self.full_response = ""

    def load_game_state(self):
        game_state_dir = '../data'
        game_state_files = [f for f in os.listdir(game_state_dir) if f.startswith('game_state_')]
        if not game_state_files:  # if the list is empty, fall back to the default game_state.txt
            game_state_file_path = os.path.join('../config', 'game_state.txt')  # Updated path to ../config
        else:
            latest_game_state_file = max(game_state_files, key=lambda f: os.path.getmtime(os.path.join(game_state_dir, f)))
            game_state_file_path = os.path.join(game_state_dir, latest_game_state_file)

        with open(game_state_file_path, 'r') as file:
            game_state = file.read()  # Read the contents of the file as a string
        
        return game_state

    @staticmethod
    def get_api_key(file_path='../openai.api_key.txt'):
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

    def initialize_openai_context(self):
        if not self.conversation_history:
            task_description_file_path = '../config/narrator_task_description.txt'
            if os.path.exists(task_description_file_path):
                with open(task_description_file_path, 'r') as file:
                    task_description = file.read()
                system_message = {"role": "system", "content": task_description}
                self.conversation_history = [system_message]
                self.save_conversation(self.conversation_history)  # Save the initial conversation
                print("[Narrator] Initialized OpenAI context with task description.")
            else:
                print(f"[Narrator] Error: Task description file not found at {task_description_file_path}")
        else:
            print("[Narrator] OpenAI context already initialized.")


    def create_prompt_string(self):

        # Load the latest game state
        game_state = self.load_game_state()
        word_list = self.lexi.load_word_list()

        # Combine the formatted strings into the final prompt string
        prompt_string = (
            "====Game State====\n" +
            game_state +
            "====Word List====\n" +
            word_list +
            "====User command====\n"
        )
        return prompt_string    

    async def process_command_streaming(self, command):
        print("[Narrator] Processing command in streaming mode")

        narrative_summary = self.history_manager.load_latest_summary()

        # Check for an existing summary in the conversation history and remove it
        self.conversation_history = [message for message in self.conversation_history if message['role'] != 'system' or 'Summary:' not in message['content']]

        # Append the new narrative summary as a system message
        system_message_summary = {"role": "system", "content": narrative_summary}
        self.conversation_history.append(system_message_summary)

        # Create the prompt string with the latest game state
        prompt_string = self.create_prompt_string()

        # Combine the prompt string with the user command
        full_command = prompt_string + command
        self.conversation_history.append({"role": "user", "content": full_command})

        full_response = ""
        client = AsyncOpenAI(api_key=self.get_api_key())

        try:
            print("[Narrator] Starting streaming from OpenAI")
            response_stream = await client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000,
                stream=True)

            print("[Narrator] Awaiting responses...")
            async for response in response_stream:
                if hasattr(response, 'choices') and response.choices and response.choices[0].delta:
                    chunk = response.choices[0].delta.content if response.choices[0].delta.content else ''
                    await self.display_chunk_in_real_time(chunk)  # Display each chunk in real time
                    full_response += chunk  # Add this line to concatenate the chunk

                if hasattr(response.choices[0], 'finish_reason') and response.choices[0].finish_reason == 'stop':
                    #print("\n\n[Narrator] Full response:")
                    #print(full_response)
                    break

            print("[Narrator] Streaming process complete, updating conversation history")
            self.conversation_history.append({"role": "assistant", "content": full_response})
            self.save_conversation(self.conversation_history)

            # Append a double newline to the console widget
            self.game_gui.console_widget.append_text("\n\n")

            self.full_response = full_response
            print("[Narrator] Streaming complete, full response stored")

            return full_response

        except Exception as e:
            print(f"[Narrator] Error during streaming: {e}")
            return None

    async def display_chunk_in_real_time(self, chunk):
        # Call the append_text method of the console_widget to display the chunk
        self.game_gui.console_widget.append_text(chunk)

    def get_full_response(self):
        """Returns the full response accumulated during the streaming process."""
        return self.full_response

    def get_filename(self):
        timestamp = SharedTimestamp.get_timestamp()  # Use the shared timestamp
        filename = os.path.join(self.data_dir, f'narrator_conversation_history_{timestamp}.json')
        return filename
    
    def save_conversation(self, conversation):
        MAX_TOKENS = 12000  # Maximum number of tokens to keep
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
        filename = self.get_filename()
        with open(filename, 'w') as file:
            json.dump(self.conversation_history, file, indent=4)

        print("[Narrator] Conversation saved. Current token count:", total_tokens)

    def load_past_conversation(self):
        # Get a list of all history files
        conversation_files = [f for f in os.listdir(self.data_dir) if f.startswith('narrator_conversation_history_') and f.endswith('.json')]
        
        # If there are no history files, return an empty list
        if not conversation_files:
            print(f'[Narrator] No conversation history found')
            return []
        
        # Calculate the start index for the timestamp
        prefix_length = len('narrator_conversation_history_')
        
        # Sort the history files based on the timestamp in the filename
        sorted_files = sorted(
            conversation_files, 
            key=lambda x: datetime.strptime(x[prefix_length:-5], '%Y%m%d_%H%M%S'),  # Dynamically calculated indices
            reverse=True
        )
        
        # Get the filename of the latest history file
        latest_file = sorted_files[0]
        latest_file_path = os.path.join(self.data_dir, latest_file)
        
        # Load and set the content of the latest history file as the current conversation history
        with open(latest_file_path, 'r') as file:
            return json.load(file)
        
    def reload_data(self):
        # Reload conversation history
        self.conversation_history = self.load_past_conversation()

        # Reinitialize OpenAI context if needed
        if not self.conversation_history:
            self.initialize_openai_context()
        else:
            print("[Narrator] OpenAI context already initialized with the latest data.")

        # You may also want to reload game state if it's relevant
        self.load_game_state()
        
        print("[Narrator] Data has been reloaded.")
    
    # ... other methods as needed ...