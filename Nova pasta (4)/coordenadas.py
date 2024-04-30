import requests
from geopy.geocoders import Nominatim


def obter_coordenadas_por_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        endereco = f"{data.get('logradouro', '')}, {data.get('localidade', '')}, {data.get('uf', '')}"

        geolocator = Nominatim(user_agent="geolocalização")
        #location = geolocator.geocode(query=endereco)
        location = geolocator.geocode(query=endereco, timeout=10)
        if location:
            return location.latitude, location.longitude

    return None, None


def obter_cep():
    while True:
        cep = input("CEP: ")
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("\nCep inválido, por favor digite novamente\n")
