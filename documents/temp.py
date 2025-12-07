import os

def list_files(directory: str) -> list[str]:
    """Lists all files in a given directory.

    Args:
        directory (str): The name of the directory

    Returns:
        list[str]: Lists of all file names in a directory.
    """

    try:
        return [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return []
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []