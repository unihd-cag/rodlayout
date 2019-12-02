from typing import List, Any, Union, Tuple, Generator, Iterable

from geometry import Rect, Segment, Group
from skillbridge import current_workspace

from .layer import Layer

Shape = Union[Rect, Segment, Group]
DbRod = Tuple[Any, Any]


class Canvas:
    def __init__(self, cell_view: Any = None) -> None:
        self.cell_view = cell_view or current_workspace.ge.get_edit_cell_view()
        self.shapes: List[Shape] = []

    def append(self, shape: Shape) -> None:
        """
        Add one shape to the Canvas

        >>> from geometry import Rect
        >>> c = Canvas()
        >>> len(c.shapes)
        0

        >>> c.append(Rect[2, 4, Layer('M1', 'drawing')])
        >>> len(c.shapes)
        1
        """
        self.shapes.append(shape)

    def extend(self, shapes: Iterable[Shape]) -> None:
        """
        Add shapes from an iterable to the Canvas

        >>> from geometry import Rect
        >>> c = Canvas()
        >>> len(c.shapes)
        0

        >>> c.extend([Rect[2, 4, Layer('M1', 'drawing')], ..., ...])
        >>> len(c.shapes)
        3
        """
        self.shapes.extend(shapes)

    def extend_star(self, *shapes: Shape) -> None:
        """
        Add shapes from var args to the Canvas

        >>> from geometry import Rect
        >>> c = Canvas()
        >>> len(c.shapes)
        0

        >>> c.extend_star(Rect[2, 4, Layer('M1', 'drawing')], ..., ...)
        >>> len(c.shapes)
        3
        """
        self.shapes.extend(shapes)

    def _draw(self, shapes: List[Shape]) -> Generator[DbRod, None, None]:
        for shape in shapes:
            type_name = type(shape).__name__.lower()
            yield getattr(self, f'_draw_{type_name}')(shape)

    def draw(self) -> List[DbRod]:
        """
        Draw all shapes in the Canvas, i.e. instantiate them in Virtuoso.
        """
        return list(self._draw(self.shapes))

    def _draw_rect(self, rect: Rect) -> DbRod:
        layer = rect.user_data
        assert isinstance(layer, Layer)

        b_box = rect.bottom_left, rect.top_right
        rod = current_workspace.rod.create_rect(cv_id=self.cell_view, layer=layer,
                                                b_box=b_box)
        return None, rod

    def _draw_segment(self, segment: Segment) -> DbRod:
        layer = segment.user_data
        assert isinstance(layer, Layer)

        points = segment.start, segment.end
        rod = current_workspace.rod.create_path(cv_id=self.cell_view, layer=layer,
                                                pts=points)
        return None, rod

    def _draw_group(self, group: Group) -> DbRod:
        db = current_workspace.db.create_fig_group(self.cell_view,
                                                   None, False, [0, 0], "R0")

        for child_db, child_rod in self._draw(group.shapes):
            if child_db is None:
                child_db = child_rod.db_id
            current_workspace.db.add_fig_to_fig_group(db, child_db)

        return db, None
