import asyncio
import logging
from typing import Set, Dict
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import UpdatedGroupCallParticipant, GroupCallParticipant
from pytgcalls import filters as fl
from IstkharMusic import app, userbot
from IstkharMusic.core.call import Istu
from IstkharMusic.utils.database import is_vc_logger, set_vc_logger, get_served_chats
from IstkharMusic.misc import SUDOERS
from config import adminlist

logger = logging.getLogger(__name__)

enabled_chats: Set[int] = set()
user_join_count: Dict[tuple, int] = {}
user_cache: Dict[int, tuple] = {}
vc_participants_cache: Dict[int, list] = {}
DELETE_DELAY = 7


async def delete_message_after_delay(chat_id: int, message_id: int):
    try:
        await asyncio.sleep(DELETE_DELAY)
        await app.delete_messages(chat_id, message_id)
    except:
        pass


async def get_user_info(chat_id: int, user_id: int) -> tuple:
    if user_id in user_cache:
        return user_cache[user_id]

    name = None
    username = "Iɢɴᴏʀᴇᴅ"

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member and member.user:
            user = member.user
            name = user.first_name or ""
            if user.last_name:
                name += f" {user.last_name}"
            username = f"@{user.username}" if user.username else "Iɢɴᴏʀᴇᴅ"
    except:
        pass

    user_cache[user_id] = (name, username)
    return name, username


async def send_join_notification(chat_id: int, user_id: int):
    key = (chat_id, user_id)
    user_join_count[key] = user_join_count.get(key, 0) + 1
    count = user_join_count[key]

    name, username = await get_user_info(chat_id, user_id)
    mention = f'<a href="tg://user?id={user_id}">{name or "User"}</a>'

    text = (
        "<b>#JoinVideoChat</b>\n\n"
        f"<b>● ɴᴀᴍᴇ ➛</b> {mention}\n"
        f"<b>● ɪᴅ ➛</b><code>{user_id}</code>\n"
        f"<b>● ᴜsᴇʀɴᴀᴍᴇ ➛</b> {username}"
    )

    if count > 1:
        text += f"\n\n<b>🔁 ᴊᴏɪɴ ᴄᴏᴜɴᴛ ➛</b> <code>{count}</code>"

    msg = await app.send_message(chat_id, text)
    asyncio.create_task(delete_message_after_delay(chat_id, msg.id))


async def send_leave_notification(chat_id: int, user_id: int):
    name, username = await get_user_info(chat_id, user_id)
    mention = f'<a href="tg://user?id={user_id}">{name or "User"}</a>'

    text = (
        "<b>#LeaveVideoChat</b>\n\n"
        f"<b>● ɴᴀᴍᴇ ➛</b> {mention}\n"
        f"<b>● ɪᴅ ➛</b><code>{user_id}</code>\n"
        f"<b>● ᴜsᴇʀɴᴀᴍᴇ ➛</b> {username}"
    )

    msg = await app.send_message(chat_id, text)
    asyncio.create_task(delete_message_after_delay(chat_id, msg.id))


async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        if user_id in SUDOERS:
            return True
        admins = adminlist.get(chat_id)
        if admins and user_id in admins:
            return True
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False


@Istu.one.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
@Istu.two.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
@Istu.three.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
@Istu.four.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
@Istu.five.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
async def participant_join(_, update: UpdatedGroupCallParticipant):
    chat_id = update.chat_id
    user_id = update.participant.user_id

    if not await is_vc_logger(chat_id):
        return

    await send_join_notification(chat_id, user_id)


@Istu.one.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
@Istu.two.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
@Istu.three.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
@Istu.four.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
@Istu.five.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
async def participant_left(_, update: UpdatedGroupCallParticipant):
    chat_id = update.chat_id
    user_id = update.participant.user_id

    if not await is_vc_logger(chat_id):
        return

    await send_leave_notification(chat_id, user_id)


async def setup_vc_logger():
    try:
        await asyncio.sleep(5)
        chats = await get_served_chats()

        for chat in chats:
            chat_id = chat.get("chat_id")
            if chat_id:
                if await is_vc_logger(chat_id):
                    enabled_chats.add(chat_id)

        logger.info("VC Logger setup done")

    except Exception as e:
        logger.error(f"Setup VC logger error: {e}")


@app.on_message(filters.command(["vclogger", "vclog"]) & filters.group)
async def vclogger_cmd(client, message: Message):
    chat_id = message.chat.id

    if message.from_user and not await is_admin(chat_id, message.from_user.id):
        return await message.reply_text("**❌ ᴀᴅᴍɪɴ ᴏɴʟʏ!**")

    if len(message.command) < 2:
        status = await is_vc_logger(chat_id)
        await message.reply_text(
            f"**📊 ᴠᴄ ʟᴏɢɢᴇʀ :** {'✅ ON' if status else '❌ OFF'}\n\n"
            "**ᴄᴏᴍᴍᴀɴᴅs :**\n\n**• /vclogger on**\n•** /vclogger off**"
        )
        return

    action = message.command[1].lower()

    if action == "on":
        await set_vc_logger(chat_id, True)
        enabled_chats.add(chat_id)
        await message.reply_text("**✅ ᴠᴄ ʟᴏɢɢᴇʀ ᴇɴᴀʙʟᴇᴅ!**")

    elif action == "off":
        await set_vc_logger(chat_id, False)
        enabled_chats.discard(chat_id)
        user_join_count.clear()
        await message.reply_text("**ᴠᴄ ʟᴏɢɢᴇʀ ᴅɪsᴀʙʟᴇᴅ!**")

    else:
        await message.reply_text("**ᴜsᴇ:** /vclogger on | off")


try:
    asyncio.create_task(setup_vc_logger())
except Exception as e:
    logger.error(f"Failed to schedule setup: {e}")


