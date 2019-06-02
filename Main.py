import requests
import json
import datetime

# TODO: Exception handling


def get_prayer_times():

    country = "TURKEY"  # Ülke
    province = "ANKARA"  # Şehir
    district = "ANKARA"  # İlçe
    url = "https://ezanvakti.herokuapp.com"

    # Find country ID
    countries = requests.get(url + "/ulkeler")
    for data_country in countries.json():
        if data_country["UlkeAdiEn"] == country.upper():
            country_id = data_country["UlkeID"]

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
    with open(filename, mode='r', encoding='utf-8') as json_file:
        data = json.loads(json_file.read())
    present_time = datetime.datetime.now()
    for ptime in data:
        if ptime["MiladiTarihKisa"] == present_time.strftime('%d.%m.%Y'):
            maghrib = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Aksam"], '%d.%m.%Y%H:%M')
            sunrise = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Gunes"], '%d.%m.%Y%H:%M')
            asr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ikindi"], '%d.%m.%Y%H:%M')
            fajr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Imsak"], '%d.%m.%Y%H:%M')
            dhuhr = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Ogle"], '%d.%m.%Y%H:%M')
            isha = datetime.datetime.strptime(ptime["MiladiTarihKisa"] + ptime["Yatsi"], '%d.%m.%Y%H:%M')

            if present_time < fajr:
                print("Fajr:", datetime.datetime.strftime(fajr, '%H:%M'))
                print("Remaining time until fajr:", fajr - present_time)
            elif present_time < sunrise:
                print("Sunrise:", datetime.datetime.strftime(sunrise, '%H:%M'))
                print("Remaining time until sunrise:", sunrise - present_time)
            elif present_time < dhuhr:
                print("Dhuhr:", datetime.datetime.strftime(dhuhr, '%H:%M'))
                print("Remaining time until dhuhr:", dhuhr - present_time)
            elif present_time < asr:
                print("Asr:", datetime.datetime.strftime(asr, '%H:%M'))
                print("Remaining time until asr:", asr - present_time)
            elif present_time < maghrib:
                print("Maghrib:", datetime.datetime.strftime(maghrib, '%H:%M'))
                print("Remaining time until maghrib:", maghrib - present_time)
            elif present_time < isha:
                print("Isha:", datetime.datetime.strftime(isha, '%H:%M'))
                print("Remaining time until isha:", isha - present_time)
            else:
                print("no")
            return

    print("Cache is outdated. Updating...")
    write_to_file(get_prayer_times())
    convert_datetime('.ptimes.json')


# write_to_file(get_prayer_times())
convert_datetime('.ptimes.json')

