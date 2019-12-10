from warnings import warn, simplefilter

from pytest import fixture, raises
from geometry import Rect, Segment, Point, Group
from skillbridge import Workspace, current_workspace

from rodlayout import Canvas, Layer
from rodlayout.proxy import DbShape


@fixture
def ws():
    return Workspace.open().make_current()


@fixture
def canvas():
    return Canvas(current_workspace.ge.get_edit_cell_view())


saved_shapes = []


@fixture
def cleanup():
    try:
        yield None
    finally:
        for db in saved_shapes:
            try:
                db.delete(children=True)
            except Exception as e:
                simplefilter('always', UserWarning)
                warn(f"Failed to delete shape {db}: {e}", category=UserWarning, stacklevel=1)
                simplefilter('default', UserWarning)

        saved_shapes.clear()


def register_and_draw(self):
    shapes = self.pytest_saved_old_draw()
    saved_shapes.extend(shapes)
    return shapes


Canvas.pytest_saved_old_draw = Canvas.draw
Canvas.draw = register_and_draw


def point_equal(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    return dx < 1e-9 and dy < 1e-9


def layer_of(remote):
    lpp = remote.lpp
    if lpp is None and remote.db_id is not None:
        lpp = remote.db_id.lpp

    return None if lpp is None else Layer(*lpp)


def to_rect(r):
    if isinstance(r, Rect):
        return r
    (l, b), (right, t) = (r.b_box or r.db_id.b_box)

    return Rect.from_edges(l, right, b, t, layer_of(r))


def nearly_equal(x, y):
    if isinstance(x, (list, tuple)):
        return all(nearly_equal(xx, yy) for xx, yy in zip(x, y))
    return abs(x - y) < 1e-9


def rect_equal(r1, r2):
    r1 = to_rect(r1)
    r2 = to_rect(r2)

    return (
        nearly_equal(r1.bottom_left, r2.bottom_left)
        and nearly_equal(r1.top_right, r2.top_right)
        and r1.user_data == r2.user_data
    )


def to_segment(s):
    if isinstance(s, Segment):
        return s
    points = s.db_id.points if s.db_id else s.points
    width = s.db_id.width if s.db_id else s.width
    start, end = (Point(x, y) for x, y in points)
    return Segment.from_start_end(start, end, width, layer_of(s))


def segment_equal(s1, s2):
    s1 = to_segment(s1)
    s2 = to_segment(s2)

    return (
        nearly_equal(s1.start, s2.start)
        and nearly_equal(s1.end, s2.end)
        and nearly_equal(s1.thickness, s2.thickness)
        and s1.user_data == s2.user_data
    )


def test_cannot_draw_without_workspace():
    with raises(RuntimeError):
        Canvas()


def test_cannot_draw_without_layer(ws):
    with raises(AssertionError, match="layer"):
        c = Canvas()
        c.append(Rect[1, 2])
        c.draw()


def test_create_rect(ws, canvas, cleanup):
    layer = Layer('M1', 'drawing')
    r = Rect[0:0.1, 0.2:0.3, layer]

    canvas.append(r)
    rod, = canvas.draw()

    assert rod.valid
    assert rect_equal(r, rod.db)


def test_create_segment(ws, canvas, cleanup):
    layer = Layer('M2', 'pin')
    s = Segment.from_start_end(Point(0, 1), Point(10, 1), 2, layer)
    canvas.append(s)
    rod, = canvas.draw()

    assert rod.valid
    assert segment_equal(s, rod.db)


def test_create_group(ws, canvas, cleanup):
    r = Rect[0:0.1, 0.2:0.3, Layer('M1', 'drawing')]
    s = Segment.from_start_end(Point(1, 1), Point(2, 1), 0.1, Layer('M2', 'pin'))
    g = Group([r, s])

    canvas.append(g)
    db, = canvas.draw()

    assert db.valid
    assert rect_equal(g.bbox, db.db)
    assert rect_equal(db.db.figs[0], r)
    assert segment_equal(db.db.figs[1], s)


def test_create_nested_group(ws, canvas, cleanup):
    one = Rect[0:0.1, 0.2:0.3, Layer('M1', 'drawing')]
    two = one.copy()
    two.translate(left=one.right)
    group_one = Group([one, two])

    three = one.copy()
    three.translate(top=one.bottom)

    group_two = Group([group_one, three])

    canvas.append(group_two)
    db, = canvas.draw()

    assert rect_equal(group_two.bbox, db.db)
    assert rect_equal(db.db.figs[1], three)
    assert rect_equal(db.db.figs[0].figs[0], one)
    assert rect_equal(db.db.figs[0].figs[1], two)


def test_delete_works(ws, canvas, cleanup):
    one = Rect[0:0.1, 0.2:0.3, Layer('M1', 'drawing')]
    group = Group([one])

    canvas.append(group)
    db, = canvas.draw()

    rect_db = DbShape(db.db.figs[0])

    rect_db.delete()

    assert not db.db.figs
    assert not rect_db.valid
    assert db.valid
