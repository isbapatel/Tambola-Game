const SERVER_URL = "wss://python-tambola.onrender.com";
let ws = null;
let isHost = false;

// -------- SCREEN UTILITY --------
function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(screenId).classList.add('active');
}

// -------- CONNECT TO SERVER --------
function connectSocket() {
  ws = new WebSocket(SERVER_URL);

  ws.onopen = () => {
    console.log("Connected to server");
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleServerEvent(msg.type, msg.data);
  };

  ws.onerror = (e) => console.error("WebSocket error", e);
}

// -------- HANDLE SERVER EVENTS --------
function handleServerEvent(type, data) {

  if (type === "ROOM_CREATED") {
    document.getElementById("room-id").innerText = data.room_id;
    isHost = true;
    showScreen("waiting-screen");
  }

  if (type === "GAME_STARTED") {
    showScreen("game-screen");
  }

  if (type === "NUMBER_DRAWN") {
    document.getElementById("current-number").innerText = data.number;
    // Scores next step me update karenge
  }

  if (type === "GAME_OVER") {
    showScreen("leaderboard-screen");
  }
}

// -------- SEND TO SERVER --------
function send(type, data = {}) {
  ws.send(JSON.stringify({ type, data }));
}

// -------- BUTTON HANDLERS --------
document.addEventListener("DOMContentLoaded", () => {
  connectSocket();

  document.getElementById("create-room-btn").onclick = () => {
    const name = document.getElementById("player-name").value.trim();
    if (!name) return alert("Enter name");
    send("CREATE_ROOM", { player_name: name });
  };

  document.getElementById("join-room-btn").onclick = () => {
    const name = document.getElementById("player-name").value.trim();
    const roomId = document.getElementById("room-input").value.trim();
    if (!name || !roomId) return alert("Enter name & room ID");
    send("JOIN_ROOM", { room_id: roomId, player_name: name });
    showScreen("waiting-screen");
  };

  document.getElementById("start-game-btn").onclick = () => {
    if (!isHost) return;
    send("START_GAME");
  };
});
