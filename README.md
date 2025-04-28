# Twitch-LEDs
 Connect Twitch chat to addressable LEDs via WLED


The software for the Twitch chatbot is written in Python. The Twitch sections of the code are based on the wonderful work done by the TwitchIO team (https://twitchio.dev/). Check their projects and documentation for more information about how to use this awesome framework!

The software establishes a connection with Twitch chat servers, then listens to the chat. If a chat message starts with “!LED”, then the bot sends a message to the WLED device to change the preset. For example, if a chat user typed, “!LED 3”, then the chatbot would recognize this command, and reach out to the ESP32 to tell WLED to display the third preset, or the preset with an ID of 3, which was the Rainbow preset in the WLED_presets.json example. The chat user could also type “!LED Rainbow” to achieve the same result.

There are two python modules in the github repository:

wled_connect.py – This handles connections to the ESP32 running WLED. It has functionality that allows you to test things such as: check the connection between the computer and the ESP32; change preconfigured WLED presets; or list the presets stored on the device. The computer running wled_connect.py will need to be on the same network as the ESP32 so they can talk to each other over WiFi. In the ‘main()’ function of wled_connect.py, manually type the IP address of your ESP32 (ex: 192.168.0.72), then run the program. You can find the IP address of the ESP32 from the WLED Config settings (we did this earlier when we set up WLED). Once running, the wled_connect.py will prompt you to enter the ID or name of a preset that you’d like to display. Type the number of a preset to watch it change. If you’re just using bot_Twitch_v3.py, then you’ll never need to set the IP address of the ESP32, nor will you need to run this program as a standalone at all. Its job is to support the code in other programs.

bot_Twitch_v3.py – This is the main guts of the Twitch bot based on v3 of the TwitchIO library. It handles establishing a connection to the Twitch servers, authenticating tokens, reading the chat in real time, and dealing with logic as needed. You can do all sorts of cool things here that are similar to the bots you’ve seen on other peoples’ Twitch channels. I haven’t found something in other chatbots that I can’t emulate with TwitchIO and Python. Check https://twitchio.dev for more info on all the amazing stuff they have packed into their library. This bot_Twitch_v3.py program focuses on reading the chat for the specific command, “!LED”. Any text following that command will be read by the program and then sent to the ESP32. To get it working you’ll need to add a few things in the code outlined below.

Here is what you'll need to insert into your code: 
    * the "client ID", the "client secret", and the "bot ID" of your bot
    * your Twitch ID 
    * the IP address of the ESP32
    
You can find the client ID and client secret for your bot in the Twtich dev console after you add a project. Because I found them years ago, I don't remember how I found my Twitch ID or my bots Twitch ID, which has its own account on Twitch (my channel is 'djpfeifdnb'; my bot's is 'htpbot').

The initial workflow for v3 of TwitchIO requires you to setup some things before you begin using your bot locally. Follow their instructions here: https://twitchio.dev/en/latest/getting-started/quickstart.html#quickstart

Note: Changes in local networks, like power loss or resetting your WiFi router might result in your ESP32 obtaining a different IP address. If your code isn’t working, this is a good place to start troubleshooting.

Run the program bot_Twitch_v3.py, and if all goes well, then you’ll have a working connection between your Twitch chat and WLED!

bot_Twitch_v2.py is a version of the bot that runs on the TwitchIO v2 library.
WELD_presets.json is a copy of the test presets for my own WLED rig. Running bot_Twitch_v2.py, bot_Twich_v3.py, or wled_connect.py will overwrite my version with your own.