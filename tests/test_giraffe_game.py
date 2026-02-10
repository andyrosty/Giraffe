"""
Unit tests for giraffe_game.py.

This suite is self-contained and can run without a real display and without
pygame installed. It injects a minimal pygame stub into sys.modules so the
module can be imported headlessly in CI.

Covered:
- clamp and lerp helpers
- circle_rect_collide collision checks (inside, outside, grazing)
- Giraffe.apply_neck_change clamping of neck and head_offset
- Leaf.update vertical motion (with randomized variance disabled for the test)

How to run:
    python -m unittest discover -s tests -p "test_*.py" -v

Notes:
- The tests never call main(); they only exercise pure logic.
- The stub is local to the test process and won’t affect running the game.
"""
import sys
import types
import unittest

# ---- Minimal pygame stub so we can import giraffe_game without a real display or pygame installed
pygame_stub = types.ModuleType("pygame")

# constants used in the game
pygame_stub.K_LEFT = 1
pygame_stub.K_a = 2
pygame_stub.K_RIGHT = 3
pygame_stub.K_d = 4
pygame_stub.K_UP = 5
pygame_stub.K_w = 6
pygame_stub.K_DOWN = 7
pygame_stub.K_s = 8
pygame_stub.K_r = 9
pygame_stub.K_ESCAPE = 10
pygame_stub.SRCALPHA = 32


def _noop(*args, **kwargs):
    return None


class _Surface:
    def __init__(self, size=(0, 0)):
        self.size = size

    def fill(self, *args, **kwargs):
        return None

    def blit(self, *args, **kwargs):
        return None

    def get_width(self):
        # minimal method used by some font surfaces, if ever called
        return self.size[0] if self.size else 0


class _Rect:
    def __init__(self, left, top, width, height):
        self._left = int(left)
        self._top = int(top)
        self._width = int(width)
        self._height = int(height)

    # properties expected by the game
    @property
    def left(self):
        return self._left

    @property
    def top(self):
        return self._top

    @property
    def right(self):
        return self._left + self._width

    @property
    def bottom(self):
        return self._top + self._height

    @property
    def centerx(self):
        return self._left + self._width // 2

    @property
    def centery(self):
        return self._top + self._height // 2

    # allow indexing by attributes in potential future usages
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class _Clock:
    def tick(self, fps):
        return 16  # pretend ~60 FPS


class _Font:
    def render(self, text, antialias, color):
        return _Surface((100, 20))


class _DisplayNS:
    def set_caption(self, *args, **kwargs):
        return None

    def set_mode(self, size):
        return _Surface(size)


class _TimeNS:
    def Clock(self):
        return _Clock()


class _FontNS:
    def SysFont(self, *args, **kwargs):
        return _Font()


class _DrawNS:
    def polygon(self, *args, **kwargs):
        return None

    def rect(self, *args, **kwargs):
        return None

    def line(self, *args, **kwargs):
        return None

    def circle(self, *args, **kwargs):
        return None


# attach namespaces and functions
pygame_stub.init = _noop
pygame_stub.quit = _noop
pygame_stub.display = _DisplayNS()
pygame_stub.time = _TimeNS()
pygame_stub.font = _FontNS()
pygame_stub.draw = _DrawNS()
pygame_stub.Rect = _Rect

# very small event/key stubs used only when running the real game loop (not in these tests)
class _EventNS:
    def get(self):
        return []

class _KeyNS:
    def get_pressed(self):
        # Return a dict-like object for key states; we won't use it in these tests
        return {pygame_stub.K_LEFT: False, pygame_stub.K_RIGHT: False,
                pygame_stub.K_a: False, pygame_stub.K_d: False,
                pygame_stub.K_UP: False, pygame_stub.K_DOWN: False,
                pygame_stub.K_w: False, pygame_stub.K_s: False}

pygame_stub.event = _EventNS()
pygame_stub.key = _KeyNS()

# install stub before importing the game
sys.modules["pygame"] = pygame_stub

import giraffe_game as gg


class TestUtils(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(gg.clamp(-5, 0, 10), 0)
        self.assertEqual(gg.clamp(12, 0, 10), 10)
        self.assertEqual(gg.clamp(5, 0, 10), 5)

    def test_lerp(self):
        self.assertAlmostEqual(gg.lerp(0, 10, 0.0), 0.0)
        self.assertAlmostEqual(gg.lerp(0, 10, 0.5), 5.0)
        self.assertAlmostEqual(gg.lerp(0, 10, 1.0), 10.0)


class TestCollision(unittest.TestCase):
    def test_circle_rect_collide(self):
        r = gg.pygame.Rect(10, 10, 10, 10)
        self.assertTrue(gg.circle_rect_collide(15, 15, 10, r))  # circle center inside rect
        self.assertFalse(gg.circle_rect_collide(0, 0, 5, r))    # far away
        # grazing the corner should count as a collision when distance <= radius
        self.assertTrue(gg.circle_rect_collide(10, 0, 10, r))


class TestGiraffe(unittest.TestCase):
    def test_head_and_top_positions(self):
        g = gg.Giraffe()
        expected_base_x = gg.WIDTH // 2
        expected_base_y = gg.GROUND_Y
        self.assertEqual(g.base_x, expected_base_x)
        self.assertEqual(g.base_y, expected_base_y)

        hx, hy = g.head_pos()
        tx, ty = g.top_pos()
        self.assertEqual(hx, expected_base_x)
        self.assertAlmostEqual(hy, expected_base_y - g.head_offset)
        self.assertEqual(tx, expected_base_x)
        self.assertAlmostEqual(ty, expected_base_y - g.neck)

    def test_update_movement_and_clamps(self):
        g = gg.Giraffe()
        start_x = g.base_x

        keys = {
            gg.pygame.K_LEFT: True,
            gg.pygame.K_a: False,
            gg.pygame.K_RIGHT: False,
            gg.pygame.K_d: False,
            gg.pygame.K_UP: True,
            gg.pygame.K_w: False,
            gg.pygame.K_DOWN: False,
            gg.pygame.K_s: False,
        }
        g.update(dt=1.0, keys=keys, move_speed=300.0, head_speed=400.0)
        self.assertLess(g.base_x, start_x)
        self.assertLessEqual(g.base_x, gg.WIDTH - 60)
        self.assertGreaterEqual(g.base_x, 60)
        self.assertLessEqual(g.head_offset, g.neck)

        keys[gg.pygame.K_LEFT] = False
        keys[gg.pygame.K_RIGHT] = True
        keys[gg.pygame.K_UP] = False
        keys[gg.pygame.K_DOWN] = True
        g.update(dt=10.0, keys=keys, move_speed=10_000.0, head_speed=10_000.0)
        self.assertEqual(g.base_x, gg.WIDTH - 60)
        self.assertGreaterEqual(g.head_offset, 20.0)
        self.assertLessEqual(g.head_offset, g.neck)

    def test_apply_neck_change_clamps(self):
        g = gg.Giraffe()
        # grow beyond cap
        g.apply_neck_change(10_000)
        self.assertEqual(g.neck, gg.NECK_CAP)
        # then shrink beyond min and ensure head_offset is also clamped within [20, neck]
        g.apply_neck_change(-10_000)
        self.assertEqual(g.neck, gg.NECK_MIN)
        self.assertGreaterEqual(g.head_offset, 20.0)
        self.assertLessEqual(g.head_offset, g.neck)
        self.assertEqual(g.head_offset, gg.NECK_MIN)  # since NECK_MIN=40 and min head clamp is 20, expect 40


class TestLeaf(unittest.TestCase):
    def test_leaf_rect_and_draw(self):
        leaf = gg.Leaf(x=100, y=200, rotten=True, fall_speed=120.0)
        leaf.w = 20
        leaf.h = 10
        leaf.angle = 0.0
        leaf.spin = 1.0
        rect = leaf.rect()

        self.assertEqual(rect.left, 90)
        self.assertEqual(rect.top, 195)
        self.assertEqual(rect.width, 20)
        self.assertEqual(rect.height, 10)

        surface = gg.pygame.display.set_mode((gg.WIDTH, gg.HEIGHT))
        leaf.draw(surface)

    def test_leaf_update_moves_down(self):
        leaf = gg.Leaf(x=50, y=0, rotten=False, fall_speed=100.0)
        # override randomized fall_speed for determinism
        leaf.fall_speed = 100.0
        leaf.spin = 2.0
        leaf.angle = 0.0
        y0 = leaf.y
        dt = 0.25
        leaf.update(dt)
        self.assertAlmostEqual(leaf.y, y0 + 100.0 * dt)
        self.assertAlmostEqual(leaf.angle, leaf.spin * dt, delta=0.0001)


if __name__ == "__main__":
    unittest.main()
