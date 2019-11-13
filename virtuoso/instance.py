from __future__ import annotations

from typing import NamedTuple, Union

from skillbridge.client.objects import RemoteObject

from .transform import Transform, identity


class Instance(NamedTuple):
    handle: RemoteObject

    @classmethod
    def from_skill(cls, handle: RemoteObject) -> Instance:
        return Instance(handle)

    @property
    def transform(self) -> Transform:
        return Transform.from_skill(self.handle.transform)

    @property
    def parent(self) -> str:
        return str(self.handle.cell_view._variable.split('_')[-1])


class RootInstance:
    transform = identity
    parent = 'root'


root_instance = RootInstance()

AnyInstance = Union[Instance, RootInstance]
