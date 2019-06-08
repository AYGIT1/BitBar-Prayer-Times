import datetime
import json
import sys
import requests


# For printing to stderr
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


# Dump JSON formatted data to file
def write_to_file(data):
    with open('.ptimes.json', 'w') as json_file:
        json.dump(data, json_file)


def rerun(error_text):
    errprint(error_text)
    write_to_file(get_prayer_times())
    convert_datetime('.ptimes.json')


# Convert JSON formatted file to datetime object
def convert_datetime(filename):
    data = []
    try:
        with open(filename, mode='r', encoding='utf-8') as json_file:
            try:
                data = json.loads(json_file.read())
            except json.decoder.JSONDecodeError:
                rerun("Cache file corrupted, downloading file...")
    except FileNotFoundError:
        rerun("Cache file not found, downloading file...")
        return 1
    present_time = datetime.datetime.now()
    present_time = present_time - datetime.timedelta(microseconds=present_time.microsecond)
    for ptime in data:
        try:
            if ptime["MiladiTarihKisa"] == present_time.strftime('%d.%m.%Y'):
                index_nextday = data.index(ptime) + 1
                maghrib = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Aksam"], '%d.%m.%Y%H:%M')
                sunrise = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Gunes"], '%d.%m.%Y%H:%M')
                asr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ikindi"], '%d.%m.%Y%H:%M')
                fajr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Imsak"], '%d.%m.%Y%H:%M')
                dhuhr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ogle"], '%d.%m.%Y%H:%M')
                isha = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Yatsi"], '%d.%m.%Y%H:%M')
                try:
                    fajr_next = datetime.datetime.strptime(
                        data[index_nextday]["MiladiTarihKisa"] + data[index_nextday]["Imsak"], '%d.%m.%Y%H:%M')
                except IndexError:
                    rerun("Cache is outdated, updating...")
                ptimeslist = [fajr, sunrise, dhuhr, asr, maghrib, isha, fajr_next]
                pnameslist = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
                for ptime in ptimeslist:
                    if present_time < ptime:
                        remtime = str(ptime - present_time)
                        remtime = ':'.join(remtime.split(':')[0:2])
                        print(remtime)
                        for pname in pnameslist:
                            print(pname + ':\t', datetime.datetime.strftime(ptime, '%H:%M'),
                                  '| font = Menlo size = 12')
                        return
        except KeyError:
            rerun("Unidentified JSON file, downloading file from server: https://ezanvakti.herokuapp.com  ...")
    rerun("Cache is outdated, updating...")


convert_datetime('.ptimes.json')
