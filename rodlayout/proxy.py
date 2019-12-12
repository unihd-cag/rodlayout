from typing import Generator
from dataclasses import dataclass

from skillbridge import current_workspace
from skillbridge.client.objects import RemoteObject

from geometry import Point

from .transform import Transform


@dataclass(frozen=True)
class DbShape:
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

    def delete(self, children=True, redraw=False) -> None:
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
        return current_workspace.db.valid_p(self.db)

    def copy(
        self, translate: Point = Point(0, 0), transform: Transform = Transform.identity
    ) -> 'DbShape':
        """
        Copy the dbShape and translate, transform the copy.
        """
        cv = self.db.cell_view
        return DbShape(current_workspace.db.copy_fig(self.db, cv, (translate, transform.value)))

    def children(self) -> Generator['RodShape', None, None]:
        """
        Get all RodShapes within a Group and its hierarchy
        """
        for fig in self.db.figs:
            if fig.obj_type == 'figGroup':
                yield from DbShape(fig).children()
            else:
                yield RodShape.from_rod(current_workspace.rod.get_obj(fig))


@dataclass(frozen=True)
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
        cv = self.rod.cv_id
        db_id = current_workspace.db.copy_fig(self.db, cv, (translate, transform.value))

        return RodShape.from_rod(current_workspace.rod.name_shape(shape_id=db_id))
