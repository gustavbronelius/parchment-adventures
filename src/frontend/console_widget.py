# File: console_widget.py

import tkinter as tk

class ConsoleWidget(tk.Text):
    def __init__(self, parent, game_gui, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.game_gui = game_gui
        self.configure(bd=0, highlightthickness=0, relief='ridge', wrap=tk.WORD, bg='#e1dbcb', padx=10, pady=10)
        self.bind("<BackSpace>", self.handle_backspace)
        self.user_input_start = "1.0"  # Initialize the user input start position
        self.bind("<KeyPress>", self.handle_key_press)

    def handle_backspace(self, event):
        current_pos = self.index(tk.INSERT)
        #print("[ConsoleWidget] Backspace pressed. Current position:", current_pos, "User input start:", self.user_input_start)

        if self.compare(current_pos, "<=", self.user_input_start):
            #print("[ConsoleWidget] Preventing backspace.")
            return "break"  # Prevent backspace
        return None  # Allow backspace

    def handle_key_press(self, event):
        if self.game_gui.is_streaming_narrative:
            return "break"  # Ignore the keypress

    def append_text(self, text):
        #print("[ConsoleWidget] Appending text. Current user input start:", self.user_input_start)
        self.insert(tk.END, text)
        self.see(tk.END)
        # Adjusting user_input_start to the position before the last newline
        self.user_input_start = self.index(tk.END + "-1c")  # "-1c" moves one character back from tk.END
        #print("[ConsoleWidget] Text appended. New user input start:", self.user_input_start)

    def clear_text(self):
        #print("[ConsoleWidget] Clearing text.")
        self.delete("1.0", tk.END)
        self.user_input_start = "1.0"
        #print("[ConsoleWidget] Text cleared. Resetting user input start to:", self.user_input_start)

    def get_command(self):
        full_text = self.get("1.0", tk.END).strip()
        #print("[ConsoleWidget] Getting command. Full text:", full_text)
        lines = full_text.split("\n")
        command = lines[-1] if lines else ""
        #print("[ConsoleWidget] Extracted command:", command)
        return command
    
    def disable_input(self):
        # Disable editing in the text widget itself
        self.config(state='disabled')

    def enable_input(self):
        # Re-enable editing in the text widget itself
        self.config(state='normal')

    # ... any other methods you need for the console widget ...