# Telegram RSS Bot

A Python bot that:
- Periodically scrapes RSS feeds from pinned messages in a Telegram channel
- Posts new articles into that same channel

## Project Goals

- 📰 Read RSS feeds
- 📣 Post updates to Telegram
- 🧠 Use the channel itself (pinned messages) as a persistence store
- ☁️ Deploy and run on AWS Lambda

## Tech Stack

- Python 3.12
- [`feedparser`](https://pypi.org/project/feedparser/)
- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot)
- AWS Lambda
- PyCharm for development

## Getting Started

### 1. Setup environment variables

Set these on your machine or Lambda:
```bash
TELEGRAM_API_KEY=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
