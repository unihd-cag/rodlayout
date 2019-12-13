from typing import List, Any, Union, Generator, cast

from geometry import Rect, Segment, Group
from geometry.mixins import AppendMany
from skillbridge import current_workspace
from skillbridge.client.hints import SkillTuple
from skillbridge.client.objects import RemoteObject

from .layer import Layer
from .proxy import RodShape, DbShape

Shape = Union[Rect, Segment, Group]


class Canvas(AppendMany[Shape]):
    """
    A Canvas class, similar to the geometry.Canvas class.

    Instead of creating a visual output of the shapes, this
    canvas creates shapes in virtuoso.

    The layer is controlled by the user_data field of the shapes

    >>> c = Canvas(...)
    """

    def __init__(self, cell_view: Any = None) -> None:
        self.cell_view = cell_view or current_workspace.ge.get_edit_cell_view()
        self.shapes: List[Shape] = []

    def append(self, shape: Shape) -> None:
        """
        Add one shape to the Canvas

        >>> from geometry import Rect
        >>> c = Canvas(...)
        >>> len(c.shapes)
        0

        >>> c.append(Rect[2, 4, Layer('M1', 'drawing')])
        >>> len(c.shapes)
        1
        """
        self.shapes.append(shape)

    def _draw(self, shapes: List[Shape]) -> Generator[DbShape, None, None]:
        for shape in shapes:
            type_name = type(shape).__name__.lower()
            yield getattr(self, f'_draw_{type_name}')(shape)

    def draw(self, redraw: bool = False) -> List[DbShape]:
        """
        Draw all shapes in the Canvas, i.e. instantiate them in Virtuoso.

        Pass ``True```to ``redraw`` to automatically redraw the shapes in Virtuoso.
        Without this, you must first change the view in Virtuoso to see the created shapes
        """
        shapes = list(self._draw(self.shapes))
        if redraw:
            current_workspace.hi.redraw()
        return shapes

    def _draw_rect(self, rect: Rect) -> DbShape:
        layer = cast(SkillTuple, rect.user_data)
        assert isinstance(layer, Layer), "Rectangle needs a layer."

        bbox = cast(SkillTuple, (rect.bottom_left, rect.top_right))
        rod = current_workspace.rod.create_rect(cv_id=self.cell_view, layer=layer, b_box=bbox)
        return RodShape.from_rod(cast(RemoteObject, rod))

    def _draw_segment(self, segment: Segment) -> DbShape:
        layer = cast(SkillTuple, segment.user_data)
        assert isinstance(layer, Layer), "Segment needs a layer."

        points = segment.start, segment.end
        rod = current_workspace.rod.create_path(
            cv_id=self.cell_view, layer=layer, pts=points, width=segment.thickness
        )
        return RodShape.from_rod(rod)

    def _draw_group(self, group: Group) -> DbShape:
        center = cast(SkillTuple, (0, 0))
        db = current_workspace.db.create_fig_group(self.cell_view, None, False, center, "R0")

        for child in self._draw(group.shapes):
            current_workspace.db.add_fig_to_fig_group(db, child.db)

        return DbShape(cast(RemoteObject, db))
