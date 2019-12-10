from typing import NamedTuple


class Layer(NamedTuple):
    """
    A named tuple for the layer purpose pair in Virtuoso

    >>> Layer('M1', 'drawing')
    Layer(name='M1', purpose='drawing')

    """

    name: str
    purpose: str
