import asyncio
import os
from pyrogram import Client, filters, utils
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.types import InputPeerChannel, ReactionEmoji

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"

utils.get_peer_type = get_peer_type_new

app = Client("sugarwheep_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


async def process_reaction_list(client: Client, message: Message):
    target_msg = message.reply_to_message
    pemberi_ma = []
    pemberi_sa = []

    if not target_msg:
        return pemberi_ma, pemberi_sa

    try:
        if message.chat.type in ["supergroup", "channel"]:
            channel_id = int(str(message.chat.id).replace("-100", ""))
            resolved_peer = await client.resolve_peer(message.chat.id)
            access_hash = getattr(resolved_peer, "access_hash", 0)

            chat_peer = InputPeerChannel(
                channel_id=channel_id,
                access_hash=access_hash,
            )
        else:
            chat_peer = await client.resolve_peer(message.chat.id)

        raw_reply = await client.invoke(
            functions.messages.GetMessageReactionsList(
                peer=chat_peer,
                id=target_msg.id,
                limit=100,
            )
        )

        users_map = {u.id: u for u in raw_reply.users}

        if hasattr(raw_reply, "reactions"):
            for reaction in raw_reply.reactions:
                user_id = getattr(reaction.peer_id, "user_id", None)
                if not user_id:
                    continue

                raw_user = users_map.get(user_id)
                if not raw_user:
                    continue

                username = None
                if getattr(raw_user, "username", None):
                    username = raw_user.username
                elif getattr(raw_user, "usernames", None):
                    for u in raw_user.usernames:
                        if getattr(u, "active", False) or getattr(u, "editable", False):
                            username = u.username
                            break

                if username:
                    user_mention = f"@{username}"
                else:
                    first_name = raw_user.first_name or "User"
                    user_mention = f"{first_name} (ga pake usn)"

                if isinstance(reaction.reaction, ReactionEmoji):
                    emoji = reaction.reaction.emoticon

                    if emoji in ["❤️", "♥️", "\u2764\ufe0f", "\u2764"]:
                        pemberi_ma.append(user_mention)

                    elif emoji in ["🔥", "👍", "👍\ufe0f"]:
                        pemberi_sa.append(user_mention)

    except Exception as e:
        print(f"[REACTION ERROR] {e}")

    pemberi_ma = list(dict.fromkeys(pemberi_ma))
    pemberi_sa = list(dict.fromkeys(pemberi_sa))

    return pemberi_ma, pemberi_sa


@app.on_message(filters.command("done", prefixes=["/", "."]) & (filters.group | filters.me))
async def cmd_done(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep ke pesan yg ingin dihitung reactnya")
        return

    pemberi_ma, pemberi_sa = await process_reaction_list(client, message)

    if not pemberi_ma and not pemberi_sa:
        await message.reply_text("Gak ada react")
        return

    bagian_hasil = []

    if pemberi_ma:
        str_ma = " ".join(pemberi_ma)
        bagian_hasil.append(f"{str_ma} [{len(pemberi_ma)} MA]")

    if pemberi_sa:
        str_sa = " ".join(pemberi_sa)
        bagian_hasil.append(f"{str_sa} [{len(pemberi_sa)} SA]")

    teks_akhir = f"`{' '.join(bagian_hasil)}`"
    await message.reply_text(text=teks_akhir)


@app.on_message(filters.command("doni", prefixes=["/", "."]) & (filters.group | filters.me))
async def cmd_doni(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Rep ke pesan yg ingin dihitung reactnya")
        return

    pemberi_ma, pemberi_sa = await process_reaction_list(client, message)

    if not pemberi_ma and not pemberi_sa:
        await message.reply_text("Gak ada react")
        return

    main_section = ""
    if pemberi_ma:
        str_ma = " ".join(pemberi_ma)
        main_section = (
            "⊹ ࣪ ˖ ໒꒱ 𝗠𝗔𝗜𝗡 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦:\n"
            f"{str_ma} ({len(pemberi_ma)})\n\n"
        )

    side_section = ""
    if pemberi_sa:
        str_sa = " ".join(pemberi_sa)
        side_section = (
            "⊹ ࣪ ˖ ໒꒱ 𝗦𝗜𝗗𝗘 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦:\n"
            f"{str_sa} ({len(pemberi_sa)})\n\n"
        )

    caption_template = (
        "```\n"
        "   , ´´; __ , ´´; \n"
        " ;  𓂂 · ˔ · 𓂂   ;\n"
        " ´  っ♡ c    𝗦𝗨𝗚𝗔𝗥𝗪𝗛𝗘𝗘𝗣 𝗦𝗔𝗡𝗖𝗧𝗨𝗔𝗥𝗬 ☁️\n\n"
        "꒰ 🍰 ๋࣭⭑꒱  𝙖 𝙟𝙤𝙮𝙛𝙪𝙡 𝙧𝙚𝙘𝙞𝙥𝙚 𝙜𝙪𝙞𝙙𝙚𝙨 𝙩𝙝𝙚 𝙟𖦹𝙪𝙧𝙣𝙚𝙮...݁ ˖Ი𐑼⋆\n\n"
        "in a sanctuary where the world softens x3! ☆ ˖˟ \n"
        "๑˚。🎀 a warm oven meets the coolness of \n"
        "vanilla ice cream with chocolate🍦.* ♡\n\n"
        f"{main_section}"
        f"{side_section}"
        "໒ 𓈒° 🧁 time is savored like a slow melting\n"
        "chocolate truffle, and every shared ⠾ (❥) \n"
        "𔓐𑇓 .. experience becomes a decadent\n"
        "cupcake indulgence. 🥣🥛♪ ྀི\n\n"
        "🛋 ◛ ۫ ּ 𝗠𝗘𝗡𝗦𝗜𝗩𝗘𝗥𝗦𝗔𝗥𝗬 𝗗𝗔𝗧𝗘:\n"
        "➴ .. https://t.me/wheepylove/12\n"
        "```"
    )

    await message.reply_text(text=caption_template)


async def main():
    async with app:
        print("Memperbarui database sesi ID chat...")
        async for dialog in app.get_dialogs():
            pass
        print("Sesi siap digunakan!")
        await asyncio.Event().wait()


if __name__ == "__main__":
    print("Berhasil")
    app.run(main())