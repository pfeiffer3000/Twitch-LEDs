# This connects to the WLED device at the specified IP address,
# retrieves a list of presets, and allows the user to set a preset by ID or name.

import requests
import json

# url = "http://<ip_address>/json/" to get the whole JSON file from the WLED device. 
# If you want to get specific info, use the following paths:
# current state:        /json/state 
# general info:         /json/info
# array of effects:     /json/eff 
# array of palettes:    /json/pal
# presets data:         /presets.json

def confirm_wled_ip(wled_ip: str) -> int:
    # Checks to see if the WLED device is reachable
    url: str = f"http://{wled_ip}"
    print(f"Connecting to WLED device at {wled_ip}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Connected to WLED device at {wled_ip} !")
        else:
            print(f"Failed to connect to WLED device at {wled_ip}. Status code: {response.status_code}")
            print("Please check the IP address and try again.")
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to WLED device: {e}")
        return None
    
def set_to_preset(wled_ip: str, preset: str) -> None:
    # Send the ID number of the preset you want to set.
    # These are the same as the "Preset IDs" in the WLED app.
    # The "ps" in data is the preset ID number.
    url: str = f"http://{wled_ip}/json/state"
    data: dict = {"on": True, "transition": 7, "ps": preset}
    requests.post(url, json=data)

def turn_off_LEDs(wled_ip: str) -> None:
    print(f"Turning off {wled_ip}...")
    url: str = f"http://{wled_ip}/json/state"
    data: dict = {"on": False, "transition": 30}
    requests.post(url, json=data)

def list_presets(wled_ip: str) -> dict:
    # Get the preset data in json format from the WLED device
    url: str = f"http://{wled_ip}/presets.json"
    response = requests.get(url)
    if response.status_code == 200:
        presets = response.json()
        # Write the presets to a json file for later use.
        json.dump(presets, open("WLED_presets.json", "w"), indent=4)
        print(f"Retrieved presets from {wled_ip}!")
    else:
        print(f"Failed to retrieve presets from {wled_ip}. Status code: {response.status_code}")
        presets = {}

    return presets

def get_preset_names_ids(presets: dict) -> dict:
    # Get the preset names and IDs from the presets data
    return {preset: data["n"] for preset, data in presets.items() if data.get("n")}



# ========== Main function ==========================================
def main():
    # Set your WLED device IP address here
    wled_ip: str = 'your.IP.address.here' # '192.168.0.72'

    # Confirm the that we can talk to the WLED device
    status_code: int = confirm_wled_ip(wled_ip)
    if status_code != 200:
        print("Exiting...")
        return

    # Get a list of the presets on the WLED device
    presets: dict = list_presets(wled_ip)
    preset_id_names: dict = get_preset_names_ids(presets)
    
    while True:
        input_ID: str = input("Enter preset ID or name: ")
        if input_ID.isdigit() and input_ID in presets.keys():
            preset_id: str = input_ID
        elif input_ID in preset_id_names.values():
            preset_id: str = [k for k, v in preset_id_names.items() if v == input_ID][0]
        else:
            print(f"Invalid preset name or ID. Available presets: {preset_id_names}")
            continue
        print(f"Setting preset {preset_id}: {preset_id_names[preset_id]}")
        set_to_preset(wled_ip, preset_id)


if __name__ == "__main__":
    main()
