# Telegram Business Message Monitor

A self-hosted Telegram Business bot that keeps a local archive of messages delivered to a Telegram Business account and sends the account owner notifications when a stored message is edited or deleted.

> Use this project only with a Telegram Business account and conversations you own or are authorized to administer. Respect applicable law, platform rules, and participant privacy.

## Features

- Stores incoming Telegram Business messages in a local SQLite database.
- Downloads ordinary media up to a configurable size limit.
- Alerts the configured owner when an archived message is edited or deleted.
- Keeps credentials and runtime data out of Git.

## Requirements

- Python 3.10+
- A Telegram Business account
- A bot created through [@BotFather](https://t.me/BotFather)

## Setup

```bash
git clone https://github.com/ruslanbadaev01/telegram-business-message-monitor.git
cd telegram-business-message-monitor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set these values in `.env`:

- `TELEGRAM_BOT_TOKEN` — the bot token from BotFather.
- `OWNER_CHAT_ID` — the Telegram chat ID that receives notifications.
- `DATA_DIR` — optional local runtime directory; defaults to `./data`.
- `MAX_FILE_SIZE_MB` — optional media download limit; defaults to `20`.

In Telegram, connect the bot to the Business account under **Settings → Telegram Business → Chatbots**. Then run:

```bash
python main.py
```

## Project layout

```text
app/
  bot.py          # Telegram update handlers
  config.py       # environment-based settings
  downloader.py   # ordinary media download helper
  notifier.py     # owner notifications
  storage.py      # SQLite archive
main.py
```

## Security notes

- Never commit `.env`, SQLite files, downloaded media, or chat exports.
- The application stores message content locally; protect the host and its data directory appropriately.
- Rotate a bot token immediately if it is ever exposed.

## License

MIT. See [LICENSE](LICENSE).
