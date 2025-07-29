import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!help for commands"))

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

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