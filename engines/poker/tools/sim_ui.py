"""Tkinter-based UI for running poker simulations and choosing strategies."""

import math
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from agents.agent_random import Player as RandomPlayer
from agents.agent_strong_hand import Player as StrongHandPlayer
from agents.agent_pro import Player as ProPlayer
from gym_env.env import HoldemTable

AGENT_TYPES = {
    "Random": RandomPlayer,
    "StrongHand": StrongHandPlayer,
    "Pro": ProPlayer,
}
UV_BINARY = shutil.which("uv")


class PokerUI:
    """Simple poker control panel with a table view and strategy selectors."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Neuron Poker Control Panel")
        self.root.geometry("800x600")
        self._create_widgets()
        self.last_env = None
        self.uv_process = None
        self.uv_launching = False
        self.hands_running = False

    def _create_widgets(self):
        control_frame = ttk.Frame(self.root, padding=8)
        control_frame.grid(row=0, column=0, sticky="nsew")
        table_frame = ttk.Frame(self.root, padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        log_frame = ttk.Frame(self.root, padding=8)
        log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        self.player1_label = ttk.Label(control_frame, text="Player 1 Strategy:")
        self.player1_label.grid(row=0, column=0, sticky="w")
        self.player1_var = tk.StringVar(value="StrongHand")
        self.player1_combo = ttk.Combobox(control_frame, values=list(AGENT_TYPES), textvariable=self.player1_var,
                                           state="readonly")
        self.player1_combo.grid(row=0, column=1, sticky="ew")

        self.player2_label = ttk.Label(control_frame, text="Player 2 Strategy:")
        self.player2_label.grid(row=1, column=0, sticky="w")
        self.player2_var = tk.StringVar(value="Random")
        self.player2_combo = ttk.Combobox(control_frame, values=list(AGENT_TYPES), textvariable=self.player2_var,
                                           state="readonly")
        self.player2_combo.grid(row=1, column=1, sticky="ew")

        self.count_label = ttk.Label(control_frame, text="Hands:")
        self.count_label.grid(row=2, column=0, sticky="w")
        self.hands_var = tk.IntVar(value=400)
        self.hands_entry = ttk.Entry(control_frame, textvariable=self.hands_var, width=8)
        self.hands_entry.grid(row=2, column=1, sticky="w")

        self.run_button = ttk.Button(control_frame, text="Run Simulation", command=self._run_hands_async)
        self.run_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        self.test_button = ttk.Button(control_frame, text="Run Mode Tests", command=self._run_tests_async)
        self.test_button.grid(row=4, column=0, columnspan=2, pady=4, sticky="ew")

        self.uv_button = ttk.Button(control_frame, text="Launch External Run (uv)", command=self._launch_uv_render_async)
        self.uv_button.grid(row=5, column=0, columnspan=2, pady=4, sticky="ew")

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(control_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=2, pady=10)

        self.canvas = tk.Canvas(table_frame, width=300, height=300, bg="#2d5a27")
        self.canvas.pack(fill="both", expand=True)
        self.table_cards_var = tk.StringVar()
        ttk.Label(table_frame, textvariable=self.table_cards_var).pack(pady=4)

        self.log_widget = ScrolledText(log_frame, height=10, state="disabled")
        self.log_widget.pack(fill="both", expand=True)

    def _run_tests_async(self):
        def runner():
            self._set_status("Running smoke tests...")
            cmd = [sys.executable, "-m", "pytest", "tests/test_simulation.py"]
            try:
                completed = subprocess.run(cmd, check=False)
                result = "passed" if completed.returncode == 0 else f"failed ({completed.returncode})"
                self._append_log(f"[tests] {result}")
            except Exception as exc:
                self._append_log(f"[tests] error: {exc}")
            self._set_status("Idle")

        threading.Thread(target=runner, daemon=True).start()

    def _run_hands_async(self):
        if self.hands_running:
            self._append_log("[hands] already running")
            return
        count = self._get_run_count(prefix="[hands]")
        if count is None:
            return
        strategy_one = self.player1_var.get()
        strategy_two = self.player2_var.get()
        self.hands_running = True
        self.run_button.configure(state="disabled")
        self._set_status(f"Running {count} hand(s)...")
        self._append_log(f"[hands] start poker: {strategy_one} vs {strategy_two}, count={count}")
        self._run_next_hand(1, count, strategy_one, strategy_two)

    def _run_next_hand(self, index, count, strategy_one, strategy_two):
        try:
            env = self._build_env(strategy_one, strategy_two)
            env.reset()
            self.last_env = env
            stacks = [player.stack for player in env.players]
            table = env.table_cards.copy() if env.table_cards else []
            written = f"[hand {index}] {strategy_one} vs {strategy_two} winner={env.winner_ix}, stacks={stacks}, table={table}"
            self._append_log(written)
            self._update_table(env)
        except Exception as exc:  # pylint: disable=broad-except
            self._append_log(f"[hands] error on hand {index}: {exc}")
            self._finish_hands_run()
            return

        if index >= count:
            self._finish_hands_run()
            return

        self.root.after(10, lambda: self._run_next_hand(index + 1, count, strategy_one, strategy_two))

    def _finish_hands_run(self):
        def finish():
            self.hands_running = False
            self.run_button.configure(state="normal")
            self.status_var.set("Idle")
            self.log_widget.configure(state="normal")
            self.log_widget.insert("end", "[hands] done\n")
            self.log_widget.configure(state="disabled")
            self.log_widget.yview_moveto(1.0)

        self.root.after(0, finish)

    def _launch_uv_render_async(self):
        if self.uv_launching:
            self._append_log("[uv] launch already in progress; please wait")
            return
        self.uv_launching = True
        
        running_proc = self._get_running_uv_process()
        if running_proc is not None:
            self._append_log(
                f"[uv] external run active (pid={running_proc.pid}); stopping and restarting"
            )
            running_proc.terminate()
            running_proc.wait()

        if not UV_BINARY:
            self._append_log("[uv] command not found in PATH")
            self.uv_launching = False
            return

        strategy_one = self.player1_var.get()
        strategy_two = self.player2_var.get()
        run_count = self._get_run_count(prefix="[uv]")
        if run_count is None:
            self.uv_launching = False
            return

        def runner():
            self._set_status("Launching uv render...")
            self._set_uv_controls(running=True)
            cmd = [
                UV_BINARY,
                "run",
                "python",
                "tools/render_match.py",
                "--player1",
                strategy_one,
                "--player2",
                strategy_two,
                "--max-hands",
                str(run_count),
            ]
            self._append_log("[uv] poker mode selected: a render window should open")
            self._append_log(f"[uv] {' '.join(cmd)}")
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self.uv_process = proc
                self._append_log(f"[uv] started pid={proc.pid}")
                for line in proc.stdout:
                    rendered = f"[uv] {line.rstrip()}"
                    self._append_log(rendered)
                proc.wait()
                self._append_log(f"[uv] exited ({proc.returncode})")
            except Exception as exc:
                self._append_log(f"[uv] error: {exc}")
            finally:
                self.uv_process = None
                self.uv_launching = False
                self._set_uv_controls(running=False)
                self._set_status("Idle")

        threading.Thread(target=runner, daemon=True).start()

    def _set_uv_controls(self, running: bool):
        state = "disabled" if running else "normal"
        self.root.after(0, lambda: self.uv_button.configure(state=state))

    def _build_env(self, strategy_one: str, strategy_two: str) -> HoldemTable:
        env = HoldemTable(initial_stacks=100, render=False, funds_plot=False, max_hands=1)
        for selection in (strategy_one, strategy_two):
            cls = AGENT_TYPES.get(selection, RandomPlayer)
            env.add_player(cls(name=selection))
        return env

    def _update_table(self, env: HoldemTable):
        self.canvas.delete("all")
        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        center_x = width / 2
        center_y = height / 2
        radius = min(center_x, center_y) - 40
        self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                                fill="#2d5a27", outline="white", width=2)
        for idx, player in enumerate(env.players):
            angle = math.radians(90 - idx * 360 / len(env.players))
            px = center_x + radius * math.cos(angle)
            py = center_y - radius * math.sin(angle)
            self.canvas.create_oval(px - 20, py - 20, px + 20, py + 20, fill="white", outline="black")
            info = f"{player.name}\n${player.stack:.1f}"
            self.canvas.create_text(px, py, text=info, fill="black", font=("Helvetica", 8), justify="center")
        table_cards = env.table_cards or []
        self.table_cards_var.set("Table: " + " ".join(table_cards))

    def _append_log(self, message: str):
        def write():
            self.log_widget.configure(state="normal")
            self.log_widget.insert("end", message + "\n")
            self.log_widget.configure(state="disabled")
            self.log_widget.yview_moveto(1.0)

        self.root.after(0, write)

    def _set_status(self, text: str):
        self.root.after(0, lambda: self.status_var.set(text))

    def _get_run_count(self, prefix: str) -> int | None:
        try:
            return max(1, int(self.hands_var.get()))
        except (ValueError, tk.TclError):
            self._append_log(f"{prefix} invalid Hands value")
            self._set_status("Idle")
            return None

    def _get_running_uv_process(self):
        proc = self.uv_process
        if proc is None:
            return None
        if proc.poll() is not None:
            self.uv_process = None
            return None
        return proc

    def run(self):
        self.root.mainloop()


def main():
    try:
        PokerUI().run()
    except tk.TclError as exc:
        print(f"UI startup failed: {exc}")
        print("Run this from a desktop session with a valid DISPLAY (or over SSH with X11 forwarding).")


if __name__ == "__main__":
    main()
