const path = require("path");
const fs = require("fs");
const express = require("express");
const session = require("express-session");

const PORT = process.env.PORT || 3000;
const ROOT = path.join(__dirname, "..");
const MESSAGES_FILE = path.join(__dirname, "data", "messages.json");

/** Демо-пользователи. Позже заменим на БД. */
const USERS = {
  admin: { password: "admin", name: "Администратор", role: "admin" },
  doktor: { password: "doktor", name: "Демо-врач", role: "member" },
};

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(
  session({
    name: "boar.sid",
    secret: process.env.SESSION_SECRET || "boar-dev-secret-change-me",
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      sameSite: "lax",
      maxAge: 1000 * 60 * 60 * 12,
    },
  })
);

function loadMessages() {
  try {
    const raw = fs.readFileSync(MESSAGES_FILE, "utf8");
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function saveMessages(messages) {
  fs.mkdirSync(path.dirname(MESSAGES_FILE), { recursive: true });
  fs.writeFileSync(MESSAGES_FILE, JSON.stringify(messages, null, 2), "utf8");
}

function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.status(401).json({ error: "Нужен вход" });
  }
  next();
}

app.get("/api/me", (req, res) => {
  if (!req.session.user) {
    return res.json({ user: null });
  }
  res.json({ user: req.session.user });
});

app.post("/api/login", (req, res) => {
  const login = String(req.body.login || "").trim().toLowerCase();
  const password = String(req.body.password || "");
  const account = USERS[login];

  if (!account || account.password !== password) {
    return res.status(401).json({ error: "Неверный логин или пароль" });
  }

  req.session.user = {
    login,
    name: account.name,
    role: account.role,
  };

  res.json({ user: req.session.user });
});

app.post("/api/logout", (req, res) => {
  req.session.destroy(() => {
    res.clearCookie("boar.sid");
    res.json({ ok: true });
  });
});

app.get("/api/messages", requireAuth, (req, res) => {
  res.json({ messages: loadMessages() });
});

app.post("/api/messages", requireAuth, (req, res) => {
  const text = String(req.body.text || "").trim();
  if (!text) {
    return res.status(400).json({ error: "Пустое сообщение" });
  }
  if (text.length > 2000) {
    return res.status(400).json({ error: "Слишком длинное сообщение" });
  }

  const messages = loadMessages();
  const message = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    text,
    author: req.session.user.name,
    login: req.session.user.login,
    createdAt: new Date().toISOString(),
  };
  messages.push(message);
  saveMessages(messages);
  res.status(201).json({ message });
});

app.get("/cabinet", (req, res) => {
  res.sendFile(path.join(ROOT, "cabinet", "index.html"));
});

app.use("/cabinet", express.static(path.join(ROOT, "cabinet")));
app.use(express.static(ROOT));

app.listen(PORT, () => {
  console.log(`БОАР локально: http://localhost:${PORT}`);
  console.log(`Кабинет:       http://localhost:${PORT}/cabinet`);
  console.log(`Вход: admin / admin  ·  doktor / doktor`);
});
