import requests
import json

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


write_to_file(get_prayer_times())
