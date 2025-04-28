# This is the main bot guts.
# It handles signing in to Twitch, authenticating tokens, setting up webhooks, reading chat, and sending messages.
# Thanks to TwitchIO for the framework!
# wled_connect_public.py is a module that handles communications with the WLED device.

import asyncio
import logging
import sqlite3
import asqlite
import twitchio
from twitchio.ext import commands
from twitchio import eventsub
import wled_connect_public

LOGGER: logging.Logger = logging.getLogger("Bot")


# === Insert your specific info here =======
CLIENT_ID = ""      # The CLIENT ID from the Twitch Dev Console
CLIENT_SECRET = ""  # The CLIENT SECRET from the Twitch Dev Console
BOT_ID = ""         # The Account ID of the bot user. Make sure this is a string, not an int.
OWNER_ID = ""       # Your personal User ID. Make sure this is a string, not an int.
WLED_IP = ""        # ex: 192.168.0.72
# ==========================================

class Bot(commands.Bot):
    def __init__(self, *, token_database: asqlite.Pool) -> None:
        self.token_database = token_database
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=OWNER_ID,
            prefix="!",
        )

        LOGGER.info("==== Bot initialized ====")

    async def setup_hook(self) -> None:
        # Add our component which contains our commands
        await self.add_component(CommandsComponent(self))

        # https://twitchio.dev/en/latest/references/events/events.html for more on the webhook subscriptions below

        # Subscribe to read chat (event_message) from our channel as the bot
        # This creates and opens a websocket to Twitch EventSub
        subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=OWNER_ID, user_id=BOT_ID)
        await self.subscribe_websocket(payload=subscription)

    async def event_ready(self) -> None:
        # do this when the bot is ready

        # log the bot's name and id
        user = await self.fetch_users(ids=[self.bot_id])
        self.nick = user[0].name        
        LOGGER.info(f"Successfully logged in as {self.nick}:{self.bot_id}")
        LOGGER.info(f"Ready!")


    # ==== DATABASE STUFF ====
    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens internally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def load_tokens(self, path: str | None = None) -> None:
        # We don't need to call this manually, it is called in .login() from .start() internally...

        async with self.token_database.acquire() as connection:
            rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        for row in rows:
            await self.add_token(row["token"], row["refresh"])

    async def setup_database(self) -> None:
        # Create our token table, if it doesn't exist..
        query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
        async with self.token_database.acquire() as connection:
            await connection.execute(query)


# ========================================================================================
class CommandsComponent(commands.Component):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # Set the WLED device IP address here
        self.wled_ip = WLED_IP
        
        # Confirm that we can reach the WLED device
        wled_connect_public.confirm_wled_ip(self.wled_ip)

    # ==== MESSAGE HANDLER ====
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        LOGGER.info(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    # ==== COMMANDS ====
    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.reply(f'Testing of the mugtion hacking system complete!')

    @commands.command(name="LED", aliases=("leds", "led", "light", "lights", "LEDs", "LEDS"))
    async def leds(self, ctx: commands.Context):
        # Get a list of the presets from the WLED device
        presets = wled_connect_public.list_presets(self.wled_ip)

        # Create a dictionary of preset names and IDs
        preset_id_names = wled_connect_public.get_preset_names_ids(presets)

        # Check to see if the !LED command has an argument
        if len(ctx.message.text.split()) > 1:
            input_ID = " ".join(ctx.message.text.split()[1:])

            # Check if the input is a number...
            if input_ID.isdigit() and input_ID in presets.keys():
                preset_id = input_ID
            # ...or a string...
            elif input_ID in preset_id_names.values():
                preset_id = [k for k, v in preset_id_names.items() if v == input_ID][0]
            # ...or if it's neither.
            else:
                preset_id = None
                presets_string = ", ".join([f"{k}, {v}" for k, v in preset_id_names.items()])
                await ctx.send(f"Invalid preset name or ID. Available presets: {presets_string}")
            
            # If the preset ID is valid, then send the command to the WLED device!
            if preset_id:
                await ctx.send(f"Setting LED preset {preset_id}: {preset_id_names[preset_id]}")
                wled_connect_public.set_to_preset(self.wled_ip, preset_id)
        
        else:
            await ctx.send("Please provide a preset ID or name.")



# ========================================================================================
def main() -> None:
    # setup main logging instead to replace printing to the console
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb, Bot(token_database=tdb) as bot:
            await bot.setup_database()
            await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt...")


if __name__ == "__main__":
    main()