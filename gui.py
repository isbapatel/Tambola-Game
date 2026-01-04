import tkinter as tk
from tkinter import messagebox
from tambola_game import TambolaGame
from player import Player

class TambolaGUI:
    def __init__(self, root, player_names):
        self.root = root
        self.root.title("Tambola Multiplayer")
        self.root.geometry("900x600")

        self.game = TambolaGame()
        self.players = [Player(name) for name in player_names]

        self.current_number = tk.StringVar(value="--")

        tk.Label(root, text="🎉 MULTIPLAYER TAMBOLA 🎉",
                 font=("Arial", 20, "bold")).pack(pady=10)

        tk.Label(root, textvariable=self.current_number,
                 font=("Arial", 36, "bold"),
                 fg="blue").pack()

        tk.Button(root, text="Draw Number",
                  font=("Arial", 14),
                  bg="orange", fg="white",
                  command=self.draw_number).pack(pady=10)

        self.board = tk.Frame(root)
        self.board.pack()

        self.player_cells = {}
        self.create_tickets()

    def create_tickets(self):
        for idx, player in enumerate(self.players):
            frame = tk.LabelFrame(
                self.board,
                text=player.name,
                font=("Arial", 12, "bold"),
                padx=10, pady=10
            )
            frame.grid(row=0, column=idx, padx=10)

            self.player_cells[player.name] = {}

            for r in range(3):
                for c in range(5):
                    num = player.ticket.rows[r][c]
                    lbl = tk.Label(
                        frame, text=str(num),
                        width=4, height=2,
                        font=("Arial", 12),
                        relief="solid", borderwidth=1
                    )
                    lbl.grid(row=r, column=c, padx=3, pady=3)
                    self.player_cells[player.name][num] = lbl

    def draw_number(self):
        number = self.game.draw()
        if number is None:
            messagebox.showinfo("Game Over", "No numbers left!")
            return

        self.current_number.set(number)

        for player in self.players:
            player.ticket.mark(number)

            if number in self.player_cells[player.name]:
                self.player_cells[player.name][number].config(bg="lightgreen")

            if not player.claims["row1"] and player.ticket.check_row(0):
                player.claims["row1"] = True
                messagebox.showinfo("Winner", f"{player.name} completed FIRST ROW")

            if not player.claims["row2"] and player.ticket.check_row(1):
                player.claims["row2"] = True
                messagebox.showinfo("Winner", f"{player.name} completed SECOND ROW")

            if not player.claims["row3"] and player.ticket.check_row(2):
                player.claims["row3"] = True
                messagebox.showinfo("Winner", f"{player.name} completed THIRD ROW")

            if not player.claims["full_house"] and player.ticket.full_house():
                player.claims["full_house"] = True
                messagebox.showinfo("🏆 FULL HOUSE 🏆",
                                    f"{player.name} WON THE GAME!")
                return
