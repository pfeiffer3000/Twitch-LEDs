# This is the main bot guts.
# It handles signing in to Twitch, reading chat, and sending messages.
# Thanks to Twitchio for the framework!
# wled_connect_public.py is a module that handles communications with the WLED device.

from twitchio.ext import commands, eventsub
import wled_connect_public


# === Insert your specific info here =======
access_token = "your access token here"     # This is the OAuth token for your bot account.
initial_channels = ['your channel name']    # ex: I use ['djpfeifdnb'] to connect to my own channel's chat
wled_ip = "your.IP.address.here"            # ex: 192.168.0.72
prefix_char = "!"                           # the prefix for commands
# ==========================================


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=access_token, prefix=prefix_char, initial_channels=initial_channels)
        self.esclient = eventsub.EventSubWSClient(self)

        # Set the WLED device IP address here
        self.wled_ip = wled_ip
        
        # Confirm that we can reach the WLED device
        wled_connect_public.confirm_wled_ip(self.wled_ip)
        
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is   | {self.user_id}')
        print(f"Ready!")
        print()

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot.
        if message.echo:
            print(f"    {self.nick}: {message.content}")
            return

        # Print the contents of messages to the console
        print(f"{message.author.name}: {message.content}")

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands.
        await self.handle_commands(message)

    # This error replaces the one in ext.commands.bot.event_command_errors()
    # Comment it out for the original error to show up
    async def event_command_error(self, context: commands.Context, error: Exception):
        pass

    # ========== Put COMMANDS below ========================================

    @commands.command(name="LED", aliases=("leds", "led", "light", "lights", "LEDs", "LEDS"))
    async def leds(self, ctx: commands.Context):
        # Get a list of the presets from the WLED device
        presets = wled_connect_public.list_presets(self.wled_ip)

        # Create a dictionary of preset names and IDs
        preset_id_names = wled_connect_public.get_preset_names_ids(presets)

        # Check to see if the !LED command has an argument
        if len(ctx.message.content.split()) > 1:
            input_ID = " ".join(ctx.message.content.split()[1:])

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
            
    # ==== End Commands ========================
    
bot = Bot()
bot.run()