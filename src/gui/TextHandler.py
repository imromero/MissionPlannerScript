import logging

class TextHandler(logging.Handler):
    """
    A logging handler that writes log messages to a Tkinter Text widget.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # Append the message to the Text widget in the Tkinter main thread
        self.text_widget.after(0, self.append, msg)

    def append(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', msg + "\n")
        self.text_widget.configure(state='disabled')
        self.text_widget.yview('end')
