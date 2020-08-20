from api import on_command, on_raw_reaction_add
import discord
from pathlib import Path

loto_db = Path("db/loto.db")
loto_db.touch(exist_ok=True)

lotos = {}

for loto in loto_db.read_text().split("\n"):
    if len(loto) == 0:
        continue
    channel, msgid = loto.split(",")
    lotos[channel] = msgid


def save_db():
    lotostr = ""
    for i in lotos:
        lotostr = str(i) + "," + str(lotos[i]) + "\n"

    loto_db.write_text(lotostr)


@on_command('loto')
async def loto(client, message: discord.Message, args):
    if len(args) > 1:
        return await message.channel.send("Error. Sintaxis: loto <on/off> [#canal]")

    if message.channel_mentions:
        chan: discord.abc.GuildChannel = message.channel_mentions[0]
    else:
        chan: discord.abc.GuildChannel = message.channel
    if not isinstance(chan, discord.TextChannel):
        return await message.channel.send("Error. No es un canal de texto")
    if args[0] == 'on':
        if chan.mention in lotos:
            return await message.channel.send("Error. Loto activo para ese canal")
        color = discord.Colour.green()
        embed = discord.Embed(colour=color, title="Lock-out tag-out", description="Click en la reacción para indicar que se está trabajando en esto")
        embed.add_field(name="Owner", value="Nobody")
        embed.set_footer(text="Modificado: nunca")

        messg = await chan.send(embed=embed)
        await messg.add_reaction("\U0001f534")

        lotos[chan.mention] = messg.id
        save_db()
    if args[0] == 'off':
        if chan.mention not in lotos:
            return await message.channel.send("Error. Loto no activo para ese canal")

        mesg: discord.Message = await chan.fetch_message(lotos[chan.mention])
        del lotos[chan.mention]
        save_db()
        await mesg.delete()



@on_raw_reaction_add
async def loto_reaction(client: discord.Client, payload: discord.RawReactionActionEvent):
    found = False
    for i in lotos:
        if str(lotos[i]) == str(payload.message_id):
            found = True
    if not found:
        return

    channel: discord.TextChannel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    embed = message.embeds[0]
    owner = embed.fields[0].value
    await message.clear_reactions()

    if owner == 'Nobody' and payload.emoji.name == '\U0001f534':
        embed.remove_field(0)
        embed.add_field(name='Owner', value=payload.member.name)
        embed.color = discord.Colour.red()
        await message.add_reaction('\U0001f7e5')
        await message.edit(embed=embed)
    elif payload.emoji.name == '\U0001f534':
        await message.add_reaction('\U0001f534')
    elif owner == payload.member.name and payload.emoji.name == '\U0001f7e5':
        embed.remove_field(0)
        embed.add_field(name='Owner', value='Nobody')
        embed.color = discord.Colour.green()
        await message.add_reaction('\U0001f534')
        await message.edit(embed=embed)
    else:
        await message.add_reaction('\U0001f7e5')
