import os
import threading
import telebot

from config import (
    BOT_TOKEN,
    GROUP_ID,
    MAIN_CHANNEL,
    BACKUP_CHANNEL,
    PAYMENT_PROOF,
    CONTACT_OWNER
)

from database import setup_database, get_next_video, set_next_video


bot = telebot.TeleBot(BOT_TOKEN)

# Video sequence ko ek time par sirf ek join process karega
video_lock = threading.Lock()

setup_database()

VIDEO_FOLDER = "videos"


# ==============================
# GET ALL VIDEOS
# ==============================

def get_videos():

    if not os.path.exists(VIDEO_FOLDER):
        return []

    videos = []

    for filename in os.listdir(VIDEO_FOLDER):

        if filename.lower().endswith(".mp4"):

            path = os.path.join(VIDEO_FOLDER, filename)

            if os.path.isfile(path):
                videos.append(path)

    videos.sort(key=lambda x: os.path.basename(x).lower())

    return videos


# ==============================
# /ID COMMAND
# ==============================

@bot.message_handler(commands=["id"])
def get_id(message):

    bot.reply_to(
        message,
        f"✅ CHAT ID:\n`{message.chat.id}`",
        parse_mode="Markdown"
    )


# ==============================
# NEW MEMBER JOIN
# ==============================

@bot.chat_member_handler()
def member_update(update):

    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    print("CHAT MEMBER UPDATE")
    print("Old:", old_status)
    print("New:", new_status)

    # ONLY NEW JOIN
    if old_status not in ("left", "kicked"):
        return

    if new_status != "member":
        return

    if update.chat.id != GROUP_ID:
        return


    # ==============================
    # GET VIDEOS
    # ==============================

    videos = get_videos()

    if not videos:

        print("❌ No videos found.")

        bot.send_message(
            update.chat.id,
            "👋 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣! ❤️"
        )

        return


    # ==============================
    # USER INFO
    # ==============================

    user = update.new_chat_member.user

    name = user.first_name or "User"

    if user.username:
        username = f"@{user.username}"
    else:
        username = "Not User ID"


    # ==============================
    # WELCOME CAPTION
    # ==============================

    caption = (
        f"👤 <b>𝗡𝗔𝗠𝗘:</b> {name}\n"
        f"🆔 <b>𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘:</b> {username}\n\n"

        f"✨ <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣! ❤️</b>\n"
        f"🤝 <b>𝗪𝗘'𝗥𝗘 𝗛𝗔𝗣𝗣𝗬 𝗧𝗢 𝗛𝗔𝗩𝗘 𝗬𝗢𝗨 𝗛𝗘𝗥𝗘!</b>\n\n"

        f"🔰 <b>𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 👇</b>\n"
        f'<a href="{MAIN_CHANNEL}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗝𝗢𝗜𝗡 𝗡𝗢𝗪</a>\n'
        f'<a href="{MAIN_CHANNEL}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗝𝗢𝗜𝗡 𝗡𝗢𝗪</a>\n\n'

        f"🛡️ <b>𝗕𝗔𝗖𝗞𝗨𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 👇</b>\n"
        f'<a href="{BACKUP_CHANNEL}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗝𝗢𝗜𝗡 𝗡𝗢𝗪</a>\n'
        f'<a href="{BACKUP_CHANNEL}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗝𝗢𝗜𝗡 𝗡𝗢𝗪</a>\n\n'

        f"💳 <b>𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗣𝗥𝗢𝗢𝗙 👇</b>\n"
        f'<a href="{PAYMENT_PROOF}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗩𝗜𝗘𝗪 𝗣𝗥𝗢𝗢𝗙</a>\n'
        f'<a href="{PAYMENT_PROOF}">🔗 𝗖𝗟𝗜𝗖𝗞 𝗩𝗜𝗘𝗪 𝗣𝗥𝗢𝗢𝗙</a>\n\n'

        f"👤 <b>𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥 👇</b>\n"
        f'<a href="{CONTACT_OWNER}"><b>@BLACKTHUNDER999</b></a>'
    )


    # ==============================
    # VIDEO SEQUENCE
    # ==============================

    with video_lock:

        current_number = get_next_video()

        if current_number < 1 or current_number > len(videos):
            current_number = 1

        video_path = videos[current_number - 1]

        print(
            f"🎬 Sending video "
            f"{current_number}/{len(videos)}: "
            f"{os.path.basename(video_path)}"
        )


        # ==============================
        # SEND VIDEO
        # ==============================

        try:

            with open(video_path, "rb") as video:

                bot.send_video(
                    update.chat.id,
                    video,
                    caption=caption,
                    parse_mode="HTML",
                    timeout=180
                )

            print(
                f"✅ Video {current_number} sent successfully"
            )


            # ==============================
            # NEXT VIDEO
            # ==============================

            next_number = current_number + 1

            if next_number > len(videos):
                next_number = 1

            set_next_video(next_number)

            print(
                f"➡️ Next video: "
                f"{next_number}/{len(videos)}"
            )


        except Exception as error:

            print(
                f"❌ VIDEO SEND ERROR: {error}"
            )


# ==============================
# START BOT
# ==============================

print("🤖 TG WELCOME BOT STARTED")

print(
    f"🎬 Videos available: "
    f"{len(get_videos())}"
)


bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60,
    skip_pending=False,
    allowed_updates=[
        "message",
        "chat_member"
    ]
)