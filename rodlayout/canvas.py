from typing import List, Any, Union

from geometry import Rect, Segment, Group
from skillbridge import Workspace, current_workspace

from .layer import Layer

Shape = Union[Rect, Segment, Group]


class Canvas:
    def __init__(self, cell_view: Any) -> None:
        self.cell_view = cell_view or current_workspace.ge.get_edit_cell_view()
        self.shapes: List[Shape] = []

    def append(self, shape: Shape) -> None:
        self.shapes.append(shape)

    def _draw(self, shapes: List[Shape]):
        for shape in shapes:
            type_name = type(shape).__name__.lower()
            yield getattr(self, f'_draw_{type_name}')(shape)

    def draw(self):
        return self._draw_group(Group(*self.shapes))

    def _draw_rect(self, rect: Rect):
        layer = rect.user_data
        assert isinstance(layer, Layer)

        b_box = rect.bottom_left, rect.top_right
        rod = current_workspace.rod.create_rect(cv_id=self.cell_view, layer=layer, b_box=b_box)
        return rod

    def _draw_segment(self, segment: Segment):
        layer = segment.user_data
        assert isinstance(layer, Layer)

        points = segment.start, segment.end
        rod = current_workspace.rod.create_path(cv_id=self.cell_view, layer=layer, pts=points)
        return rod

    def _draw_group(self, group: Group):
        db = current_workspace.db.create_fig_group(self.cell_view, None, False, [0, 0], "R0")

        for child in self._draw(group.shapes):
            current_workspace.db.add_fig_to_fig_group(db, child.db_id)

        return db

