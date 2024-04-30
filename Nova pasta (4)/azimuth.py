import ephem
import datetime


def calcular_azimuth(latitude, longitude):
    # Criar objeto observador
    observador = ephem.Observer()
    observador.lat = latitude
    observador.long = longitude

    # Definir data e hora
    data_hora_atual = datetime.datetime.now()
    observador.date = data_hora_atual.strftime('%Y/%m/%d %H:%M:%S') #'data e hora no formato YYYY/MM/DD HH:MM:SS'

    # Calcular posição do sol
    sol = ephem.Sun()
    sol.compute(observador)

    # Obter ângulo azimute do sol em graus
    azimuth = sol.az * 180 / ephem.pi

    return azimuth
