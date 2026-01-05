const WS_URL = "wss://python-tambola.onrender.com";
let socket = new WebSocket(WS_URL);
let isHost = false;

// ---------------- SCREEN ----------------

function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s =>
    s.classList.remove("active")
  );
  document.getElementById(id).classList.add("active");
}

// ---------------- SOCKET ----------------

socket.onopen = () => {
  console.log("WebSocket connected");
};

socket.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  handleEvent(msg.type, msg.data);
};

// ---------------- EVENTS ----------------

function handleEvent(type, data) {

  if (type === "ROOM_CREATED") {
    document.getElementById("room-id").innerText = data.room_id;
    isHost = true;
    showScreen("waiting-screen");
  }

  if (type === "PLAYER_LIST") {
    const ul = document.getElementById("players-list");
    ul.innerHTML = "";
    data.players.forEach(p => {
      const li = document.createElement("li");
      li.innerText = p;
      ul.appendChild(li);
    });
  }

  if (type === "TICKET_ASSIGNED") {
    renderTicket(data.ticket);
  }

  if (type === "NUMBER_DRAWN") {
    document.getElementById("current-number").innerText = data.number;
    updateScores(data.scores);
  }

  if (type === "GAME_OVER") {
    const ul = document.getElementById("leaderboard");
    ul.innerHTML = "";
    data.leaderboard.forEach(p => {
      const li = document.createElement("li");
      li.innerText = `${p.name} : ${p.score}`;
      ul.appendChild(li);
    });
    showScreen("leaderboard-screen");
  }
}

// ---------------- UI HELPERS ----------------

function renderTicket(ticket) {
  const box = document.getElementById("ticket-box");
  box.innerHTML = "";
  ticket.forEach(n => {
    const span = document.createElement("span");
    span.innerText = n;
    box.appendChild(span);
  });
}

function updateScores(scores) {
  const ul = document.getElementById("score-list");
  ul.innerHTML = "";
  for (const p in scores) {
    const li = document.createElement("li");
    li.innerText = `${p}: ${scores[p]}`;
    ul.appendChild(li);
  }
}

// ---------------- BUTTONS ----------------

document.getElementById("create-room-btn").onclick = () => {
  const name = document.getElementById("player-name").value.trim();
  if (!name) return alert("Enter name");

  socket.send(JSON.stringify({
    type: "CREATE_ROOM",
    data: { player_name: name }
  }));
};

document.getElementById("join-room-btn").onclick = () => {
  const name = document.getElementById("player-name").value.trim();
  const room = document.getElementById("room-input").value.trim();
  if (!name || !room) return alert("Missing");

  socket.send(JSON.stringify({
    type: "JOIN_ROOM",
    data: { player_name: name, room_id: room }
  }));

  showScreen("waiting-screen");
};

document.getElementById("start-game-btn").onclick = () => {
  if (!isHost) return;
  socket.send(JSON.stringify({ type: "START_GAME" }));
};