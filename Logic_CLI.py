import ast
import os


class FileSystem:
    def __init__(self):
        # The internal data structure
        self.directory = {
            "C:\\": {
                "Document": {"Folder": {},
                             "File1": (
                             "txt", "1kB", "hello world. \nThis is a file with multiple lines. \ncoding is painful"),
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
        print("\\".join(self.path_stack))

    def cd(self, *args):
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
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.txt")
        with open(file_path, "w") as f:
            f.write(str(self.directory))
        print("System saved.")

    def load(self):
        global directory
        directory = directory
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.txt")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                directory = ast.literal_eval(f.read())
            print("System loaded.")
        else:
            print("No save file found.")


class TerminalInterface:
    def __init__(self):
        self.fs = FileSystem()
        self.running = True

    def run(self):
        print("> Please use the 'load' command to start.")
        while self.running:
            prompt = f"{self.fs.path_stack[-1]}> "
            user_input = input(prompt).split(" ")
            cmd = user_input[0].lower()

            if cmd == "exit":
                self.running = False
            elif cmd == "ls":
                self.fs.ls(*user_input)
            elif cmd == "cd":
                self.fs.cd(*user_input)
            elif cmd == "pwd":
                self.fs.pwd()
            elif cmd == "cat":
                self.fs.cat(*user_input)
            elif cmd == "save":
                self.fs.save()
            elif cmd == "load":
                self.fs.load()
            elif cmd == "help":
                # Note: help is tricky inside classes, usually defined as a method
                print("Help: ls, cd, pwd, cat, save, load, exit")


if __name__ == "__main__":
    app = TerminalInterface()
    app.run()
