import tkinter as tk
import sys
from Logic_CLI import TerminalInterface


# This class "pretends" to be the terminal output
class Redirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.config(state='normal')
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)
        self.widget.config(state='disabled')

    def flush(self):
        pass


class PLinuxGUI:
    def __init__(self, root):
        self.root = root
        self.interface = TerminalInterface()

        self.console = tk.Text(root, bg="black", fg="#00FF00", font=("Courier", 10), state='disabled')
        self.console.pack(expand=True, fill='both')

        # Redirect all 'print' statements to the console widget
        sys.stdout = Redirector(self.console)

        self.entry = tk.Entry(root, bg="black", fg="white", insertbackground="white", font=("Courier", 10))
        self.entry.pack(fill='x')
        self.entry.bind("<Return>", self.handle_input)
        self.entry.focus_set()

        print("Welcome to PLinux GUI. Use 'load' to begin.\n")

    def handle_input(self, event):
        event = None
        user_text = self.entry.get()
        if not user_text.strip():
            return

        # 1. Print the prompt and command so the user sees what they typed
        current_path = self.interface.fs.path_stack[-1]
        print(f"{current_path}> {user_text}")

        # 2. Execute the logic from your TerminalInterface
        # We manually call the logic based on the first word
        parts = user_text.split(" ")
        cmd = parts[0].lower()

        if cmd == "exit":
            print("Shutting down system...")
            # Optionally call save before closing
            self.interface.fs.save()
            # Properly closes the Tkinter window and ends the loop
            self.root.destroy()
            return
        elif cmd == "ls":
            self.interface.fs.ls(*parts)
        elif cmd == "cd":
            self.interface.fs.cd(*parts)
        elif cmd == "pwd":
            self.interface.fs.pwd()
        elif cmd == "cat":
            self.interface.fs.cat(*parts)
        elif cmd == "save":
            self.interface.fs.save()
        elif cmd == "load":
            self.fs_load_fix()  # See note below
        elif cmd == "help":
            print("Commands: ls, cd, pwd, cat, save, load, exit")
        else:
            print(f"Command '{cmd}' not recognized.")

        self.entry.delete(0, tk.END)

    def fs_load_fix(self):
        # Your current load() uses a global 'directory' which will fail in a class.
        # This calls the load method and ensures it's handled.
        self.interface.fs.load()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mini-PLinux")
    app = PLinuxGUI(root)
    root.mainloop()
