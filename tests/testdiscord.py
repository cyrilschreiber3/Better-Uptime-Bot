from email import message
import os
import discord
import discord.ext.commands
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(946437156086358016)
    await channel.send("Bot is online !")



client.run(TOKEN)