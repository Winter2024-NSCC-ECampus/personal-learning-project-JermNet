import tkinter as tk

class TextHistoryManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.text_history = []

    def add_to_history(self, text):
        self.text_history.append(text)

    def show_text_history(self):
        """Show the text history in a new window."""
        history_window = tk.Toplevel(self.parent_window)
        history_window.title("Text History")
        text_widget = tk.Text(history_window, wrap="word", font=("Arial", 14))
        text_widget.pack(expand=True, fill="both")
        text_widget.insert("1.0", "\n".join(self.text_history))
        text_widget.config(state="disabled")