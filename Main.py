import requests
import json
import datetime

# TODO: Exception handling


def get_prayer_times():

    Country_to_search = "TURKEY"  # Ülke
    Province_to_search = "ANKARA"  # Şehir
    District_to_search = "ANKARA"  # İlçe

    # Find country ID
    countries = requests.get("http://ezanvakti.herokuapp.com/ulkeler")
    for data_country in countries.json():
        if data_country["UlkeAdiEn"] == Country_to_search.upper():
            country_id = data_country["UlkeID"]

    # Find province ID
    url_province = "http://ezanvakti.herokuapp.com/sehirler?ulke=" + country_id
    provinces = requests.get(url_province)
    for data_province in provinces.json():
        if data_province["SehirAdiEn"] == Province_to_search.upper():
            province_id = data_province["SehirID"]

    # Find district ID
    url_district = "http://ezanvakti.herokuapp.com/ilceler?sehir=" + province_id
    districts = requests.get(url_district)
    for data_district in districts.json():
        if data_district["IlceAdiEn"] == District_to_search.upper():
            district_id = data_district["IlceID"]

    # Get prayer times for the district
    url_prayer = "http://ezanvakti.herokuapp.com/vakitler?ilce=" + district_id
    prayer = requests.get(url_prayer)
    return prayer.json()


def write_to_file(filename, data):
    file = open(filename + ".ezan", mode='w', encoding='utf-8')
    file.write(json.dumps(data))
    file.close()
    return

def read_file(filename):
    file = open(filename + ".ezan", mode='r', encoding='utf-8')
    data = json.loads(file.read())
    present_day = datetime.datetime.now()
    present_day = present_day.strftime('%d.%m.%Y')
    print(data)
    for day in data:
        if day["MiladiTarihKisa"] == present_day:
            print(day["Aksam"])


#write_to_file("testfile01", get_prayer_times())
read_file("testfile01")

