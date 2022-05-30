import discord
from discord.ext import tasks
from dotenv import dotenv_values
from datetime import datetime as dt
from get_info import send_daily_notification

####################INITS_VARIABLE####################
client = discord.Client()
secrets = dotenv_values(".env")
token_discord = secrets["DISCORD_TOKEN"]
channel_id = secrets["CHANNEL_ID"]
######################MAIN#################################

@tasks.loop(minutes = 1)
async def send_notification_at_x_time(client) -> None:
    now = dt.now()
    if (now.strftime("%H:%M") != "00:00"):
        return
    await send_daily_notification(client, (int)(channel_id))

@client.event
async def on_ready():
    send_notification_at_x_time.start(client)

client.run(token_discord)
