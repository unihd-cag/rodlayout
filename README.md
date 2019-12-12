Canvas Backend to Cadence Rod Objects 
=====================================

[![PyPI version](https://badge.fury.io/py/rodlayout.svg)](https://badge.fury.io/py/rodlayout)
![status](https://github.com/unihd-cag/rodlayout/workflows/Python%20package/badge.svg)

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

rod, = c.draw()
print(rod)  # rect@...

r2 = Rect[0:4, 0:2, Layer('M2', 'drawing')]
c = Canvas()
c.append(Group([r, r2]))
db, = c.draw()

print(db)  # figGroup@...


```
