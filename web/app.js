const WS_URL = "wss://python-tambola.onrender.com";
const socket = new WebSocket(WS_URL);

let isHost = false;

/* DEBUGiing*/
socket.onopen = () => console.log("WS connected");
socket.onerror = e => console.error(e);

/* SCREEN */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

/* TICKET */
function renderTicket(ticket) {
  const div = document.getElementById("ticket");
  div.innerHTML = "";

  ticket.forEach(row => {
    const r = document.createElement("div");
    r.className = "ticket-row";

    row.forEach(n => {
      const c = document.createElement("div");
      if (n === 0) {
        c.className = "ticket-cell empty";
      } else {
        c.className = "ticket-cell";
        c.innerText = n;
        c.dataset.number = n;
      }
      r.appendChild(c);
    });
    div.appendChild(r);
  });
}

/* SOCKET EVENTS */
socket.onmessage = e => {
  const { type, data } = JSON.parse(e.data);

  if (type === "ROOM_CREATED") {
    document.getElementById("room-id").innerText = data.room_id;
    isHost = true;
    showScreen("waiting-screen");
  }

  if (type === "PLAYERS_UPDATE") {
    const ul = document.getElementById("players-list");
    ul.innerHTML = "";
    data.players.forEach(p => {
      const li = document.createElement("li");
      li.innerText = p;
      ul.appendChild(li);
    });
  }

  if (type === "TICKET_ASSIGNED") renderTicket(data.ticket);

  if (type === "GAME_STARTED") {
    showScreen("game-screen");
    if (isHost) document.getElementById("draw-btn").style.display = "block";
  }

  if (type === "NUMBER_DRAWN") {
    document.getElementById("current-number").innerText = data.number;
    document.querySelectorAll(".ticket-cell").forEach(c => {
      if (c.dataset.number == data.number) c.classList.add("marked");
    });
  }

  if (type === "SCORE_UPDATE") {
    const ul = document.getElementById("score-list");
    ul.innerHTML = "";
    Object.entries(data.scores).forEach(([p,s]) => {
      const li = document.createElement("li");
      li.innerText = `${p}: ${s}`;
      ul.appendChild(li);
    });
  }

  if (type === "CLAIM_RESULT") alert(data.message);

  if (type === "GAME_ENDED") {
    const ol = document.getElementById("leaderboard-list");
    ol.innerHTML = "";
    data.leaderboard.forEach(p => {
      const li = document.createElement("li");
      li.innerText = `${p.name} - ${p.score}`;
      ol.appendChild(li);
    });
    showScreen("leaderboard-screen");
  }
};

/* BUTTONS */
document.getElementById("create-room-btn").onclick = () => {
  const n = document.getElementById("player-name").value.trim();
  if (!n) return alert("Enter name");
  socket.send(JSON.stringify({ type:"CREATE_ROOM", data:{player_name:n} }));
};

document.getElementById("join-room-btn").onclick = () => {
  const n = document.getElementById("player-name").value.trim();
  const r = document.getElementById("room-input").value.trim();
  if (!n || !r) return alert("Fill all");
  socket.send(JSON.stringify({ type:"JOIN_ROOM", data:{player_name:n, room_id:r} }));
  showScreen("waiting-screen");
};

document.getElementById("start-game-btn").onclick = () => {
  if (isHost) socket.send(JSON.stringify({ type:"START_GAME" }));
};

document.getElementById("draw-btn").onclick = () => {
  socket.send(JSON.stringify({ type:"DRAW_NUMBER" }));
};

document.getElementById("claim-line-btn").onclick = () => {
  socket.send(JSON.stringify({ type:"CLAIM_LINE" }));
};

document.getElementById("claim-tambola-btn").onclick = () => {
  socket.send(JSON.stringify({ type:"CLAIM_TAMBOLA" }));
};