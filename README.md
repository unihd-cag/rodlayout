Python-Virtuoso Wrapper
=======================

```
from skillbridge import Workspace
from geometry import Rect

from rodlayout import Canvas, Layer

Workspace.open().make_current()


r = Rect[0:2, 0:4, Layer('M1', 'drawing')
c = Canvas()
c.append(r)
[db_id, rod_id] = c.draw()
```