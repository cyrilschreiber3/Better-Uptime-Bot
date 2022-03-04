import os
import re
import sqlite3
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import discordBot
import mailBox
import processor


discordBot.client.run(discordBot.TOKEN) # start the bot