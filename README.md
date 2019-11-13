Python-Virtuoso Wrapper
=======================

Examples
--------

```python
from skillbridge import Workspace
from virtuoso import CellView, ShapeTemplate, Align
from geometry import Rect, Point
```

**Create a Rect**

```python
ws = Workspace.open()
cv = CellView.get_edit_cell_view(ws)

template = ShapeTemplate(
    Layer('M1', 'drawing'),
    #    lower left , upper right
    Rect(Point(0, 0), Point(0.1, 0.1))
)

# create the rect in Virtuoso
rod = template.create(cv)
# either call this or move the view in Virtuoso
cv.redraw()

print(rod)
# > RectView(rod=0x3514d260 db=0x2146836d @root)

input("press enter to continue")

# deletes the shape in Virtuoso
rod.delete()
cv.redraw()
```

**Align two Objects**

```python

fixed = template.create(cv)
move = template.create(cv)

where = Align.lower_left
move.align(where, where.mirror_x, fixed, ws)
cv.redraw()

input("press enter to continue")
move.delete()
fixed.delete()
cv.redraw()
```

This moves the `move` rect such that its lower left point is identical
to the lower right point of `fixed`

```
           +----+----+
           |    |    |
 fixed ->  |    |    |  <- move
           +----X----+
                ^
          alignment point
```
