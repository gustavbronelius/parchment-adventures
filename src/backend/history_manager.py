# File: history_manager.py

import os
import json
import tiktoken
from openai import AsyncOpenAI
from datetime import datetime
from backend.shared_timestamp import SharedTimestamp

class HistoryManager:
    
    def __init__(self):
        self.narrative_history_dir = '../data'
        self.data_dir = '../data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.narrative_history = self.load_narrative_history()  # Load existing narrative history
        self.conversation_history = self.load_past_conversation()  # Load past conversation history
        self.api_key = self.get_api_key()  # Get API key
        self.client = AsyncOpenAI(api_key=self.api_key)  # Initialize AsyncOpenAI client
        self.initialize_openai_context()

    def load_narrative_history(self):
        """Loads the existing narrative history from the latest file."""
        files = [f for f in os.listdir(self.narrative_history_dir) if f.startswith('narrative_history_') and f.endswith('.txt')]
        
        if not files:
            print("[HistoryManager] No Narrative found")
            return ""

        latest_file = max(files, key=lambda x: datetime.strptime(x[18:-4], '%Y%m%d_%H%M%S'))
        latest_file_path = os.path.join(self.narrative_history_dir, latest_file)

        with open(latest_file_path, 'r') as file:
            narrative_history = file.read()

        return narrative_history

    def append_latest_narrative(self, user_command, assistant_response):
        """Appends the latest user command and assistant response to the narrative history."""
        user_command = user_command.strip()
        assistant_response = assistant_response.strip()
        
        # Append the new entry to the narrative history string
        self.narrative_history += f"User: {user_command}\n\nAssistant: {assistant_response}\n\n"

    def save_narrative_history(self):
        """Saves the narrative history to a new file with a timestamp."""
        timestamp = SharedTimestamp.get_timestamp()
        filename = f'narrative_history_{timestamp}.txt'
        file_path = os.path.join(self.narrative_history_dir, filename)

        with open(file_path, 'w') as file:
            file.write(self.narrative_history)  # Write the entire narrative history string to the file

        print("[HistoryManager] Narrative history saved.")

    def extract_latest_narrative_entries(self):
        narrative_history_files = [f for f in os.listdir(self.narrative_history_dir) if f.startswith('narrative_history_')]

        if not narrative_history_files:
            print("[HistoryManager] No narrative history files found.")
            return None

        latest_narrative_history_file = max(narrative_history_files, key=lambda f: os.path.getmtime(os.path.join(self.narrative_history_dir, f)))
        narrative_history_file_path = os.path.join(self.narrative_history_dir, latest_narrative_history_file)

        with open(narrative_history_file_path, 'r') as file:
            content = file.read()

        last_user_index = content.rfind('User:')
        if last_user_index == -1:
            print(f"[HistoryManager] Could not find 'User:' in {latest_narrative_history_file}.")
            return None
        
        latest_narrative_entries = content[last_user_index:]
        print(f"[HistoryManager] Latest narrative successfully extracted.")
        return latest_narrative_entries
    
    def extract_recent_narrative_entries(self):
        """Extracts up to three recent narrative entries, including the last one if it's the only entry."""
        narrative_history_files = [f for f in os.listdir(self.narrative_history_dir) if f.startswith('narrative_history_')]

        if not narrative_history_files:
            print("[HistoryManager] No narrative history files found.")
            return None

        latest_file = max(narrative_history_files, key=lambda f: os.path.getmtime(os.path.join(self.narrative_history_dir, f)))
        latest_file_path = os.path.join(self.narrative_history_dir, latest_file)

        with open(latest_file_path, 'r') as file:
            content = file.read()

        user_occurrences = [i for i in range(len(content)) if content.startswith('User:', i)]

        if len(user_occurrences) == 0:
            print("[HistoryManager] No narrative entries found.")
            return None

        # Number of entries to extract
        num_entries = min(3, len(user_occurrences))

        # Extract the entries
        recent_entries = ""
        for index in user_occurrences[-num_entries:]:
            end_index = content.find('\n\n', index)  # Find the end of each entry
            recent_entries += content[index:end_index] + "\n\n"

        return recent_entries
    
    def reload_data(self):
        # Reload narrative history
        self.narrative_history = self.load_narrative_history()

        # Reload any other relevant data
        # ...

        print("[HistoryManager] Data has been reloaded.")

    def load_latest_summary(self):
        summary_dir = '../data'
        summary_files = [f for f in os.listdir(summary_dir) if f.startswith('narrative_summary_')]
        if not summary_files:  # if the list is empty, fall back to the default game_state.txt
            summary_file_path = os.path.join('..', 'config', 'summary.txt')  # Updated path to ../config
        else:
            latest_summary_file = max(summary_files, key=lambda f: os.path.getmtime(os.path.join(summary_dir, f)))
            summary_file_path = os.path.join(summary_dir, latest_summary_file)

        with open(summary_file_path, 'r') as file:
            summary = file.read()  # Read the contents of the file as a string
        
        return summary

    def initialize_openai_context(self):
        self.conversation_history = self.load_past_conversation()
        if not self.conversation_history:
            task_description_file_path = '../config/history_manager_task_description.txt'
            if os.path.exists(task_description_file_path):
                with open(task_description_file_path, 'r') as file:
                    task_description = file.read()
                system_message = {"role": "system", "content": task_description}
                self.conversation_history = [system_message]
                self.save_conversation(self.conversation_history)  # Save the initial conversation
                print("[HistoryManager] Initialized OpenAI context with task description.")
            else:
                print(f"[HistoryManager] Error: Task description file not found at {task_description_file_path}")
        else:
            print("[HistoryManager] OpenAI context already initialized.")

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
    
    async def create_summary(self):
        print("[HistoryManager] Creating summary...")

        narrative_summary = self.load_latest_summary()
        self.conversation_history.append({"role": "system", "content": narrative_summary})

        latest_narrative_entries = self.extract_latest_narrative_entries()  # Call the method
        self.conversation_history.append({"role": "user", "content": latest_narrative_entries})
        print("[HistoryManager] Latest narrative appended.")

        try:
            response_stream = await self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=self.conversation_history,
                temperature=0.2,
                max_tokens=1000,
                stream=True
            )

            full_response = ""
            async for response in response_stream:
                if hasattr(response, 'choices') and response.choices and response.choices[0].delta:
                    chunk = response.choices[0].delta.content if response.choices[0].delta.content else ''
                    full_response += chunk

                if hasattr(response.choices[0], 'finish_reason') and response.choices[0].finish_reason == 'stop':
                    break

            # Save the full response as a summary
            self.save_summary(full_response)
            self.conversation_history.append({"role": "assistant", "content": full_response})
            # Save the API conversation
            self.save_conversation(self.conversation_history)

            print("[HistoryManager] OpenAI has asynchronously processed command with streaming")
            return full_response

        except Exception as e:
            print(f"[HistoryManager] Error in API call: {e}")

    def save_summary(self, summary):
        """Saves the summary to a file with a timestamp."""
        timestamp = SharedTimestamp.get_timestamp()
        filename = f'narrative_summary_{timestamp}.txt'
        summary_file_path = os.path.join(self.narrative_history_dir, filename)

        try:
            with open(summary_file_path, 'w') as file:
                file.write(summary)
            print(f"[HistoryManager] Summary saved in {filename}.")
        except Exception as e:
            print(f"[HistoryManager] Error saving summary: {e}")
        
    def load_past_conversation(self):
        os.makedirs(self.data_dir, exist_ok=True)
        conversation_files = [f for f in os.listdir(self.data_dir) if f.startswith('hm_conversation_history_') and f.endswith('.json')]
        if not conversation_files:
            print("[HistoryManager] No conversation history files found.")
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
        filename = os.path.join(self.data_dir, f'hm_conversation_history_{timestamp}.json')
        with open(filename, 'w') as file:
            json.dump(self.conversation_history, file, indent=4)

        print("[HistoryManager] Conversation saved. Current token count:", total_tokens)
