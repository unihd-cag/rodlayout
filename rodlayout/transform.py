from enum import Enum


class Transform(Enum):
    identity = "R0"
    rotate90 = "R90"
    rotate180 = "R180"
    rotate270 = "R270"
    mirror_x = "MX"
    mirror_y = "MY"
