import subprocess
import threading
import queue
import time
from typing import Optional, List, Callable
import os

from common.base import GameEngine

class LibreBlackjackAdapter(GameEngine):
    def __init__(self, executable_path: str = "./blackjack"):
        self.executable_path = executable_path
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None
        self._error_thread: Optional[threading.Thread] = None
        self.on_message: Optional[Callable[[str], None]] = None

    def start(self, args: Optional[List[str]] = None, cwd: Optional[str] = None):
        if self.process:
            self.stop()

        cmd = [self.executable_path]
        if args:
            cmd.extend(args)

        # Ensure we are in the right directory or provide full path
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line buffered
            env=os.environ.copy(),
            cwd=cwd
        )

        self._stop_event.clear()
        self._reader_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader_thread.start()
        self._error_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._error_thread.start()

    def stop(self):
        self._stop_event.set()
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def send_command(self, command: str):
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()

    def _read_stdout(self):
        while not self._stop_event.is_set() and self.process:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line:
                if self.on_message:
                    self.on_message(line)
                self.output_queue.put(line)

    def _read_stderr(self):
        while not self._stop_event.is_set() and self.process:
            line = self.process.stderr.readline()
            if not line:
                break
            line = line.strip()
            if line:
                # Stderr often contains the report or progress
                self.error_queue.put(line)

    def get_next_message(self, timeout: float = 0.1) -> Optional[str]:
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
