import os

def load_files(path, extensions=None, ignore_dirs=None):
    """
    Recursively yield file paths under `path` filtered by extensions.

    :param path: Directory to walk.
    :param extensions: List of extensions, e.g. ['.py', '.js', '.ts']. Case insensitive.
    :param ignore_dirs: List of directory names to skip, e.g. ['node_modules', '__pycache__']
    """
    extensions = [ext.lower() for ext in extensions] if extensions else None
    ignore_dirs = set(ignore_dirs) if ignore_dirs else set()

    for root, dirs, files in os.walk(path):
        # Remove ignored dirs from walk
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            if extensions is None or any(filename.lower().endswith(ext) for ext in extensions):
                yield os.path.join(root, filename)
