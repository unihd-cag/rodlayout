Canvas Backend to Cadence Rod Objects ![status](https://github.com/unihd-cag/rodlayout/workflows/Python%20package/badge.svg)
=====================================

Install
-------

```bash
pip install rodlayout
```

Read more in the [full documentation](https://unihd-cag.github.io/rodlayout/).


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
