const loginPanel = document.getElementById("login-panel");
const chatPanel = document.getElementById("chat-panel");
const topUser = document.getElementById("top-user");
const userName = document.getElementById("user-name");
const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
const logoutBtn = document.getElementById("logout-btn");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("message-input");
const messagesEl = document.getElementById("messages");

let currentUser = null;
let pollTimer = null;

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "same-origin",
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || "Ошибка запроса");
  }
  return data;
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function renderMessages(messages) {
  if (!messages.length) {
    messagesEl.innerHTML = `<p class="empty-chat">Пока тихо. Напишите первое сообщение.</p>`;
    return;
  }

  const nearBottom =
    messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 80;

  messagesEl.innerHTML = messages
    .map((msg) => {
      const mine = currentUser && msg.login === currentUser.login;
      return `
        <article class="msg ${mine ? "is-mine" : ""}">
          <div class="msg-meta">
            <span>${escapeHtml(msg.author)}</span>
            <span>${formatTime(msg.createdAt)}</span>
          </div>
          <div class="msg-text">${escapeHtml(msg.text)}</div>
        </article>
      `;
    })
    .join("");

  if (nearBottom) {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function showLogin() {
  currentUser = null;
  loginPanel.hidden = false;
  chatPanel.hidden = true;
  topUser.hidden = true;
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function showChat(user) {
  currentUser = user;
  loginPanel.hidden = true;
  chatPanel.hidden = false;
  topUser.hidden = false;
  userName.textContent = user.name;
  loadMessages();
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(loadMessages, 3000);
}

async function loadMessages() {
  try {
    const data = await api("/api/messages");
    renderMessages(data.messages || []);
  } catch {
    showLogin();
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.hidden = true;
  const form = new FormData(loginForm);
  try {
    const data = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({
        login: form.get("login"),
        password: form.get("password"),
      }),
    });
    showChat(data.user);
  } catch (err) {
    loginError.textContent = err.message;
    loginError.hidden = false;
  }
});

logoutBtn.addEventListener("click", async () => {
  await api("/api/logout", { method: "POST", body: "{}" });
  showLogin();
});

composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = "";
  try {
    await api("/api/messages", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    await loadMessages();
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } catch (err) {
    messageInput.value = text;
    alert(err.message);
  }
});

api("/api/me")
  .then((data) => {
    if (data.user) showChat(data.user);
    else showLogin();
  })
  .catch(showLogin);
