from __future__ import annotations

from typing import NamedTuple, Any, Generator, List

from skillbridge import Workspace
from geometry import Rect

from .instance import AnyInstance, root_instance, Instance
from .shape import ShapeView, rod_dummy
from .transform import Transform


class CellView(NamedTuple):
    ws: Workspace
    cv: Any
    instance: AnyInstance

    @classmethod
    def get_edit_cell_view(cls, ws: Workspace) -> CellView:
        return CellView(ws, ws.ge.get_edit_cell_view(), root_instance)

    @property
    def transform(self) -> Transform:
        return self.instance.transform

    def shapes(self, depth: int = -1) -> Generator[ShapeView, None, None]:
        yield from (
            ShapeView(self.ws.rod.get_obj(shape) or rod_dummy, shape, self.instance)
            for shape in self.cv.shapes
        )

        if depth != 0:
            for child in self.children():
                yield from child.shapes(depth - 1)

    def b_box(self) -> Rect:
        return Rect.skill(self.cv.pr_boundary.b_box)

    def children(self) -> List[CellView]:
        return [CellView(self.ws, inst.master, Instance(inst)) for inst in
                (self.cv.instances or ())]

    def __str__(self) -> str:
        id_ = self.cv._variable.split('_')[-1]
        return f"CellView({id_} in {self.instance.parent} @{self.ws._id})"

    def __repr__(self) -> str:
        return self.__str__()

    def redraw(self) -> bool:
        return bool(self.ws.hi.redraw())
