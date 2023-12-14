# File: word_widget.py

import tkinter as tk

class WordWidget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = tk.Text(self, bd=0, highlightthickness=0, relief='ridge', wrap=tk.WORD, bg='#e1dbcb', padx=10, pady=10)
        self.text_widget.insert(tk.END, "Replace this text with words that you want the game to incorporate in the story.\n\n")  # Initial placeholder text
        self.text_widget.pack(expand=True, fill='both')  # Pack the text widget to fill the frame
        self.pack_propagate(False)  # Prevent the frame from resizing based on the text widget
    
    def update_word_list(self, word_list):
        self.text_widget.delete('1.0', tk.END)  # Clear existing content
        if word_list is None or not word_list:
            self.text_widget.insert(tk.END, "No word entries available.\n")
        elif isinstance(word_list, str):
            self.text_widget.insert(tk.END, word_list)
        else:
            print(f"Unexpected type for word_list: {type(word_list)}")  # Debug output

    def get_text(self):
        return self.text_widget.get("1.0", tk.END)  # Retrieves all text from the widget   

    def show_processing_message(self):
        self.text_widget.insert(tk.END, "\n\nProcessing...\n")

    def update_font(self, font_name, font_size):
        self.text_widget.configure(font=(font_name, font_size))

    def update_bg_color(self, color):
        self.text_widget.configure(bg=color)
        self.configure(bg=color)

    def update_text_color(self, color):
        self.text_widget.configure(fg=color)