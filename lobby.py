import tkinter as tk
from tkinter import messagebox
from game_screen import GameScreen

class LobbyScreen:
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.is_host = False

        self.root.title("Tambola Lobby")
        self.root.geometry("420x420")

        tk.Label(root, text="Tambola Lobby", font=("Arial", 18)).pack(pady=10)

        tk.Label(root, text="Player Name").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        tk.Button(
            root, text="Create Room", width=20,
            command=self.create_room
        ).pack(pady=10)

        tk.Label(root, text="Room ID").pack(pady=(15, 0))
        self.room_entry = tk.Entry(root)
        self.room_entry.pack(pady=5)

        tk.Button(
            root, text="Join Room", width=20,
            command=self.join_room
        ).pack(pady=10)

        self.start_btn = tk.Button(
            root, text="Start Game", width=20,
            state=tk.DISABLED,
            command=self.start_game
        )
        self.start_btn.pack(pady=15)

        self.client.on("ROOM_CREATED", self.on_room_created)
        self.client.on("GAME_STARTED", self.on_game_started)
        self.client.on("ERROR", self.on_error)

    def create_room(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter player name")
            return
        self.client.send("CREATE_ROOM", {"player_name": name})

    def join_room(self):
        name = self.name_entry.get().strip()
        room_id = self.room_entry.get().strip().upper()
        if not name or not room_id:
            messagebox.showerror("Error", "Enter name and Room ID")
            return
        self.client.send("JOIN_ROOM", {
            "room_id": room_id,
            "player_name": name
        })

    def start_game(self):
        self.client.send("START_GAME")

    def on_room_created(self, data):
        self.is_host = True
        self.start_btn.config(state=tk.NORMAL)
        self.room_entry.delete(0, tk.END)
        self.room_entry.insert(0, data["room_id"])
        messagebox.showinfo(
            "Room Created",
            f"Room ID: {data['room_id']}"
        )

    def on_game_started(self, data):
        GameScreen(self.root, self.client, self.is_host)

    def on_error(self, data):
        messagebox.showerror("Error", data.get("message", "Unknown error"))
