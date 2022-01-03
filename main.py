import os
import discord
from discord.ext import tasks
from discord import utils
from discord import Embed
import datetime
from pytz import timezone

BOT_TOKEN = os.environ['botToken']
#BOT_TOKEN = os.getenv('botToken')
Client = discord.Client()
Channel_ID = 927097884564922391 #Needs to be changed if channel changes/is deleted
Tourney_Role_1 = "2nd Chancers"
Tourney_Role_2 = "2ndest Chancers"
Role_Added_Users = []

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
    await channel.send("You have been added to " + role)


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
    #await channel.send("You have been removed from " + role)
    print(user.name + "has been removed from " + role)


"""
Event for when the bot is ready. 
"""
@Client.event
async def on_ready():
  tourney_check.start()
  print("Ready")
  
  await Client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Grain Grow'))


"""
Event for when a reaction is added
"""
@Client.event
async def on_reaction_add(reaction, user):
  if(Role_Added_Users.length < 3 and user != Client.user):
    await add_role(user, Tourney_Role_1,  Client.get_channel(Channel_ID))
    Role_Added_Users.append(user)
  elif(Role_Added_Users.length < 6 and user != Client.user):
    await add_role(user, Tourney_Role_2,  Client.get_channel(Channel_ID))
    Role_Added_Users.append(user)
    
  
"""
Looping task every hour to check for tourney
"""
@tasks.loop(hours=1)
async def tourney_check():
  text_channel = Client.get_channel(Channel_ID) #Needs to be changed if channel changes/is deleted
  current_hour = datetime.datetime.now(timezone('EST')).hour

  #Check for normal, everyday tourney times (4, 6, 8, 10, 12)
  if(current_hour == 15 or current_hour == 17 or current_hour == 19 or current_hour == 21 or current_hour == 23):
    #Clear last tournament user roles
    for user in Role_Added_Users:
      remove_role(user, Tourney_Role_1, text_channel)
      remove_role(user, Tourney_Role_2, text_channel)
    Role_Added_Users.clear()

    message = await text_channel.send(embed=create_embed("There is a tourney starting in an hour", "React to this message to be assigned a tourney role"))
    await message.add_reaction("🏆")
    

def main():
    Client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
