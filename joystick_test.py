#!/usr/bin/env python3
"""Test graphique d'un joystick d'arcade relie aux GPIO."""

import argparse
from contextlib import ExitStack
import signal
import sys
import tkinter as tk


PINS = {"haut": 19, "bas": 13, "gauche": 5, "droite": 6}
POSITIONS = (
    ("haut-gauche", "haut", "haut-droite"),
    ("gauche", "centre", "droite"),
    ("bas-gauche", "bas", "bas-droite"),
)


def position_from_states(states):
    """Return a grid position, or None for contradictory switch states."""
    if (states["haut"] and states["bas"]) or (
        states["gauche"] and states["droite"]
    ):
        return None
    vertical = "haut" if states["haut"] else "bas" if states["bas"] else ""
    horizontal = (
        "gauche" if states["gauche"] else "droite" if states["droite"] else ""
    )
    return "-".join(part for part in (vertical, horizontal) if part) or "centre"


class JoystickView:
    def __init__(self, root, read_states):
        self.root = root
        self.read_states = read_states
        self.stopping = False
        root.title("Test du joystick")
        root.configure(bg="#101827")
        root.attributes("-fullscreen", True)

        title = tk.Label(
            root, text="TEST JOYSTICK", bg="#101827", fg="#f8fafc",
            font=("Helvetica", 20, "bold"),
        )
        title.pack(pady=(18, 8))

        grid = tk.Frame(root, bg="#101827")
        grid.pack(fill="both", expand=True, padx=16, pady=8)
        self.cells = {}
        for row, positions in enumerate(POSITIONS):
            grid.rowconfigure(row, weight=1, uniform="row")
            for column, name in enumerate(positions):
                grid.columnconfigure(column, weight=1, uniform="column")
                cell = tk.Label(
                    grid, text=name.replace("-", "\n").upper(),
                    bg="#293548", fg="#e2e8f0", font=("Helvetica", 12, "bold"),
                    relief="flat",
                )
                cell.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
                self.cells[name] = cell

        self.status = tk.Label(
            root, bg="#101827", fg="#f8fafc", font=("Helvetica", 14, "bold"),
            wraplength=360,
        )
        self.status.pack(fill="x", padx=12, pady=(8, 4))
        self.raw = tk.Label(
            root, bg="#101827", fg="#cbd5e1", font=("Helvetica", 10),
            wraplength=360,
        )
        self.raw.pack(fill="x", padx=12, pady=(0, 18))
        root.protocol("WM_DELETE_WINDOW", self.stop)
        root.bind("<Escape>", lambda event: self.stop())

    def stop(self):
        self.stopping = True

    def update(self):
        if self.stopping:
            self.root.destroy()
            return
        states = self.read_states()
        position = position_from_states(states)
        for name, cell in self.cells.items():
            active = name == position
            cell.configure(bg="#22c55e" if active else "#293548",
                           fg="#052e16" if active else "#e2e8f0")
        if position is None:
            self.status.configure(text="DIRECTIONS CONTRADICTOIRES", fg="#f87171")
        else:
            self.status.configure(
                text="Position : " + position.replace("-", " ").upper(),
                fg="#f8fafc",
            )
        pressed = [name for name, active in states.items() if active]
        self.raw.configure(text="Contacts : " + (", ".join(pressed) if pressed else "aucun"))
        self.root.after(50, self.update)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--simulation", action="store_true",
        help="utiliser les fleches du clavier au lieu des GPIO",
    )
    args = parser.parse_args()

    with ExitStack() as stack:
        if args.simulation:
            states = dict.fromkeys(PINS, False)

            def read_states():
                return states.copy()
        else:
            try:
                from gpiozero import Button
            except ImportError:
                print("Installez python3-gpiozero sur le Raspberry Pi.", file=sys.stderr)
                return 1
            buttons = {}
            for name, pin in PINS.items():
                buttons[name] = stack.enter_context(Button(pin, pull_up=True))

            def read_states():
                return {name: button.is_pressed for name, button in buttons.items()}

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            print("Impossible d'ouvrir l'ecran graphique : {}".format(exc), file=sys.stderr)
            return 1
        view = JoystickView(root, read_states)
        if args.simulation:
            keys = {"Up": "haut", "Down": "bas", "Left": "gauche", "Right": "droite"}
            for key, name in keys.items():
                root.bind("<KeyPress-{}>".format(key),
                          lambda event, direction=name: states.__setitem__(direction, True))
                root.bind("<KeyRelease-{}>".format(key),
                          lambda event, direction=name: states.__setitem__(direction, False))
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous = signal.signal(signum, lambda _signum, _frame: view.stop())
            stack.callback(signal.signal, signum, previous)
        view.update()
        root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
