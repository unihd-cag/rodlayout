from enum import Enum


class Transform(Enum):
    """
    Represents a transformation mapping to dbTransforms

    identity  -> "R0"
    rotate90  -> "R90"
    rotate180 -> "R180"
    rotate270 -> "R270"
    mirror_x  -> "MX"
    mirror_y  -> "MY"
    """
    identity = "R0"
    rotate90 = "R90"
    rotate180 = "R180"
    rotate270 = "R270"
    mirror_x = "MX"
    mirror_y = "MY"
