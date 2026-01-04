import tkinter as tk
from lobby import LobbyScreen
from client_adapter import TambolaClient

SERVER_URI = "ws://localhost:8765"

def main():
    root = tk.Tk()

    client = TambolaClient(SERVER_URI)
    client.connect()

    LobbyScreen(root, client)
    root.mainloop()

if __name__ == "__main__":
    main()
