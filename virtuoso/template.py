from __future__ import annotations

from dataclasses import dataclass

from geometry import Rect, Point, Number, Path, Shape
from skillbridge.client.objects import RemoteObject

from .shape import ShapeView
from .layer import Layer
from .instance import root_instance
from .cell import CellView


@dataclass
class ShapeTemplate:
    layer: Layer
    shape: Shape

    @classmethod
    def rect(cls, layer: Layer, bottom_left: Point, top_right: Point) -> ShapeTemplate:
        return ShapeTemplate(layer, Rect(bottom_left, top_right))

    @classmethod
    def path(cls, layer: Layer, width: Number, *points: Point) -> ShapeTemplate:
        return ShapeTemplate(layer, Path(points, width))

    def _create_rect(self, cell_view: CellView, shape: Rect) -> RemoteObject:
        cv_id = cell_view.cv
        layer = list(self.layer)
        b_box = [[i for i in p] for p in shape]
        return cell_view.ws.rod.create_rect(
            cv_id=cv_id, layer=layer, b_box=b_box)

    def _create_path(self, cell_view: CellView, shape: Path) -> RemoteObject:
        cv_id = cell_view.cv
        layer = list(self.layer)
        points = list(map(list, shape.points))
        return cell_view.ws.rod.create_path(
            cv_id=cv_id, layer=layer, pts=points,
            width=self.shape.width
        )

    def create(self, cell_view: CellView) -> ShapeView:
        if isinstance(self.shape, Rect):
            rod = self._create_rect(cell_view, self.shape)
        else:
            rod = self._create_path(cell_view, self.shape)

        if rod is None:
            raise RuntimeError("Could not create shape")

        return ShapeView(rod, rod.db_id, root_instance)
