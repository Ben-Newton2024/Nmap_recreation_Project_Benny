import os
import json
import socket
import time


class FileSystem:
    """
    The 'Model' of the system.
    It holds the actual dictionary and handles data manipulation.
    It does NOT know about the GUI or the TerminalInterface.
    """

    def __init__(self):
        # The internal data structure
        # hard coded if factory state is needed?
        self.directory = {
            "root:\\": {
                "Document": {},
                "Desktop": {}
            }
        }
        self.path_stack = ["root:\\"]
        self.load()

    def _get_current_level(self):
        """Helper to find where we are in the dict based on path_stack"""
        current = self.directory
        for folder in self.path_stack:
            current = current[folder]
        return current

    def pwd(self, *args):
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
                if isinstance(value, list):
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
            elif isinstance(value, list):
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
            if isinstance(item, list):
                print(f">File: {target}\n")
                lines = item[2].splitlines()
                for line in lines[:10]:
                    print(line)
            else:
                print(f"cat: {target}: Is a directory")
        else:
            print("File not found")

    def save(self, *args):
        """ save function,
            This command is used to save the entire directory.

            Format:
            >save       :   Saves the current directory and any changes you have made to a txt file
        """
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.json")
        with open(file_path, "w") as f:
            # indent=4 creates the 'Pretty Print' look automatically
            # sort_keys=True is optional, but keeps your folders alphabetical
            json.dump(self.directory, f, indent=4, sort_keys=True)
        print("System saved to JSON.")

    def load(self, *args):
        """ load function,
            This command is used to load your directory.

            Format:
            >load       :   Loads the latest save of your directory to continue working
        """
        file_path = os.path.join(os.path.dirname(__file__), "plinux_save.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.directory = json.load(f)
            print("System loaded.")
        else:
            # Fallback if no save exists
            print("No save found, using default structure.")

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
            if isinstance(current[filename], list):
                # Return the filename and the content (index 2 of your list)
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

        # 1. Calculate size: len() gives bytes.
        # We'll show bytes if small, or kB if larger.
        bytes_size = len(new_content)
        if bytes_size < 1024:
            size_str = f"{bytes_size}B"
        else:
            size_str = f"{bytes_size // 1024}kB"

        # 2. Get the extension (default to txt if it's a new file)
        extension = "txt"
        if "." in filename:
            extension = filename.split(".")[-1]

        # 3. Save the list: (extension, size, content)
        current[filename] = (extension, size_str, new_content)

    def mkdir(self, *args):
        """ mkdir function
            This command creates a new directory.

            Format:
            >mkdir <name>   : Creates a new empty folder
        """
        if len(args) < 2:
            print("mkdir: missing operand")
            return

        new_dir = args[1]
        current = self._get_current_level()

        if new_dir in current:
            print(f"mkdir: cannot create directory '{new_dir}': File exists")
        else:
            # Create the new folder as an empty dictionary
            current[new_dir] = {}
            print(f"Created directory: {new_dir}")

    def touch(self, *args):
        """ touch function
            This command creates a new empty file.

            Format:
            >touch <name>   : Creates a new empty file with default metadata
        """
        if len(args) < 2:
            print("touch: missing operand")
            return

        filename = args[1]
        current = self._get_current_level()

        if filename in current:
            # In real Linux, touch updates the 'timestamp' if the file exists.
            # For now, we can just say it exists.
            print(f"touch: {filename} already exists.")
            # Create the new file as an empty list
        else:
            # Determine extension if provided, else default to 'txt'
            ext = filename.split(".")[-1] if "." in filename else "txt"

            # Create the file with default [extension, size, content]
            current[filename] = [ext, "0B", ""]
            print(f"Touched file: {filename}")

    def rm(self, *args):
        """ rm function
            This command removes a file or folder.

            Format:
            >rm <name>      : Removes the target file or folder
        """
        if len(args) < 2:
            print("rm: missing operand")
            return

        target = args[1]
        current = self._get_current_level()

        if target in current:
            del current[target]
            print(f"Removed: {target}")
        else:
            print(f"rm: cannot remove '{target}': No such file or directory")


class NetworkEngine:
    """
    Backend: Handles all network sockets, port scanning,
    and connection logic. It does not touch the file system.
    """

    def __init__(self):
        # You can store scan history or target profiles here later
        self.scan_history = []

    def nmap(self, *args):
        """
        nmap function: Scans a target IP for open ports.
        Format: nmap <ip>
        """
        if len(args) < 2:
            print("nmap: missing target IP operand")
            return

        target_ip = args[1]
        common_ports = [21, 22, 80, 139, 443, 8080]

        print(f"\nStarting Mini-NMAP scan against {target_ip}...")
        print("PORT\t\tSTATE")
        print("-" * 30)

        for port in common_ports:
            # Create IPv4 TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Prevent the GUI from freezing too long

            # connect_ex returns 0 on success, or an error code
            result = s.connect_ex((target_ip, port))
            s.close()

            if result == 0:
                print(f"{port}/tcp\t\topen")
            # Closed ports are omitted for cleaner output, just like real NMAP
        print("Scan finished.\n")

    def ping(self, *args):
        """ ping function
                Checks if a target host is responsive by opening a quick TCP connection.

                Format:
                >ping <ip_or_domain>   : Pings the target host 4 times and prints latency.
            """
        if len(args) < 2:
            print("ping: missing target operand")
            return

        target = args[1]
        port = 80  # Use standard HTTP port for a quick responsiveness check
        print(f"\nPING {target} on TCP port {port}:")

        success_count = 0
        total_time = 0

        # Run 4 ping cycles (standard terminal behaviour)
        for i in range(4):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)  # Time out quickly if host is offline

            # Start the high-precision timer
            start_time = time.perf_counter()

            try:
                # Attempt connection
                result = s.connect_ex((target, port))
                # Stop the timer immediately after connection attempt returns
                end_time = time.perf_counter()

                # Calculate latency in milliseconds
                latency = (end_time - start_time) * 1000

                if result == 0 or result == 10061:
                    # Note: Error 10061 means "Connection Refused" which actually
                    # proves the host is alive and actively blocking the port!
                    print(f"Reply from {target}: time={latency:.2f}ms")
                    success_count += 1
                    total_time += latency
                else:
                    print(f"Request timed out. (Error code: {result})")

            except socket.gaierror:
                print(f"ping: unknown host {target}")
                s.close()
                return
            finally:
                s.close()

            # Brief pause between packet cycles (100ms) to prevent flood flags
            time.sleep(0.1)

        # Print statistics summary
        if success_count > 0:
            avg_time = total_time / success_count
            print(f"\n--- {target} ping statistics ---")
            print(f"Packets: Sent = 4, Received = {success_count}, Lost = {4 - success_count}")
            print(f"Approximate round trip times: Average = {avg_time:.2f}ms\n")
        else:
            print(f"\n--- {target} ping statistics ---")
            print("Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)\n")


class TerminalInterface:
    """ This is to act as the interface between the logic Class and the main.py GUI Classes"""

    def __init__(self):
        """ Initialize the command list for input from the user to use for the CLI Logic"""
        self.fs = FileSystem()
        self.ne = NetworkEngine()
        self.running = True

        # Command map: Maps string names to the actual method objects
        self.commands = {
            # File System .fs.
            "ls": self.fs.ls,
            "cd": self.fs.cd,
            "pwd": self.fs.pwd,
            "cat": self.fs.cat,
            "save": self.fs.save,
            "load": self.fs.load,
            "help": self.fs.help,
            "nano": self.fs.nano,
            "touch": self.fs.touch,
            "mkdir": self.fs.mkdir,
            "rm": self.fs.rm,
            # Networking Engine .ne.
            "nmap": self.ne.nmap,
            "ping": self.ne.ping
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
