import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='.env')


# Retrieve the token and webhook URLs from the environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
STEAM_WEBHOOK_URL = os.getenv('STEAM_WEBHOOK_URL')
UBISOFT_CONNECT_WEBHOOK_URL = os.getenv('UBISOFT_CONNECT_WEBHOOK_URL')

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Enable receiving message events
intents.guilds = True  # Enable receiving guild events

# Define your bot with the command prefix and intents
class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Sync the command tree to a specific guild to avoid changes propagation delay
        GUILD_ID = '1224193663685361705'  # Replace with your guild ID
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

# Initialize the bot
bot = MyBot(command_prefix='/', intents=intents)

# Define the webhooks
webhooks = {
    'Steam': STEAM_WEBHOOK_URL,
    'Ubisoft Connect': UBISOFT_CONNECT_WEBHOOK_URL
}

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')

@bot.tree.command(name='postgameaccount')
@app_commands.describe(platform='Select the platform', account_number='Account number', username='Username', password='Password')
@app_commands.choices(platform=[
    app_commands.Choice(name='Steam', value='Steam'),
    app_commands.Choice(name='Ubisoft Connect', value='Ubisoft Connect')
])
async def post_game_account(interaction: discord.Interaction, platform: app_commands.Choice[str], account_number: int, username: str, password: str):
    platform = platform.value
    if platform not in webhooks:
        await interaction.response.send_message(f'Invalid platform. Choose from: {", ".join(webhooks.keys())}')
        return

    webhook_url = webhooks[platform]
    data = {
        "content": "|| @everyone || 🎮",
        "embeds": [
            {
                "title": f"**🎉 {platform} Account - {account_number} 🌟**",
                "description": f"_**Note: **After downloading the game, please ensure your internet is turned off while playing, as this account belongs to someone. _\n\n**Account information:**\nUsername:  `{username}`\nPassword: `{password}`",
                "color": 2829617
            }
        ],
        "attachments": []
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        await interaction.response.send_message('Account information posted successfully!')
    else:
        await interaction.response.send_message('Failed to post account information.')

# Run the bot with your token
bot.run(DISCORD_BOT_TOKEN)