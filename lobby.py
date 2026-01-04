import tkinter as tk
from tkinter import messagebox
from gui import TambolaGUI

class LobbyScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Tambola Lobby")
        self.root.geometry("400x400")

        tk.Label(root, text="🎉 Tambola Lobby 🎉",
                 font=("Arial", 20, "bold")).pack(pady=15)

        tk.Label(root, text="Number of Players",
                 font=("Arial", 12)).pack()

        self.count_entry = tk.Entry(root, font=("Arial", 14))
        self.count_entry.pack(pady=5)

        tk.Button(root, text="Next",
                  font=("Arial", 12),
                  bg="orange", fg="white",
                  command=self.next_step).pack(pady=10)

        self.name_entries = []

    def next_step(self):
        try:
            count = int(self.count_entry.get())
            if count < 1 or count > 4:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter 1–4 players")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Enter Player Names",
                 font=("Arial", 16, "bold")).pack(pady=10)

        for i in range(count):
            entry = tk.Entry(self.root, font=("Arial", 14))
            entry.pack(pady=5)
            self.name_entries.append(entry)

        tk.Button(self.root, text="Start Game",
                  font=("Arial", 14),
                  bg="green", fg="white",
                  command=self.start_game).pack(pady=15)

    def start_game(self):
        names = [e.get().strip() for e in self.name_entries]

        if any(not name for name in names):
            messagebox.showerror("Error", "All names required!")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        TambolaGUI(self.root, names)
