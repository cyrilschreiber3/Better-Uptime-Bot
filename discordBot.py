import processor
import mailBox
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import discord
import chilkat
import sqlite3
import re
import sys
import os
print("Loading libraries...", end=" ", flush=True)


# load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
teamID = os.getenv("BETTERUPTIME_TEAMID")

print("Done")

print("Initializing Discord and SQL connections...", end=" ", flush=True)
# initialize discord library
client = discord.Client()

# initialize database
db = sqlite3.connect("emails.db")  # Connect to database
db.row_factory = sqlite3.Row  # Select row formating
cursor = db.cursor()
print("Done")


def embed_builder(data):
    print("Building embed...", end=" ", flush=True)
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
    embed = discord.Embed(title=embed_title, url=incidentURL, description="New incident started", color=embed_color)
    embed.add_field(name=nat, value=monitor_name, inline=False)
    if nature == "monitor":
        embed.add_field(name="CheckedURL :", value=monitor_url, inline=False)
    embed.add_field(name="Cause :", value=cause, inline=False)
    embed.add_field(name="Started at :", value=startTime, inline=True)
    if status == "RESOLVED":
        embed.add_field(name="Resolved at:", value=endTime, inline=False)
        embed.add_field(name="Length :", value=incidentLength, inline=True)
    embed.set_footer(text="Cyril Schreiber" + "\u3000" * 20 + "Better Uptime", icon_url="https://i.imgur.com/8R9zpmT.png")

    print("Done")
    return embed

async def send_alert(data):
    # send incident alert message
    alert_embed = embed_builder(data)
    print("Sending alert message...", end=" ", flush=True)
    alert_message = await channel.send(embed=alert_embed)
    print("Done")

    # add message ID to database
    print("Adding message ID to database...", end=" ", flush=True)
    incidentURL = data[0]
    updateQuery = f"UPDATE alerts SET message_id = {alert_message.id} WHERE link = '{incidentURL}'"
    cursor.execute(updateQuery)
    db.commit()
    print("Done")
    print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")


async def send_resolved(data):
    # search and reply to the alert message
    print("Searching original alert messaage...", end=" ", flush=True)
    incidentURL = data[0]
    cursor.execute(f"SELECT * FROM alerts WHERE link IS '{incidentURL}'")
    results_alerts = cursor.fetchone()
    message = await channel.fetch_message(results_alerts[8])
    alert_embed = message.embeds[0]
    alert_embed.color = 0xff9500
    print("Done")

    resolved_embed = embed_builder(data)
    print("Replying to and editing alert message...", end=" ", flush=True)
    reply = await message.reply(embed=resolved_embed)
    reply_link = reply.jump_url
    await message.edit(content=f"This incident is resolved. Resolution message : {reply_link}", embed=alert_embed)
    print("Done")


@client.event
async def on_ready():  # execute when bot is ready
    global channel
    channel = client.get_channel(946437156086358016)
    await channel.send("Bot is online !")
    print("Bot is ready !")
    print("Starting processing loop...")
    check_emails.start()  # start email check loop

@tasks.loop(seconds=30)
async def check_emails():

    mails = mailBox.fetchemails()

    print("Processing emails...")
    for i in mails:
        data_list = processor.mailParser(i[0], i[1])
        processor.dumpInDatabase(data_list, data_list[7])

        if data_list[7] == "ALERT":  # If event is an alert
            await send_alert(data_list)
        elif data_list[7] == "RESOLVED":  # else if event is a resolution
            await send_resolved(data_list)

    if len(mails) == 0:
        print("No new emails to process\n")
    else:
        print(f"Done processing {len(mails)} email(s) !\n")

print("Starting bot...", end=" ", flush=True)
client.run(TOKEN)  # start the bot
