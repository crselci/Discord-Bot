from DungeonInstance import Dungeon
from CharacterCreation import CharacterCreator
import database as db
import Arena
import discord
import textGPT as text
from Merchant import Market
from datetime import datetime

colors = ['\u001b[1;32m', '\u001b[1;33m', '\u001b[1;4;40;31m', '\u001b[1;47m', '\u001b[1;36m', '\u001b[0m', '\u001b[1;47;35m']

dungeon_channel = "dungeon-crawl"  # Make an list eventually for multiple channels/players.
arena_channel = "arena-battles"    # Make an list eventually for multiple channels/players.
dm_category = "DM RON'S WAITING ROOM"
active_category = "RON'S REALM"
merchant_channel = "market"

dungeon_intro = f"""```ansi\n{colors[2]}YOU MAY TRY TO RUN FROM COMBAT(50% CHANCE OF FAILURE)\n\nYOU MAY LEAVE THE DUNGEON FROM WHERE YOU ENTERED\n
DEATH MEANS START OVER ENTIRELY.\n\nYOU WILL BE FULLY HEALED EVERY NEW DAY FOLLOWING REALM TIME\n{colors[5]}```\nToday's Board:```ansi\n{colors[6]}{text.waiting_room().upper()}{colors[5]}\n```\n\n1 - To start the adventure. Good luck!\n
2 - Get character info and realm time.\n\n"""

arena_intro = f"""```ansi\n{colors[2]}THE LOSER WILL DIE AND THEIR ITEMS WILL BE GIVEN TO THE VICTORIOUS PLAYER.\n\nYOU MAY FORFEIT AT THE COST OF YOUR ITEMS AND PRIDE.\n
DEATH MEANS START OVER AS A LEVEL 1 CHARACTER WITH NOTHING.\n\nINACTIVITY MEANS DEATH (FIVE MINUTES)\n\nYOU WILL BE FULLY HEALED EVERY NEW DAY FOLLOWING REALM TIME\n{colors[5]}```\n
WELCOME TO THE ARENA! FIGHT WELL AND EMERGE VICTORIOUS!\n\n1 - To join the battle.\n"""

merchant_intro = """Welcome to the Market!\nYou can buy and sell items here. I'll have new items every day!\nGood luck!\n\n1 - Get character info and realm time.
2 - Sell items.\n\n"""

#DATABASE METHODS
async def get_character(name):
    if db.check_character(name):
        return db.load_character(name)
    else:
        character = CharacterCreator(name)
        db.store_character(name, character)  
        return character    

async def update_character(name, character):
    db.store_character(name, character)
    
async def dungeon(name):
    if db.check_dungeon(name):
        return db.load_dungeon(name)
    else:
        db.dungeon_instance(name, Dungeon(name))        
        return db.load_dungeon(name)
    
async def update_dungeon(name, dungeon):
    db.dungeon_instance(name, dungeon)
    
#BOT STARTS HERE 
async def start(bot):
    print(f'Starting up. Logged in as {bot.user.name} (ID: {bot.user.id})')
    
    global dungeoneers
    dungeoneers = []
    
    global merchant
    merchant = Market()
    
    global active_dungeons
    active_dungeons = db.load_guilds_actives_list()
    for guild in bot.guilds:
        await delete_channels(guild)
    await create_channels(guild)
    
    db.clear_db() #Test Method!!
    db.create_db() #Test Method!!
    
    global sellers
    sellers = []

#CHANNEL MANIPULATION AND SAFETIES
async def create_channels(guild):
    dm_cat = await create_category(guild, dm_category)
    await create_category(guild, active_category)
    await create_channel(guild, dungeon_channel, dm_cat)
    await create_channel(guild, arena_channel, dm_cat)
    await create_channel(guild, merchant_channel, dm_cat)
            
async def create_category(guild, category_name):
    try:
        # Create a new category
        new_category = await guild.create_category(category_name)
        print(f'Category created: {new_category.name}')
        return new_category
    except Exception as e:
        print(f"Failed to create a category: {str(e)}")

async def create_channel(guild, channel_name, category):
    try:
        # Create a new text channel
        new_channel = await guild.create_text_channel(name=channel_name, category=category)
        print(f'Channel created: {new_channel.name}')
    except Exception as e:
        print(f"Failed to create a channel: {str(e)}")
                    
async def create_active_channel(guild, player):
    try:
        for category in guild.categories:
            if category.name == active_category:
                category_tab = category
        new_channel = await guild.create_text_channel(name = (dungeon_channel + ' ' + player.nick), category=category_tab)
        active_dungeons.append(new_channel.name)
        db.store_guilds_actives(new_channel.name)
        await lock_channel_to_player(new_channel, player)
        print(f'Channel created: {new_channel.name}')
    except Exception as e:
        print(f"Failed to create a channel: {str(e)}")
        
async def delete_channels(guild):
    for channel in guild.channels:
        if channel.name == dungeon_channel or channel.name == arena_channel or channel.name == merchant_channel or channel.name == dm_category or channel.name == active_category:
            await channel.delete()
        elif channel.name in active_dungeons:
            active_dungeons.remove(channel.name)
            db.remove_guilds_active(channel.name)
            await channel.delete()
            
async def refresh_channel_messages(channel):
    async for message in channel.history():
        await message.delete()
    await channel_message(channel)
            
async def lock_channel_to_player(channel, player):
    await channel.set_permissions(player, read_messages=True, send_messages=True)
    for member in channel.members:
        if member != player:
            await channel.set_permissions(member, read_messages=True, send_messages=False)
            
async def lock_actives_on_join(guild, user):
    for channel in guild.channels:
        if channel.name in active_dungeons:
            await lock_channel_to_player(channel, user)

async def channel_message(channel):
    if channel.name == dungeon_channel:
        await channel.send(dungeon_intro) 
    elif channel.name == arena_channel:
        await channel.send(arena_intro) 
    elif channel.name == merchant_channel:
        await channel.send(f"{merchant_intro}\n{merchant}")
            
async def dungeon_channel_interactions(message, content):
    if content.strip() == '1':
        await message.delete()
        #player = await get_character(message.author.name)
        if message.author.name not in dungeoneers:
            dungeoneers.append(message.author.name)
            await create_active_channel(message.guild, message.author)
            newMessage = await message.channel.send("Your dungeon has been created " + str(message.author.nick) + ". Channel name: " + active_dungeons[-1])
            await newMessage.delete(delay=15)
    elif content.startswith('2'):
        await message.delete()
        await charInfo(message)
    else:
        await message.delete()
        
async def arena_channel_interactions(message):
    pass

async def merchant_channel_interactions(message, content):
    if content.strip() =='1':
        await message.delete()
        await charInfo(message)
    elif content.strip() == '2' and not message.author.name in sellers:
        sellers.append(message.author.name) 
        await message.delete()
        await sellItems(message)
    elif message.author.name in sellers and content!='2' and content!='1':
        await player_sell(message)
    else:
        await message.delete()
             
async def sellItems(message):
    player = await get_character(message.author.name)

    new_message = await message.channel.send(f"""What would you like to sell?\n```ansi\n{colors[4]}Player: {message.author.nick}\n
    Gold: {player.getGold()}\n\nInventory:\n{player.getListings(options = merchant.stockCount())}{colors[5]}\n```""")
    await new_message.delete(delay=15)
    
async def player_sell(message):
    player = await get_character(message.author.name)
    content = int(message.content.strip())
    keylist = player.getInventory().keys()
    stock = merchant.stockCount() - 1
    adjusted = content - stock - 1
    
    print(keylist, stock, content)
    if content > stock and content <= stock + len(keylist):
        item = list(keylist)[adjusted]
        print(item)        
        trade = merchant.buyItem(item, player)
        sellers.remove(message.author.name)
        if trade:
            await message.channel.send(f"{item.getName()} sold!")
            await update_character(message.author.name, player)
            await refresh_channel_messages(message.channel)
        else:
            await refresh_channel_messages(message.channel)
    else:
        await message.delete()
        sellers.remove(message.author.name)

async def charInfo(message):
    player = await get_character(message.author.name)
    new_message = await message.channel.send(f"```ansi\n{colors[4]}Name: {message.author.nick}{player}{colors[5]}\n\nTime: {datetime.now().strftime('%H:%M %Y-%m-%d')}```")
    await new_message.delete(delay=15)