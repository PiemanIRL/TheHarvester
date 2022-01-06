import os
import discord
from discord.ext import tasks
from discord import utils
from discord import Embed
#import datetime
#from time import sleep
#from pytz import timezone

#All 'custom plugins imported below
import TournyManager




BOT_TOKEN = os.environ['botToken']
Client = discord.Client()

def main():
    Client.run(BOT_TOKEN)
    
if __name__ == "__main__":
    main()
