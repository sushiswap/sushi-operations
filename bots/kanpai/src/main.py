import discord
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv

from utils.kanpai_fetcher import fetch_kanpai_data


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=discord.Intents.default())


@tasks.loop(hours=24)
async def change_kanpai_status():
    eth_amounts = fetch_kanpai_data()
    await client.change_presence(
        activity=discord.Game(
            name=f"Kanpai - daily: {int(eth_amounts['day_before'])} eth, weekly: {int(eth_amounts['week_before'])} eth, monthly: {int(eth_amounts['month_before'])} eth, total: {int(eth_amounts['start_of_year'])} eth"
        )
    )


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    change_kanpai_status.start()


client.run(DISCORD_TOKEN)
