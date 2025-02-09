from pathlib import Path

ROOT_LEVELS_UP = 2


def generate_path(path: str) -> str:
    """generate the absolute path

    Args:
        path (str): Relative path from root directory.

    Returns:
        str: Absolute path
    """
    return str(Path(__file__).parents[ROOT_LEVELS_UP]) + path
