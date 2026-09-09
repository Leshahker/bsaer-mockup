const USERS = {
  admin: { password: "admin", name: "Администратор", role: "admin" },
  doktor: { password: "doktor", name: "Демо-врач", role: "member" },
};

const STORAGE_USER = "boar-demo-user";
const STORAGE_MESSAGES = "boar-demo-messages";

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

function loadMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_MESSAGES);
    const data = raw ? JSON.parse(raw) : [];
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function saveMessages(messages) {
  localStorage.setItem(STORAGE_MESSAGES, JSON.stringify(messages));
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

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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

function showLogin() {
  currentUser = null;
  localStorage.removeItem(STORAGE_USER);
  loginPanel.hidden = false;
  chatPanel.hidden = true;
  topUser.hidden = true;
}

function showChat(user) {
  currentUser = user;
  localStorage.setItem(STORAGE_USER, JSON.stringify(user));
  loginPanel.hidden = true;
  chatPanel.hidden = false;
  topUser.hidden = false;
  userName.textContent = user.name;
  renderMessages(loadMessages());
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loginError.hidden = true;
  const form = new FormData(loginForm);
  const login = String(form.get("login") || "").trim().toLowerCase();
  const password = String(form.get("password") || "");
  const account = USERS[login];

  if (!account || account.password !== password) {
    loginError.textContent = "Неверный логин или пароль";
    loginError.hidden = false;
    return;
  }

  showChat({ login, name: account.name, role: account.role });
});

logoutBtn.addEventListener("click", () => {
  showLogin();
});

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text || !currentUser) return;

  const messages = loadMessages();
  messages.push({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    text,
    author: currentUser.name,
    login: currentUser.login,
    createdAt: new Date().toISOString(),
  });
  saveMessages(messages);
  messageInput.value = "";
  renderMessages(messages);
  messagesEl.scrollTop = messagesEl.scrollHeight;
});

try {
  const saved = JSON.parse(localStorage.getItem(STORAGE_USER) || "null");
  if (saved && saved.login && USERS[saved.login]) {
    showChat(saved);
  } else {
    showLogin();
  }
} catch {
  showLogin();
}
