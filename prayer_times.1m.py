#!/usr/local/bin/python3
# <bitbar.title>Prayer Times BitBar</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Aykut ALADAG</bitbar.author>
# <bitbar.author.github>AYGIT1</bitbar.author.github>
# <bitbar.desc>Prayer times are based on Presidency of Religious Affairs, Turkey.</bitbar.desc>
# <bitbar.dependencies>python3</bitbar.dependencies>
# <bitbar.image></bitbar.image>
# <bitbar.abouturl>https://github.com/AYGIT1/Ezan_Saati</bitbar.abouturl>

import datetime
import json
import sys
import requests
import os
import argparse

# Redirect stderr to null by default
# sys.stderr = open(os.devnull, "w")


parser = argparse.ArgumentParser()

parser.add_argument("-l", "--location", type=int, default=0,
        help="District ID")

args = parser.parse_args()

# Get script fullpath
SCRIPT_PATH = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"

# TODO: Add "location name" key to ptimes.json file
# Default location: ANKARA / TURKEY
default_id = 9206

# For printing to stderr
def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Updates prayer times for given id and reformats ptimes.json file
def update_and_format(data, location_id):
    url = "https://ezanvakti.herokuapp.com"
    prayer = ""
    new_location = {}
    try:
        prayer = requests.get(url + "/vakitler?ilce=" + str(location_id))
        new_location["ptimes"] = prayer.json()
        new_location["location_id"] = location_id
        new_location["current"] = True
        data.append(new_location)
        # Write to file with JSON format.
        with open(f"{SCRIPT_PATH}.ptimes.json", "w") as json_file:
            json.dump(data, json_file)
    except:
        if "<Response [429]>" in str(prayer):
            errprint("HTTP error 429 (Too Many Requests)")
        else:
            errprint("No network or" + str(prayer))

        raise SystemExit(0)
    return


# Get prayer times of the selected location
def check_cache():

    try:
        with open(f"{SCRIPT_PATH}.ptimes.json", mode="r", encoding="utf-8") as json_file:
            data = json.loads(json_file.read())
            if args.location == 0:
                return
            else:
                for locations in data:
                    if args.location == locations["location_id"]:
                        locations["current"] = True
                    else:
                        locations["current"] = False
                update_and_format(data, args.location)
                return

    except (json.decoder.JSONDecodeError, FileNotFoundError, KeyError) as error:
        # Create cache file and set default location.
        data = []
        update_and_format(data, default_id)
    return


# Run the python script in case of error.
def rerun(error_text):
    errprint(error_text)
    check_cache()
    convert_datetime(f"{SCRIPT_PATH}.ptimes.json")
    return


# Convert JSON formatted file to datetime object
def convert_datetime(filename):
    data = []

    try:
        with open(filename, mode="r", encoding="utf-8") as json_file:
            data = json.loads(json_file.read())
    except (json.decoder.JSONDecodeError, FileNotFoundError) as error:
        rerun("Creating cache file...")
        return

    present_time = datetime.datetime.now()
    present_time = present_time - datetime.timedelta(microseconds=present_time.microsecond)

    for flag in data:
        if flag["current"]:
            for ptimes in flag["ptimes"]:
                gregorian_date = ptimes["MiladiTarihKisa"]
                if gregorian_date == present_time.strftime("%d.%m.%Y"):
                    index_nextday = flag["ptimes"].index(ptimes) + 1
                    date_format = "%d.%m.%Y%H:%M"

                    maghrib = datetime.datetime.strptime(gregorian_date + ptimes["Aksam"],  date_format)
                    sunrise = datetime.datetime.strptime(gregorian_date + ptimes["Gunes"],  date_format)
                    asr     = datetime.datetime.strptime(gregorian_date + ptimes["Ikindi"], date_format)
                    fajr    = datetime.datetime.strptime(gregorian_date + ptimes["Imsak"],  date_format)
                    dhuhr   = datetime.datetime.strptime(gregorian_date + ptimes["Ogle"],   date_format)
                    isha    = datetime.datetime.strptime(gregorian_date + ptimes["Yatsi"],  date_format)

                    try:
                        fajr_next = datetime.datetime.strptime(
                            flag["ptimes"][index_nextday]["MiladiTarihKisa"] + flag["ptimes"][index_nextday]["Imsak"], date_format)
                    except IndexError:
                        rerun("Cache is outdated, updating...")
                        return

                    ptimeslist = [fajr, sunrise, dhuhr, asr, maghrib, isha, fajr_next]
                    pnameslist = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
                    max_name_length = len(max(pnameslist))

                    counter_a = 0
                    counter_b = 1
                    for ptime in ptimeslist:
                        counter_a += 1
                        if present_time < ptime:
                            if (ptime - present_time) < datetime.timedelta(minutes=16):
                                remtime = str(ptime - present_time)
                                remtime = ":".join(remtime.split(":")[0:2])
                                print("0" + remtime, "| color=red\n---")
                                break
                            remtime = str(ptime - present_time)
                            remtime = ":".join(remtime.split(":")[0:2])
                            if len(remtime) < 5:
                                remtime = "0" + remtime
                            print(remtime, "\n---")
                            break
                    for ptime, pname in zip(ptimeslist, pnameslist):
                        counter_b += 1
                        padding = max_name_length - len(pname)
                        if counter_a == counter_b :
                            print(pname + padding * " " + "\t\t:", datetime.datetime.strftime(ptime, "%H:%M"),
                                  "| color = green font = Menlo size = 12")
                        else:
                            print(pname + padding*" " + "\t\t:", datetime.datetime.strftime(ptime, "%H:%M"),
                                  "| font = Menlo size = 12")
                    return
            # Remove outdated entry from list
            print ("Updating cache...")
            new_data = []
            for entries in data:
                if entries != flag:
                    new_data.append(entries)
            update_and_format(new_data,flag["location_id"])
            rerun("Update completed.")
            return
    # Run with default if no "current" flag set to true
    data = []
    update_and_format(data, default_id)
    rerun("Flag error: all false. Recreating cache...")
    return


# Print selectable locations for bitbar plugin
def print_location():
    print("---")
    print("Locations")
    print("-- Select Country")
    with open(f"{SCRIPT_PATH}.places.json", mode="r", encoding="utf-8") as json_file:
        all_places = json.loads(json_file.read())
    for country in all_places:
        print(f"-- {country['UlkeAdiEn']}")
        for province in country['province']:
            print(f"---- {province['SehirAdiEn']}")
            for district in province['district']:
                print(f"------ {district['IlceAdiEn']} | bash='{SCRIPT_PATH}prayer_times.1m.py' param1=-l param2={district['IlceID']} terminal=false refresh=true")

check_cache()
convert_datetime(f"{SCRIPT_PATH}.ptimes.json")
print_location()
