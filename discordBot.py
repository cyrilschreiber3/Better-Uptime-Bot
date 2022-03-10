print("Loading libraries...", end=" ", flush=True)
import os
import sys
import sqlite3
import discord
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord.ext import commands, tasks

import mailBox
import processor

# load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOTID = os.getenv('DISCORD_BOT_ID')
teamID = os.getenv("BETTERUPTIME_TEAMID")

print("Done")

print("Initializing Discord and SQL connections...", end=" ", flush=True)
# initialize discord library
client = discord.Client()
bot = commands.Bot(command_prefix="$")

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
    embed_description = "New incident started"
    embed_color = 0xff0000
    # setup additional variables if status is resolved
    if status == "RESOLVED":
        endTime = data[5]
        incidentLength = data[6]
        embed_title = "Better Uptime Incident Resolved"
        embed_description = "Incident resolved"
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
    embed = discord.Embed(title=embed_title, url=incidentURL, description=embed_description, color=embed_color)
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

    print("Adding message ID to database...", end=" ", flush=True)
    updateQuery = f"UPDATE resolutions SET message_id = {reply.id} WHERE link = '{incidentURL}'"
    cursor.execute(updateQuery)
    db.commit()
    print("Done")
    print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")


@bot.event
async def on_ready():  # execute when bot is ready
    global channel
    channel = bot.get_channel(946437156086358016)
    await channel.send("Bot is online !")
    print("Bot is ready !")
    print("Starting processing loop...")
    # check_emails.start()  # start email check loop

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    print("Shutting down...")
    await ctx.send("Shutting down...")
    sys.exit()

@bot.command()
@commands.is_owner()
async def stop(ctx):
    print("Stopping email chacking loop...")
    await ctx.send("Stopping email checking loop...")
    check_emails.stop()

@bot.command()
@commands.is_owner()
async def start(ctx):
    print("Starting email chacking loop...")
    await ctx.send("Starting email checking loop...")
    check_emails.start()

@bot.command()
@commands.is_owner()
async def clear(ctx):
    print("Fetching messages to delete...", end=" ", flush=True)
    mgs = []
    async for i in ctx.history():
        if i.embeds == []:
            mgs.append(i)
    print("Done")
    print("Deleting messages...", end=" ", flush=True)
    await channel.delete_messages(mgs)
    print(f"Done, deleted {len(mgs)} messages")
    logMessage = await ctx.send(f"Deleted `{len(mgs)} message(s)`!")
    time.sleep(5)
    await logMessage.delete()

@tasks.loop(seconds=30)
async def check_emails():

    mails = mailBox.fetchemails()

    print("Processing emails...")
    with channel.typing():
        for i in mails:
            data_list = processor.mailParser(i[0], i[1])
            processor.dumpInDatabase(data_list, data_list[7])

            if data_list[7] == "ALERT":  # If event is an alert
                await send_alert(data_list)
            elif data_list[7] == "RESOLVED":  # else if event is a resolution
                await send_resolved(data_list)

        if len(mails) == 0:
            print("No new emails to process")
        else:
            print(f"Done processing {len(mails)} email(s) !")
    
    # delete old alert messages
    print("Searching for messages older than 30 days...")
    oneMonthAgo = datetime.today() - timedelta(days=30)
    oneMonthAgoTimestamp = datetime.timestamp(oneMonthAgo)
    cursor.execute("SELECT * FROM alerts")
    alertsresults = cursor.fetchall()

    for alert in alertsresults:
        alertTimeList = alert[5].split()[:-1:]
        alertTimeString = " ".join([str(elem) for elem in alertTimeList])
        alertTimeDatetime = datetime.strptime(alertTimeString, '%d %b %Y at  %H:%M%p')
        alertTimeTimestamp = datetime.timestamp(alertTimeDatetime)
        isResolved = alert[7]
        if oneMonthAgoTimestamp > alertTimeTimestamp and isResolved != None:
            print("Found old message...", end=" ", flush=True)
            message_id = alert[8]
            try:
                message = await channel.fetch_message(message_id)
            except:
                print("Error, already deleted")
            else:
                await message.delete()
                print("Deleted")
            finally:
                print("Updating database...", end=" ", flush=True)
                updateQuery = f"UPDATE alerts SET message_id = NULL WHERE link = '{alert[6]}'"
                cursor.execute(updateQuery)
                db.commit()
                print("Done")
                print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")

    # update status
    print("Updating bot alert status...", end=" ", flush=True)
    cursor.execute("SELECT * FROM alerts")
    alertsresults = cursor.fetchall()
    cursor.execute("SELECT * FROM resolutions")
    resolutionsresults = cursor.fetchall()

    # if there is more alerts then resolutions, change status
    if len(alertsresults) > len(resolutionsresults): 
        activity = discord.Activity(name="Ongoing incident(s)", type=1)
        status = discord.Status.dnd
        await bot.change_presence(activity=activity, status=status)
        print("Done, ongoing incident(s)\n")
    else:
        await bot.change_presence(activity=None, status=None)
        print("Done, no ongoing incidents\n")

print("Starting bot...", end=" ", flush=True)
bot.run(TOKEN)  # start the bot
