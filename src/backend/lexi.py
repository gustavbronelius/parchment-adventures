# file: lexi.py

import os
import json

from backend.shared_timestamp import SharedTimestamp


class Lexi:
    def __init__(self):
        self.data_dir = '../data'
        self.word_list_dir = self.data_dir

    def load_content(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return ""

    def get_content(self, word_widget):
        return word_widget.get_text()

    def set_content(self, word_widget, content):
        word_widget.set_text(content)

    def load_word_list(self):
        word_list_dir = self.data_dir
        word_list_files = [f for f in os.listdir(word_list_dir) if f.startswith('word_list_')]
        if not word_list_files:  # if the list is empty, fall back to the default word list
            word_list_file_path = os.path.join('../config', 'word_list.txt')
        else:
            latest_word_list_file = max(word_list_files, key=lambda f: os.path.getmtime(os.path.join(word_list_dir, f)))
            word_list_file_path = os.path.join(word_list_dir, latest_word_list_file)

        with open(word_list_file_path, 'r') as file:
            word_list = file.read()
        
        return word_list
    
    def save_word_list(self, word_list):
        timestamp = SharedTimestamp.get_timestamp()
        filename = f'word_list_{timestamp}.txt'
        word_list_file_path = os.path.join(self.word_list_dir, filename)

        try:
            with open(word_list_file_path, 'w') as file:
                file.write(word_list)
            print(f"[Lexi] Word list saved in {filename}.")
        except Exception as e:
            print(f"[Lexi] Error saving word list: {e}")