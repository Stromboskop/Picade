import itertools
import unittest
from unittest.mock import Mock

from joystick_test import JoystickView, PINS, position_from_states


class PositionTests(unittest.TestCase):
    def test_rotated_wiring(self):
        cases = (
            ((5,), "gauche"),
            ((6,), "droite"),
            ((13,), "bas"),
            ((19,), "haut"),
            ((5, 19), "haut-gauche"),
            ((19, 6), "haut-droite"),
            ((13, 5), "bas-gauche"),
            ((6, 13), "bas-droite"),
            ((), "centre"),
        )
        for active_pins, expected in cases:
            states = {name: pin in active_pins for name, pin in PINS.items()}
            with self.subTest(active_pins=active_pins):
                self.assertEqual(position_from_states(states), expected)

    def test_all_switch_combinations(self):
        expected = {
            (): "centre",
            ("haut",): "haut",
            ("bas",): "bas",
            ("gauche",): "gauche",
            ("droite",): "droite",
            ("haut", "gauche"): "haut-gauche",
            ("haut", "droite"): "haut-droite",
            ("bas", "gauche"): "bas-gauche",
            ("bas", "droite"): "bas-droite",
        }
        for values in itertools.product((False, True), repeat=4):
            states = dict(zip(PINS, values))
            pressed = tuple(name for name, active in states.items() if active)
            with self.subTest(pressed=pressed):
                self.assertEqual(position_from_states(states), expected.get(pressed))

    def test_view_highlights_one_position_or_none_for_invalid_input(self):
        view = JoystickView.__new__(JoystickView)
        view.root = Mock()
        view.cells = {name: Mock() for row in (
            ("haut-gauche", "haut", "haut-droite"),
            ("gauche", "centre", "droite"),
            ("bas-gauche", "bas", "bas-droite"),
        ) for name in row}
        view.status = Mock()
        view.raw = Mock()
        view.stopping = False
        states = dict.fromkeys(PINS, False)
        view.read_states = lambda: states.copy()
        for pressed, expected in (
            ((), "centre"), (("haut", "droite"), "haut-droite"),
            (("haut", "bas"), None),
        ):
            states.update({name: name in pressed for name in PINS})
            view.update()
            active = [
                name for name, cell in view.cells.items()
                if cell.configure.call_args.kwargs["bg"] == "#22c55e"
            ]
            self.assertEqual(active, [expected] if expected else [])
        self.assertIn("CONTRADICTOIRES", view.status.configure.call_args.kwargs["text"])

    def test_stop_destroys_window_without_scheduling_more_updates(self):
        view = JoystickView.__new__(JoystickView)
        view.root = Mock()
        view.stopping = True
        view.update()
        view.root.destroy.assert_called_once_with()
        view.root.after.assert_not_called()


if __name__ == "__main__":
    unittest.main()
