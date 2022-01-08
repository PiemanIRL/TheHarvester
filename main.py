import os
import discord
from discord.ext import tasks,commands
from discord import utils
from discord import Embed
import datetime
from time import sleep
from pytz import timezone

BOT_TOKEN = os.environ['botToken']
Client = discord.Client()
Channel_ID = 927097884564922391 #Needs to be changed if channel changes/is deleted
Tourney_Role_1 = "2nd Chancers"
Tourney_Role_2 = "2ndest Chancers"
Role_Added_Users = []
Sent_Messages = []
Has_Slept = False

"""
Creates an embed message
:param - label: Title
:param - description: Details
:return: Formatted embed
"""
def create_embed(label, description):
  embed = Embed(title=label, description=description, color=0xffffff)
  return embed


"""
Adds a user to a specified role
:param - user: User that asked to be added
:param - role: Role to be applied to user
:param - channel: Channel that the verification message can be sent to
"""
async def add_role(user, role, channel):
  try:
    await user.add_roles(utils.get(user.guild.roles, name=role))
  except Exception as e:
    print("There was an error adding " + user.name +  " to " + role + ": " + str(e))
  else:
    message = await channel.send(user.name + " has been added to " + role)
    Sent_Messages.append(message)


"""
Removes a user from specified role
:param - user: User that asked to be removed
:param - role: Role to be removed to user
:param - channel: Channel that the verification message can be sent to
"""
async def remove_role(user, role, channel):
  try:
    await user.remove_roles(utils.get(user.guild.roles, name=role))
  except Exception as e:
    print("There was an error removing " + user.name +  " from " + role + ": " + str(e))
  else:
    print(user.name + " has been removed from " + role)
    #message = await channel.send(user.name + " have been removed from " + role)
    #Sent_Messages.append(message)


"""
Event for when the bot is ready. 
"""
@Client.event
async def on_ready():
  print("Ready")
  global Has_Slept
  await Client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Grain Grow'))
  
  if(not Has_Slept):
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=1)
    wait_seconds = (next_hour - now).seconds   
    sleep(wait_seconds)
    Has_Slept = True
    tourney_check.start()
  

"""
Event for when a reaction is added
"""
@Client.event
async def on_reaction_add(reaction, user):
  if(len(Role_Added_Users) < 3 and user != Client.user):
    await add_role(user, Tourney_Role_1,  Client.get_channel(Channel_ID))
    Role_Added_Users.append(user)
  elif(len(Role_Added_Users) < 6 and user != Client.user):
    await add_role(user, Tourney_Role_2,  Client.get_channel(Channel_ID))
    Role_Added_Users.append(user)  
    
  
"""
Looping task every hour to check for tourney
"""
@tasks.loop(hours=1)
async def tourney_check():
  text_channel = Client.get_channel(Channel_ID) #Channel_ID needs to be changed if channel changes/is deleted
  current_hour = datetime.datetime.now(timezone('EST')).hour
    
  #Check for normal, everyday tourney times (4, 6, 8, 10, 12)
  if(current_hour == 15 or current_hour == 17 or current_hour == 19 or current_hour == 21 or current_hour == 23):
    #Clear last tournament user roles
    for user in Role_Added_Users:
      await remove_role(user, Tourney_Role_1, text_channel)
      await remove_role(user, Tourney_Role_2, text_channel)
    Role_Added_Users.clear()

    #Delete last message
    if(len(Sent_Messages) != 0):
      for m in Sent_Messages:
        await m.delete()
    Sent_Messages.clear()
    
    message = await text_channel.send(embed=create_embed("There is a tourney starting in an hour", "React to this message to be assigned a tourney role"))
    await message.add_reaction("🏆")
    Sent_Messages.append(message)
    
    
#--------------------------------------------------------------------------------------------------------------- Music Bot code begins below
from dotenv import load_dotenv
import youtube_dl


load_dotenv()

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
      
#-----------------------------------------------------------------------------------------------------------
      
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
      
#----------------------------------------------------------------------------------------------------------     

@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")   

def main():
    Client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
