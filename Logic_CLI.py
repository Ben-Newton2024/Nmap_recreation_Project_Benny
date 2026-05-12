import ast
import os


class FileSystem:
    """
    The 'Model' of the system.
    It holds the actual dictionary and handles data manipulation.
    It does NOT know about the GUI or the TerminalInterface.
    """

    def __init__(self):
        # The internal data structure
        self.directory = {
            "C:\\": {
                "Document": {"Folder": {},
                             "File1": (
                                 "txt", "1kB",
                                 "hello world. \nThis is a file with multiple lines. \ncoding is painful"),
                             "File2": ("txt", "1kB", "goodbye world")},
                "Desktop": {"-Hidden_File": ("txt", "1kB", "Secret Code: XNA39TA")},
                "-system": {"-x64": {"-hidden_folder": {}}, "-x32": {}}
            }
        }
        self.path_stack = ["C:\\"]

    def _get_current_level(self):
        """Helper to find where we are in the dict based on path_stack"""
        current = self.directory
        for folder in self.path_stack:
            current = current[folder]
        return current

    def pwd(self):
        """ pwd function
            This command is to print the working directory you are in

            format
            pwd     :   Outputs your current working directory length from root folder (C:\\)
        """
        print("\\".join(self.path_stack))

    def cd(self, *args):
        """ cd function,
            This command is used to change directory.

            Format:
            >cd <>      :   <> changes to <> directory
                ..      :   goes back up one level of directory
        """
        if len(args) < 2:
            print("Error: No directory specified.")
            return

        target = args[1]
        current = self._get_current_level()

        if target == "..":
            if len(self.path_stack) > 1:
                self.path_stack.pop()
            else:
                print("Already in root directory")
        elif target in current:
            if isinstance(current[target], dict):
                self.path_stack.append(target)
            else:
                print(f"Error: '{target}' is a file.")
        else:
            print(f"Access Denied: '{target}' not found.")

    def ls(self, *args):
        """ List function,
            This command will output a list of the current directory.

            Format:
            >ls         :   Default value lists current directory.
                -la     :   List with all details.
                -lh     :   List with human-readable sizes.
                -R      :   recursive list though entire structure from current directory.
        """
        current = self._get_current_level()

        if "-la" in args:
            for key, value in current.items():
                if isinstance(value, tuple):
                    print(f"{key}\t Ext: {value[0]}\tSize: {value[1]}")
                else:
                    print(f"{key}/")
        elif "-R" in args:
            self._list_recursive(current)
        else:
            print(*list(current.keys()), sep="\n")

    def _list_recursive(self, current_dict, indent=0):
        """ Recursive search for ls -R """
        for key, value in current_dict.items():
            print("|\t" * indent + str(key))
            if isinstance(value, dict):
                if not value:
                    print("|\t" * (indent + 1) + "(empty folder)")
                else:
                    self._list_recursive(value, indent + 1)
            elif isinstance(value, tuple):
                print("|\t" * (indent + 1) + f"{key}.{value[0]}")

    def cat(self, *args):
        """ cat function,
            This command is used to display the contents of a file.

            Format:
            >cat <>     :   displays the first 10 lines of the target <> file
        """
        if len(args) < 2:
            print("cat: Missing filename")
            return

        target = args[1]
        current = self._get_current_level()

        if target in current:
            item = current[target]
            if isinstance(item, tuple):
                print(f">File: {target}\n")
                lines = item[2].splitlines()
                for line in lines[:10]:
                    print(line)
            else:
                print(f"cat: {target}: Is a directory")
        else:
            print("File not found")

    def save(self):
        """ save function,
            This command is used to save the entire directory.

            Format:
            >save       :   Saves the current directory and any changes you have made to a txt file
        """
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.txt")
        with open(file_path, "w") as f:
            f.write(str(self.directory))
        print("System saved.")

    def load(self):
        """ load function,
            This command is used to load your directory.

            Format:
            >load       :   Loads the latest save of your directory to continue working
        """
        global directory
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.txt")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                directory = ast.literal_eval(f.read())
            print("System loaded.")
        else:
            print("No save file found.")

    def help(self, *args):
        """ Help function,
            This command will output the documentation section of the commands

            Format
            >help <>
                  <> is any command you wish to query.

        """
        # If user just types 'help'
        if len(args) == 1:
            print("Usage: help <command>")
            # Print help's own docstring
            print(self.help.__doc__.strip())
            return

        if len(args) > 2:
            print("Please only use help on one command at a time.")
            return

        command_name = args[1].lower()

        # Look for the method inside 'self' (the current class instance)
        if hasattr(self, command_name):
            method = getattr(self, command_name)
            doc = method.__doc__
            if doc:
                print(f"\n--- {command_name.upper()} Help ---")
                print(doc.strip())
            else:
                print(f"No documentation found for '{command_name}'.")
        else:
            print(f"Unknown command: '{command_name}'")

    def nano(self, *args):
        """Prepares file data for the GUI to edit."""
        if len(args) < 2:
            print("nano: Missing filename")
            return None  # No data to edit

        filename = args[1]
        current = self._get_current_level()

        if filename in current:
            if isinstance(current[filename], tuple):
                # Return the filename and the content (index 2 of your tuple)
                return filename, current[filename][2]
            else:
                print(f"nano: {filename}: Is a directory")
        else:
            # Create a blank file if it doesn't exist (like real nano)
            return filename, ""
        return None

    def update_file(self, filename, new_content):
        """ Replaces or creates a file with new content from Nano editor. """
        current = self._get_current_level()
        # Defaulting to .txt and auto-calculating size
        new_size = f"{len(new_content) // 1024 + 1}kB"
        current[filename] = ("txt", new_size, new_content)


class TerminalInterface:
    """ This is to act as the interface between the logic Class and the main.py GUI Classes"""

    def __init__(self):
        """ Initialize the command list for input from the user to use for the CLI Logic"""
        self.fs = FileSystem()
        self.running = True

        # Command map: Maps string names to the actual method objects
        self.commands = {
            "ls": self.fs.ls,
            "cd": self.fs.cd,
            "pwd": self.fs.pwd,
            "cat": self.fs.cat,
            "save": self.fs.save,
            "load": self.fs.load,
            "help": self.fs.help,
            "nano": self.fs.nano
        }

    def run(self):
        """ Used for standard console mode """
        print("> Please use the 'load' command to start.")
        while self.running:
            prompt = f"{self.fs.path_stack[-1]}> "
            user_input = input(prompt).split(" ")
            cmd = user_input[0].lower()

            if cmd == "exit":
                self.running = False
            elif cmd in self.commands:
                # uses commands dictionary mapping to reduce if statement hell
                self.commands[cmd](*user_input)
            else:
                print(f"Command '{cmd}' not found.")


    def execute_for_gui(self, user_input):
        """ Used for the Tkinter GUI to call commands
            it executes all commands the user inputs, through to the cli logic
        """
        parts = user_input.split(" ")
        cmd = parts[0].lower()

        if cmd == "exit":
            return "EXIT_SIGNAL", None

        if cmd == "nano":
            data = self.fs.nano(*parts)
            if data:
                return "NANO_SIGNAL", data  # data is (filename, content)
            return "ERROR", None

        if cmd in self.commands:
            self.commands[cmd](*parts)
            return "SUCCESS", None

        print(f"Command '{cmd}' not found.")
        return "ERROR", None

if __name__ == "__main__":
    app = TerminalInterface()
    app.run()
