import os
import asyncio
import logging
import io
import random
import yt_dlp
import edge_tts
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from telethon.tl.functions.channels import InviteToChannelRequest
from aiohttp import web
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
import google.generativeai as genai
from PIL import Image

# ---------------------------------------------------------
# 1. SETUP & CONFIGURATION
# ---------------------------------------------------------

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION")
app_url = os.environ.get("RENDER_EXTERNAL_URL", "http://0.0.0.0:8080")
gemini_key = os.environ.get("GEMINI_KEY")

if not api_id or not api_hash or not session_string:
    logger.error("❌ Error: Credentials missing!")
    exit(1)

try:
    client = TelegramClient(StringSession(session_string), int(api_id), api_hash)

    # AI Setup
    if gemini_key:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("✅ Gemini AI Connected!")
    else:
        logger.warning("⚠️ GEMINI_KEY missing. AI features will not work.")

except Exception as e:
    logger.error(f"❌ Init Error: {e}")
    exit(1)

# --- GLOBAL VARIABLES ---
reply_cache = {}
download_cache = {}
MY_ID = None  
MY_KEYWORDS = ["cipher", "CIPHER", "first comment", "surafel", "ሱራፌል"] 
# ለ Identity Thief ማስታወሻ
ORIGINAL_PROFILE = {}
# --- AFK VARIABLES ---
IS_AFK = False
AFK_REASON = ""

# --- SNIPER VARIABLES ---
TARGET_CHANNEL_ID = None
SNIPER_TEXT = None
SNIPER_MODE = "OFF"
# --- HUNTER ID VARIABLE (The Key Fix) ---
HUNTER_TARGET_ID = None 

# --- AI AUTO-CHAT VARIABLES ---
AUTO_CHAT_CHATS = set()

# --- HUMAN-LIKE SENDING HELPERS ---
async def human_send(chat, text, **kwargs):
    async with client.action(chat, 'typing'):
        await asyncio.sleep(0.2)
        return await client.send_message(chat, text, **kwargs)

async def human_edit(event, text, **kwargs):
    await asyncio.sleep(0.2)
    return await event.edit(text, **kwargs)

# ---------------------------------------------------------
# 2. GIVEAWAY SNIPER COMMANDS
# ---------------------------------------------------------

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.monitor"))
async def set_monitor(event):
    """አሁን ያለህበትን ቻናል ኢላማ ያደርጋል"""
    global TARGET_CHANNEL_ID
    TARGET_CHANNEL_ID = event.chat_id
    title = event.chat.title if event.chat else str(event.chat_id)
    await event.delete()
    await human_send("me", f"🎯 **Sniper Locked on:** `{title}`\n🆔 `{TARGET_CHANNEL_ID}`")

# --- IMPROVED: HUNT COMMAND (REPLY ONLY) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.hunt"))
async def set_hunt_target(event):
    """
    ይሄ በጣም ወሳኝ ነው! ስህተትን ለማስወገድ፣
    ማደን የምትፈልገው ሰው የላከው ሜሴጅ ላይ REPLY አድርገህ .hunt በል።
    """
    global HUNTER_TARGET_ID
    reply = await event.get_reply_message()
    
    if not reply:
        return await human_edit(event, "❌ **Error:** Reply to a message to hunt that user!")
    
    # የላከውን ሰው ID በትክክል ይይዛል (Private Channel ቢሆንም ይሰራል)
    # ቻናል ከሆነ የቻናሉን ID፣ ሰው ከሆነ የሰውየውን ID ይይዛል።
    HUNTER_TARGET_ID = reply.sender_id
    
    # ስሙን ለማግኘት እንሞክር (ለማረጋገጫ ብቻ)
    try:
        sender = await reply.get_sender()
        name = sender.first_name if sender else getattr(sender, 'title', 'Hidden Entity')
    except:
        name = "Unknown Target"

    await event.delete()
    await human_send("me", f"🦅 **Hunter Protocol Active!**\n\n🎯 **Target:** `{name}`\n🆔 **ID:** `{HUNTER_TARGET_ID}`\n\n⚠️ **NOTE:** System locked. Will ONLY reply if THIS ID speaks.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.win (.*)"))
async def set_flash_mode(event):
    """Flash Mode: ጽሁፍ አዘጋጅቶ መጠበቅ"""
    global SNIPER_MODE, SNIPER_TEXT
    SNIPER_TEXT = event.pattern_match.group(1)
    SNIPER_MODE = "FLASH"
    await event.delete()
    
    # behavior verificayion
    status = f"⚡ **Flash Mode ARMED!**\nAuto-Reply: `{SNIPER_TEXT}`"
    if HUNTER_TARGET_ID:
        status += "\n🔒 **Target Locked:** YES (SECURE MODE)"
    else:
        status += "\n⚠️ **Target Locked:** NO (RISKY - WILL FIRE AT ANYONE)"
        
    await human_send("me", status)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.quiz"))
async def set_quiz_mode(event):
    """Quiz Mode: AI response like human"""
    global SNIPER_MODE
    SNIPER_MODE = "QUIZ"
    await event.delete()
    await human_send("me", f"🧠 **Quiz Mode (TURBO) ARMED!**\nAI optimized for millisecond response.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.stop"))
async def stop_sniper(event):
    """Sniping stop"""
    global SNIPER_MODE, TARGET_CHANNEL_ID, HUNTER_TARGET_ID
    SNIPER_MODE = "OFF"
    TARGET_CHANNEL_ID = None
    HUNTER_TARGET_ID = None 
    await event.delete()
    await human_send("me", "🛑 **Sniper & Hunter Disengaged.**\nAll targets cleared.")

# ---------------------------------------------------------
# 3. GOD MODE COMMANDS
# ---------------------------------------------------------

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ai ?(.*)"))
async def ai_handler(event):
    if not gemini_key: return await human_edit(event, "❌ No Key")
    query = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    await human_edit(event, "🧠")
    try:
        if reply and reply.media and reply.photo:
            photo_data = await reply.download_media(file=bytes)
            img = Image.open(io.BytesIO(photo_data))
            prompt = query if query else "Describe this image detail."
            response = model.generate_content([prompt, img])
        else:
            if not query: return await human_edit(event, "❌ Text/Image needed")
            response = model.generate_content(query)

        text = response.text
        if len(text) > 4000: text = text[:4000] + "..."
        await human_edit(event, f"🤖 **AI:**\n\n{text}")
    except Exception as e: await human_edit(event, f"❌ Error: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.img (.*)"))
async def generate_image(event):
    prompt = event.pattern_match.group(1)
    await human_edit(event, f"🎨 `{prompt}`...")
    try:
        encoded = prompt.replace(" ", "%20")
        style = random.choice(["cinematic", "anime", "photorealistic"])
        url = f"https://image.pollinations.ai/prompt/{encoded}%20{style}"
        await client.send_file(event.chat_id, url, caption=f"🎨 {prompt}")
        await event.delete()
    except: await human_edit(event, "❌ Error")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.info"))
async def user_info(event):
    reply = await event.get_reply_message()
    if not reply: return await human_edit(event, "❌ Reply to user")
    await human_edit(event, "🕵️")
    try:
        user = await reply.get_sender()
        info = f"👤 **DOSSIER**\n🆔 `{user.id}`\n🗣️ {user.first_name}\n🔗 @{user.username}\n🤖 Bot: {user.bot}\n💎 Premium: {user.premium}"
        photo = await client.download_profile_photo(user.id)
        if photo:
            await client.send_file(event.chat_id, photo, caption=info)
            os.remove(photo)
            await event.delete()
        else: await human_edit(event, info)
    except: await human_edit(event, "❌ Error")

# --- HUMAN-LIKE VOICE (.say) [FIXED] ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.say (.*)"))
async def text_to_speech(event):
    text = event.pattern_match.group(1)
    await human_edit(event, "🗣️ **Generating Human Voice...**")
    try:
        # Check if text contains Amharic characters
        is_amharic = any("\u1200" <= char <= "\u137F" for char in text)
        voice = 'am-ET-AmehaNeural' if is_amharic else 'en-US-ChristopherNeural'
        
        communicate = edge_tts.Communicate(text, voice)
        filename = "human_voice.mp3"
        await communicate.save(filename)
        
        await client.send_file(event.chat_id, filename, voice_note=True, caption=None)
        
        if os.path.exists(filename):
            os.remove(filename)
        await event.delete()
    except Exception as e:
        await human_edit(event, f"❌ Voice Error: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.clone"))
async def clone_identity(event):
    global ORIGINAL_PROFILE
    reply = await event.get_reply_message()
    if not reply: return await human_edit(event, "❌ Reply to a user!")
    await human_edit(event, "🎭 **Stealing Identity...**")
    try:
        user = await reply.get_sender()
        me = await client.get_me()
        me_full = await client(functions.users.GetFullUserRequest(me))
        if not ORIGINAL_PROFILE:
            my_photo = await client.download_profile_photo("me", file=bytes)
            ORIGINAL_PROFILE = {
                "first_name": me.first_name,
                "last_name": me.last_name,
                "about": me_full.full_user.about,
                "photo_bytes": my_photo
            }
        target_full = await client(functions.users.GetFullUserRequest(user))
        target_about = target_full.full_user.about or ""
        target_photo = await client.download_profile_photo(user, file=bytes)
        await client(functions.account.UpdateProfileRequest(
            first_name=user.first_name,
            last_name=user.last_name or "",
            about=target_about
        ))
        if target_photo:
            f = io.BytesIO(target_photo)
            f.name = "clone.jpg"
            uploaded = await client.upload_file(f)
            await client(functions.photos.UploadProfilePhotoRequest(file=uploaded))
        await human_edit(event, f"🎭 **Identity Stolen:** {user.first_name}")
    except Exception as e:
        await human_edit(event, f"❌ Clone Error: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.revert"))
async def revert_identity(event):
    global ORIGINAL_PROFILE
    if not ORIGINAL_PROFILE: return await human_edit(event, "❌ No backup found!")
    await human_edit(event, "🔄 **Reverting...**")
    try:
        await client(functions.account.UpdateProfileRequest(
            first_name=ORIGINAL_PROFILE["first_name"],
            last_name=ORIGINAL_PROFILE["last_name"] or "",
            about=ORIGINAL_PROFILE["about"] or ""
        ))
        photo_bytes = ORIGINAL_PROFILE.get("photo_bytes")
        if photo_bytes:
            f = io.BytesIO(photo_bytes)
            f.name = "revert.jpg"
            uploaded = await client.upload_file(f)
            await client(functions.photos.UploadProfilePhotoRequest(file=uploaded))
        ORIGINAL_PROFILE = {}
        await human_edit(event, "✅ **Identity Restored!**")
    except Exception as e:
        await human_edit(event, f"❌ Revert Error: {e}")

# --- ACTIVE MEMBER SCRAPER ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.scrape (.*)"))
async def scrape_members(event):
    target = event.pattern_match.group(1)
    my_group = event.chat_id
    await event.delete() # Stealth Mode

    status_msg = await human_send("me", f"🕵️ **Scraping from {target}...**")
    try:
        entity = await client.get_entity(target)
        participants = await client.get_participants(entity, aggressive=True)
        active_users = []
        for user in participants:
            if not user.bot and (isinstance(user.status, types.UserStatusOnline) or isinstance(user.status, types.UserStatusRecently)):
                active_users.append(user)

        await human_edit(status_msg, f"✅ Found {len(active_users)} ACTIVE users! Adding...")

        count = 0
        for user in active_users:
            if count >= 40: break # Safety limit
            try:
                await client(InviteToChannelRequest(my_group, [user]))
                count += 1
                await asyncio.sleep(10)
            except: pass

        await human_edit(status_msg, f"✅ **Done:** Added {count} users.")
    except Exception as e:
        await human_edit(status_msg, f"❌ Error: {e}")

# ---------------------------------------------------------
# 4. ከሰራ ሞክሩት/ልሞክረው 😁(Premium Tools)
# ---------------------------------------------------------

# --- MUSIC DOWNLOADER (Dual Mode) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.song (.*)"))
async def download_song(event):
    song_name = event.pattern_match.group(1)
    await human_edit(event, f"🔍 **Searching for:** `{song_name}`...")
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloaded_song.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Try YouTube first
            try:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            except Exception:
                # Fallback to SoundCloud
                await human_edit(event, f"⚠️ **YouTube Blocked! Bypassing via SoundCloud...**")
                info = ydl.extract_info(f"scsearch:{song_name}", download=False)

            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                title = video['title']
                duration = video.get('duration', 0)
                webpage_url = video['webpage_url']
                
                await human_edit(event, f"⬇️ **Downloading:** `{title}`...")
                ydl.download([webpage_url])
                
                await human_edit(event, f"⬆️ **Uploading...**")
                
                for ext in ['webm', 'm4a', 'mp3', 'opus']:
                    if os.path.exists(f"downloaded_song.{ext}"):
                        await client.send_file(
                            event.chat_id, f'downloaded_song.{ext}',
                            caption=f"🎧 **Song:** {title}\n⏱ **Duration:** {duration} sec\n👤 **By:** sura bot",
                            supports_streaming=True
                        )
                        os.remove(f"downloaded_song.{ext}")
                        break
                
                await event.delete()
            else: await human_edit(event, "❌ **Song not found!**")
    except Exception as e:
        await human_edit(event, f"❌ Error: {e}")

# --- VIDEO PROFILE SETTER (.vpic) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.vpic"))
async def set_video_profile(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await human_edit(event, "❌ Reply to a video or gif!")
    await human_edit(event, "🎬 **Processing Video Profile...**")
    try:
        video = await reply.download_media()
        uploaded = await client.upload_file(video)
        await client(functions.photos.UploadProfilePhotoRequest(video=uploaded))
        if os.path.exists(video): os.remove(video)
        await human_edit(event, "✅ **Video Profile Set!**")
    except Exception as e:
        await human_edit(event, f"❌ Error: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.tr"))
async def translate_msg(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await human_edit(event, "❌ Reply to a text message!")
    await human_edit(event, "🌐 **Translating...**")
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(reply.text)
        await human_edit(event, f"🌐 **Translated (EN):**\n\n{translated}")
    except Exception as e:
        await human_edit(event, f"❌ Translation Error: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.hack"))
async def fake_hack(event):
    await event.edit("▓▒░ LOADING EXPLOIT...")
    await asyncio.sleep(1)
    await event.edit("░▓▒ CONNECTION ESTABLISHED...")
    await asyncio.sleep(1)
    await event.edit("▒░▓ INJECTING SQL...")
    await asyncio.sleep(1)
    await event.edit("✅ **SYSTEM HACKED!**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.purge"))
async def purge_messages(event):
    reply = await event.get_reply_message()
    if not reply: return await human_edit(event, "❌ Reply to a message to start purge!")
    await human_edit(event, "🧹 **Purging...**")
    try:
        msgs = []
        async for m in client.iter_messages(event.chat_id, min_id=reply.id-1):
            msgs.append(m.id)
        await client.delete_messages(event.chat_id, msgs)
    except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.all (.*)"))
async def tag_all(event):
    msg = event.pattern_match.group(1)
    await event.delete()
    try:
        users = await client.get_participants(event.chat_id)
        mentions = ""
        for u in users:
            if not u.bot:
                mentions += f"[\u2063](tg://user?id={u.id})"
        await client.send_message(event.chat_id, f"{msg}{mentions}")
    except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.qrl (.*)"))
async def qr_link(event):
    link = event.pattern_match.group(1)
    await human_edit(event, "🎨")
    try:
        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={link}"
        await client.send_file(event.chat_id, qr, caption="📱 Scan to Join!")
        await event.delete()
    except: await human_edit(event, "❌")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.web (.*)"))
async def web_screenshot(event):
    url = event.pattern_match.group(1)
    await human_edit(event, f"📸 **Capturing:** `{url}`...")
    try:
        shot = f"https://image.thum.io/get/width/1200/crop/800/no_redirect/{url}"
        await client.send_file(event.chat_id, shot, caption=f"🌐 **Web:** {url}")
        await event.delete()
    except: await human_edit(event, "❌ Error")

# --- AI AUTO-CHAT COMMANDS ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.autochat"))
async def toggle_autochat(event):
    global AUTO_CHAT_CHATS
    chat_id = event.chat_id
    if chat_id in AUTO_CHAT_CHATS:
        AUTO_CHAT_CHATS.remove(chat_id)
        await human_edit(event, "🤖 **AI Auto-Chat:** `DISABLED` for this chat.")
    else:
        AUTO_CHAT_CHATS.add(chat_id)
        await human_edit(event, "🤖 **AI Auto-Chat:** `ENABLED` for this chat.\nI will now analyze and reply automatically.")
    await asyncio.sleep(3)
    await event.delete()

# --- AFK Logic ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk (.*)"))
async def set_afk(event):
    global IS_AFK, AFK_REASON
    AFK_REASON = event.pattern_match.group(1)
    IS_AFK = True
    await human_edit(event, f"💤 **AFK Mode Active:** `{AFK_REASON}`")
    await asyncio.sleep(3)
    await event.delete()

@client.on(events.NewMessage(outgoing=True))
async def unset_afk_check(event):
    global IS_AFK
    if IS_AFK and not event.text.startswith(".afk"):
        IS_AFK = False
        await human_send(event.chat_id, "✅ **I am back online!**")

# --- GLOBAL HANDLER FOR INCOMING MESSAGES ---
@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    global MY_ID, SNIPER_MODE, IS_AFK, AFK_REASON, HUNTER_TARGET_ID, AUTO_CHAT_CHATS

    # --- AI AUTO-CHAT LOGIC ---
    # Trigger ONLY if chat_id is in AUTO_CHAT_CHATS AND it's NOT a message from ME
    if event.chat_id in AUTO_CHAT_CHATS and not event.out:
        logger.info(f"🤖 Auto-Chat Triggered in chat {event.chat_id}")
        try:
            # Get last 20 messages for deep context
            messages = await client.get_messages(event.chat_id, limit=20)
            context = ""
            for m in reversed(messages):
                sender = "Me" if m.out else "Them"
                if m.text:
                    context += f"{sender}: {m.text}\n"
            
            prompt = f"You are ME. Analyze the CONVERSATION HISTORY below to understand my 'vibe', my slang, my tone, and how I talk to this person. Your goal is to reply exactly like I would. \n\nRULES:\n1. Match my energy and style perfectly.\n2. Use the same language (Amharic or English) as the last few messages.\n3. Keep it short, casual, and friendly. \n4. NO formal or robotic language.\n\nCONVERSATION HISTORY:\n{context}\nReply to the last message as ME."
            
            async with client.action(event.chat_id, 'typing'):
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                await asyncio.sleep(random.uniform(1, 3)) # More human-like delay
                await client.send_message(event.chat_id, reply_text)
                logger.info(f"🤖 Auto-Chat Sent: {reply_text}")
        except Exception as e:
            logger.error(f"Auto-Chat Error: {e}")

    # --- AFK AUTO REPLY ---
    if IS_AFK and event.is_private:
        sender = await event.get_sender()
        if sender and not sender.bot:
            await human_send(event.chat_id, f"🤖 **Auto-Reply:**\nI am currently AFK (Away From Keyboard).\n\nReason: `{AFK_REASON}`")

    # --- A. SNIPER LOGIC ---
    if TARGET_CHANNEL_ID and event.chat_id == TARGET_CHANNEL_ID:
        if HUNTER_TARGET_ID and event.sender_id != HUNTER_TARGET_ID:
            return 

        if SNIPER_MODE == "FLASH" and SNIPER_TEXT:
            try:
                await client.send_message(event.chat_id, SNIPER_TEXT, reply_to=event.id)
                SNIPER_MODE = "OFF"
                await human_send("me", f"✅ **FLASH SNIPED:** {SNIPER_TEXT}")
            except: pass
            return
            
        elif SNIPER_MODE == "QUIZ" and event.text:
            try:
                prompt = f"Ans: {event.text}. Short."
                response = model.generate_content(prompt)
                answer = response.text.strip()
                await client.send_message(event.chat_id, answer, reply_to=event.id)
                SNIPER_MODE = "OFF"
                await human_send("me", f"✅ **QUIZ SNIPED:** {answer}")
            except: pass
            return

    # --- B. EAVESDROPPER ---
    if (event.is_group or event.is_channel) and event.raw_text:
        try:
            for k in MY_KEYWORDS:
                if k.lower() in event.raw_text.lower():
                    l = f"https://t.me/c/{str(event.chat_id).replace('-100','')}/{event.id}"
                    await human_send("me", f"🚨 **{k}** Found!\n🔗 {l}")
                    break
        except: pass

    # --- C. VAULT BREAKER ---
    is_vanishing = False
    if event.message.ttl_period: is_vanishing = True
    elif event.media and hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds: is_vanishing = True

    if is_vanishing:
        try:
            sender = await event.get_sender()
            name = sender.first_name if sender else "Unknown"
            f = await event.download_media(file=bytes)
            if f:
                img_file = io.BytesIO(f)
                img_file.name = "captured_media.jpg"
                await client.send_file("me", img_file, caption=f"Bomb **Captured View-Once**\n👤 From: {name}")
        except Exception as e:
            logger.error(f"Vault Error: {e}")
        return

    # --- D. GHOST MODE ---
    if event.is_private and not event.is_group and not event.is_channel:
        try:
            if MY_ID and event.sender_id != MY_ID:
                fwd = await client.forward_messages("me", event.message)
                if fwd: reply_cache[fwd.id] = event.sender_id
                if len(reply_cache) > 500: reply_cache.clear()
        except: pass

# --- SAVED MESSAGES ACTIONS ---
@client.on(events.NewMessage(chats="me"))
async def saved_msg_actions(event):
    if event.text and "t.me/c/" in event.text and not event.is_reply:
        try:
            await human_edit(event, "🔓")
            parts = event.text.split("/")
            chan_id = int("-100" + parts[-2])
            msg_id = int(parts[-1])
            msg = await client.get_messages(chan_id, ids=msg_id)
            if msg and msg.media:
                f = await client.download_media(msg)
                if f:
                    await client.send_file("me", f, caption="✅")
                    os.remove(f)
                    await event.delete()
        except: await human_edit(event, "❌")

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_id = None
        if reply_msg.id in reply_cache:
            target_id = reply_cache[reply_msg.id]
        elif reply_msg.fwd_from:
             if reply_msg.fwd_from.from_id:
                 target_id = getattr(reply_msg.fwd_from.from_id, 'user_id', None) or reply_msg.fwd_from.from_id

        if target_id and isinstance(target_id, int):
            try:
                await client.send_message(target_id, event.message.text)
                await human_edit(event, f"😊 **Sent:** {event.message.text}")
            except: pass

# --- Web Server ---
async def home(r): return web.Response(text="Bot Active!")

async def download(r):
    fid = r.match_info['file_id']
    if fid in download_cache:
        try:
            path = await client.download_media(download_cache[fid])
            if path:
                with open(path, 'rb') as f: d = f.read()
                os.remove(path)
                return web.Response(body=d, headers={'Content-Disposition': f'attachment; filename="{os.path.basename(path)}"'})
        except: pass
    return web.Response(text="Error", status=404)

async def main():
    global MY_ID
    logger.info("⏳ Starting...")
    await client.start()

    me = await client.get_me()
    MY_ID = me.id
    logger.info(f"✅ LOGGED IN AS: {me.first_name} (ID: {MY_ID})")

    app = web.Application()
    app.router.add_get('/', home)
    app.router.add_get('/download/{file_id}', download)

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    while True:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(60)
        except: await asyncio.sleep(10)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
