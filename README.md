# Discord Bot

A simple Discord bot built with Python and discord.py library.

## Features

- **Hello Command**: Greets users with a friendly message
- **Ping Command**: Shows bot latency
- **Info Command**: Displays server information in an embed
- **Echo Command**: Repeats user messages
- **Clear Command**: Deletes specified number of messages (requires permissions)

## Setup Instructions

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Go to "OAuth2" → "URL Generator"
6. Select "bot" under scopes
7. Select the permissions you want (at minimum: Send Messages, Read Message History, Use Slash Commands)
8. Use the generated URL to invite your bot to your server

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Create a `.env` file in the project root
2. Add your bot token:
```
DISCORD_TOKEN=your_actual_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Commands

- `!hello` - Greets the user
- `!ping` - Shows bot latency
- `!info` - Displays server information
- `!echo <message>` - Repeats the message
- `!clear [amount]` - Deletes messages (default: 5, max: 100)
- `!help` - Shows all available commands

## File Structure

```
discord-bot/
├── bot.py              # Main bot code
├── requirements.txt     # Python dependencies
├── env_example.txt     # Example environment variables
└── README.md          # This file
```

## Customization

You can easily add new commands by creating new functions with the `@bot.command()` decorator. For example:

```python
@bot.command(name='custom')
async def custom_command(ctx):
    await ctx.send("This is a custom command!")
```

## Troubleshooting

- **Bot not responding**: Make sure the bot has the correct permissions in your server
- **Token error**: Verify your bot token is correct in the `.env` file
- **Permission errors**: Ensure the bot has the necessary permissions for the commands you're trying to use

## Security Notes

- Never share your bot token publicly
- Keep your `.env` file in your `.gitignore`
- Regularly rotate your bot token if compromised