# sura bot - Personal Telegram Userbot

**sura bot** is a powerful, feature-rich Telegram userbot built with Telethon. It is designed for automation, AI-powered interactions, and stealth operations.

---

## 🚀 Features

### 🧠 AI & Intelligence
*   `.ai [query]` - Ask Gemini AI any question. Reply to an image to analyze it.
*   `.tr` - Reply to any message to translate it to English instantly.
*   `.img [prompt]` - Generate high-quality AI images.

### 🎯 Sniper & Hunter Protocol
*   `.monitor` - Lock the sniper on the current channel for giveaways.
*   `.hunt` - **(Reply Only)** Lock onto a specific user ID to trigger auto-replies only when they post.
*   `.win [text]` - **Flash Mode:** Auto-replies with the specified text instantly when the target posts.
*   `.quiz` - **AI Quiz Mode:** Automatically solves and replies to giveaway questions using Gemini AI.
*   `.stop` - Disengages all sniper and hunter protocols.

### 🎬 Media & Utilities
*   `.song [name]` - Download music from YouTube or SoundCloud.
*   `.vpic` - Reply to a video to set it as your Telegram Video Profile.
*   `.web [url]` - Capture a screenshot of any website.
*   `.qrl [link]` - Convert any text or link into a QR Code.
*   `.say [text]` - Generate human-like voice notes (supports Amharic and English).

### 🎭 Identity & Stealth
*   `.clone` - Reply to a user to copy their Name, Bio, and Profile Picture.
*   `.revert` - Restore your original profile identity.
*   `.afk [reason]` - Set Away From Keyboard status with auto-reply.
*   `.hack` - Display a fake "hacking" terminal animation.

### 👻 Ghost Mode (Privacy)
*   **Stealth Reading**: Incoming private messages are forwarded to **Saved Messages**.
*   **Ghost Reply**: Reply to the forwarded message in Saved Messages to respond anonymously without opening the original chat.
*   **Vault Breaker**: Automatically saves "View-Once" media to Saved Messages.

### 🛠 Administration
*   `.purge` - Reply to a message to delete it and all subsequent messages.
*   `.scrape [channel]` - Scrapes active members from a target group and invites them to your current group (Limit: 40 per run).
*   `.all [message]` - Tags all members in a group using hidden mentions.

---

## ⚙️ Configuration

The bot is configured using the following Environment Variables:

| Key | Description |
| :--- | :--- |
| `API_ID` | Your Telegram API ID. |
| `API_HASH` | Your Telegram API Hash. |
| `SESSION` | Telethon String Session. |
| `GEMINI_KEY` | Google Gemini API Key. |
| `PORT` | Web server port (Default: 8080). |

---

## 📦 Deployment

This bot is optimized for **Render** using Docker.

1.  **Host**: [Render.com](https://render.com)
2.  **Runtime**: Docker (uses the included `dockerfile`).
3.  **Keep-Alive**: Use [UptimeRobot](https://uptimerobot.com) to ping your Render URL every 5 minutes to maintain 24/7 uptime on the free tier.

---

## 📝 Notes
*   **Human Simulation**: All bot responses include a 0.2-second typing delay to simulate human behavior.
*   **Always Online**: The bot automatically updates your status to "Online" every 60 seconds.

**Author**: surafel
**Version**: 2.0 (Full Release)
