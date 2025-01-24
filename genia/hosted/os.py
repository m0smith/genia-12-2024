import os

from genia.seq import IterSeq

def files_in_paths(*paths):
    """
    Returns an IterSeq of all files in the given paths.
    
    :param paths: One or more paths to files or directories.
    :return: An IterSeq containing all the files in the given paths.
    """
    def file_generator():
        for path in paths:
            if os.path.isfile(path):
                yield path  # Yield file directly
            elif os.path.isdir(path):
                # Walk through directories recursively
                for root, _, files in os.walk(path):
                    for file in files:
                        yield os.path.join(root, file)
            else:
                # If the path doesn't exist, ignore it or raise an error
                raise ValueError(f"Path does not exist: {path}")

    return IterSeq(file_generator())
