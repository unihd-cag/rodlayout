from __future__ import annotations

from typing import NamedTuple, Any, Tuple

from geometry import Point, Number

SkillTransform = Tuple[Tuple[Number, Number], str, Number]


class Transform(NamedTuple):
    offset: Point
    rotation: Number
    scale: Number

    @classmethod
    def from_skill(cls, transform: SkillTransform) -> Transform:
        offset, rotation, scale = transform
        return Transform(Point(*offset), int(rotation[1:]), scale)

    def __mul__(self, other: Any) -> Transform:
        assert isinstance(other, Transform)

        return Transform(
            self.offset + other.offset,
            (self.rotation + self.rotation) % 360,
            self.scale * other.scale
        )


identity = Transform(Point(0, 0), 0, 1.0)
