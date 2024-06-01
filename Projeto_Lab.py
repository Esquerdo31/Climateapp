from ast import NotEq, Param
from calendar import c
from ctypes.wintypes import SIZE
import tkinter as tk
from tkinter import ANCHOR, NE, W, simpledialog, messagebox, ttk, Canvas, PhotoImage, Button
from tkinter.font import BOLD, Font
from token import NOTEQUAL
from turtle import title
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
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os
import pystray
from pystray import MenuItem as item
import threading
import time
from winotify import Notification, audio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import folium
import tkintermapview
from pathlib import Path
import locale

API_KEY_WEATHER = '6de9d4c574f54850af113b86005202b2'
API_KEY_GEO = 'cc88a6dd1b8de7'
EMAIL_FILE = 'emails.txt'
locale.setlocale(locale.LC_TIME, 'pt_PT')

loc = "Localidade: Nenhuma"
selected_email = ""
warning = 0
checking_disasters = False
buttons = []
detail_labels = []
map_widget = None  # Global map widget reference
selected_day_data = None
# Definir variáveis globais para armazenar labels e botões persistentes
icon_label = None
icon_button = None
day_label = None


def fetch_initial_location():
    try:
        response = requests.get(f"https://ipinfo.io?token={API_KEY_GEO}")
        if response.status_code == 200:
            data = response.json()
            loc = data['city'] + ' - ' + data['country']
            lat, lon = data['loc'].split(',')
            cor_var.set(f"Latitude: {lat} - Longitude: {lon}")
            localidade_var.set(f"Localidade: {loc}")
            cidade, pais = loc.split(' - ')
            print(f"Localidade inicial definida: {loc}")
        else:
            print("Não foi possível obter a localização inicial.")
    except Exception as e:
        print(f"Erro ao buscar localização inicial: {e}")
  
def set_localidade():
    localidade_window = ctk.CTkToplevel(root)
    localidade_window.title("Definir Localidade")
    localidade_window.geometry("300x200")

    ctk.CTkLabel(localidade_window, text="Digite a localidade:").pack()
    localidade_entry = ctk.CTkEntry(localidade_window)
    localidade_entry.pack()

    ctk.CTkLabel(localidade_window, text="Selecione o país:").pack()
    country_combo = ctk.CTkComboBox(localidade_window, values=country_list)
    country_combo.pack()
    country_combo.set('Escolha um país')

    def confirm_action():
        localidade = localidade_entry.get()
        country = country_combo.get()
        if localidade and country:
            localidade_var.set(f"Localidade: {localidade} - {country}")
            butoesfunction()
            localidade_window.destroy()

    confirm_button = ctk.CTkButton(localidade_window, text="Confirmar", command=confirm_action)
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
                cidade = data['data'][0]['city_name']
                resultado_var.set(f"Temperatura em {cidade}, {pais}: {temperatura}ºC")
            else:
                resultado_var.set("Nenhum dado de temperatura disponível para esta localidade.")
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
                cidade = data['data'][0]['city_name']
                resultado_var.set(f"Velocidade do vento em {cidade}, {pais}: {velocidade}m/s")
            else:
                resultado_var.set("Nenhum dado de velocidade disponível para esta localidade.")
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
                cidade = data['data'][0]['city_name']
                resultado_var.set(f"Humidade em {cidade}, {pais}: {humidade}%")
            else:
                resultado_var.set("Nenhum dado de humidade disponível para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

def load_emails():
    if not os.path.exists(EMAIL_FILE):
        return []
    with open(EMAIL_FILE, 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    return emails

def save_email(new_email):
    with open(EMAIL_FILE, 'a') as file:
        file.write(new_email + '\n')

def fetch_temperature_data():
    try:
        coordenadas = cor_var.get().replace("Latitude: ", "").replace("Longitude: ", "").split(" - ")
        if len(coordenadas) != 2:
            raise ValueError("Formato de coordenadas inválido. Esperado: 'Latitude: X - Longitude: Y'")

        lat, lon = coordenadas

        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d') 

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m"
        }

        response = requests.get(url, params=params)
        print("URL da API:", response.url)  # Verificar a URL completa com parâmetros
        print("Status Code:", response.status_code)
        print("Resposta da API:", response.text)  # Imprimir a resposta completa da API

        if response.status_code == 200:
            if response.text.strip() == "":
                raise ValueError("Resposta da API está vazia")
            try:
                data = response.json()
                if 'hourly' not in data or 'temperature_2m' not in data['hourly'] or 'time' not in data['hourly']:
                    raise ValueError("Estrutura esperada não encontrada no JSON")

                temperatures = data['hourly']['temperature_2m']
                dates = [datetime.strptime(day, "%Y-%m-%dT%H:%M") for day in data['hourly']['time']]
                return dates, temperatures
            except ValueError as ve:
                raise Exception(f"Erro ao processar JSON: {ve}")
        else:
            raise Exception(f"Falha ao buscar dados da API: Status {response.status_code}")
    except Exception as e:
        print("Erro ao buscar dados da API:", e)
        raise

def selecionar_dia(dia, img_path, day_of_week):
    global selected_day_data, tempmax_var, tempmin_var, icon_button, day_label
    selected_day_data = (dia, img_path, day_of_week)
    tempmax_var.set(f"Max: {dia['max_temp']}°C")
    tempmin_var.set(f"Min: {dia['min_temp']}°C")
    atualizar_resumo(selected_day_data)

def mostrar_detalhes():
    global selected_day_data
    if selected_day_data:
        dia, img_path, day_of_week = selected_day_data
        detalhes_janelaframe = ctk.CTkFrame(root)
        detalhes_janelaframe.place(x=248.0, y=129.0)
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
        ctk.CTkLabel(detalhes_janelaframe, text=detalhes_texto, font=("Poppins Regular", 14), text_color="black", bg_color="#FFFFFF", justify=tk.LEFT).pack(pady=10)
        detail_labels.append(detalhes_janelaframe)
    
def ocultar_detalhes():
    global detail_labels
    # Ocultar apenas os detalhes adicionais, mantendo ícone e temperaturas
    for label in detail_labels:
        label.destroy()
    detail_labels.clear()  # Limpar a lista de labels de detalhes adicionais

def map_weather_codes_to_images():
    # Defina o caminho base absoluto para o diretório de ícones
    base_dir = r'C:\Users\costi\Desktop\Uni\Cadeiras2semestre1ano\lab\Trabalho2\icons'
    weather_codes_to_images = {
        '200': os.path.join(base_dir, 'icon200.png'),
        '201': os.path.join(base_dir, 'icon201.png'),
        '202': os.path.join(base_dir, 'icon202.png'),
        '230': os.path.join(base_dir, 'icon230.png'),
        '231': os.path.join(base_dir, 'icon231.png'),
        '232': os.path.join(base_dir, 'icon232.png'),
        '233': os.path.join(base_dir, 'icon233.png'),
        '300': os.path.join(base_dir, 'icon300.png'),
        '301': os.path.join(base_dir, 'icon301.png'),
        '302': os.path.join(base_dir, 'icon302.png'),
        '500': os.path.join(base_dir, 'icon500.png'),
        '501': os.path.join(base_dir, 'icon501.png'),
        '502': os.path.join(base_dir, 'icon502.png'),
        '511': os.path.join(base_dir, 'icon511.png'),
        '520': os.path.join(base_dir, 'icon520.png'),
        '521': os.path.join(base_dir, 'icon521.png'),
        '522': os.path.join(base_dir, 'icon522.png'),
        '600': os.path.join(base_dir, 'icon600.png'),
        '601': os.path.join(base_dir, 'icon601.png'),
        '602': os.path.join(base_dir, 'icon602.png'),
        '610': os.path.join(base_dir, 'icon610.png'),
        '611': os.path.join(base_dir, 'icon611.png'),
        '612': os.path.join(base_dir, 'icon612.png'),
        '621': os.path.join(base_dir, 'icon621.png'),
        '622': os.path.join(base_dir, 'icon622.png'),
        '623': os.path.join(base_dir, 'icon623.png'),
        '700': os.path.join(base_dir, 'icon700.png'),
        '711': os.path.join(base_dir, 'icon711.png'),
        '721': os.path.join(base_dir, 'icon721.png'),
        '731': os.path.join(base_dir, 'icon731.png'),
        '741': os.path.join(base_dir, 'icon741.png'),
        '751': os.path.join(base_dir, 'icon751.png'),
        '800': os.path.join(base_dir, 'icon800.png'),
        '801': os.path.join(base_dir, 'icon801.png'),
        '802': os.path.join(base_dir, 'icon802.png'),
        '803': os.path.join(base_dir, 'icon803.png'),
        '804': os.path.join(base_dir, 'icon804.png'),
        '900': os.path.join(base_dir, 'icon900.png'),
        '901': os.path.join(base_dir, 'icon901.png'),
        '902': os.path.join(base_dir, 'icon902.png'),
        '903': os.path.join(base_dir, 'icon903.png'),
        '904': os.path.join(base_dir, 'icon904.png'),
        '905': os.path.join(base_dir, 'icon905.png'),
        '906': os.path.join(base_dir, 'icon906.png'),
        '951': os.path.join(base_dir, 'icon951.png'),
        '952': os.path.join(base_dir, 'icon952.png'),
        '953': os.path.join(base_dir, 'icon953.png'),
        '954': os.path.join(base_dir, 'icon954.png'),
        '955': os.path.join(base_dir, 'icon955.png'),
        '956': os.path.join(base_dir, 'icon956.png'),
        '957': os.path.join(base_dir, 'icon957.png'),
        '958': os.path.join(base_dir, 'icon958.png'),
        '959': os.path.join(base_dir, 'icon959.png'),
        '960': os.path.join(base_dir, 'icon960.png'),
        '961': os.path.join(base_dir, 'icon961.png'),
        '962': os.path.join(base_dir, 'icon962.png'),
    }
    return weather_codes_to_images

def butoesfunction():
    global buttons, butoesinteiros, selected_day_data, detail_labels
    
    full_localidade = localidade_var.get().split(': ')[1]
    butoesinteiros = 0
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/forecast/daily?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                # Se os botões já foram criados, destrua-os
                if 'buttons' in globals() and buttons:
                    for button in buttons:
                        button.destroy()
               
                # Se as labels de detalhes já foram criadas, destrua-as
                if 'detail_labels' in globals() and detail_labels:
                    for label in detail_labels:
                        label.destroy()
                # Crie os botões novamente
                today = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                today.place(x=16.0, y=124.0)
                
                tomorrow = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                tomorrow.place(x=16.0, y=179.0)
                
                twodaysafter = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                twodaysafter.place(x=16.0, y=234.0)
                
                threedayafter = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                threedayafter.place(x=16.0, y=289.0)
                
                fourdaysafter = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                fourdaysafter.place(x=16.0, y=344.0)
                
                fivedaysafter = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=120,
                    height=40
                )
                fivedaysafter.place(x=16.0, y=399.0)
                
                sixdaysafter = ctk.CTkButton(
                    root,
                    bg_color="#466653",
                    fg_color="#6FAFEA",
                    text="Dia",
                    corner_radius=25,
                    border_width=0,
                    width=60,
                    height=40
                )
                sixdaysafter.place(x=16.0, y=453.0)
                
                buttons = [today, tomorrow, twodaysafter, threedayafter, fourdaysafter, fivedaysafter, sixdaysafter]
                for i in range(7):
                    dia = data['data'][i]
                    icon_code = dia['weather']['code']
                    image_path = map_weather_codes_to_images().get(str(icon_code), 'C:\\Users\\costi\\Desktop\\Uni\\Cadeiras2semestre1ano\\lab\\Trabalho2\\icons\\default.png')
                    
                    if not os.path.exists(image_path):
                        image_path = 'icons/default.png'
                    
                    img = Image.open(image_path)
                    img = img.resize((25, 25), Image.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                    
                    temp = dia['temp']
                    date_str = dia['datetime']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')
                    button_text = f"{day_of_week}: {temp}°C"

                    button = buttons[i]
                    button.configure(text=button_text, image=img, compound=tk.LEFT, width=80, height=40, command=lambda d=dia, img=image_path, day_of_week=day_of_week: selecionar_dia(d, img, day_of_week))
                    button.image = img  # keep a reference to avoid garbage collection
                    butoesinteiros = 1
                
                if butoesinteiros == 1:
                    # Código repetido aqui parece redundante e desnecessário, removendo para simplificação
                    pass
            else:
                no_data_label = ctk.CTkLabel(root, text="Nenhum dado de previsão disponível para esta localidade.")
                no_data_label.pack()
                detail_labels.append(no_data_label)
        else:
            error_label = ctk.CTkLabel(root, text=f"Erro ao buscar dados da API: {response.status_code}")
            error_label.pack()
            detail_labels.append(error_label)

def atualizar_resumo(selected_day_data):
    global icon_button, day_label
    dia, img_path, day_of_week = selected_day_data
    # Manter os ícones e as temperaturas ao atualizar
    for label in detail_labels:
        label.destroy()
    
    # Atualizar o ícone e o dia à direita
    if day_label:
        day_label.destroy()
    day_label = ctk.CTkLabel(root, text=day_of_week, width=116, height=16, text_color="black", bg_color="#D9D9D9")
    day_label.place(x=601, y=101)
    
    img = Image.open(img_path)
    img = img.resize((159, 144), Image.LANCZOS)  # Ajuste o tamanho conforme necessário
    img = ImageTk.PhotoImage(img)
    if icon_button:
        icon_button.destroy()
    icon_button = ctk.CTkButton(root, text="", image=img, bg_color="transparent", width=204, height=215, border_width=0, state="disabled")
    icon_button.place(x=557.0, y=124.0)
    icon_button.image = img  # Manter referência para evitar coleta de lixo

def show_temperature_graph():
    try:
        dates, temperatures = fetch_temperature_data()
        plt.figure(figsize=(10, 5))
        plt.plot(dates, temperatures, marker='o')
        plt.title('Temperatura Máxima Diária (Últimos 7 dias)')
        plt.xlabel('Data')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def emailconfirma():
    global selected_email
    emails = load_emails()

    def choose_email():
        framelistbox=ctk.CTkFrame(root)
        framelistbox.place(x=248.0, y=129.0)
        listbox = tk.Listbox(framelistbox,width=25)
        for email in emails:
            listbox.insert(tk.END, email)
        listbox.pack()

        def on_select():
            global selected_email
            selected_email = listbox.get(tk.ACTIVE)
            if selected_email:
                framelistbox.destroy()

        select_button = ctk.CTkButton(framelistbox, text="Selecionar", command=on_select)
        select_button.pack(pady=5)

        def add_new_email():
            global selected_email
            new_email = simpledialog.askstring("Novo E-mail", "Digite o novo e-mail:")
            if new_email:
                save_email(new_email)
                selected_email = new_email
                framelistbox.destroy()

        new_email_button = ctk.CTkButton(framelistbox, text="Adicionar Novo E-mail", command=add_new_email)
        new_email_button.pack()

    choose_email()

def usar_email_selecionado():
    global selected_email
    global warning
    global checking_disasters
    if selected_email:
        if warning == 0:
            send_notification(selected_email)
            messagebox.showinfo("Aviso", "Caso seja detectado um aviso, será enviado para o teu email!")
            warning = 1
            checking_disasters = True
            disaster_thread = threading.Thread(target=check_disasters, daemon=True)
            disaster_thread.start()
        else:
            send_notification(selected_email)
    else:
        messagebox.showinfo("Informação", "Nenhum e-mail selecionado.")

def check_disasters():
    global checking_disasters
    while checking_disasters:
        if selected_email:
            send_notification(selected_email)
        time.sleep(60)

def send_notification(to_email):
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/alerts?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'alerts' in data and len(data['alerts']) > 0:
                alerta = data['alerts'][0]['severity']
                if alerta in ["Advisory", "Watch", "Warning"]:
                    alertatit = data['alerts'][0]['title']
                    alertadesc = data['alerts'][0]['description']
                    subject = f"Alerta Meteorológico: {alertatit}"
                    body = f"Título: {alertatit}\n\nDescrição: {alertadesc}"
                    send_email(subject, body, to_email)
                    notif = Notification(app_id="Aplicação Meteorológica", title="Aviso de Desastres", msg=alerta, duration="short", icon=icon_path)
                    notif.set_audio(audio.Default, loop=False)
                    notif.add_actions(label="Alerta Detectado!", launch="https://gmail.com/")
                    notif.show()
                else:
                    print("Nenhum alerta relevante encontrado.")
            else:
                print("Nenhum alerta disponível para esta localidade.")
        else:
            print(f"Erro ao buscar dados da API: {response.status_code}")

def send_email(subject, body, to_email):
    from_email = "contadeavisos@gmail.com"
    from_password = "wiwz wnwm ieeu tsuq"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

def create_image():
    icon_path = "iconmestre.png"
    image = Image.open(icon_path)
    return image

def on_quit(icon, item):
    global checking_disasters
    checking_disasters = False
    icon.stop()
    root.quit()
    root.destroy()

def open_main_window(icon, item):
    root.after(0, root.deiconify)
    icon.stop()

def minimize_to_tray():
    global icon
    icon = pystray.Icon("test_icon", create_image(), "Climate APP", menu=pystray.Menu(
        item('Abrir', open_main_window),
        item('Fechar', on_quit)
    ))
    icon.run()

def mapa():
    global map_widget
    if map_widget is not None:
        map_widget.destroy()
    api_key_op = '46effc38253ccbfe1327746b4cbb41ef'
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                humidade = data['data'][0]['rh']
                cidade = data['data'][0]['city_name']
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                map_widget = tkintermapview.TkinterMapView(root, width=257, height=247)
                map_widget.place(x=248.0,y=129.0)
                map_widget.set_position(lat, lon)
                map_widget.set_zoom(15)
            else:
                resultado_var.set("Nenhum dado de humidade disponível para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

def destruir_mapa():
    global map_widget
    if map_widget:
        map_widget.destroy()
        map_widget = None
         
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

root = ctk.CTk()
root.title("Informações Meteorológicas")
root.geometry("800x600")
root.configure(bg="#D9D9D9")

# Defina o ícone da janela principal
icon_path = "iconmestre.png"
img = Image.open(icon_path)
photo = ImageTk.PhotoImage(img)
root.iconphoto(True, photo)
root.iconbitmap("iconmestre.ico")
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\costi\Desktop\Uni\Cadeiras2semestre1ano\lab\Trabalho2\build\assets\frame0")

cor_var = tk.StringVar(root, "Latitude: Nenhuma - Longitude: Nenhuma")
localidade_var = tk.StringVar(root, "Localidade: Nenhuma")
resultado_var = tk.StringVar(root)
# Definir variáveis globais para armazenar as temperaturas máxima e mínima
tempmax_var = tk.StringVar()
tempmin_var = tk.StringVar()

country_list = ['BR', 'US', 'PT', 'ES', 'FR', 'DE', 'IT']

fetch_initial_location()
butoesfunction()


# Adicionar as labels de localidade, temperatura máxima e mínima
label_localidade = ctk.CTkLabel(root, textvariable=localidade_var, bg_color="#4DB1C7", fg_color="#4DB1C7", font=("Poppins Regular", 15))
label_localidade.pack(side=tk.LEFT, anchor=tk.N, pady=20, padx=20)
label_localidade.place(x=541.0, y=23.0)

label_max_temp = ctk.CTkLabel(root, textvariable=tempmax_var, bg_color="#D9D9D9", fg_color="#D9D9D9", font=("Poppins Regular", 15))
label_max_temp.place(x=601, y=279)

label_min_temp = ctk.CTkLabel(root, textvariable=tempmin_var, bg_color="#D9D9D9", fg_color="#D9D9D9", font=("Poppins Regular", 15))
label_min_temp.place(x=601, y=304)


canvas = Canvas(
    root,
    bg="#FFFFFF",
    height=600,
    width=800,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
canvas.create_rectangle(
    0.0,
    0.0,
    800.0,
    600.0,
    fill="#D9D9D9",
    outline=""
)

canvas.create_text(
    410.0,
    574.0,
    anchor="nw",
    text="Desenvolvido por: Hugo Costa, Bruno Sousa, Gustavo Costa, Lucas Cerqueira",
    fill="#000000",
    font=("Poppins Regular", 10 * -1)
)

canvas.create_text(
    250.0,
    436.0,
    anchor="nw",
    text="Fecha o mapa se quiseres que\n todos os dados apareçam",
    fill="#000000",
    font=("Poppins Regular", 12 * -1)
)

canvas.create_rectangle(
    0.0,
    80.0,
    216.0,
    600.0,
    fill="#456652",
    outline=""
)

canvas.create_rectangle(
    0.0,
    0.0,
    800.0,
    80.0,
    fill="#4DB1C7",
    outline=""
)

lupa_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
lupa_1 = Button(
    image=lupa_image_1,
    bg="#4DB1C7",
    borderwidth=0,
    highlightthickness=0,
    command= set_localidade,
    relief="flat"
)
lupa_1.place(
    x=720.0,
    y=20.0,
    width=39.0,
    height=39.0
)

label_localidade = ctk.CTkLabel(root,textvariable=localidade_var, bg_color="#4DB1C7",fg_color="#4DB1C7")
label_localidade.pack(side=tk.LEFT, anchor=tk.N,pady=20,padx=20)
label_localidade.place(x=541.0,y=23.0)

canvas.create_text(
    17.0,
    23.0,
    anchor="nw",
    text="Climate APP",
    fill="#FFFFFF",
    font=("Poppins Regular", 24 * -1)
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    40.99999078539349,
    471.0,
    image=image_image_1
)

email_image_9 = PhotoImage(
    file=relative_to_assets("button_9.png"))
email_9 = Button(
    image=email_image_9,
    borderwidth=0,
    bg="#466653",
    highlightthickness=0,
    command=emailconfirma,
    relief="flat"
)
email_9.place(
    x=47.0,
    y=508.0,
    width=126.0,
    height=28.0
)

button_image_10 = PhotoImage(
    file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    bg="#466653",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_10 clicked"),

)
button_10.place(
    x=48.0,
    y=544.0,
    width=126.0,
    height=28.0
)


abrirmapa_image_11 = PhotoImage(
    file=relative_to_assets("button_11.png"))
abrirmapa_11 = Button(
    image=abrirmapa_image_11,
    bg="#D9D9D9",
    borderwidth=0,
    highlightthickness=0,
    command=mapa,
    relief="flat"
)
abrirmapa_11.place(
    x=248.0,
    y=399.0,
    width=130.0,
    height=30.0
)

fecharmapa_image_12 = PhotoImage(
    file=relative_to_assets("button_12.png"))
fecharmapa_12 = Button(
    image=fecharmapa_image_12,
    bg="#D9D9D9",
    borderwidth=0,
    highlightthickness=0,
    command=destruir_mapa,
    relief="flat"
)
fecharmapa_12.place(
    x=379.0,
    y=399.0,
    width=130.0,
    height=30.0
)

detalhes_image_13 = PhotoImage(
    file=relative_to_assets("button_13.png"))
detalhes_13 = Button(
    image=detalhes_image_13,
    bg="#D9D9D9",
    borderwidth=0,
    highlightthickness=0,
    command=mostrar_detalhes,
    relief="flat",
    pady=10
)
detalhes_13.place(
    x=557.0,
    y=408.0,
    width=210.0,
    height=35.0
)

ocultar_button = ctk.CTkButton(
    root,
    bg_color="#D9D9D9",
    text="Ocultar Detalhes",
    text_color="black",
    command=ocultar_detalhes,
    font=("Poppins Regular", 14),
    corner_radius=25,
    width=210.0,
    height=35.0,
    fg_color="#37A376"
)
ocultar_button.place(
    x=557.0,
    y=450.0
)

button_image_14 = PhotoImage(
    file=relative_to_assets("button_14.png"))
button_14 = Button(
    bg="#D9D9D9",
    image=button_image_14,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_14 clicked"),
    relief="flat"
)
button_14.place(
    x=220.0,
    y=507.0,
    width=130.0,
    height=35.0
)

button_image_15 = PhotoImage(
    file=relative_to_assets("button_15.png"))
button_15 = Button(
    image=button_image_15,
    bg="#D9D9D9",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_15 clicked"),
    relief="flat"
)
button_15.place(
    x=351.0,
    y=507.0,
    width=130.0,
    height=35.0
)




# button_frame = ctk.CTkFrame(root, fg_color="blue")
# button_frame.pack(side=tk.LEFT,anchor=W, pady=10)

# framelocal= ctk.CTkFrame(root,fg_color="transparent")
# framelocal.pack(side=tk.TOP,anchor=tk.NE, pady=10,padx=10)

# btn_localidade = ctk.CTkButton(framelocal,text="Definir Localidade", command=set_localidade)
# btn_localidade.pack(side=tk.RIGHT,anchor=tk.NE, pady=20)

# # frametemp= ctk.CTkFrame(root,fg_color="transparent")
# # frametemp.pack(side=tk.CENTER, pady=10,padx=10)

# # btn_temperatura = ctk.CTkButton(button_frame, text="Temperatura", command=temperatura_action)
# # btn_temperatura.grid(column=1,row=0, padx=5)

# # btn_humidade = ctk.CTkButton(button_frame, text="Humidade", command=get_humidade)
# # btn_humidade.grid(column=1,row=1, padx=5)

# # btn_vv = ctk.CTkButton(button_frame, text="Velocidade do Vento", command=get_velocidade)
# # btn_vv.grid(column=1,row=2,padx=5)

# btn_show_graph = ctk.CTkButton(root, text="Mostrar Gráfico de Temperaturas", command=show_temperature_graph)
# btn_show_graph.pack(pady=10)

# btn_prev = ctk.CTkButton(root, text="Previsão de Temperatura", command=previsao_temperatura)
# btn_prev.pack(pady=10)

label_localidade = ctk.CTkLabel(root,textvariable=localidade_var,bg_color="#4DB1C7",fg_color="#4DB1C7",font=("Poppins Regular",15))
label_localidade.pack(side=tk.LEFT, anchor=tk.N,pady=20,padx=20)
label_localidade.place(x=541.0,y=23.0)

# label_resultado = ctk.CTkLabel(root, textvariable=resultado_var)
# label_resultado.pack(side=tk.TOP, anchor=tk.N, pady=20)
# label_resultado.place(x=541.0,y=23.0)

# btn_aviso = ctk.CTkButton(root, text="⚠️Avisar desastres!⚠️", command=usar_email_selecionado, fg_color="red")
# btn_aviso.pack(side=ctk.BOTTOM, anchor=tk.SE, pady=10, padx=10)

# btn_email = ctk.CTkButton(root, text="Inserir email", command=emailconfirma, fg_color="green")
# btn_email.pack(side=tk.BOTTOM, anchor=tk.SE, pady=10, padx=10)

# btn_mapa = ctk.CTkButton(root, text="Abrir Mapa", command=mapa, fg_color="green")
# btn_mapa.pack(side=tk.BOTTOM, anchor=tk.SE, pady=10, padx=10)

def on_close():
    if messagebox.askokcancel("Fechar", "Minimizar invés de fechar totalmente?"):
        root.withdraw()
        minimize_to_tray()
    else:
        global checking_disasters
        checking_disasters = False
        root.quit()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

def main_task():
    while True:
        print("Ainda estou a trabalhar no background")
        time.sleep(5)

butoesfunction()
task_thread = threading.Thread(target=main_task, daemon=True)
task_thread.start()

root.resizable(False, False)
root.mainloop()






