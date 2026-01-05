// ================= CONFIG =================
const SERVER_URL = "wss://python-tambola.onrender.com";

let ws = null;
let isHost = false;


// ================= SCREEN UTILITY =================
function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach(s =>
    s.classList.remove("active")
  );
  document.getElementById(screenId).classList.add("active");
}


// ================= CONNECT SOCKET =================
function connectSocket() {
  ws = new WebSocket(SERVER_URL);

  ws.onopen = () => {
    console.log("✅ WebSocket connected");
  };

  ws.onmessage = (event) => {
    console.log("📩 RAW:", event.data);

    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (e) {
      console.error("❌ Invalid JSON", e);
      return;
    }

    console.log("📦 PARSED:", msg);
    handleServerEvent(msg.type, msg.data);
  };

  ws.onerror = (err) => {
    console.error("❌ WebSocket error", err);
    alert("WebSocket connection failed");
  };

  ws.onclose = () => {
    console.warn("⚠️ WebSocket closed");
  };
}


// ================= HANDLE SERVER EVENTS =================
function handleServerEvent(type, data) {

  switch (type) {

    case "ROOM_CREATED":
      document.getElementById("room-id").innerText = data.room_id;
      isHost = true;
      showScreen("waiting-screen");
      break;

    case "PLAYER_JOINED":
      updatePlayerList(data.players);
      break;

    case "GAME_STARTED":
      showScreen("game-screen");
      break;

    case "NUMBER_DRAWN":
      document.getElementById("current-number").innerText = data.number;
      updateScores(data.scores);
      break;

    case "GAME_OVER":
      updateLeaderboard(data);
      showScreen("leaderboard-screen");
      break;

    default:
      console.warn("⚠️ Unknown event:", type);
  }
}


// ================= SEND TO SERVER =================
function send(type, data = {}) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert("Server not connected yet");
    console.error("❌ WebSocket not OPEN");
    return;
  }

  ws.send(JSON.stringify({ type, data }));
}


// ================= UI HELPERS =================
function updatePlayerList(players) {
  const ul = document.getElementById("player-list");
  ul.innerHTML = "";

  players.forEach(p => {
    const li = document.createElement("li");
    li.innerText = p;
    ul.appendChild(li);
  });
}

function updateScores(scores) {
  const ul = document.getElementById("score-list");
  ul.innerHTML = "";

  Object.entries(scores).forEach(([name, score]) => {
    const li = document.createElement("li");
    li.innerText = `${name}: ${score}`;
    ul.appendChild(li);
  });
}

function updateLeaderboard(leaderboard) {
  const ol = document.getElementById("leaderboard-list");
  ol.innerHTML = "";

  leaderboard.forEach(([name, score], index) => {
    const li = document.createElement("li");
    li.innerText = `${index + 1}. ${name} — ${score} pts`;
    ol.appendChild(li);
  });
}


// ================= BUTTON HANDLERS =================
document.addEventListener("DOMContentLoaded", () => {
  connectSocket();

  document.getElementById("create-room-btn").onclick = () => {
    const name = document.getElementById("player-name").value.trim();
    if (!name) return alert("Enter your name");

    send("CREATE_ROOM", { player_name: name });
  };

  document.getElementById("join-room-btn").onclick = () => {
    const name = document.getElementById("player-name").value.trim();
    const roomId = document.getElementById("room-input").value.trim();

    if (!name || !roomId) {
      return alert("Enter name & room ID");
    }

    send("JOIN_ROOM", {
      room_id: roomId,
      player_name: name
    });

    showScreen("waiting-screen");
  };

  document.getElementById("start-game-btn").onclick = () => {
    if (!isHost) {
      alert("Only host can start the game");
      return;
    }

    send("START_GAME");
  };

  document.getElementById("play-again-btn").onclick = () => {
    window.location.reload();
  };
});