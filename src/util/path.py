from pathlib import Path


def generate_path(path: str) -> str:
    """generate the absolute path

    Args:
        path (str): Relative path from root directory.

    Returns:
        str: Absolute path
    """
    return str(Path(__file__).parents[2]) + path
