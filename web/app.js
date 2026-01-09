const WS_URL = "wss://python-tambola.onrender.com";
const socket = new WebSocket(WS_URL);

let isHost = false;
let marked = new Set();
let ticketFlat = [];

/* Screen handling */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

/* Ticket render */
function renderTicket(ticket) {
  const div = document.getElementById("ticket");
  div.innerHTML = "";
  marked.clear();
  ticketFlat = [];

  ticket.forEach(row => {
    const r = document.createElement("div");
    r.className = "ticket-row";

    row.forEach(n => {
      const c = document.createElement("div");
      c.className = "ticket-cell";
      c.innerText = n;
      c.dataset.number = n;
      ticketFlat.push(n);
      r.appendChild(c);
    });

    div.appendChild(r);
  });
}

/* Claim logic */
function claim(type) {
  let valid = false;

  const rows = [
    ticketFlat.slice(0,5),
    ticketFlat.slice(5,10),
    ticketFlat.slice(10,15)
  ];

  if (type === "QUICK_5") valid = marked.size >= 5;

  if (type === "FOUR_CORNERS") {
    valid = [
      rows[0][0], rows[0][4],
      rows[2][0], rows[2][4]
    ].every(n => marked.has(n));
  }

  if (type === "FIRST_LINE") valid = rows[0].every(n => marked.has(n));
  if (type === "SECOND_LINE") valid = rows[1].every(n => marked.has(n));
  if (type === "THIRD_LINE") valid = rows[2].every(n => marked.has(n));
  if (type === "TAMBOLA") valid = ticketFlat.every(n => marked.has(n));

  if (!valid) return alert("❌ Invalid Claim");

  socket.send(JSON.stringify({
    type: "MAKE_CLAIM",
    data: { claim: type }
  }));
}

/* WebSocket events */
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

  if (type === "GAME_STARTED") showScreen("game-screen");

  if (type === "NUMBER_DRAWN") {
    document.getElementById("current-number").innerText = data.number;
    document.querySelectorAll(".ticket-cell").forEach(c => {
      if (c.dataset.number == data.number) {
        c.classList.add("marked");
        marked.add(Number(c.dataset.number));
      }
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

/* Buttons */
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
