import requests
from coordenadas import obter_coordenadas_por_cep
import numpy as np
import pandas as pd

def execute():
    _localização()

def _localização():

    escolha = int(input(f"\nDefinir localização:\nDigite 1 para CEP e 2 para latitude longitude: "))
    

    if escolha == 1:
        cep = input("\nDigite o CEP da localidade desejada: ")
        latitude, longitude = obter_coordenadas_por_cep(cep)
    elif escolha == 2:
        latitude = input("Digite a latitude desejada:")
        longitude = input("Digite a longitude desejada:")
    else:
        print("\nEscolha invalida")
        _localização()

    if latitude is not None and longitude is not None:
        print("Latitude:", latitude)
        print("Longitude:", longitude)

        _DadosDoVento(latitude,longitude)
        _previsao_15_dias(latitude, longitude)
        _HistoricoDoVento(latitude, longitude)
    else:
        print("\nNão foi possível obter as coordenadas para o CEP:", cep)

def _DadosDoVento(latitude, longitude):
    
    api_key = "bd5e378503939ddaee76f12ad7a97608"


    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}")

    if response.status_code == 200:
        data = response.json()
        _ForcaDoVento(data)
    else:
        print("\nErro ao acessar a API do OpenWeatherMap. Código de status:", response.status_code)

def _ForcaDoVento(data):

    altura_desejada = 115
    altura_referencia = 10
    alpha = 0.2  # coeficiente de potência

    if "wind" in data:
        wind_speed = data["wind"]["speed"]  # Velocidade do vento em m/s
        wind_speed_gust = data["wind"]["gust"]
        wind_direction = data["wind"].get("deg", "N/A")  # Direção do vento em graus

        wind_speed_adjusted = wind_speed * (altura_desejada / altura_referencia) ** alpha
        speed_wind = round(wind_speed_adjusted, 3)

        wind_gust_adjusted = wind_speed_gust * (altura_desejada / altura_referencia) ** alpha
        gust_wind = round(wind_gust_adjusted, 3)

        print("\nVelocidade do vento:", speed_wind , "m/s")
        print("Velocidade das rajadas de vento:", gust_wind , "m/s")
        print("Direção do vento:", wind_direction, "graus")
    else:
        print("\nNão foram encontrados dados de vento para esta localização.")

def _HistoricoDoVento(latitude, longitude):
    api_key = "d78bf35444264600964175412242804"

    start_date = "2023-01-01"
    end_date = "2023-12-31"

    url = (f"http://api.worldweatheronline.com/premium/v1/past-weather.ashx?q={latitude},{longitude}&date={start_date}&enddate={end_date}&format=json&key={api_key}")
    response = requests.get(url)

    wind_speeds = []
    wind_gusts = []
    wind_directions = []

    if response.status_code == 200:
        data = response.json()
        
        for day in data['data']['weather']:
            for hourly_data in day['hourly']:
                wind_speeds.append(int(hourly_data['windspeedKmph']))
                wind_gusts.append(int(hourly_data.get('WindGustKmph', 0)))
                wind_directions.append(int(hourly_data['winddirDegree']))
        
        _MediaHistorica(data, wind_speeds, wind_gusts, wind_directions)
    else:
        print("\nErro ao acessar a API do worldweatheronline. Código de status:", response.status_code)

def _MediaHistorica(data, speeds, gusts, directions):

    altura_desejada = 115
    altura_referencia = 10
    alpha = 0.2

    average_wind_speed = sum(speeds) / len(speeds)
    average_wind_gust = sum(gusts) / len(gusts)

    radians = np.radians(directions)
    x = np.cos(radians)
    y = np.sin(radians)

    mean_x = np.mean(x)
    mean_y = np.mean(y)

    average_wind_direction = round(np.degrees(np.arctan2(mean_y, mean_x)), 3)

    fator_conversao = 1 / 3.6

    wind_speed = average_wind_speed * fator_conversao
    wind_gust = average_wind_gust * fator_conversao

    wind_speed = wind_speed * (altura_desejada/altura_referencia) ** alpha
    wind_gust = wind_gust * (altura_desejada/altura_referencia) ** alpha

    print("\nMédia da velocidade do vento durante o ultimo ano:", round(wind_speed,3), "m/s")
    print("Média das rajadas de vento durante o ultimo ano:", round(wind_gust,3), "m/s")
    print("Média da direção do vento durante o ultimo ano:", round(average_wind_direction,3), "graus")

    _Viabilidade(data, wind_speed,wind_gust)

def _previsao_15_dias(latitude, longitude):

    api_key = "bd5e378503939ddaee76f12ad7a97608" 

    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/forecast/daily?lat={latitude}&lon={longitude}&cnt=15&appid={api_key}&units=metric"
    )

    if response.status_code == 200:
        if not response.text.strip():
            print("\nNão possuimos previsão para sua localidade.")

        else:
            data = response.json()

            altura_desejada = 115
            altura_referencia = 10
            alpha = 0.2

            wind_speed = []
            wind_gust = []
            radians = []

            for forecast in data["list"]:

                wind_speed.append(forecast["speed"])
                wind_gust.append(forecast["gust"])
                radians.append(np.radians(forecast.get("deg", "N/A")))
        
            x = np.cos(radians)
            y = np.sin(radians)

            mean_x = np.mean(x)
            mean_y = np.mean(y)

            average_wind_direction = round(np.degrees(np.arctan2(mean_y, mean_x)), 3)
            average_wind_speed = np.mean(wind_speed)
            average_wind_gust = np.mean(wind_gust)

            wind_speed_adjusted = average_wind_speed * (altura_desejada / altura_referencia) ** alpha
            wind_gust_adjusted = average_wind_gust * (altura_desejada / altura_referencia) ** alpha

            print(f"\nMédia da previsão da velociade dos ventos para os proximos 15 dias: {round(wind_speed_adjusted, 3)} m/s")
            print(f"Média da previsão das rajadas de ventos para os proximos 15 dias: {round(wind_gust_adjusted, 3)} m/s")
            print(f"Média da previsão da direção dos ventos para os proximos 15 dias: {average_wind_direction} graus")

    else:
        print("\nErro ao acessar a API do OpenWeatherMap. Código de status:", response.status_code)

def _Viabilidade(data, speed,gust):
    
    raio = int(input("\nDigite o comprimento das pás da turbina: "))
    eficiencia = float(input("Digite a eficência da turbina eólica ex 0.4 : "))

    densidade_ar = _PressaoDoAr(data)

    area =  raio ** 2 * 3.141592

    potencia = (0.5 * densidade_ar * area * (speed ** 3)) * eficiencia

    potencia = (potencia * 720)/ 1000000

    if speed <= 5:
        print("\nLocal possui ventos fracos, portanto não ira gerar grandes quantidades de energia, assim o local não é indicado para geração eolica")
        print(f"\nEstimativa de energia gerada no local em 1 mes: ", round(potencia,3), "MW/h")
    elif speed >= 25:
        print("\nLocal possui ventos fortes, verifique se sua turbina suporta esta velocidade")
        print(f"\nEstimativa de energia gerada no local em 1 mes: ", round(potencia,3), "MW/h")
    elif gust >= 25:
        print("\nLocal possui rajadas fortes, procure turbinas que suportem fortes rajadas")
        print(f"\nEstimativa de energia gerada no local em 1 mes: ", round(potencia,3), "MW/h")
    else:
        print("\nLocal possui um bom clima para geração de energia eolica, portanto pode ser indicado a geração")
        print(f"\nEstimativa de energia gerada no local em 1 mes: ", round(potencia,3), "MW/h")

def _PressaoDoAr(data):

    pressure = []
    temp = []
    humidity = []

    for day in data['data']['weather']:
            for hourly_data in day['hourly']:
                pressure.append(int(hourly_data['pressure']))
                temp.append(int(hourly_data['tempC']))
                humidity.append(int(hourly_data['humidity']))

    pressureFinal = sum(pressure) / len(pressure)
    tempFinal = sum(temp) / len(temp)
    humidityFinal = sum(humidity) / len(humidity)

    # Constante do gás ideal para o ar
    R = 287.05 # J/kg/K para o ar
    # Converter pressão para pascais
    pressure_pa = pressureFinal * 100
    #converter temperatura para kelvin
    temp_k = tempFinal + 273.15

    # Calcular pressão parcial do vapor d'água em pascal
    pressure_vapor = (humidityFinal / 100) * _calcular_pressao_saturacao(tempFinal)

    densidade_ar = (pressure_pa / (R * temp_k)) * (1 + 0.378 * (pressure_vapor / pressure_pa))
    return densidade_ar

# Calcular a pressão de saturação do vapor d'água (aproximação)
def _calcular_pressao_saturacao(temp_c):
    A = 8.07131
    B = 1730.63
    C = 233.426
    return 10 ** (A - (B / (temp_c + C))) * 133.322368  # Converter para pascal