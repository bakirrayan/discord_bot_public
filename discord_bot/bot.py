import asyncio
from discord.ext import commands, tasks
import discord
from itertools import cycle
from googleapiclient.discovery import build
import json
import os
import requests
from requests.api import request
import link_parser
import re
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
load_dotenv('./discord_bot/.env')

TOKEN = os.getenv("TOKEN")
API = os.getenv("API")


#################################################
#             custom help command               #
#################################################

@bot.command(name="help")
async def help(ctx):
    embed=discord.Embed(title="Help Menu", description="Type /help {command} for more info on a command.", color=0x00ffcc)
    embed.set_author(name="ex-machina", icon_url="https://cdn.pngsumo.com/font-help-svg-png-icon-free-download-137547-onlinewebfontscom-help-icon-png-980_980.png")
    embed.set_image(url="https://www.unil.ch/files/live/sites/help/files/home/visuels%20unil/Homepage_Web_HELP.jpg?t=w1200")
    embed.add_field(name="create_channel", value="create a text channel with a default name or you own name / you can add the name (in lowercase) of a category of your choice", inline=False)
    embed.add_field(name="del", value="delete the nimber of messages you want", inline=False)
    embed.add_field(name="nb_users", value="get the number of users in the server", inline=False)
    embed.add_field(name="quiz", value="play quiz game ( you have 15 s to respond with the number of the correct answer)", inline=False)
    embed.add_field(name="score", value="publish an embed of leaderboard", inline=False)
    embed.add_field(name="server_report", value="report about users in the server", inline=False)
    embed.add_field(name="youtube", value="publish an embed about tarik last youtube video and add the domains ai / robotics / embedded / control / iot / factory-io", inline=False)
    embed.add_field(name="url_info", value="publish an embed about an article / put the link between <url>", inline=False)
    embed.set_footer(text=f"requested by {ctx.author.name}",icon_url="https://e7.pngegg.com/pngimages/981/276/png-clipart-v-for-vendetta-logo-comic-book-grafitti-comics-leaf.png")
    await ctx.channel.send(embed=embed) 


#################################################
#                 quiz_system                   #
#################################################

def update_score(user, points):
    url = "http://127.0.0.1:8000/api/score/update"
    new_score = {"name" : user, "points" : points}
    x = requests.post(url, data = new_score)
    return 

def get_question():
    qs = ""
    id = 1
    answer = 0
    response = requests.get("http://127.0.0.1:8000/api/random")
    json_data = json.loads(response.text)
    qs += "Question : \n"
    qs += json_data[0]["title"] + "\n"
    
    for item in json_data[0]["answer"]:
        qs += str(id) + ". " + item["answer"] + "\n"
        if item["is_correct"]:
            answer = id
        id += 1
    points = json_data[0]["points"]
    
    return qs, answer, points

def get_score():
    leaderboard = ''
    id = 1
    response = requests.get("http://127.0.0.1:8000/api/score/leaderboard")
    json_data = json.loads(response.text)

    for item in json_data:
        leaderboard += str(id) + " " + item["name"] + " ===> " + str(item["points"]) + "\n"
        id += 1
    
    return leaderboard

@bot.command(name="score")
async def score(ctx):
    leader = get_score()
    await ctx.channel.send(leader)

@bot.command(name="quiz")
async def quiz(ctx):
    user_name = ctx.message.author
    qus, ans, pts = get_question()
    points = int(pts)
    await ctx.channel.send(qus)

    def check(m):

        return m.author == user_name and m.content.isdigit()
    
    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0)
    except asyncio.TimeoutError:
        print("not done Time out Error")
        return await ctx.channel.send("you take too long to respond")

    print(msg.content)
    if int(msg.content) == ans:
        update_score(user_name, points)
        msg_send = str(user_name) + " got it right !!! + " + str(points) + " points"
        await ctx.channel.send(msg_send)
    else:
        await ctx.channel.send("wrong !!!! maybe next time")
        
    
#################################################
#                   tasks                       #
#################################################

status=cycle(["I'm not a robot", "I'm human", "AI takeover", "CS:GO", "DOOM", "WARFACE", "DOTA 2", "R6", "BF2042"])

@tasks.loop(minutes=1)
async def change_status():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(next(status)))


#################################################
#                   event                       #
#################################################
      
@bot.event
async def on_ready():
    change_status.start()
    print(f"connected as {bot.user}")

@bot.event 
async def on_member_join(member):
    print(f"new member has joined {member.name}")
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to Tarik's Summer School and Learning Group")
    await member.dm_channel.send("please choose in welcome channel of the server the fields you want to learn")

@bot.event       
async def on_raw_reaction_add(payload):
    print("hello, I had a reaction")
    message_id = payload.message_id
    if message_id == 874072402441678890:
        guild_id=payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        role = discord.utils.get(guild.roles, name=payload.emoji.name)
    
        if role is not None:
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members )
            if member is not None:
                await member.add_roles(role)
                print(f"role added {role.name} to {member.name}")
            else:
                print("member not found")
        else:
            print("role not found")

@bot.event       
async def on_raw_reaction_remove(payload):
    print("hello, I don't want to be part of this")
    message_id = payload.message_id
    if message_id == 874072402441678890:
        guild_id=payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        role = discord.utils.get(guild.roles, name=payload.emoji.name)
    
        if role is not None:
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members )
            if member is not None:
                await member.remove_roles(role)
                print(f"role removed {role.name} to {member.name}")
            else:
                print("member not found")
        else:
            print("role not found")


#################################################
#               server-commands                 #
#################################################

@bot.command(name='nb_users')
@commands.has_role(872585219880935435)
async def nb_users(ctx):
    guild = ctx.guild
    channel_send = discord.utils.get(guild.channels, name="member")
    await channel_send.edit(name=f"member: {guild.member_count}")
    
@bot.command(name="server_report")
@commands.has_role(872585219880935435)
async def server_report(ctx):
    guild=ctx.guild
    channel_send = discord.utils.get(guild.channels, name="bot-test")
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        elif str(m.status) == "offline":
            offline += 1
        elif str(m.status) == "invisible":
            idle += 1
        else:
            idle += 1

    await channel_send.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

@bot.command(name='create_channel')
@commands.has_role(872585219880935435)
async def cr_ch(ctx, channel_name: str, cate_name = None):
    guild = ctx.guild
    if cate_name is not None:
        try:
            category = discord.utils.get(guild.categories, name=cate_name)
        except:
            await ctx.channel.send(f"there is no category named {cate_name}")
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating a new channel: {channel_name}')
            await guild.create_text_channel(channel_name, category=category)
    else:
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating a new channel: {channel_name}')
            await guild.create_text_channel(channel_name)
        
@bot.command(name='del')
@commands.has_role(872585219880935435)
async def clear(ctx, num: int):
    print(f"{num} deleted msg")
    await ctx.channel.purge(limit=num+1)

#################################################
#                  youtube                      #
#################################################

def pub_yt():
    youtube = build('youtube', 'v3', developerKey=API)
    channelId="UCuge9LdHlUgvGaBmdF3TAgA"
    request = youtube.search().list(
            part="snippet",
            channelId=channelId,
            order="date"
        )
    response = json.dumps(request.execute(), indent=4)
    print("out.json has been updated")
    with open('out.json', 'w') as sourcefile:
        print(response, file = sourcefile)
    
    request2 = youtube.channels().list(
        part="snippet",
        id=channelId,
        fields="items/snippet/thumbnails/high/url"
    )
    response2 = json.dumps(request2.execute(), indent=4)
    print("out2.json has been updated")
    with open('out2.json', 'w') as sourcefile2:
        print(response2, file = sourcefile2)
    
def get_info():
    
    with open("out.json") as f:
        data = json.load(f)

    with open("out2.json") as e:
        data2 = json.load(e)
    
    video_id = data["items"][0]["id"]["videoId"]
    video_title = data["items"][0]["snippet"]["title"]
    video_des = data["items"][0]["snippet"]["description"]
    video_thumb = data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
    pub_date = data["items"][0]["snippet"]["publishedAt"]
    chan_id = data["items"][0]["snippet"]["channelId"]
    chan_name = data["items"][0]["snippet"]["channelTitle"]
    chan_thumb = data2["items"][0]["snippet"]["thumbnails"]["high"]["url"]
    infos = [chan_id, video_id, video_title, video_des, pub_date, chan_name, video_thumb, chan_thumb]
    
    return infos

@bot.command(name="youtube")
@commands.has_role(872585219880935435)
async def youtube(ctx, fields=None):
    pub_yt()
    infos=get_info()
    video_url = f"https://www.youtube.com/watch?v={infos[1]}"
    channel_url = f"https://www.youtube.com/channel/{infos[0]}"
    embed = discord.Embed(
        title=infos[2], 
        colour=discord.Colour(0xffb7), 
        url=video_url, 
        description=infos[3])

    embed.set_image(url=infos[6])
    embed.set_author(name=infos[5], icon_url=infos[7], url=channel_url)
    embed.set_footer(text=f"Published at {infos[4]}")

    ia = discord.utils.get(ctx.guild.roles, id=873158978383790081)
    robotics = discord.utils.get(ctx.guild.roles, id=873156659135000627)
    embedded = discord.utils.get(ctx.guild.roles, id=873154878329999360)
    control = discord.utils.get(ctx.guild.roles, id=873157184379289653)
    iot = discord.utils.get(ctx.guild.roles, id=873153844706680832)
    factory_io = discord.utils.get(ctx.guild.roles, id=873154533725962361)


    if fields == None:
        channel = bot.get_channel(874072072417083452)
        await channel.send(content="@everyone check the last video", embed=embed)

    elif str(fields) == "ai":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(873334424702443530)
        await channel.send(content=f"{ia.mention} check the last video", embed=embed)

    elif str(fields) == "robotics":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(871837899023331328)
        await channel.send(content=f"{robotics.mention} check the last video", embed=embed)

    elif str(fields) == "embedded":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(873341834913513492)
        await channel.send(content=f"{embedded.mention} check the last video", embed=embed)

    elif str(fields) == "control":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(873341568969482280)
        await channel.send(content=f"{control.mention} check the last video", embed=embed)

    elif str(fields) == "iot":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(873339673223770192)
        await channel.send(content=f"{iot.mention} check the last video", embed=embed)

    elif str(fields) == "factory-io":
        channel1 = bot.get_channel(874072072417083452)
        await channel1.send(content="@everyone check the last video", embed=embed)

        channel = bot.get_channel(874072072417083452)
        await channel.send(content=f"{factory_io.mention} check the last video", embed=embed)

    print("every thing has been sent")
    if os.path.exists("out.json"):
        os.remove("out.json")
        print("out.json has been removed")
    else:
        print("The file out.json does not exist")
    if os.path.exists("out2.json"):
        os.remove("out2.json")
        print("out2.json has been removed")
    else:
        print("The file out2.json does not exist")


#################################################
#                  urls infos                   #
#################################################

@bot.command(name="url_info")
async def linkInfo(ctx, link):
    link = re.sub("\<|\>","",link)
    print(link)
    test = link_parser.scrape_page_metadata(link)
    
    des = test["description"]
    title = test["title"]
    sitename = test["sitename"]
    urls = test["url"]
    image = test["image"]
    sitelogo = test["favicon"]

    embed = discord.Embed(title=title, url=urls, description=des, colour=discord.Colour(0xffb7))
    embed.set_image(url=image)
    embed.set_author(name=sitename, icon_url=sitelogo)
    embed.set_footer(text=f"Shared by {ctx.author.name}")

    await ctx.channel.send(content="@everyone check this article", embed=embed)


#################################################
#           commands_error_handler              #
#################################################

@cr_ch.error
async def cr_ch_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("baliz put the name of the new channel")
        
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("baliz put the number of msgs to delete !!!!!")
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("this command doesn't exist, try something else !!!!! ")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("you still a young padawan go play somewhere else ")

bot.run(TOKEN)
