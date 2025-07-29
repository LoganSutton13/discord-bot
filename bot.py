import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
# intents.members = True  # Commented out to avoid privileged intents error

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="/help for commands"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "WSU":
        await message.channel.send("WSU is the best!")
        

# Application Commands (Slash Commands)
@bot.tree.command(name="hello", description="Say hello to the bot")
async def slash_hello(interaction: discord.Interaction):
    """Slash command version of hello"""
    await interaction.response.send_message(f'Hello {interaction.user.mention}! 👋')

@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    """Slash command version of ping"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'Pong! Latency: {latency}ms')

@bot.tree.command(name="info", description="Display server information")
async def slash_info(interaction: discord.Interaction):
    """Slash command version of info"""
    guild = interaction.guild
    embed = discord.Embed(
        title=f"Server Information",
        color=discord.Color.blue()
    )
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="echo", description="Echo a message")
async def slash_echo(interaction: discord.Interaction, message: str):
    """Slash command version of echo"""
    await interaction.response.send_message(message)

@bot.tree.command(name="blueberry", description="Secret Command")
async def blueberry(interaction: discord.Interaction, amount: int):
    """Secret blueberry command"""
    await interaction.response.send_message("<3"*amount)

@bot.tree.command(name="clear", description="Clear messages from the channel")
async def slash_clear(interaction: discord.Interaction, amount: int = 5):
    """Slash command version of clear"""
    # Check permissions
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message("You can only delete up to 100 messages at once!", ephemeral=True)
        return
    
    # Defer the response since we need time to delete messages
    await interaction.response.defer(ephemeral=True)
    
    # Delete messages
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {len(deleted)} messages!", ephemeral=True)

@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show all available slash commands"""
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all the available slash commands:",
        color=discord.Color.blue()
    )
    
    # Add slash commands
    embed.add_field(name="/hello", value="Greets the user", inline=True)
    embed.add_field(name="/ping", value="Shows bot latency", inline=True)
    embed.add_field(name="/info", value="Shows server information", inline=True)
    embed.add_field(name="/echo <message>", value="Repeats your message", inline=True)
    embed.add_field(name="/blueberry <amount>", value="Secret command", inline=True)
    embed.add_field(name="/clear [amount]", value="Deletes messages (default: 5)", inline=True)
    embed.add_field(name="/help", value="Shows this help message", inline=True)
    
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
    else:
        bot.run(token)