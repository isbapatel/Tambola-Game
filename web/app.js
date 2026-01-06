const WS_URL = "wss://python-tambola.onrender.com";
const socket = new WebSocket(WS_URL);

let isHost = false;
let myTicket = [];

/* SCREEN */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s =>
    s.classList.remove("active")
  );
  document.getElementById(id).classList.add("active");
}

/* TICKET */
function renderTicket(ticket) {
  myTicket = ticket;
  const ticketDiv = document.getElementById("ticket");
  ticketDiv.innerHTML = "";

  ticket.forEach((row, r) => {
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
        cell.onclick = () => cell.classList.toggle("marked");
      }
      rowDiv.appendChild(cell);
    });

    ticketDiv.appendChild(rowDiv);
  });
}

/* SOCKET */
socket.onmessage = (e) => {
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
    const number = data.number;
    document.getElementById("current-number").innerText = number;

    document.querySelectorAll(".ticket-cell").forEach(cell => {
      if (cell.dataset.number == number) {
        cell.classList.add("marked");
      }
    });
  }

  if (type === "SCORE_UPDATE") {
    const ul = document.getElementById("score-list");
    ul.innerHTML = "";
    Object.entries(data.scores).forEach(([p, s]) => {
      const li = document.createElement("li");
      li.innerText = `${p}: ${s}`;
      ul.appendChild(li);
    });
  }

  if (type === "CLAIM_RESULT") {
    alert(data.message);
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