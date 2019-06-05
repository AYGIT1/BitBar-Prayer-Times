import requests
import json
import datetime
import sys


# TODO: MORE Exception handling!
# TODO: Too many recurring lines, try to use loops.


def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_prayer_times():
    country = "TURKEY"  # Ülke
    province = "ANKARA"  # Şehir
    district = "ANKARA"  # İlçe
    url = "https://ezanvakti.herokuapp.com"

    # Find country ID
    try:
        countries = requests.get(url + "/ulkeler")
        for data_country in countries.json():
            if data_country["UlkeAdiEn"] == country.upper():
                country_id = data_country["UlkeID"]
    except:
        if str(countries) == '<Response [429]>':
            errprint('HTTP error 429 (Too Many Requests)')
        else:
            errprint('No network')

    # Find province ID
    provinces = requests.get(url + f"/sehirler?ulke={country_id}")
    for data_province in provinces.json():
        if data_province["SehirAdiEn"] == province.upper():
            province_id = data_province["SehirID"]

    # Find district ID
    districts = requests.get(url + f"/ilceler?sehir={province_id}")
    for data_district in districts.json():
        if data_district["IlceAdiEn"] == district.upper():
            district_id = data_district["IlceID"]

    # Get prayer times for the district
    prayer = requests.get(url + f"/vakitler?ilce={district_id}")
    return prayer.json()


def write_to_file(data):
    with open('.ptimes.json', 'w') as json_file:
        json.dump(data, json_file)


def convert_datetime(filename):
    try:
        with open(filename, mode='r', encoding='utf-8') as json_file:
            try:
                data = json.loads(json_file.read())
            except json.decoder.JSONDecodeError:
                errprint("Cache file corrupted, downloading file...")
                write_to_file(get_prayer_times())
                convert_datetime('.ptimes.json')
    except FileNotFoundError:
        print("Cache file not found, downloading file...")
        write_to_file(get_prayer_times())
        convert_datetime('.ptimes.json')

    present_time = datetime.datetime.now()
    present_time = present_time - datetime.timedelta(microseconds=present_time.microsecond)
    for ptime in data:
        next_date = present_time + datetime.timedelta(days=1)
        if ptime["MiladiTarihKisa"] == present_time.strftime('%d.%m.%Y'):
            maghrib = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Aksam"], '%d.%m.%Y%H:%M')
            sunrise = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Gunes"], '%d.%m.%Y%H:%M')
            asr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ikindi"], '%d.%m.%Y%H:%M')
            fajr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Imsak"], '%d.%m.%Y%H:%M')
            dhuhr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ogle"], '%d.%m.%Y%H:%M')
            isha = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Yatsi"], '%d.%m.%Y%H:%M')

        if ptime["MiladiTarihKisa"] == next_date.strftime('%d.%m.%Y'):
            fajr_next = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Imsak"], '%d.%m.%Y%H:%M')
            # TODO: The statements below could be shortened.
            if present_time < fajr:
                remtime = str(fajr - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < sunrise:
                remtime = str(sunrise - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < dhuhr:
                remtime = str(dhuhr - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < asr:
                remtime = str(asr - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < maghrib:
                remtime = str(maghrib - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < isha:
                remtime = str(isha - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)
            elif present_time < fajr_next:
                remtime = str(fajr_next - present_time)
                remtime = ':'.join(remtime.split(':')[0:2])
                print(remtime)

            print('\n' '---' + '\n')
            print( 'Fajr:\t', datetime.datetime.strftime(fajr, '%H:%M'), '| font = Menlo size = 12' + '\n')
            print( 'Sunrise:\t', datetime.datetime.strftime(sunrise, '%H:%M'), '| font = Menlo size = 12' + '\n')
            print( 'Dhuhr:\t', datetime.datetime.strftime(dhuhr, '%H:%M'), '| font = Menlo size = 12' + '\n')
            print( 'Asr:\t', datetime.datetime.strftime(asr, '%H:%M'), '| font = Menlo size = 12' + '\n')
            print( 'Maghrib:\t', datetime.datetime.strftime(maghrib, '%H:%M'), '| font = Menlo size = 12' + '\n')
            print( 'Isha:\t', datetime.datetime.strftime(isha, '%H:%M'), '| font = Menlo size = 12' + '\n')
            return

    # print("no")
    # print(sunrise)

    # errprint("Cache is outdated, updating...")
    # write_to_file(get_prayer_times())
    # convert_datetime('.ptimes.json')


# write_to_file(get_prayer_times())
convert_datetime('.ptimes.json')
