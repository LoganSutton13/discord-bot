import discord
from discord.ext import commands
from discord import app_commands
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
    
    # Sync application commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!help or /help for commands"))

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

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
@app_commands.describe(message="The message to echo")
async def slash_echo(interaction: discord.Interaction, message: str):
    """Slash command version of echo"""
    await interaction.response.send_message(message)

@bot.tree.command(name="blueberry", description="Secret Command")
@app_commands.describe(message='How many?')
async def blueberry(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message("<3"*amount)


@bot.tree.command(name="clear", description="Clear a specified number of messages")
@app_commands.describe(amount="Number of messages to delete (max 100)")
async def slash_clear(interaction: discord.Interaction, amount: int = 5):
    """Slash command version of clear"""
    # Check permissions
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message("You can only delete up to 100 messages at once!", ephemeral=True)
        return
    
    if amount < 1:
        await interaction.response.send_message("Please specify a number greater than 0!", ephemeral=True)
        return
    
    # Defer the response since deletion might take time
    await interaction.response.defer(ephemeral=True)
    
    # Delete messages (excluding the interaction message)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {len(deleted)} messages!", ephemeral=True)

# Prefix Commands (keeping existing ones)
@bot.command(name='hello')
async def hello(ctx):
    """Simple hello command"""
    await ctx.send(f'Hello {ctx.author.mention}! 👋')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='info')
async def info(ctx):
    """Display server information"""
    guild = ctx.guild
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
    
    await ctx.send(embed=embed)

@bot.command(name='echo')
async def echo(ctx, *, message):
    """Echo a message"""
    await ctx.send(message)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    """Clear a specified number of messages (default: 5)"""
    if amount > 100:
        await ctx.send("You can only delete up to 100 messages at once!")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
    await ctx.send(f"Deleted {len(deleted) - 1} messages!", delete_after=3)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
    else:
        bot.run(token)