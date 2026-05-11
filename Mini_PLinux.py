""" Practice to create a mini Linux like CLI with NMAP capabilities in the future
    this is to practice the use of *args and **kwargs specifically"""
import ast
import os.path

""" File structure
    file: (extension type, size, content data, etc etc)"""

__name__ = "__main__"

directory = {
    "C:\\": {
        "Document": {"Folder": {},
                     "File1": ("txt", "1kB", "hello world. \nThis is a file with multiple lines. \ncoding is painful"),
                     "File2": ("txt", "1kB", "goodbye world")},
        "Desktop": {"-Hidden_File": ("txt", "1kB", "Secret Code: XNA39TA")},
        "-system": {"-x64": {"-hidden_folder": {}},
                    "-x32": {}
                    }
    }
}

path_stack = ["C:\\"]


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


def cat(*args):
    """ Output first 10 lines of a file
        displays contents only
    """
    global directory, path_stack
    direct_tree = directory
    path = path_stack

    # navigate current folder and have the target value ready
    target_file = args[1]
    for folder in path:
        direct_tree = direct_tree[folder]

    # if the target file is in the directory folder
    if target_file in direct_tree:
        item = direct_tree[target_file]

        # 3. Check if it's a file (tuple) or folder (dict)
        if isinstance(item, tuple):
            # Print the content (index 2 of file tuple handling)
            print(f">File: {target_file}\n")
            content = item[2].splitlines()
            for line in content[:10]:
                print(line, end="\n")

        elif isinstance(item, dict):
            print(f"cat: {target_file}: Is a directory")
    else:
        print(f"cat: {target_file}: No such file")


def cd(*args):
    """ cd function
        to traverse between directories

        Format
        cd  <>  :   to move to <> directory
            ..  :   to move back up a directory
    """
    global path_stack
    global directory

    # args[0] is "cd", args[1] is the folder
    if len(args) < 2:
        print("Error: No directory specified.")
        return

    target_folder = args[1]

    # get current folder level within the tree.
    current_folder = directory
    for folder in path_stack:
        current_folder = current_folder[folder]

    if target_folder == "..":
        # check if in root directory already
        if len(path_stack) > 1:
            path_stack.pop()
            print(f"Moved up. Current path: {'/'.join(path_stack)}")
        else:
            print("already in root directory")
    elif target_folder in current_folder:

        # if current instance is a folder ten 'i' can append to stack and move into it
        if isinstance(current_folder[target_folder], dict):
            path_stack.append(target_folder)
            print(f"Moved to: {'/'.join(path_stack)}")
        # if current instance is a tuple this is a file
        elif isinstance(current_folder[target_folder], tuple):
            print(f"Error:'{target_folder}' is a file. Use 'cat' to read it.")
        else:
            print(f"Error: '{target_folder}' is a file.")
    else:
        print(f"Access Denied: '{target_folder}' not found.")


def pwd():
    """ Print Working Directory Function """
    global path_stack
    print("\\".join(path_stack))


def list_recursive(current_dict, indent=0):
    """ Recursive search through the directory dictionary/ or list """
    for key, value in current_dict.items():
        # Print the current item with indentation (4 spaces per level)
        print("|\t" * indent + str(key))

        # If the value is another dictionary, recurse into it
        if isinstance(value, dict):
            if not value:  # Check if the dictionary is EMPTY
                print("|\t" * (indent + 1) + "(empty folder)")
            else:
                list_recursive(value, indent + 1)

        if isinstance(value, tuple):
            # if FILE print details - not content.
            print("|\t" * (indent + 1) + f"{key}.{value[0]}", end="\n")


def ls(*args):
    """ List function,
            This command will output a list of the current directory

            Format
            >ls         :   lists all items from the current directory
                -la     :   list all with all details
                -lh     :   list all in current directory, with human-readable sizes
                -R      :   list recursively from the current directory to the lowest point
    """
    global directory, path_stack
    direct_tree = directory
    path = path_stack

    # Print everything within current working directory
    if len(args) == 1:
        for folder in path:
            direct_tree = direct_tree[folder]
        print(*list(direct_tree.keys()), sep="\n")

    elif "-la" in args:
        # List with all details
        for folder in path:
            direct_tree = direct_tree[folder]
        for key, value in direct_tree.items():
            if isinstance(value, tuple):
                # if FILE print details - not content.
                print(f"{key}\t Ext: {value[0]}\tSize: {value[1]}", end="\n")

            else:
                # if FOLDER, must be a dictionary, so only print the key
                print(f"{key}", end="\n")
    elif "-lh" in args:
        # List readable human sizes
        print("TODO")
    elif "-R" in args:
        # List everything from the current directory - recursive to the lowest point.
        print(f"Recursive mapping for {'/'.join(path_stack)}:")
        list_recursive(direct_tree)


def save():
    global directory
    print("saving file structure for exit")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "plinux_save.txt")

    with open(file_path, "w") as f1:
        f1.write(str(directory))
    f1.close()


def load(*args):
    global directory
    print("loading file structure for exit")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "plinux_save.txt")
    print(script_dir)
    print(file_path)
    if os.path.exists(file_path):
        print(True)
        with open(file_path, "r") as f1:  # Note: "r" for reading"
            data = f1.read()
            print(data)
            if data:
                # Convert the string back into a dictionary
                directory = ast.literal_eval(data)
                print("File structure loaded successfully.")
            else:
                print("Save file is empty.")

    else:
        print("No save file found. Starting fresh.")
    print(directory)


class py_input:
    def __init__(self, *args):
        self.args = args[0]
        if "exit" in self.args or "EXIT" in self.args:
            global __name__
            __name__ = None
        elif "save" in self.args:
            save()
        if "load" in self.args:
            load()
        elif "help" in self.args:
            help(*self.args)
        elif "ls" in self.args:
            ls(*self.args)
        elif "pwd" in self.args:
            pwd()
        elif "cd" in self.args:
            cd(*self.args)
        elif "cat" in self.args:
            cat(*self.args)
        elif len(self.args) <= 1:
            print(end="")
        else:
            print(*self.args)


while __name__ == "__main__":
    py_input(input(path_stack[-1] + '>').split(" "))
