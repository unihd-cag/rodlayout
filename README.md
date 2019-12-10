Python-Virtuoso Wrapper
=======================

```python
from skillbridge import Workspace
from geometry import Rect, Group

from rodlayout import Canvas, Layer

Workspace.open().make_current()


r = Rect[0:2, 0:4, Layer('M1', 'drawing')]
c = Canvas()
c.append(r)
(db_id, rod_id), = c.draw()
print(rod_id)  # <remote rodObj@...>

r2 = Rect[0:4, 0:2, Layer('M2', 'drawing')]
c = Canvas()
c.append(Group([r, r2]))
(db_id, rod_id), = c.draw()
print(db_id)  # <remote figGroup@...>


```