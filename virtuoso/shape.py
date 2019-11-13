from __future__ import annotations

from typing import NamedTuple, Any, NoReturn, Dict, Type, Callable
from enum import Enum

from geometry import Rect, Path, Shape
from skillbridge import Workspace
from skillbridge.client.hints import Skillable, SkillCode
from skillbridge.client.objects import RemoteObject

from .layer import Layer
from .instance import AnyInstance

OBJ_TYPE_TO_TYPE: Dict[str, Type[Shape]] = {
    'rect': Rect,
    'pathSeg': Path
}

OBJ_TYPE_TO_SHAPE: Dict[str, Callable[[RemoteObject], Shape]] = {
    'rect': lambda db: Rect.skill(db.b_box),
    'pathSeg': lambda db: Path(db.points, db.width)
}


class RodDummy(Skillable):
    def __getattr__(self, item: str) -> NoReturn:
        raise RuntimeError("You need a Rod object to do this")

    def __setattr__(self, key: str, value: Any) -> NoReturn:
        raise RuntimeError("You need a Rod object to do this")

    def __str__(self) -> str:
        return "<missing rod object>"

    def __repr_skill__(self) -> SkillCode:
        raise RuntimeError("You need a Rod object to do this")

    __repr__ = __str__

    _variable = '__py_rod_missing'


rod_dummy = RodDummy()


class Align(Enum):
    lower_left = 'lowerLeft', 'lower_right', 'upper_left', 'upper_right'
    lower_center = 'lowerCenter', 'lower_center', 'upper_center', 'upper_center'
    lower_right = 'lowerRight', 'lower_left', 'upper_right', 'upper_left'
    upper_left = 'upperLeft', 'upper_right', 'lower_left', 'lower_right'
    upper_center = 'upperCenter', 'upper_center', 'lower_center', 'lower_center'
    upper_right = 'upperRight', 'upper_left', 'lower_right', 'lower_left'
    center_left = 'centerLeft', 'center_right', 'center_left', 'center_right'
    center_center = 'centerCenter', 'center_center', 'center_center', 'center_center'
    center_right = 'centerRight', 'center_left', 'center_right', 'center_left'

    def __init__(self, value: str, x: str, y: str, xy: str) -> None:
        self.id = value
        self.x = x
        self.y = y
        self.xy = xy

    @property
    def mirror_x(self) -> Align:
        return Align[self.x]

    @property
    def mirror_y(self) -> Align:
        return Align[self.y]

    @property
    def mirror_xy(self) -> Align:
        return Align[self.xy]

    def __repr__(self) -> str:
        return f"<Align.{self.id}>"


class ShapeView(NamedTuple):
    rod: Any
    db: Any
    instance: AnyInstance

    def get(self, key: str, default: Any = None) -> Any:
        for prop in (self.db.prop or ()):
            if prop.name == key:
                return prop.value
        return default

    def properties(self) -> Dict[str, Any]:
        return {
            prop.name: prop.value for prop in self.db.prop or ()
        }

    @property
    def valid_rod(self) -> bool:
        return self.rod is not rod_dummy

    @property
    def type(self) -> Type[Shape]:
        return OBJ_TYPE_TO_TYPE[self.db.obj_type]

    def shape(self) -> Shape:
        return OBJ_TYPE_TO_SHAPE[self.db.obj_type](self.db)

    def delete(self) -> bool:
        return bool(self.db.db_delete_object())

    def layer(self) -> Layer:
        return Layer(*self.db.lpp)

    def align(self, align: Align, ref: Align, target: ShapeView, ws: Workspace) -> None:
        """
        Aligns the caller such that its `align` point is moved to `ref` point of `target`

        Example:

        `move.align(Align.lower_left, Align.lower_right, fix, ws)`

        This moves `move` such that its lower left point is identical to `fix`s lower
        right point:

        +-------+ <- fix
        |       |
        |       +---+
        |       |   |
        |       |   | <- move
        +-------O---+

        """
        assert self.valid_rod and target.valid_rod

        rod = ws.rod.align(
            align_obj=self.rod,
            ref_obj=target.rod,
            align_handle=align.id,
            ref_handle=ref.id
        )

        assert rod is not None, "align failed"

    def __str__(self) -> str:
        type_name = self.type.__name__
        rod_id = self.rod._variable.split('_')[-1]
        db_id = self.db._variable.split('_')[-1]
        return f"{type_name}View(rod={rod_id} db={db_id} @{self.instance.parent})"

    def __repr__(self) -> str:
        return self.__str__()
