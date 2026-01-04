import tkinter as tk
from tkinter import messagebox
from ticket import Ticket
import time


class GameScreen:
    GAME_DURATION = 180  # seconds (3 minutes)

    def __init__(self, root, client, is_host):
        self.root = root
        self.client = client
        self.is_host = is_host
        self.ticket = Ticket()

        self.start_time = time.time()
        self.game_running = True

        # ---------------- WINDOW ----------------
        self.window = tk.Toplevel(root)
        self.window.title("Tambola Game")
        self.window.geometry("600x740")
        self.window.resizable(False, False)

        # ---------------- TIMER ----------------
        self.timer_label = tk.Label(
            self.window,
            text="03:00",
            font=("Arial", 18, "bold"),
            fg="red"
        )
        self.timer_label.pack(pady=5)

        # ---------------- NUMBER DISPLAY ----------------
        self.number_label = tk.Label(
            self.window, text="--", font=("Arial", 36, "bold")
        )
        self.number_label.pack(pady=10)

        # ---------------- TICKET ----------------
        self.ticket_frame = tk.Frame(self.window)
        self.ticket_frame.pack(pady=15)

        self.cells = {}
        for r in range(3):
            for c in range(5):
                num = self.ticket.rows[r][c]
                lbl = tk.Label(
                    self.ticket_frame,
                    text=str(num),
                    width=6,
                    height=2,
                    font=("Arial", 12),
                    relief="ridge",
                    bg="white"
                )
                lbl.grid(row=r, column=c, padx=5, pady=5)
                self.cells[num] = lbl

        # ---------------- SCOREBOARD ----------------
        tk.Label(
            self.window,
            text="Live Scores",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.score_box = tk.Label(
            self.window,
            text="Waiting for scores...",
            font=("Arial", 12),
            justify="left"
        )
        self.score_box.pack()

        # ---------------- SOCKET EVENTS ----------------
        self.client.on("NUMBER_DRAWN", self.on_number_drawn)
        self.client.on("GAME_OVER", self.on_game_over)

        # Start countdown
        self.update_timer()

    # ---------------- TIMER ----------------
    def update_timer(self):
        if not self.game_running:
            return

        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.GAME_DURATION - elapsed)

        mins = remaining // 60
        secs = remaining % 60

        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

        if remaining > 0:
            self.window.after(1000, self.update_timer)

    # ---------------- SOCKET HANDLERS ----------------
    def on_number_drawn(self, data):
        number = data["number"]
        scores = data["scores"]

        self.ticket.mark(number)
        self.number_label.config(text=str(number))

        if number in self.cells:
            self.cells[number].config(bg="lightgreen")

        score_text = ""
        for player, score in scores.items():
            score_text += f"{player}: {score} pts\n"

        self.score_box.config(text=score_text)

    def on_game_over(self, data):
        self.game_running = False

        leaderboard = data["leaderboard"]
        text = "🏆 FINAL LEADERBOARD 🏆\n\n"

        medals = ["🥇", "🥈", "🥉"]
        for i, (player, score) in enumerate(leaderboard):
            prefix = medals[i] if i < 3 else ""
            text += f"{prefix} {player} — {score} pts\n"

        messagebox.showinfo("Game Over", text)
        self.window.destroy()
