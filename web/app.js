const WS_URL = "wss://python-tambola.onrender.com";
const socket = new WebSocket(WS_URL);

let isHost = false;

/* SCREEN */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s =>
    s.classList.remove("active")
  );
  document.getElementById(id).classList.add("active");
}

/* TICKET */
function renderTicket(ticket) {
  const ticketDiv = document.getElementById("ticket");
  ticketDiv.innerHTML = "";

  ticket.forEach(row => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "ticket-row";

    row.forEach(num => {
      const cell = document.createElement("div");

      if (num === 0) {
        cell.className = "ticket-cell empty";
      } else {
        cell.className = "ticket-cell";
        cell.innerText = num;
        cell.dataset.number = num;
      }
      rowDiv.appendChild(cell);
    });
    ticketDiv.appendChild(rowDiv);
  });
}

/* SOCKET */
socket.onmessage = e => {
  const msg = JSON.parse(e.data);
  handleEvent(msg.type, msg.data);
};

function handleEvent(type, data) {

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

  if (type === "TICKET_ASSIGNED") {
    renderTicket(data.ticket);
  }

  if (type === "GAME_STARTED") {
    showScreen("game-screen");
    if (isHost) document.getElementById("draw-btn").style.display = "block";
  }

  if (type === "NUMBER_DRAWN") {
    document.getElementById("current-number").innerText = data.number;
    document.querySelectorAll(".ticket-cell").forEach(cell => {
      if (cell.dataset.number == data.number) {
        cell.classList.add("marked");
      }
    });
  }

  if (type === "SCORE_UPDATE") {
    const ul = document.getElementById("score-list");
    ul.innerHTML = "";
    Object.entries(data.scores).forEach(([p,s])=>{
      const li = document.createElement("li");
      li.innerText = `${p}: ${s}`;
      ul.appendChild(li);
    });
  }

  if (type === "GAME_ENDED") {
    const list = document.getElementById("leaderboard-list");
    list.innerHTML = "";

    data.leaderboard.forEach(p => {
      const li = document.createElement("li");
      li.innerText = `${p.name} — ${p.score}`;
      list.appendChild(li);
    });

    showScreen("leaderboard-screen");
  }
}

/* BUTTONS */
document.getElementById("draw-btn").onclick = () => {
  socket.send(JSON.stringify({ type: "DRAW_NUMBER" }));
};

document.getElementById("claim-line-btn").onclick = () => {
  socket.send(JSON.stringify({ type: "CLAIM_LINE" }));
};

document.getElementById("claim-tambola-btn").onclick = () => {
  socket.send(JSON.stringify({ type: "CLAIM_TAMBOLA" }));
};