# Quiz Bot

Telegram and VK bots for history quizzes. Bots ask trivia questions from "What? Where? When?" database and check user answers.

## Demo

Try the bots live:

- **Telegram**: [t.me/devman_quizzzz_bot](https://t.me/devman_quizzzz_bot)
- **VKontakte**: [vk.com/club235825452](https://vk.com/club235825452)

## Features

- Dual platform support: Telegram and VKontakte
- 4000+ trivia questions from "What? Where? When?" tournaments
- Answer checking with smart cleanup (ignores comments and clarifications)
- "Give up" button to reveal the correct answer
- Redis-based state storage per user

## Prerequisites

- Python 3.8 or later
- Redis server (local or cloud)
- Telegram Bot Token (from @BotFather)
- VK Community Token with messaging and bot permissions

## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/grigory-zhovtun/quiz-bot-devman.git
cd quiz-bot-devman
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download and unpack the quiz questions archive into `quiz-questions/` directory.

Configure environment variables:

Create a `.env` file in the project root directory.

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token from @BotFather |
| `VK_GROUP_TOKEN` | VK Community token with messaging permissions |
| `REDIS_HOST` | Redis server host (default: `localhost`) |
| `REDIS_PORT` | Redis server port (default: `6379`) |

Example `.env` file:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
VK_GROUP_TOKEN=your_vk_community_token_here
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Usage

Run Telegram bot:

```bash
python tg_bot.py
```

Run VK bot:

```bash
python vk_bot.py
```

## Project Structure

| File | Description |
|------|-------------|
| `tg_bot.py` | Telegram bot with ConversationHandler |
| `vk_bot.py` | VKontakte bot with Long Poll API |
| `read_quiz_files.py` | Parser for quiz question files (KOI8-R encoding) |
