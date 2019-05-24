import requests


Country_to_search = "TURKEY"        #Ülke
Province_to_search = "ANKARA"       #Şehir
District_to_search = "cankaya"      #İlçe


def find_country_id():
    countries = requests.get("http://ezanvakti.herokuapp.com/ulkeler")
    for data in countries.json():
        if data["UlkeAdiEn"] == Country_to_search.upper():
            print(data)
            return data["UlkeID"]


def find_province_id(ID):
    url = "http://ezanvakti.herokuapp.com/sehirler?ulke=" + ID
    provinces = requests.get(url)
    for data in provinces.json():
        if data["SehirAdiEn"] == Province_to_search.upper():
            print(data)
            return data["SehirID"]


def find_district_id(ID):
    url = "http://ezanvakti.herokuapp.com/ilceler?sehir=" + ID
    districts = requests.get(url)
    for data in districts.json():
        if data["IlceAdiEn"] == Province_to_search.upper():
            print(data)
            return data["IlceID"]


def pull_prayer_times(ID):
    return


def write_to_file():
    file = open("test.ezan", mode='w', encoding='utf-8')
    return



print("test")
find_district_id(find_province_id(find_country_id()))
