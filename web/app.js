const WS_URL = "wss://python-tambola.onrender.com";
const socket = new WebSocket(WS_URL);

let isHost = false;

/* ---------- SCREEN ---------- */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s =>
    s.classList.remove("active")
  );
  document.getElementById(id).classList.add("active");
}

/* ---------- TICKET ---------- */
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
        cell.onclick = () => cell.classList.toggle("marked");
      }

      rowDiv.appendChild(cell);
    });

    ticketDiv.appendChild(rowDiv);
  });
}

/* ---------- SOCKET ---------- */
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
  }
}

/* ---------- BUTTONS ---------- */
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
  if (!name || !room) return alert("Enter all fields");

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