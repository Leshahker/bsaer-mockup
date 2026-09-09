# Локальный запуск макета БОАР

## Что внутри

- Статический макет сайта (HTML/CSS/JS)
- Простой сервер Express с кабинетом и общим чатом
- Сессии в cookie, сообщения в `server/data/messages.json`

## Запуск

```bash
npm install
npm start
```

Открыть: http://localhost:3000  
Кабинет: http://localhost:3000/cabinet

Демо-вход:

- `admin` / `admin`
- `doktor` / `doktor`

## Важно

Это заглушка для показа заказчику. Не выкладывать в интернет с паролями `admin/admin`.
