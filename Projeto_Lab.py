from ast import Param
from ctypes.wintypes import SIZE
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from tkinter.font import BOLD, Font
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import emoji
from datetime import datetime
from tkinter import font



API_KEY_WEATHER = '6de9d4c574f54850af113b86005202b2'  # Chave da API do Weatherbit
API_KEY_GEO = 'cc88a6dd1b8de7'         # Chave da API IPinfo
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def fetch_initial_location():
    try:
        response = requests.get(f"https://ipinfo.io?token={API_KEY_GEO}")
        if response.status_code == 200:
            data = response.json()
            loc = data['city'] + ' - ' + data['country']
            lat,lon = data['loc'].split(',')
            coordenadas = f"{lat} - {lon}"
            cor_var.set(f"Latitude: {lat} - Longitude: {lon}")
            localidade_var.set(f"Localidade: {loc}")

            print(f"Localidade inicial definida: {loc}")
        else:
            print("Não foi possivel obter a localizaçao inicial.")
    except Exception as e:
        print(f"Erro ao buscar localizaçao inicial: {e}")

def set_localidade():
    localidade_window = tk.Toplevel(root)
    localidade_window.title("Definir Localidade")
    localidade_window.geometry("300x200")

    tk.Label(localidade_window, text="Digite a localidade:").pack()
    localidade_entry = tk.Entry(localidade_window)
    localidade_entry.pack()

    tk.Label(localidade_window, text="Selecione o país:").pack()
    country_combo = ttk.Combobox(localidade_window, values=country_list)
    country_combo.pack()
    country_combo.set('Escolha um país')

    def confirm_action():
        localidade = localidade_entry.get()
        country = country_combo.get()
        if localidade and country:
            localidade_var.set(f"Localidade: {localidade} - {country}")
            localidade_window.destroy()

    confirm_button = tk.Button(localidade_window, text="Confirmar", command=confirm_action)
    confirm_button.pack()

def temperatura_action():
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                temperatura = data['data'][0]['temp']
                cidade= data['data'][0]['city_name']
                latitude = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                resultado_var.set(f"Temperatura em {cidade}, {pais}: {temperatura}C")
            else:
                resultado_var.set("Nenhum dado de temperatura disponivel para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

def get_velocidade():
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                velocidade = data['data'][0]['wind_spd']
                cidade= data['data'][0]['city_name']
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                resultado_var.set(f"Velocidade do vento em {cidade}, {pais}: {velocidade}m/s")
            else:
                resultado_var.set("Nenhum dado de velocidade disponivel para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

def get_humidade():
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                humidade = data['data'][0]['rh']
                cidade= data['data'][0]['city_name']
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                resultado_var.set(f"Humidade em {cidade}, {pais}: {humidade}%")
            else:
                resultado_var.set("Nenhum dado de humidade disponivel para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")
          
def fetch_temperature_data():
    try:
        coordenadas = cor_var.get().replace("Latitude: ", "").replace("Longitude: ", "").split(" - ")
        lat, lon = coordenadas

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        # url = f"https://archive-api.open-meteo.com/v1/archive" \
        
        # params = {
	       #          "latitude": ['data']["lat"]
	       #          "longitude": 'lon'
	       #          "start_date": 
	       #          "end_date": 
	       #          "hourly": "temperature_2m"
        #          }
  
        # response = requests.get(url)
        print("URL da API:", url)  # Verificar a URL enviada
        print("Resposta da API:", response.text)  # Imprimir a resposta completa da API

        if response.status_code == 200:
            data = response.json()
            temperatures = [temp for temp in data['hourly']['temperature_2m']]
            dates = [datetime.strptime(day, "%Y-%m-%dT%H:%M") for day in data['hourly']['time']]
            return dates, temperatures
        else:
            raise Exception(f"Falha ao buscar dados da API: Status {response.status_code}")
    except Exception as e:
        print("Erro ao buscar dados da API:", e)
        raise
    
def show_temperature_graph():
    try:
        dates, temperatures = fetch_temperature_data()
        plt.figure(figsize=(10, 5))
        plt.plot(dates, temperatures, marker='o')
        plt.title('Temperatura Máxima Diaria (Ultimos 7 dias)')
        plt.xlabel('Data')
        plt.ylabel('Temperatura (C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def previsao_temperatura():
    full_localidade = localidade_var.get().split(': ')[1]
    previsaobutton = tk.Toplevel(root)
    previsaobutton.title("Previsão de Temperatura")
    previsaobutton.geometry("300x600")

    button_font = font.Font(family="Helvetica", size=12, weight="bold")
    label_font = font.Font(family="Helvetica", size=10)
    
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/forecast/daily?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                for i in range(7):
                    dia = data['data'][i]
                    icon_code = dia['weather']['code']
                    emoji_icon = map_weather_codes_to_emojis().get(str(icon_code), '❓')
                    temp = dia['temp']
                    date_str = dia['datetime']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')
                    button_text = f"{day_of_week}: {emoji_icon} {temp}°C"
                    button = tk.Button(previsaobutton, text=button_text, command=lambda d=dia: mostrar_detalhes(d), font=button_font)
                    button.pack(pady=5)
            else:
                tk.Label(previsaobutton, text="Nenhum dado de previsão disponível para esta localidade.", font=label_font).pack()
        else:
            tk.Label(previsaobutton, text=f"Erro ao buscar dados da API: {response.status_code}", font=label_font).pack()

def mostrar_detalhes(dia):
    detalhes_janela = tk.Toplevel(root)
    detalhes_janela.title("Detalhes da Previsão")
    detalhes_janela.geometry("300x300")
    
    detalhes_texto = f"""
    Data: {dia['datetime']}
    Temperatura: {dia['temp']}°C
    Máxima: {dia['max_temp']}°C
    Mínima: {dia['min_temp']}°C
    Sensação: {dia['app_max_temp']}°C
    Clima: {dia['weather']['description']}
    Velocidade do Vento: {dia['wind_spd']} m/s
    Direção do Vento: {dia['wind_cdir']}
    Precipitação: {dia['precip']} mm
    Humidade: {dia['rh']}%
    """
    tk.Label(detalhes_janela, text=detalhes_texto, justify=tk.LEFT).pack(pady=10)

def map_weather_codes_to_emojis():
    weather_codes_to_emojis = {
        '200': '⛈️',  # Tempestade com trovoadas leve
        '201': '⛈️',  # Tempestade com trovoadas
        '202': '⛈️',  # Tempestade com trovoadas forte
        '230': '⛈️',  # Tempestade com trovoadas leve (parte do tempo)
        '231': '⛈️',  # Tempestade com trovoadas (parte do tempo)
        '232': '⛈️',  # Tempestade com trovoadas forte (parte do tempo)
        '233': '⛈️',  # Tempestade com trovoadas dispersas
        '300': '🌧️',  # Chuva com garoa leve
        '301': '🌧️',  # Chuva com garoa
        '302': '🌧️',  # Chuva com garoa forte
        '500': '🌧️',  # Chuva leve
        '501': '🌧️',  # Chuva moderada
        '502': '🌧️',  # Chuva forte
        '511': '🌨️',  # Chuva congelante
        '520': '🌧️',  # Chuva leve de intensidade variável
        '521': '🌧️',  # Chuva de intensidade variável
        '522': '🌧️',  # Chuva forte de intensidade variável
        '600': '❄️',  # Neve leve
        '601': '❄️',  # Neve
        '602': '❄️',  # Neve forte
        '610': '🌨️',  # Neve e chuva fraca
        '611': '🌨️',  # Neve e chuva
        '612': '🌨️',  # Neve e chuva forte
        '621': '🌨️',  # Neve leve de intensidade variável
        '622': '🌨️',  # Neve de intensidade variável
        '623': '🌨️',  # Neve forte de intensidade variável
        '700': '🌫️',  # Névoa
        '711': '🌫️',  # Fumaça
        '721': '🌫️',  # Neblina
        '731': '🌫️',  # Areia, poeira remoinhos
        '741': '🌫️',  # Névoa
        '751': '🌫️',  # Areia
        '800': '☀️',  # Céu limpo
        '801': '🌤️',  # Poucas nuvens
        '802': '🌥️',  # Nuvens dispersas
        '803': '☁️',  # Nuvens quebradas
        '804': '☁️',  # Nublado
        '900': '🌪️',  # Tornado
        '901': '🌀',   # Ciclone tropical
        '902': '🌀',   # Furacão
        '903': '❄️',  # Tempestade de neve
        '904': '🔥',   # Calor extremo
        '905': '🌬️',  # Vento forte
        '906': '🌨️',  # Granizo
        '951': '🌬️',  # Calmo
        '952': '🌬️',  # Brisa leve
        '953': '🌬️',  # Brisa suave
        '954': '🌬️',  # Brisa moderada
        '955': '🌬️',  # Brisa fresca
        '956': '🌬️',  # Brisa forte
        '957': '🌬️',  # Ventania
        '958': '🌬️',  # Vendaval
        '959': '🌬️',  # Vendaval
        '960': '🌪️',  # Vendaval
        '961': '🌪️',  # Tempestade
        '962': '🌪️',  # Furacão
    }
    return weather_codes_to_emojis




root = tk.Tk()
root.title("Informações Meteorológicas")
root.geometry("500x400")

cor_var = tk.StringVar(root, "Latitude: Nenhuma - Longitude: Nenhuma")
localidade_var = tk.StringVar(root, "Localidade: Nenhuma")
resultado_var = tk.StringVar(root)

# Lista de códigos de país para o exemplo, use uma lista completa conforme necessário
country_list = ['BR', 'US', 'PT', 'ES', 'FR', 'DE', 'IT']

fetch_initial_location()

# Container for buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, pady=10)

btn_localidade = tk.Button(button_frame, text="Definir Localidade", command=set_localidade)
btn_localidade.pack(side=tk.TOP,pady=10)

btn_temperatura = tk.Button(button_frame, text="Temperatura", command=temperatura_action)
btn_temperatura.pack(side=tk.LEFT)

btn_humidade = tk.Button(button_frame, text="Humidade", command=get_humidade)
btn_humidade.pack(side=tk.LEFT)

btn_vv = tk.Button(button_frame, text="Velocidade do Vento", command=get_velocidade)
btn_vv.pack(side=tk.LEFT)

btn_show_graph = tk.Button(root, text="Mostrar Gráfico de Temperaturas", command=show_temperature_graph)
btn_show_graph.pack(pady=10)

btn_prev= tk.Button(root, text="Previsão de Temperatura", command=previsao_temperatura)
btn_prev.pack(pady=10)

label_localidade = tk.Label(root, textvariable=localidade_var, fg="blue")
label_localidade.pack(side=tk.TOP, anchor=tk.N)

label_resultado = tk.Label(root, textvariable=resultado_var, fg="red")
label_resultado.pack(side=tk.TOP, anchor=tk.N, pady=20)


root.mainloop()