import requests
import math
import coordenadas
from azimuth import calcular_azimuth

api_key = "BjU1fQm5wYMsZR90Tejy0NjxGYsIg54qKcz5i9mw"

def calcular_inclinacao(latitude):
    # Converte a latitude de graus para radianos
    latitude_radianos = math.radians(latitude)

    # Calcula a inclinação ideal (geralmente igual à latitude) em graus
    inclinacao_ideal = math.degrees(math.atan(math.cos(latitude_radianos)))

    return inclinacao_ideal

def media_solar(latitude, longitude):
    azimuth = calcular_azimuth(latitude, longitude)
    url = f'https://developer.nrel.gov/api/pvwatts/v8.json?api_key={api_key}&lat={latitude}&lon={longitude}&azimuth={azimuth}&system_capacity=4&losses=14&array_type=1&module_type=0&tilt=20'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        irrad_diaria = data['outputs']['solrad_monthly']  # Lista com irradiação solar diária de cada mês
        meses = data['outputs']['ac_monthly']  # Lista com a produção de energia de cada mês

    # Calcula a média da irradiação solar para todos os meses
        media_irrad = sum(irrad_diaria) / len(irrad_diaria)
        return media_irrad  # Retorna True se a média for igual ou superior a 4 kWh/m²/dia, False caso contrário

    else:
        print("Erro ao acessar a API PVWatts.")
        return False

def calcular_geracao_energia_solar(latitude, longitude, system_capacity, module_type, losses, array_type, tilt):
    eficiencia_sistema = 0.15

    azimuth = calcular_azimuth(latitude, longitude)

    url = f'https://developer.nrel.gov/api/pvwatts/v8.json?api_key={api_key}&lat={latitude}&lon={longitude}&azimuth={azimuth}&tilt={tilt}&array_type={array_type}&system_capacity={system_capacity}&module_type={module_type}&losses={losses}'

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        ghi = data['outputs']['ac_monthly']
        geracao_energia_solar = [
            ghi_mes * system_capacity * eficiencia_sistema for ghi_mes in ghi
    ]
        return geracao_energia_solar
    else:
        print("Erro ao fazer a requisição ao PVWatts API.")
        return None


def execute():
    checagem = input("\nDigite 1 para verificar a recomendação de geração de energia solar\nDigite 2 para verificar a geração de energia solar\n: ")

    if (checagem == '1'):
        viacep_data = coordenadas.obter_cep()
        lat, long = coordenadas.obter_coordenadas_por_cep(viacep_data["cep"])

        media = media_solar(lat, long) # em kWh/m²/dia
        if (media >= 4):
            print(f'A média da previsão de geração de energia é de {media} kWh/m²/dia. Então essa é uma região boa para a instalação de placas solares.')
        else:
            print(f'A média da previsão de geração de energia é de {media} kWh/m²/dia. Então infelizmente essa não é uma boa região para a instalação de placas solares.')

    else:
        viacep_data = coordenadas.obter_cep()
        latitude, longitude = coordenadas.obter_coordenadas_por_cep(viacep_data["cep"])

    #Nameplate capacity (kW)
        system_capacity = float(input("\nCapacidade nominal do sistema (kW): "))

    #module type
        module_type = int(input("\n0: Standard\n1: Premium\n2: Thin Film\n3: Nenhuma das alternativas\n:"))

    #System losses (percent)
        losses = float(input("\nPercentual de perdas do sistema ((-5) ~ 100): "))

    #Array type
        array_type = input(
            "\nDigite o array type dos paines\n0: Fixed - Open Rack\n1: Fixed - Roof Mounted\n2: 1-Axis\n3: 1-Axis Backtraking\n4: 2-Axis\n:"
    )

    #Tilt angle (degrees)
        tilt = int(input("\nInclinação dos paines (graus): 1 para digitar a inclinação dos paines:\n2 para cálcular a inclinação ideal dos paineis\n:" ))
        if tilt == 1:
            tilt = int(input("\nInclinação dos paines (graus): "))
        else:
            tilt = calcular_inclinacao(latitude)
            print(f'\nA inclinação ideal dos paines é de {tilt} graus.\n')

        geracao_energia_solar = calcular_geracao_energia_solar(latitude, longitude, system_capacity, module_type, losses, array_type, tilt)
        if geracao_energia_solar:
            for mes, geracao in enumerate(geracao_energia_solar, 1):
                print(f'Mês {mes}: {geracao} kWh')

