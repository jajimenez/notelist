"""Tools module."""


def get_border_title(title: str) -> str:
    """Return a string with borders given a title.

    :param title: Title.
    :return: Title with borders.
    """
    border = f'+{"-" * (len(title) + 2)}+'
    return f"{border}\n| {title} |\n{border}"
