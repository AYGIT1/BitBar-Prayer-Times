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


def read_file(filename):
    with open(filename, mode='r', encoding='utf-8') as json_file:
        data = json.loads(json_file.read())
    present_day = datetime.datetime.now()
    for day in data:
        if day["MiladiTarihKisa"] == present_day.strftime('%d.%m.%Y'):
            print(day["Aksam"])
            maghrib = datetime.datetime.strptime(day["Aksam"], '%H:%M')
            sunrise = datetime.datetime.strptime(day["Gunes"], '%H:%M')
            asr = datetime.datetime.strptime(day["Ikindi"], '%H:%M')
            fajr = datetime.datetime.strptime(day["Imsak"], '%H:%M')
            dhuhr = datetime.datetime.strptime(day["Ogle"], '%H:%M')
            isha = datetime.datetime.strptime(day["Yatsi"], '%H:%M')
            print(isha - present_day)


# write_to_file(get_prayer_times())
read_file('.ptimes.json')

