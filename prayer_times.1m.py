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

# TODO: Add location name to argparser
# TODO: Cache multiple locations.

args = parser.parse_args()

# Get script fullpath
SCRIPT_PATH = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"

# For printing to stderr
def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Get 30-day prayer times for the given location data
def get_prayer_times():

    # Default location
    country = "TURKEY"  # Ülke
    province = "ANKARA"  # Şehir
    district = "ANKARA"  # İlçe
    url = "https://ezanvakti.herokuapp.com"
    countries, provinces, districts, prayer = ("",)*4


    location = {31: {"District_Name": "val", "District_ID": "val"}}


    try:
        # If no argument given, run according to district id cached in ptimes.json (if exists)
        if args.location == 0:
            with open(f"{SCRIPT_PATH}.ptimes.json", mode="r", encoding="utf-8") as json_file:
                data = json.loads(json_file.read())
                district_id = data[31]["District_ID"]
        else:
            district_id = args.location
            prayer = requests.get(url + f"/vakitler?ilce={district_id}")
            prayer[31] = {"District_Name": "ANKARA", "District_ID": district_id }
            return prayer.json()
        # Dictionary key '31' hardcoded as the json file holds only 30, ugly but works.

    except (json.decoder.JSONDecodeError,  FileNotFoundError) as error:
        # File not found, run with default location and set current location as ANKARA, ID: 9206
        prayer = requests.get(url + f"/vakitler?ilce=9206")
        prayer[31] = {"District_Name": "ANKARA", "District_ID": "9206"}
        return prayer.json()

    except (NameError, KeyError) as error:
        # No location specified, run with default location and set current location as ANKARA, ID: 9206
        prayer = requests.get(url + f"/vakitler?ilce=9206")
        prayer[31] = {"District_Name": "ANKARA", "District_ID": "9206"}
        return prayer.json()

    except:
        if "<Response [429]>" in str(prayer):
            errprint("HTTP error 429 (Too Many Requests)")
        else:
            errprint("No network")
            raise SystemExit(0)


        # Check whether prayer times of args.location (which merely is a DistrictID) is contained 
        # (cached) in .ptimes.json file. If not request for it from https://ezanvakti.herokuapp.com . 
        # At the end, toggle "current"


    # Read .ptimes.json and find the location which "current" flag is set to true and go on with that one. 
    # If there is no prayer times which "current" is set true, then select and mark first one as default (current:true). 
    # If there is no prayer times in .ptimes.json (i.e. it is empty or corrupted), request prayer times for Ankara as default.
    
    # All the above comments mean that .ptimes.json data structure needs to be changed a little bit. 
    # (e.g. we need "current" flag)


# Dump JSON formatted data to file
def write_to_file(data):
    with open(f"{SCRIPT_PATH}.ptimes.json", "w") as json_file:
        json.dump(data, json_file)

# Run the script with given error text
def rerun(error_text):
    errprint(error_text)
    write_to_file(get_prayer_times())
    convert_datetime(f"{SCRIPT_PATH}.ptimes.json")

# Convert JSON formatted file to datetime object
def convert_datetime(filename):
    data = []

    try:
        with open(filename, mode="r", encoding="utf-8") as json_file:
            data = json.loads(json_file.read())
    except json.decoder.JSONDecodeError:
        rerun("Cache file corrupted, downloading file...")
    except FileNotFoundError:
        rerun("Cache file not found, downloading file...")
        return
    present_time = datetime.datetime.now()
    present_time = present_time - datetime.timedelta(microseconds=present_time.microsecond)

    for ptimes in data:
        try:
            gregorian_date = ptimes["MiladiTarihKisa"]
            if gregorian_date == present_time.strftime("%d.%m.%Y"):
                index_nextday = data.index(ptimes) + 1
                date_format = "%d.%m.%Y%H:%M"
                
                maghrib = datetime.datetime.strptime(gregorian_date + ptimes["Aksam"],  date_format)
                sunrise = datetime.datetime.strptime(gregorian_date + ptimes["Gunes"],  date_format)
                asr     = datetime.datetime.strptime(gregorian_date + ptimes["Ikindi"], date_format)
                fajr    = datetime.datetime.strptime(gregorian_date + ptimes["Imsak"],  date_format)
                dhuhr   = datetime.datetime.strptime(gregorian_date + ptimes["Ogle"],   date_format)
                isha    = datetime.datetime.strptime(gregorian_date + ptimes["Yatsi"],  date_format)

                try:
                    fajr_next = datetime.datetime.strptime(
                        data[index_nextday]["MiladiTarihKisa"] + data[index_nextday]["Imsak"], date_format)
                except IndexError:
                    rerun("Cache is outdated, updating...")

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
        except KeyError:
            rerun("Unidentified JSON file, downloading file from server: https://ezanvakti.herokuapp.com  ...")
    rerun("Cache is outdated, updating...")


convert_datetime(f"{SCRIPT_PATH}.ptimes.json")


# print("---")
# print("Locations")
# print("-- Select Country")
# all_places = {}
# with open(f"{SCRIPT_PATH}.places.json", mode="r", encoding="utf-8") as json_file:
#     all_places = json.loads(json_file.read())
# # if args.country == 0:
# for country in all_places:
#     # print(f"-- {country['UlkeAdiEn']} | bash='{SCRIPT_PATH}prayer_times.1m.py -c {country['UlkeID']}' terminal=false refresh=true")
#     print(f"-- {country['UlkeAdiEn']}")
#     for province in country['province']:
#         print(f"---- {province['SehirAdiEn']}")
#         for district in province['district']:
#             print(f"------ {district['IlceAdiEn']} | bash='{SCRIPT_PATH}prayer_times.1m.py -l {district['IlceAdiEn']}' terminal=false refresh=true")
# else:
#     for country in all_places:
#         if(str(args.country) == str(country['UlkeID'])):
#             for province in country["province"]:
#                 print(f"-- {province['SehirAdiEn']}")