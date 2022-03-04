import os
import sys
import re
import sqlite3
import chilkat
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import mailBox
import processor

# initialize discord library
client = discord.Client()

# load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
teamID = os.getenv("BETTERUPTIME_TEAMID")

# initialize database
db = sqlite3.connect("emails.db") # Connect to database
db.row_factory = sqlite3.Row # Select row formating
cursor = db.cursor()

def embed_builder(data):
    # setup the variables
    incidentURL = data[0]
    monitor_name = data[1]
    monitor_url = data[2]
    cause = data[3]
    startTime = data[4]
    status = data[7]
    nature = data[8]
    embed_title = "Better Uptime Alert"
    embed_color = 0xff0000
    # setup additional variables if status is resolved
    if status == "RESOLVED": 
        endTime = data[5]
        incidentLength = data[6]
        embed_title = "Better Uptime Incident Resolved"
        embed_color = 0x04ff00
    
    # transform nature of incident to printable string
    match nature: 
        case "monitor":
            nat = "Monitor :"
        case "heartbeat":
            nat = "Heartbeat :"
        case _:
            nat = "Monitor :"

    # create the actual embed
    embed=discord.Embed(title=embed_title, url=incidentURL, description="New incident started", color=embed_color)
    embed.add_field(name=nat, value=monitor_name, inline=False)
    if nature == "monitor":
        embed.add_field(name="CheckedURL :", value=monitor_url, inline=False)
    embed.add_field(name="Cause :", value=cause, inline=False)
    embed.add_field(name="Started at :", value=startTime, inline=True)
    if status == "RESOLVED":
        embed.add_field(name="Resolved at:", value=endTime, inline=False)
        embed.add_field(name="Length :", value=incidentLength, inline=True)
    embed.set_footer(text="B.U.B." + "\u3000" * 25 + "Better Uptime", icon_url="https://i.imgur.com/8R9zpmT.png")

    return embed

async def send_alert(data):
    print("run")
    # send incident alert message
    alert_message = await channel.send(embed = embed_builder(data))
    incidentURL = data[0]
    
    # add message ID to database
    updateQuery = f"UPDATE alerts SET message_id = {alert_message.id} WHERE link = '{incidentURL}'"
    cursor.execute(updateQuery)
    db.commit()
    print(str(cursor.rowcount) + " row(s) affected")

async def send_resolved(data):
    print("run")
    incidentURL = data[0]

    # search and edit the alert message
    cursor.execute(f"SELECT * FROM alerts WHERE link IS '{incidentURL}'")
    results_alerts = cursor.fetchone()
    message = await channel.fetch_message(results_alerts[8])

    await message.edit(embed = embed_builder(data))


@client.event 
async def on_ready(): # execute when bot is ready
    global channel 
    channel = client.get_channel(946437156086358016)
    await channel.send("Bot is online !")
    check_emails.start() # start email check loop

@tasks.loop(seconds=60)
async def check_emails():
    print("loop")    
    

    mails = mailBox.fetchemails()

    for i in mails:
        
        data_list = processor.mailParser(i[0], i[1])
        processor.dumpInDatabase(data_list, data_list[7])

        if data_list[7] == "ALERT": # If event is an alert
            print("if alert")
            await send_alert(data_list)
        elif data_list[7] == "RESOLVED": # else if event is a resolution
            print("if resolved")
            await send_resolved(data_list)




client.run(TOKEN) # start the bot