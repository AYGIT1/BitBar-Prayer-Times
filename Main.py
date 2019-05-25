import requests
import json

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


def write_to_file(data):
    file = open("test.ezan", mode='w', encoding='utf-8')
    for element in data:
        file.write(json.dumps(element) + "/n")
    file.close()
    return


write_to_file(get_prayer_times())
