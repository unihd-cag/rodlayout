from enum import Enum


class Transform(Enum):
    """
    Represents a transformation mapping to dbTransforms
    """

    identity = "R0"
    """The identity transform"""
    rotate90 = "R90"
    """rotate clock-wise 90 degrees"""
    rotate180 = "R180"
    """rotate 180 degrees"""
    rotate270 = "R270"
    """rotate clock-wise 270 degrees"""
    mirror_x = "MX"
    """mirror horizontally"""
    mirror_y = "MY"
    """mirror vertically"""
