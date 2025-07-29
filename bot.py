import discord
from discord.ext import commands
import os
import asyncio
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
# intents.members = True  # Commented out to avoid privileged intents error

bot = commands.Bot(command_prefix='!', intents=intents)

# Rate limiting variables
last_command_time = {}
RATE_LIMIT_DELAY = 1.0  # 1 second between commands per user

# Fortnite api url
url = 'https://api.fortnite.com/ecosystem/v1'

async def check_rate_limit(interaction: discord.Interaction) -> bool:
    """Check if user is rate limited"""
    user_id = interaction.user.id
    current_time = time.time()
    
    if user_id in last_command_time:
        time_since_last = current_time - last_command_time[user_id]
        if time_since_last < RATE_LIMIT_DELAY:
            remaining_time = RATE_LIMIT_DELAY - time_since_last
            await interaction.response.send_message(
                f"⏰ Please wait {remaining_time:.1f} seconds before using another command!",
                ephemeral=True
            )
            return False
    
    last_command_time[user_id] = current_time
    return True

async def command_exception_handler(interaction: discord.Interaction, e: discord.errors.HTTPException):
    if e.status == 429:
            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
            await interaction.response.send_message(
                f"🔄 Discord is rate limiting requests. Please wait {retry_after} seconds and try again.",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {e}",
            ephemeral=True
        )

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Sync slash commands with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
            break
        except discord.errors.HTTPException as e:
            if e.status == 429 and attempt < max_retries - 1:
                retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
                print(f"Rate limited during command sync. Waiting {retry_after} seconds...")
                await asyncio.sleep(retry_after)
            else:
                print(f"Failed to sync commands: {e}")
                break
        except Exception as e:
            print(f"Failed to sync commands: {e}")
            break
    
    # Set bot status
    try:
        await bot.change_presence(activity=discord.Game(name="/help for commands"))
    except Exception as e:
        print(f"Failed to set bot status: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler"""
    print(f"Error in {event}: {args} {kwargs}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Handle errors in slash commands"""
    if isinstance(error, discord.app_commands.CommandInvokeError):
        original_error = error.original
        if isinstance(original_error, discord.errors.HTTPException):
            if original_error.status == 429:
                retry_after = original_error.retry_after if hasattr(original_error, 'retry_after') else 5
                await interaction.response.send_message(
                    f"🔄 Discord is rate limiting requests. Please wait {retry_after} seconds and try again.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ An error occurred: {original_error}",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                f"❌ An unexpected error occurred: {str(original_error)}",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)}",
            ephemeral=True
        )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "WSU":
        await message.channel.send("WSU is the best!")
        

# Application Commands (Slash Commands)
@bot.tree.command(name='get_map', description='Get a Fortnite map')
async def get_map(interaction: discord.Interaction, map_code: str):
    """Get a Fornite map"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        response = requests.get(f"{url}/islands/{map_code}")
        if response.status_code == 200:
            data = response.json()
            map_name = data['displayName']
            creator_code = data['creatorCode']
            await interaction.response.send_message(f"Map: {map_name}\nCreator: {creator_code}")
        else:
            await interaction.response.send_message(f"Failed to get map: {response.status_code}")
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)

@bot.tree.command(name="hello", description="Say hello to the bot")
async def slash_hello(interaction: discord.Interaction):
    """Slash command version of hello"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        await interaction.response.send_message(f'Hello {interaction.user.mention}! 👋')
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)

@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    """Slash command version of ping"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        latency = round(bot.latency * 1000)
        await interaction.response.send_message(f'Pong! Latency: {latency}ms')
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)

@bot.tree.command(name="info", description="Display server information")
async def slash_info(interaction: discord.Interaction):
    """Slash command version of info"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        guild = interaction.guild
        embed = discord.Embed(
            title=f"Server Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.response.send_message(embed=embed)
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)
        

@bot.tree.command(name="echo", description="Echo a message")
async def slash_echo(interaction: discord.Interaction, message: str):
    """Slash command version of echo"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        await interaction.response.send_message(message)
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)


@bot.tree.command(name="blueberry", description="Secret Command")
async def blueberry(interaction: discord.Interaction, amount: int):
    """Secret blueberry command"""
    if not await check_rate_limit(interaction):
        return
    
    try:
        await interaction.response.send_message("<3"*amount)
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)
        

@bot.tree.command(name="clear", description="Clear messages from the channel")
async def slash_clear(interaction: discord.Interaction, amount: int = 5):
    """Slash command version of clear"""
    if not await check_rate_limit(interaction):
        return
    
    try:
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
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)


@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show all available slash commands"""
    if not await check_rate_limit(interaction):
        return
    
    try:
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
    except discord.errors.HTTPException as e:
        await command_exception_handler(interaction, e)
        

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
    else:
        bot.run(token)