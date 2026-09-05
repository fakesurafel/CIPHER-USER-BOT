# Sura Bot — Personal Telegram Userbot

Sura Bot is a Telethon-based Telegram userbot for personal automation, AI-assisted interactions, media utilities, profile tools, giveaway monitoring, and local privacy controls.

> **Important:** This project operates through a Telegram user account session, not a normal Bot API token. Use it only on an account you control and follow Telegram's Terms of Service. Automation, bulk messaging, scraping, and inviting users can trigger rate limits or account restrictions.

## Features and Command Reference

Commands are recognized when sent from your own account and begin with a period (`.`). Arguments shown in square brackets are required unless marked optional.

### Help and Status

| Command | Usage | Description |
|---|---|---|
| `.info` | Reply to a user's message, then send `.info` | Shows the user's ID, name, username, bot status, Premium status, and profile photo when available. |
| `.hack` | `.hack` | Displays a fictional terminal-style animation. It does not perform hacking or security actions. |
| `.autochat` | `.autochat` inside a chat | Toggles Gemini-powered automatic replies for the current chat. Run it again to disable the feature. |

### AI and Intelligence

| Command | Usage | Description |
|---|---|---|
| `.ai` | `.ai [question]` | Sends a question to Gemini AI. |
| `.ai` with an image | Reply to an image with `.ai [question]` | Asks Gemini to analyze the replied image. If no question is supplied, the bot requests a description. |
| `.img` | `.img [prompt]` | Generates an image from the prompt using the configured image service and sends it to the current chat. |
| `.tr` | Reply to a text message with `.tr` | Translates the replied message into English. |
| `.translate` | Reply to a text message with `.translate [language]` | Translates into the selected language while preserving slang, emotion, humor, sarcasm, abbreviations, profanity level, punctuation, emojis, and overall conversational vibe. Use a language name or supported language code. |
| `.quiz` | `.quiz` | Arms AI quiz mode for the monitored target. The bot attempts to answer the next matching question. Requires `GEMINI_KEY`. |

### Giveaway Sniper and Hunter Protocol

The sniper workflow is designed as **target → lock → arm**:

1. Send `.monitor` in the target channel. This records the current channel as the target.
2. Reply to a message from the target user and send `.hunt`. This locks the hunter to that sender ID.
3. Use either `.win [text]` or `.quiz` to arm a response mode.
4. Send `.stop` when the operation should end.

| Command | Usage | Description |
|---|---|---|
| `.monitor` | `.monitor` in a channel | Locks the current channel as the sniper target. |
| `.hunt` | Reply to the target user's message with `.hunt` | Locks responses to that message sender's Telegram user ID. |
| `.win` | `.win [text]` | Arms Flash Mode. The bot replies with the specified text when the target condition is met. |
| `.quiz` | `.quiz` | Arms AI Quiz Mode. The bot generates a short Gemini answer to the next matching question. |
| `.stop` | `.stop` | Disables sniper mode and clears the monitored channel and hunter target. |

> **Warning:** Giveaway automation and rapid replies may violate channel rules or trigger Telegram rate limits. Test carefully and use only where permitted.

### Media and Utility Commands

| Command | Usage | Description |
|---|---|---|
| `.song` | `.song [song name]` | Searches YouTube and falls back to SoundCloud, downloads the first result, and sends the audio. Requires `yt-dlp`; some downloads may require additional system media tools. |
| `.vpic` | Reply to a video or GIF with `.vpic` | Attempts to use the replied media as a Telegram video profile photo. |
| `.web` | `.web [URL]` | Captures a screenshot of a web page through the configured screenshot endpoint and sends it to the chat. |
| `.qrl` | `.qrl [text or link]` | Creates and sends a QR code for the supplied text or link. |
| `.say` | `.say [text]` | Generates and sends a voice note. Amharic text uses an Amharic neural voice; other text uses an English neural voice. |

Examples:

```text
.song Never Gonna Give You Up
.web https://example.com
.qrl https://t.me/example
.say Hello, how are you?
.translate Spanish
.translate am
```

For `.translate`, reply to the message first, then send the command. Examples include `.translate Spanish`, `.translate French`, `.translate Amharic`, or `.translate es`. When `GEMINI_KEY` is configured, the command uses Gemini with explicit tone-preservation instructions; without it, it falls back to the translation library.

### Profile and Identity Commands

| Command | Usage | Description |
|---|---|---|
| `.clone` | Reply to a user's message with `.clone` | Copies the user's available name, bio, and profile photo to your account. The original profile is backed up in memory for the current process. |
| `.revert` | `.revert` | Restores the profile backup created before `.clone`. |
| `.afk` | `.afk [reason]` | Enables AFK mode and automatically replies to incoming private messages with the supplied reason. Sending a normal outgoing message disables AFK mode. |

> The profile backup is held in memory and is not a permanent database backup. Restarting the process before `.revert` may remove the backup.

### Ghost Mode and Incoming Message Handling

These behaviors run automatically; they do not require commands.

- **Private-message forwarding:** Incoming private messages are forwarded to Saved Messages. Replying to the forwarded copy in Saved Messages sends the reply back to the original sender.
- **View-once media capture:** Media with a Telegram self-destruct timer is attempted to be saved to Saved Messages.
- **Keyword monitoring:** Matching words in groups or channels are reported to Saved Messages with a message link. Default keywords include `giveaway`, `first comment`, `surafel`, and `ሱራፌል`.
- **Always-online status:** The process periodically updates the account's online status while it is running.

### Administration and Group Commands

| Command | Usage | Description |
|---|---|---|
| `.purge` | Reply to a message with `.purge` | Attempts to delete the replied message and subsequent messages in the current chat. |
| `.all` | `.all [message]` in a group | Mentions non-bot group members using hidden Telegram user links. Large groups may be slow or rate-limited. |
| `.scrape` | `.scrape [channel or group]` | Finds recently active non-bot members in the target entity and attempts to invite up to 40 of them to the current group. This is subject to Telegram permissions and rate limits. |

> Bulk invitations, scraping, mass mentions, and automated actions can result in FloodWait errors or account restrictions. The `.scrape` limit is 40 users per run, but it is not a guarantee that Telegram will allow the operation.

### Silent Local Block Commands

These commands provide a **local filter** and intentionally do not call Telegram's official block action.

| Command | Usage | Description |
|---|---|---|
| `.sunblock` | Reply to a user's message with `.sunblock` | Adds the replied sender to the local silent-block list. |
| `.sunblock` with username | `.sunblock @username` | Resolves a username and adds that user to the local list. |
| `.sunblock` with phone | `.sunblock +15551234567` | Resolves a phone number if that person is available through your Telegram contacts or account visibility. |
| `.sunblock` with ID | `.sunblock 123456789` | Resolves a numeric Telegram user ID. |
| `.sunblockoff` | `.sunblockoff @username`, phone, or ID; or reply and use `.sunblockoff` | Removes a user from the local silent-block list. |
| `.sblocks` | `.sblocks` | Displays the locally blocked user IDs in Saved Messages. |

When a silently blocked user sends a private message, the bot ignores it before forwarding, AFK replies, AI auto-chat, or other incoming processing. It attempts to delete the incoming message when Telegram permits deletion.

> **Delivery limitation:** Only Telegram's official block feature can request server-side blocking. A local silent block does not guarantee that the sender sees no delivered/read indicator, and it cannot prevent the sender from attempting to send messages. The list is stored in `silent_blocks.json` on the deployment filesystem.

## Configuration

Set the following environment variables in the deployment dashboard or a local `.env` file. Do not commit secrets to Git.

| Variable | Required | Example value | Description |
|---|---:|---|---|
| `API_ID` | Yes | `12345678` | Telegram API ID from [my.telegram.org](https://my.telegram.org). This is numeric. |
| `API_HASH` | Yes | `0123456789abcdef0123456789abcdef` | Telegram API hash from [my.telegram.org](https://my.telegram.org). |
| `SESSION` | Yes | `1BVtsOH...` | Telethon StringSession for the account that will run the userbot. |
| `GEMINI_KEY` | No | `AIzaSy...` | Google Gemini API key. Required by `.ai`, `.quiz`, and `.autochat`; without it, those features are unavailable. |
| `PORT` | No | `8080` | HTTP health/download server port. Defaults to `8080`. |
| `RENDER_EXTERNAL_URL` | No | `https://your-service.onrender.com` | Deployment URL value retained for hosted deployments. |

### Generating a Telethon String Session

The `SESSION` value must be a Telethon StringSession, not a Telegram bot token. Generate it with a trusted Telethon session generator, keep it private, and rotate it immediately if it is exposed. Anyone with a valid session string may be able to access the associated Telegram account.

## Installation and Local Run

```bash
git clone https://github.com/fakesurafel/CIPHER-USER-BOT.git
cd CIPHER-USER-BOT
python3 -m pip install -r requirements.txt
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export SESSION="your_telethon_string_session"
export GEMINI_KEY="your_gemini_key" # optional
export PORT="8080"                   # optional
python3 main.py
```

The process logs in using the configured Telegram session and starts an HTTP health endpoint at `/` that returns `Bot Active!`.

## Docker and Render Deployment

The repository includes a `dockerfile` suitable for a Docker-based deployment.

1. Create a service from the GitHub repository.
2. Select **Docker** as the runtime.
3. Add `API_ID`, `API_HASH`, and `SESSION` as protected environment variables.
4. Add `GEMINI_KEY` if AI features are needed.
5. Set `PORT` to the port expected by the hosting provider, or leave it unset to use `8080`.
6. Deploy and check the service logs for the `LOGGED IN AS` message.
7. Configure an external health check against `/` only if your host requires periodic checks.

The local silent-block database is stored in `silent_blocks.json`. If the hosting platform uses an ephemeral filesystem, copy or persist that file using the platform's persistent storage option if you need the list to survive redeployments.

## Dependencies

The application uses the following Python packages:

- `Telethon` for Telegram client access.
- `aiohttp` for the health and download web server.
- `google-generativeai` for Gemini features.
- `yt-dlp` for audio search and downloads.
- `edge-tts`, `gTTS`, and `pydub` for voice and audio processing.
- `deep-translator` for translation.
- `Pillow` for image handling.

## Troubleshooting

| Problem | Possible cause and solution |
|---|---|
| `Credentials missing!` | Confirm that `API_ID`, `API_HASH`, and `SESSION` are set and available to the running process. |
| AI commands fail | Confirm `GEMINI_KEY` is set, valid, and permitted to use the selected Gemini model. |
| A username or phone cannot be silently blocked | The account may not be resolvable by your session. Reply directly to one of the user's messages and run `.sunblock`. |
| Silent blocks disappear after redeploy | The deployment filesystem is ephemeral. Persist `silent_blocks.json` or recreate the entries after deployment. |
| Telegram FloodWait or permission errors | Reduce automation frequency and confirm that the account has permission in the target chat. |
| Audio download fails | Check the source availability and install any system-level media tools required by the hosting image. |

## Security Notes

Never publish `API_HASH`, `SESSION`, `GEMINI_KEY`, or any generated session files. The `.gitignore` file excludes common secret and runtime files, but always verify the repository diff before pushing. If a session string is exposed, terminate active sessions from Telegram settings and generate a new session.

**Author:** surafel
**Version:** 2.1

## License

No license file is currently included. Add an explicit license before redistributing or reusing this project.

## Changelog

### 2.1

- Added persistent local silent-block commands: `.sunblock`, `.sunblockoff`, and `.sblocks`.
- Added complete command, configuration, deployment, and troubleshooting documentation.

### 2.0

- Full release with AI, media, profile, utility, administration, ghost-mode, and giveaway-monitoring features.
