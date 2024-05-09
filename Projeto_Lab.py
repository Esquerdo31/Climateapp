import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np


API_KEY_WEATHER = '0a862d8a9b294adb99eb68c1c92a2365'  # Chave da API do Weatherbit
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
            print("Nao foi possivel obter a localizacao inicial.")
    except Exception as e:
        print(f"Erro ao buscar localizacao inicial: {e}")

def set_localidade():
    localidade_window = tk.Toplevel(root)
    localidade_window.title("Definir Localidade")

    tk.Label(localidade_window, text="Digite a localidade:").pack()
    localidade_entry = tk.Entry(localidade_window)
    localidade_entry.pack()

    tk.Label(localidade_window, text="Selecione o pais:").pack()
    country_combo = ttk.Combobox(localidade_window, values=country_list)
    country_combo.pack()
    country_combo.set('Escolha um pais')

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

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&past_days=7"
  
        response = requests.get(url)
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
        plt.title('Temperatura Maxima Diaria (Ultimos 30 dias)')
        plt.xlabel('Data')
        plt.ylabel('Temperatura (C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erro", str(e))


root = tk.Tk()
root.title("Informacoes Meteorologicas")
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

label_localidade = tk.Label(root, textvariable=localidade_var, fg="blue")
label_localidade.pack(side=tk.TOP, anchor=tk.N)

label_resultado = tk.Label(root, textvariable=resultado_var, fg="red")
label_resultado.pack(side=tk.TOP, anchor=tk.N, pady=20)

btn_show_graph = tk.Button(root, text="Mostrar Grafico de Temperaturas", command=show_temperature_graph)
btn_show_graph.pack(pady=20)


root.mainloop()