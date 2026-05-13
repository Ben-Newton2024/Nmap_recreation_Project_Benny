import tkinter as tk
import sys
from Logic_CLI import TerminalInterface


# This class "pretends" to be the terminal output
class Redirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        """ Writes to the main wigit view above the user inputs"""
        self.widget.config(state='normal')
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)
        self.widget.config(state='disabled')

    def flush(self):
        pass


class PLinuxGUI:
    def __init__(self, init_root):
        """ Initializes the Root and all GUI objects for the user to use.
        """
        self.root = init_root
        self.interface = TerminalInterface()

        self.console = tk.Text(init_root, bg="black", fg="#00FF00", font=("Courier", 10), state='disabled')
        self.console.pack(expand=True, fill='both')

        sys.stdout = Redirector(self.console)

        # --- Create a container for the bottom part ---
        bottom_frame = tk.Frame(init_root, bg="black")
        bottom_frame.pack(fill='x')

        # --- Create the Prompt Label ---
        self.prompt_label = tk.Label(bottom_frame, text=f"{self.interface.fs.path_stack[-1]}>",
                                     bg="black", fg="white", font=("Courier", 10))
        self.prompt_label.pack(side='left')

        # --- Put the Entry inside the frame ---
        self.entry = tk.Entry(bottom_frame, bg="black", fg="white", insertbackground="white",
                              font=("Courier", 10), borderwidth=0)
        self.entry.pack(side='left', fill='x', expand=True)

        self.entry.bind("<Return>", self.handle_input)
        self.entry.focus_set()
        print("Welcome to PLinux GUI. Use 'load' to begin.\n")

    def handle_input(self, event):
        """ When a user input is detected it will handle it here
            Passing the data to the Logic_CLI for processing
        """
        user_text = self.entry.get()
        if not user_text.strip():
            return

        # 1. Get the current location
        current_path = self.interface.fs.path_stack[-1]

        # 2. PRINT IT to the large console box (via Redirector)
        # This creates the "history" you want to see
        print(f"{current_path}> {user_text}")

        # 3. Execute the command
        # Execute and unpack both the status and any data returned (like nano content)
        # Note: You'll need to update execute_for_gui in Logic_CLI to return two values
        status, data = self.interface.execute_for_gui(user_text)

        if status == "EXIT_SIGNAL":
            self.interface.fs.save()
            self.root.destroy()
        elif status == "NANO_SIGNAL":
            # data will be (filename, content)
            self.start_nano(data[0], data[1])
        else:
            self.entry.delete(0, tk.END)
            # 4. Optional: Update the small prompt label if you kept it
            if hasattr(self, 'prompt_label'):
                self.prompt_label.config(text=f"{self.interface.fs.path_stack[-1]}>")

    def fs_load_fix(self):
        # Your current load() uses a global 'directory' which will fail in a class.
        # This calls the load method and ensures it's handled.
        self.interface.fs.load()

    def start_nano(self, filename, content):
        """ Switches the console into 'Editor Mode' """
        self.nano_status = tk.Label(self.root, text="NANO MODE: Ctrl+S to Save", bg="blue", fg="white")
        self.nano_status.pack(side="bottom", fill="x")
        self.editing_file = filename

        # 1. Unlock the console and clear it
        self.console.config(state='normal')
        self.console.delete("1.0", tk.END)

        # 2. Insert the file content
        self.console.config(insertbackground="white")  # Makes the cursor white so it shows on black
        self.console.config(insertofftime=500, insertontime=500)  # Sets the flashing speed (ms)
        self.console.focus_force()  # Forces focus so the cursor starts blinking immediately
        self.console.insert(tk.END, content)

        # --- CRITICAL FIXES FOR EDITING ---
        # Force keyboard focus to the large box
        self.console.focus_force()
        # Move the text cursor to the very beginning
        self.console.mark_set("insert", "1.0")

        # 3. Disable command entry
        self.entry.config(state='disabled')

        # 4. Bind save shortcut
        self.root.bind("<Control-s>", self.exit_nano)

    def exit_nano(self, event=None):
        """ Saves content and returns to 'Console Mode' """
        # 1. Get the new text from the widget
        new_content = self.console.get("1.0", tk.END).strip()

        # 2. Update your Backend dictionary
        # (Assuming you have a method in your FS to update file content)
        self.interface.fs.update_file(self.editing_file, new_content)

        # 3. Reset the UI
        self.console.delete("1.0", tk.END)  # clears the editor screen
        self.console.config(state='disabled')  # lock the console back up
        # clear the entry box
        self.entry.config(state='normal')  # re-enables the input box
        self.entry.delete(0, tk.END)  # wipes the nano File1 from the input box
        if hasattr(self, 'nano_status'):  # Remove the Status Bar
            self.nano_status.destroy()

        self.root.unbind("<Control-s>")

        print(f"\nSaved {self.editing_file}. Returning to console...\n")


if __name__ == "__main__":
    """ Runner """
    root = tk.Tk()
    root.title("Mini-PLinux")
    app = PLinuxGUI(root)
    root.mainloop()
