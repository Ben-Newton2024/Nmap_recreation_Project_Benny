""" Practice to create a mini Linux like CLI with NMAP capabilities in the future
    this is to practice the use of *args and **kwargs specifically"""

""" File structure
    file: (extension type, content data, etc etc)"""

__name__ = "__main__"

directory = {
    "C:": {
        "Document.dir": {"File1": ("txt", "hello world"),
                         "File2": ("txt", "goodbye world")},
        "Desktop.dir": {"-Hidden_File.txt": None},
        "-system.dir": {"-x64.dir": {"-hidden_folder":{}},
                        "-x32.dir": {}
                        }
        }
    }

path_stack = ["C:"]


def cd(*args):
    global path_stack
    global directory

    # args[0] is "cd", args[1] is the folder
    if len(args) < 2:
        print("Error: No directory specified.")
        return

    target_folder = args[1]

    current_level = directory
    for folder in path_stack:
        current_level = current_level[folder]

    if target_folder in current_level:
        # if current instance is a folder ten i can append to stack and move into it
        if isinstance(current_level[target_folder], dict):
            path_stack.append(target_folder)
            print(f"Moved to: {'/'.join(path_stack)}")
        # if current instance is a tuple this is a file
        if isinstance(current_level[target_folder], tuple):
            print(f"Error: '{target_folder}' is a file. Use 'cat' to read it.")
        else:
            print(f"Error: '{target_folder}' is a file.")
    else:
        print(f"Access Denied: '{target_folder}' not found.")


def pwd():
    """ Print Working Directory Function """
    global path_stack
    working_directory = path_stack[len(path_stack)-1]
    print("\\" + working_directory)


def list_recursive(current_dict, indent=0):
    """ Recursive search through the directory dictionary/ or list """
    for key, value in current_dict.items():
        # Print the current item with indentation (4 spaces per level)
        print("|    " * indent + str(key))

        # If the value is another dictionary, recurse into it
        if isinstance(value, dict):
            list_recursive(value, indent + 1)

def ls(*args):
    """ List function,
        This command will output a list of the current directory

        Format
        >ls         :   Defaults to generic output of all directories within the current working
                        directory.
            -h      :   This outputs all hidden directories only within the current working
                        directory.
            -v      :   This outputs all non-hidden directories only - AKA all Visible directories
                        from the current working directory.
            -a      :   This outputs all directories from the current cascaded to the lowest.
                        from the current working directory.
    """
    global directory
    global path_stack
    current_level = directory

    # Print everything within current working directory
    if len(args) == 1:
        for folder in path_stack:
            print(*current_level[folder].keys(), sep="\n")
    # Print only hidden directories - "-"
    elif "-h" in args:
        for folder in path_stack:
            for item in current_level[folder].keys():
                if item[0] == "-":  # If it DOES NOT start with -
                    print(item)    # Print only Visible Directories - non "-"
                else:
                    continue
    elif "-v" in args:
        for folder in path_stack:
            for item in current_level[folder].keys():
                if item[0] != "-":  # If it DOES NOT start with -
                    print(item)    # Print only Visible Directories - non "-"
                else:
                    continue
    # Outputs all directories, this is recursive from your current to the lowest level
    if "-a" in args:
        print(f"Recursive mapping for {'/'.join(path_stack)}:")
        list_recursive(current_level)




def help(*args):
    """ Help function,
        This command will output the documentation section of the commands

        Format
        >help <>
              <> is any command you wish to query.

    """
    if len(args) == 1:
        print("please input a command you wish to use help on >help <>")
    elif len(args) > 2:
        print("please only use help on one command at a time")
    else:
        print(eval(f"{args[1]}.__doc__") or 'N/A')



class py_input:
    def __init__(self, *args):
        self.args = args[0]
        if "exit" in self.args or "EXIT" in self.args:
            global __name__
            __name__ = None
        elif "help" in self.args:
            help(*self.args)
        elif "ls" in self.args:
            ls(*self.args)
        elif "pwd" in self.args:
            pwd()
        elif "cd" in self.args:
            cd(*self.args)
        elif len(self.args) <= 1:
            print(end="")
        else:
            print(*self.args)


while __name__ == "__main__":
    py_input(input('>').split(" "))
