from typing import Generator, cast
from dataclasses import dataclass

from skillbridge import current_workspace
from skillbridge.client.hints import SkillTuple
from skillbridge.client.objects import RemoteObject

from geometry import Point, Number, Rect
from geometry.translate import CanTranslate

from .transform import Transform


@dataclass
class DbShape(CanTranslate):
    """
    A proxy to an existing shape in Virtuoso.

    The shape only consists of a db object without a rod object.
    E.g. figure groups will be represented as a ``DbShape``
    """

    db: RemoteObject

    def __str__(self) -> str:
        return f"{self.db.obj_type}@{self.db.skill_id}"

    def __repr__(self) -> str:
        return self.__str__()

    def move(self, offset: Point) -> None:
        """
        Move the db object relative by a given offset

        This actually moves the object in virtuoso
        """
        transform = cast(SkillTuple, (offset, Transform.identity.value))
        current_workspace.db.move_fig(self.db, self.db.cell_view, transform)

    def delete(self, children: bool = True, redraw: bool = False) -> None:
        """
        Delete the db object.

        Setting ``children`` to ``True`` will also delete the child shapes if this
        is a figure group.

        Setting ``redraw`` to ``True`` will refresh the view in Virtuoso

        .. warning ::

            After you deleted an object you should discard the python variable, too,
            because the underlying db object is not valid anymore.

        """
        if children:
            for fig in self.db.figs or ():
                DbShape(fig).delete(children=True, redraw=False)
        current_workspace.db.delete_object(self.db)
        if redraw:
            current_workspace.hi.redraw()

    @property
    def valid(self) -> bool:
        """
        Check if the db object is still valid and was not deleted.
        """
        return cast(bool, current_workspace.db.valid_p(self.db))

    def _promote_children_to_rod(self, fig_grp: RemoteObject) -> None:
        for fig in fig_grp.figs:
            if fig.obj_type == 'figGroup':
                self._promote_children_to_rod(cast(RemoteObject, fig))
            else:
                current_workspace.rod.name_shape(shape_id=fig)

    def _copy_figure(
        self, cell_view: RemoteObject, translate: Point, transform: Transform
    ) -> RemoteObject:

        translate_transform = cast(SkillTuple, (translate, transform.value))
        db = current_workspace.db.copy_fig(self.db, cell_view, translate_transform)

        self._promote_children_to_rod(cast(RemoteObject, db))

        return cast(RemoteObject, db)

    def copy(
        self, translate: Point = Point(0, 0), transform: Transform = Transform.identity
    ) -> 'DbShape':
        """
        Copy the dbShape and translate, transform the copy.
        """
        return DbShape(self._copy_figure(self.db.cell_view, translate, transform))

    def children(self) -> Generator['RodShape', None, None]:
        """
        Get all RodShapes within a Group and its hierarchy
        """
        for fig in self.db.figs:
            if fig.obj_type == 'figGroup':
                yield from DbShape(fig).children()
            else:
                rod = current_workspace.rod.get_obj(fig)
                yield RodShape.from_rod(cast(RemoteObject, rod))

    @property
    def _bbox(self) -> Rect:
        (left, bottom), (right, top) = self.db.b_box
        return Rect.from_edges(left, right, bottom, top)

    @property
    def xy(self) -> Point:
        """
        The center of the bounding box of the db object

        Assigning the property will translate the object
        such that the new center of its bounding box is at the
        given point
        """
        return self._bbox.xy  # type: ignore

    @xy.setter
    def xy(self, new_point: Point) -> None:
        offset = new_point - self.xy
        self.move(offset)

    @property  # type: ignore
    def x(self) -> Number:  # type: ignore
        """
        The x coordinate of the center of the bounding box of the db object

        Assigning the property will translate the object horizontally
        such that the new x coordinate and the given x coordinate match
        """
        return self._bbox.x

    @x.setter
    def x(self, new_x: Number) -> None:
        offset = Point(new_x - self.x, 0)
        self.move(offset)

    @property  # type: ignore
    def y(self) -> Number:  # type: ignore
        """
        The y coordinate of the center of the bounding box of the db object

        Assigning the property will translate the object vertically
        such that the new y coordinate and the given y coordinate match
        """
        return self._bbox.y

    @y.setter
    def y(self, new_y: Number) -> None:
        offset = Point(0, new_y - self.y)
        self.move(offset)

    @property
    def width(self) -> Number:  # type: ignore
        """
        The width of the bounding box of the db object
        """
        return self._bbox.width

    @property
    def height(self) -> Number:  # type: ignore
        """
        The height of the bounding box of the db object
        """
        return self._bbox.height


@dataclass
class RodShape(DbShape):
    """
    A proxy to an existing shape in Virtuoso with a rod object.

    This proxy also contains the rod object which allows aligning and other features.
    E.g. rectangles and paths will be represented as a ``RodShape``
    """

    # db: RemoteObject
    rod: RemoteObject

    @classmethod
    def from_rod(cls, rod: RemoteObject) -> 'RodShape':
        """
        Create a rod proxy from an existing rod object in virtuoso.
        """
        return RodShape(rod.db_id, rod)

    def copy(
        self, translate: Point = Point(0, 0), transform: Transform = Transform.identity
    ) -> 'RodShape':
        """
        Copy the RodShape and translate, transform the copy.
        """
        db = self._copy_figure(self.rod.cv_id, translate, transform)
        rod = current_workspace.rod.name_shape(shape_id=db)

        return RodShape(db, cast(RemoteObject, rod))
