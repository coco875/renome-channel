import interactions
from interactions import get
import json
from os import path
import time

with open("tokens.json") as f:
    tokens = json.load(f)

bot = interactions.Client(
    token=tokens,
    default_scope=1035865026285809674
)

if path.isfile("change.json"):
    with open("change.json", "r", encoding="UTF-8") as f:
        data:dict = json.load(f, parse_int=int, parse_float=float, )
        print(data)
else:
    data = {}

if path.isfile("order.json"):
    with open("order.json", "r", encoding="UTF-8") as f:
        order:dict = json.load(f, parse_int=int, parse_float=float, )
        print(order)
else:
    order = {}

confirm_change = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Confirmer",
    custom_id="confirm change",
    emoji=interactions.Emoji(name="✅")
)

anule_change = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Annuler",
    custom_id="anule change",
    emoji=interactions.Emoji(name="❌")
)

@bot.command(
    name="change",
    description="change le nom de channel",
    options = [
        interactions.Option(
            name="voice_channel",
            description="Le channel vocal",
            type=interactions.OptionType.CHANNEL,
            required=True,
        ),
    ],
)
async def change(ctx: interactions.CommandContext, voice_channel: interactions.Channel):    
    if voice_channel.type != interactions.ChannelType.GUILD_VOICE:
        await ctx.send("Ce channel n'est pas un channel vocal")
        return

    if not str(voice_channel.id) in data:
        await ctx.send("Ce channel n'est pas enregistré, vous pouvez l'enregistrer avec la commande `register`")
        return
    
    if not voice_channel.name in data[str(voice_channel.id)]:
        await ctx.send("Ce channel n'as pas un nom valide, vous pouvez le rénitiliser avec la commande `reset`")
        return
    
    l:list = data[str(voice_channel.id)]

    
    await ctx.send("Quel nom voulez vous donner au channel ?", components=interactions.SelectMenu(
        custom_id="select_menu",
        options=[
            interactions.SelectOption(
                label=i,
                value=str(voice_channel.id)+" "+str(l.index(i)),
        ) for i in l]
        )
    )

@bot.component("select_menu")
async def select_menu(ctx: interactions.ComponentContext, choice):
    answer = choice[0].split(" ")
    l = data[answer[0]]
    await ctx.send("Voulez vous vraiment changer le nom du channel par " + l[int(answer[1])] + " ?", components=[confirm_change, anule_change])

@bot.component("confirm change")
async def confirm_changed(ctx: interactions.ComponentContext):
    channel = await ctx.get_channel()
    last_message = await channel.get_history(limit=2)
    name = last_message[0].content.replace("Voulez vous vraiment changer le nom du channel par ", "").replace(" ?", "")
    id_channel = last_message[1].components[0].components[0].options[0].value.split(" ")[0]
    print(id_channel)
    channel = await get(bot, interactions.Channel, object_id=id_channel)
    time.sleep(1)
    await channel.modify(name=name, position=channel.position)
    time.sleep(1)
    await ctx.edit("Le nom du channel a été changé avec succès", components=[])



@bot.command(
    name="register",
    description="enregistre un channel vocal",
    options = [
        interactions.Option(
            name="voice_channel",
            description="le channel vocal à enregistrer",
            type=interactions.OptionType.CHANNEL,
            required=True,
        ),
        interactions.Option(
            name="names",
            description="les noms à utiliser",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def register(ctx: interactions.CommandContext, voice_channel: interactions.Channel, names: str):
    if voice_channel.type != interactions.ChannelType.GUILD_VOICE:
        await ctx.send("Ce channel n'est pas un channel vocal")
        return
    
    if str(voice_channel.id) in data:
        await ctx.send("Ce channel est déjà enregistré")
        return
    
    data[str(voice_channel.id)] = names.split("|")
    with open("change.json", "w", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)
    
    await ctx.send("Le channel a été enregistré")

@bot.command(
    name="reset",
    description="réinitialise le nom d'un channel vocal",
    options = [
        interactions.Option(
            name="voice_channel",
            description="le channel vocal à réinitialiser",
            type=interactions.OptionType.CHANNEL,
            required=True,
        ),
    ],
)
async def reset(ctx: interactions.CommandContext, voice_channel: interactions.Channel):
    if voice_channel.type != interactions.ChannelType.GUILD_VOICE:
        await ctx.send("Ce channel n'est pas un channel vocal")
        return
    
    if not str(voice_channel.id) in data:
        await ctx.send("Ce channel n'est pas enregistré, vous pouvez l'enregistrer avec la commande `register`")
        return
    
    await voice_channel.modify(name=data[str(voice_channel.id)][0], position=voice_channel.position)
    time.sleep(1)
    await ctx.send("Le nom a été réinitialisé")

@bot.command(
    name="unregister",
    description="désenregistre un channel vocal",
    options = [
        interactions.Option(
            name="voice_channel",
            description="le channel vocal à désenregistrer",
            type=interactions.OptionType.CHANNEL,
            required=True,
        ),
    ],
)
async def unregister(ctx: interactions.CommandContext, voice_channel: interactions.Channel):
    if voice_channel.type != interactions.ChannelType.GUILD_VOICE:
        await ctx.send("Ce channel n'est pas un channel vocal")
        return
    
    if not str(voice_channel.id) in data:
        await ctx.send("Ce channel n'est pas enregistré, vous pouvez l'enregistrer avec la commande `register`")
        return
    
    del data[str(voice_channel.id)]
    with open("change.json", "w", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)
    
    await ctx.send("Le channel a été désenregistré")

@bot.command(
    name="reset_all",
    description="réinitialise tous les noms des channels enregistrés",
)
async def reset_all(ctx: interactions.CommandContext):
    for i in data:
        channel = await get(bot, interactions.Channel, object_id=i)
        await channel.modify(name=data[i][0], position=channel.position)
        time.sleep(1)
    await ctx.send("Les noms ont été réinitialisés")

@bot.command(
    name="save_order",
    description="sauvegarde l'ordre des channels",
)
async def save_order(ctx: interactions.CommandContext):
    global order
    order = {}
    for i in await ctx.guild.get_all_channels():
        if i.type == interactions.ChannelType.GUILD_VOICE:
            order[str(i.id)] = i.position
    with open("order.json", "w", encoding="UTF-8") as f:
        json.dump(order, f, indent=4)
    await ctx.send("L'ordre a été sauvegardé")

@bot.command(
    name="reset_order",
    description="réinitialise l'ordre des channels",
)
async def reset_order(ctx: interactions.CommandContext):
    global order
    await ctx.send("L'ordre est en train d'être réinitialisé")
    for i in order:
        channel = await get(bot, interactions.Channel, object_id=int(i))
        await channel.modify(position=order[i])
        time.sleep(1)
    await ctx.channel.send("L'ordre a été réinitialisé")

@bot.event
async def on_ready():
    print("Ready!")

bot.start()