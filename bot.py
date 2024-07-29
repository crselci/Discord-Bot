import discord
from discord.ext import commands, tasks
import BotLogic as bl
import tracemalloc

tracemalloc.start()

# Intents are settings that specify what events the bot needs to listen to.
intents = discord.Intents.default()
intents.messages = True  # We want to listen to messages
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    global restarted
    restarted = False
    await bl.start(bot)
    restarted = True

@bot.event
async def on_guild_join(guild):
    print(f'Bot joined: {guild.name} (ID: {guild.id})')
    await bl.create_channels(guild)

@bot.event
async def on_message(message):
    content = message.content
    
    if message.channel.name == bl.dungeon_channel and message.author != bot.user:
        await bl.dungeon_channel_interactions(message, content)
            
    if message.channel.name == bl.arena_channel and message.author != bot.user:
        await message.delete()
        
    if message.channel.name == bl.merchant_channel and message.author != bot.user:
        await bl.merchant_channel_interactions(message, content)
        
    if message.channel.name in bl.active_dungeons and message.author != bot.user:
        await message.channel.send("You are in the active dungeon channel.")
        
@bot.event
async def on_member_join(member):
    await bl.lock_actives_on_join(member.guild, member)       
            
@bot.event
async def on_guild_channel_create(channel):
    await bl.channel_message(channel)
    
@bot.event
async def on_guild_channel_update(before, after):
    if restarted and (before.name == bl.dungeon_channel or before.name == bl.arena_channel or before.name == bl.merchant_channel or before.name == bl.dm_category or before.name == bl.active_category or before.name in bl.active_dungeons):
        if before.name != after.name:
            await after.edit(name=before.name)
        try:
            if before.category.name == bl.active_category or before.category.name == bl.dm_category:
                await after.edit(category=before.category)
        except AttributeError:
            pass   

#bot.run(BOT TOKEN HERE)
