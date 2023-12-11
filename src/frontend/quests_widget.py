# File: quests_gui.py

import tkinter as tk

class QuestsWidget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = tk.Text(self, bd=0, highlightthickness=0, relief='ridge', wrap=tk.WORD, bg='#e1dbcb', padx=10, pady=10)
        self.text_widget.insert(tk.END, "Quests:\n\n")  # Initial placeholder text
        self.text_widget.pack(expand=True, fill='both')  # Pack the text widget to fill the frame
        self.pack_propagate(False)  # Prevent the frame from resizing based on the text widget
    
    def update_quests(self, quests_section):
        self.text_widget.delete('1.0', tk.END)  # Use self.text_widget to access the Text widget
        #self.text_widget.insert(tk.END, "Quests:\n\n")  # Reset the initial placeholder text
        if quests_section is None or quests_section == '':
            self.text_widget.insert(tk.END, "No quests available.\n")  # Placeholder text when there are no quests
        elif isinstance(quests_section, str):
            self.text_widget.insert(tk.END, quests_section)  # directly insert the quests section string
        else:
            print(f"Unexpected type for quests_section: {type(quests_section)}")  # Debug output

    def show_processing_message(self):
        self.text_widget.insert(tk.END, "\n\nProcessing...\n")  # Append processing message to the text widget

    def update_font(self, font_name, font_size):
        # Update the font for the Text widget inside the QuestsGUI frame
        self.text_widget.configure(font=(font_name, font_size))
        # No need to adjust width and height here, as it's handled by the frame

    def update_bg_color(self, color):
        # Update the background color for the Text widget and the Frame
        self.text_widget.configure(bg=color)
        self.configure(bg=color)

    def update_text_color(self, color):
        # Update the text color for the Text widget
        self.text_widget.configure(fg=color)
