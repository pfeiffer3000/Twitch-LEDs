# Twitch-LEDs
 Connect Twitch chat to addressable LEDs via WLED


The software for the Twitch bot is written in Python. The Twitch parts of the code are based on the wonderful work done by the Twitchio team (https://twitchio.dev/). Check their projects and documentation for more information about how to use this awesome framework!

Overall software description:
The software establishes a connection with Twitch chat servers, then listens to the chat. If a message starts with “!LED”, then the bot sends a message to the WLED device to change the preset. For example, if a user typed, “!LED 3”, then the bot would recognize this command, and reach out to the ESP32 to tell WLED to display the third preset, or the preset with an ID of 3, which was our Rainbow preset. The user could also type “!LED Rainbow” to achieve the same result.

Note: The Twitch part of our code won’t work right out of the box. You’ll first need to obtain an ‘access token’ from Twitch that allows you to programmatically interact with the Twitch API (Application Programming Interface). This might take some research and time to figure out for your own bot depending on your level of familiarity with APIs. A good place to get started is here: https://twitchtokengenerator.com/. Warning: don’t share your access token with anyone! This means that you should delete your access code from anything that you share publicly. Anyone with your access code can act as you in chats across Twitch or change information about your channel.


There are two python modules in the github repository:

wled_connect.py – This handles connections to the ESP32 running WLED. It has functionality that allow you to test things such as: check the connection between the computer and the ESP32; change preconfigured WLED presets; or list the presets stored on the device. The computer running wled_connect.py will need to be on the same network as the ESP32 so they can talk to each other over WiFi. In the ‘main()’ function of wled_connect.py, manually type the IP address of your ESP32 (ex: 192.168.0.72), then run the program. You can find the IP address of the ESP32 from the WLED Config settings (we did this earlier when we set up WLED). Once running, the wled_connect.py will prompt you to enter the ID or name of a preset that you’d like to display. Type the number of a preset to watch it change.

bot_Twitch_main.py – This is the main guts of the Twitch bot. It handles establishing a connection to the Twitch servers, reading the chat in real time, and dealing with logic when needed. You can do all sorts of cool things here similar to all the bots you’ve seen on other peoples’ channels. Check https://twitchio.dev for more info on all the amazing stuff they have packed into their library. This bot_Twitch_main.py program focuses on reading the chat for the specific command, “!LED”. Any text following that command will be read by the program and then sent to the ESP32. To get it working you’ll need to add a few things in the code: your specific Twitch API access token; the IP address of the ESP32 running WLED; and the Twitch channel you want to connect to.

Insert the access token into your code where it says, “your access token here”. Insert the IP address of the ESP32 into the code where it says, “your.IP.address.here”. And finally, insert the name of the target channel into, “your channel name”.

Note: Changes in local networks, like power loss or resetting your WiFi router might result in your ESP32 obtaining a different IP address. If your code isn’t working, this is a good place to start troubleshooting.

Run the program bot_Twitch_main.py, and if all goes well, then you’ll have a working connection between your Twitch chat and WLED! 
