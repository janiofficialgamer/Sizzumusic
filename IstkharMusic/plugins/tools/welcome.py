import asyncio
from logging import getLogger

from pyrogram import filters, enums
from pyrogram.types import ChatMemberUpdated, Message

from IstkharMusic import app

LOGGER = getLogger(__name__)


class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = True

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]


wlcm = WelDatabase()

@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message: Message):
    usage = "**ᴜsᴀɢᴇ :-** `/welcome on / off`"

    if len(message.command) == 1:
        return await message.reply_text(usage)

    user = await app.get_chat_member(message.chat.id, message.from_user.id)

    if user.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        return await message.reply_text(
            "**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴀɴᴀɢᴇ ᴡᴇʟᴄᴏᴍᴇ!**"
        )

    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].lower()
    disabled = await wlcm.find_one(chat_id)

    if state == "off":
        if disabled:
            return await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
        await wlcm.add_wlcm(chat_id)
        await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴅɪsᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")

    elif state == "on":
        if not disabled:
            return await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
        await wlcm.rm_wlcm(chat_id)
        await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴇɴᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")

    else:
        await message.reply_text(usage)


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    disabled = await wlcm.find_one(chat_id)

    if disabled:
        return

    if member.new_chat_member and not member.old_chat_member:
        user = member.new_chat_member.user
        count = await app.get_chat_members_count(chat_id)

        text = (
            f"**𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ɢʀᴏᴜᴘ ʙᴀʙʏ ➻ {user.mention}**"
        )

        try:
            await app.send_message(chat_id, text)
        except Exception as e:
            LOGGER.error(e)
