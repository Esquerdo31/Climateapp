from ast import NotEq, Param
from calendar import c
from ctypes.wintypes import SIZE
import tkinter as tk
from tkinter import ANCHOR, NE, W, simpledialog, messagebox, ttk, Canvas, PhotoImage, Button, Text, END
from tkinter.font import BOLD, Font
from token import NOTEQUAL
from turtle import title, width
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
from plyer import notification
import os
import pystray
from pystray import MenuItem as item
import threading
import time
#from winotify import Notification, audio: Parou de funcionar devido ao ultimo update do windows
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import folium
import tkintermapview
from pathlib import Path
import locale


# Definindo as chaves de API e configurações globais
API_KEY_WEATHER = '6de9d4c574f54850af113b86005202b2'
API_KEY_GEO = 'cc88a6dd1b8de7'
EMAIL_FILE = 'emails.txt'
locale.setlocale(locale.LC_TIME, 'pt_PT')

# Variáveis globais
loc = "Localidade: Nenhuma"
selected_email = ""
warning = 0
checking_disasters = False
buttons = []
detail_labels = []
map_widget = None  # Referência global para o widget do mapa
selected_day_data = None

# Variáveis para armazenar labels e botões persistentes
icon_label = None
icon_button = None
day_label = None

# Configuração da API Open-Meteo com cache e tentativa de repetição em caso de erro
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Função para buscar a localização inicial do usuário com base no IP
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

# Função para definir a localidade através de uma janela de entrada
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

# Função para carregar os e-mails salvos
def load_emails():
    if not os.path.exists(EMAIL_FILE):
        return []
    with open(EMAIL_FILE, 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    return emails

# Função para salvar um novo e-mail
def save_email(new_email):
    with open(EMAIL_FILE, 'a') as file:
        file.write(new_email + '\n')

# Função para selecionar um dia específico na interface
def selecionar_dia(dia, img_path, day_of_week):
    global selected_day_data, tempmax_var, tempmin_var, icon_button, day_label
    selected_day_data = (dia, img_path, day_of_week)
    tempmax_var.set(f"Max: {dia['max_temp']}°C")
    tempmin_var.set(f"Min: {dia['min_temp']}°C")
    mostraricon(selected_day_data)

# Função para mostrar detalhes do dia selecionado
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

# Função para ocultar os detalhes do dia selecionado
def ocultar_detalhes():
    global detail_labels
    for label in detail_labels:
        label.destroy()
    detail_labels.clear()

# Função para mapear códigos meteorológicos para imagens
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

# Função para criar os botões dos dias com base na localidade
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

# Função para mostrar o ícone e o dia selecionado
def mostraricon(selected_day_data):
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
    tempmax_label= ctk.CTkLabel(root, textvariable=tempmax_var, width=116, height=16, text_color="black",font=("Poppins Regular",15), bg_color="#D9D9D9")
    tempmax_label.place(x=530, y=350)
    tempmin_label= ctk.CTkLabel(root, textvariable=tempmin_var, width=116, height=16, text_color="black",font=("Poppins Regular",15), bg_color="#D9D9D9")
    tempmin_label.place(x=650, y=350)
    
    img = Image.open(img_path)
    img = img.resize((159, 144), Image.LANCZOS)  # Ajuste o tamanho conforme necessário
    img = ImageTk.PhotoImage(img)
    if icon_button:
        icon_button.destroy()
    icon_button = ctk.CTkButton(root, text="", image=img, bg_color="transparent", width=204, height=215, border_width=0, state="disabled")
    icon_button.place(x=557.0, y=124.0)
    icon_button.image = img  # Manter referência para evitar coleta de lixo

# Função para confirmar o e-mail
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

# Função para usar o e-mail selecionado
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

# Função para verificar desastres meteorológicos periodicamente
def check_disasters():
    global checking_disasters
    while checking_disasters:
        if selected_email:
            send_notification(selected_email)
        time.sleep(60)

# Função para enviar notificações
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

                    # Verifique se o ícone do aplicativo está definido corretamente
                    icon_path = "iconmestre.ico"  # Caminho para o ícone

                    # Verifique se o caminho do ícone é válido
                    if not os.path.exists(icon_path):
                        print(f"Caminho do ícone inválido. A notificação não será exibida.")
                        return

                    # Crie a notificação
                    print(f"Enviar notificação")
                    notification.notify(
                        app_name="Aplicação Meteorológica",
                        title="Aviso de Desastres",
                        message=alertatit,
                        app_icon=icon_path,
                        timeout=10  # Tempo em segundos para a notificação desaparecer
                    )                  

# Função para enviar e-mails
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

# Função para criar a imagem do ícone
def create_image():
    icon_path = "iconmestre.png"
    image = Image.open(icon_path)
    return image

# Função para fechar o aplicativo
def on_quit(icon, item):
    global checking_disasters
    checking_disasters = False
    icon.stop()
    root.quit()
    root.destroy()

# Função para abrir a janela principal
def open_main_window(icon, item):
    root.after(0, root.deiconify)
    icon.stop()

# Função para minimizar a aplicação para a bandeja do sistema
def minimize_to_tray():
    global icon
    icon = pystray.Icon("iconmestre.ico", create_image(), "Climate APP", menu=pystray.Menu(
        item('Abrir', open_main_window),
        item('Fechar', on_quit)
    ))
    threading.Thread(target=icon.run, daemon=True).start()

#Função para exibir o mapa
def mapa():
    global map_widget
    try:
        # Verifique se map_widget existe e destrua-o se necessário
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
                    map_widget.place(x=248.0, y=129.0)
                    map_widget.set_position(lat, lon)
                    map_widget.set_zoom(15)
                else:
                    resultado_var.set("Nenhum dado de humidade disponível para esta localidade.")
            else:
                resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")
    except Exception as e:
        resultado_var.set(f"Ocorreu um erro ao tentar exibir o mapa: {e}")

# Função para destruir o mapa
def destruir_mapa():
    global map_widget
    if map_widget:
        map_widget.destroy()
        map_widget = None

# Função para plotar gráficos de temperatura, umidade e velocidade do vento        
def plot_graphs(times, temps, humidities, wind_speeds):
    fig, axs = plt.subplots(3, 1, figsize=(10, 6))  # Ajuste a altura da figura para 6

    # Format the x-axis to show only hours and minutes
    time_format = plt.matplotlib.dates.DateFormatter('%H:%M')

    # Plot temperature
    axs[0].plot(times, temps, label='Temperature (°C)')
    axs[0].set_title('Temperature over Time')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].xaxis.set_major_formatter(time_format)
    axs[0].legend()
    axs[0].grid(True)

    # Plot humidity
    axs[1].plot(times, humidities, label='Humidity (%)', color='orange')
    axs[1].set_title('Humidity over Time')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Humidity (%)')
    axs[1].xaxis.set_major_formatter(time_format)
    axs[1].legend()
    axs[1].grid(True)

    # Plot wind speed
    axs[2].plot(times, wind_speeds, label='Wind Speed (m/s)', color='green')
    axs[2].set_title('Wind Speed over Time')
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('Wind Speed (m/s)')
    axs[2].xaxis.set_major_formatter(time_format)
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()

# Função para analisar os dados meteorológicos
def analyze_data():
    global selected_day_data
    if selected_day_data:
        dia, img_path, day_of_week = selected_day_data
        cidade, pais = localidade_var.get().split(': ')[1].split(' - ')
        
        # Obter latitude e longitude da API Weatherbit
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                
                # Obter dados horários da API Open Meteo
                date = dia['datetime']
                start_date_str = date
                end_date_str = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,windspeed_10m&start_date={start_date_str}&end_date={end_date_str}&timezone=auto"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if 'hourly' in data:
                        times = [datetime.strptime(hour, '%Y-%m-%dT%H:%M').replace(tzinfo=None) for hour in data['hourly']['time']]
                        temps = data['hourly']['temperature_2m']
                        humidities = data['hourly']['relative_humidity_2m']
                        wind_speeds = data['hourly']['windspeed_10m']
                        plot_graphs(times, temps, humidities, wind_speeds)
                    else:
                        print("Nenhum dado horário disponível para esta localidade e data.")
                else:
                    print(f"Erro ao buscar dados da API Open Meteo: {response.status_code}")
            else:
                print("Nenhum dado de localização disponível para esta localidade.")
        else:
            print(f"Erro ao buscar dados da API Weatherbit: {response.status_code}")
 
# Função para obter o caminho relativo dos assets           
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

 #Função para salvar os dados meteorológicos em um arquivo
def save_data():
    global selected_day_data
    if selected_day_data:
        dia, img_path, day_of_week = selected_day_data
        with open("weather_data.txt", 'a') as file:  # Abra o arquivo em modo de adição
            file.write(f"Data: {dia['datetime']}\n")
            file.write(f"Temperatura: {dia['temp']}°C\n")
            file.write(f"Máxima: {dia['max_temp']}°C\n")
            file.write(f"Mínima: {dia['min_temp']}°C\n")
            file.write(f"Sensação: {dia['app_max_temp']}°C\n")
            file.write(f"Clima: {dia['weather']['description']}\n")
            file.write(f"Velocidade do Vento: {dia['wind_spd']} m/s\n")
            file.write(f"Direção do Vento: {dia['wind_cdir']}\n")
            file.write(f"Precipitação: {dia['precip']} mm\n")
            file.write(f"Humidade: {dia['rh']}%\n")
            file.write("\n")  # Adiciona uma linha em branco entre registros
        print(f"Dados salvos em weather_data.txt")
        
# Função para carregar os dados meteorológicos de um arquivo
def load_data():
    if os.path.exists("weather_data.txt"):
        with open("weather_data.txt", 'r') as file:
            data = file.read()
        show_data(data)
    else:
        print(f"Arquivo weather_data.txt não encontrado.")

# Função para exibir os dados meteorológicos em uma janela
def show_data(data):
    data_window = ctk.CTkToplevel(root)
    data_window.title("Dados do Tempo Salvos")
    data_window.geometry("400x300")

    text_widget = Text(data_window, wrap='word')
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(END, data)


# Inicialização da interface principal
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
    275.0,
    438.0,
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

# Botão de busca de localidade
lupa_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
lupa_1 = ctk.CTkButton(
    root,
    text="",
    image=lupa_image_1,
    bg_color="#4DB1C7",
    fg_color="#4DB1C7",
    command= set_localidade,
    width=39.0,
    height=39.0
    
)
lupa_1.place(
    x=720.0,
    y=20.0,
)


canvas.create_text(
    17.0,
    23.0,
    anchor="nw",
    text="Climate APP",
    fill="#FFFFFF",
    font=("Poppins Regular", 24 * -1)
)

# Botões de email
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
    command=usar_email_selecionado,

)
button_10.place(
    x=48.0,
    y=544.0,
    width=126.0,
    height=28.0
)

# Botões para abrir e fechar o mapa
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

# Botões para mostrar e ocultar detalhes
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

# Botões para salvar e carregar dados
salvardata_image_14 = PhotoImage(
    file=relative_to_assets("button_14.png"))
salvardata_14 = Button(
    bg="#D9D9D9",
    image=salvardata_image_14,
    borderwidth=0,
    highlightthickness=0,
    command=save_data,
    relief="flat"
)
salvardata_14.place(
    x=248.0,
    y=507.0,
    width=130.0,
    height=35.0
)

abridata_image_15 = PhotoImage(
    file=relative_to_assets("button_15.png"))
abridata_15 = Button(
    image=abridata_image_15,
    bg="#D9D9D9",
    borderwidth=0,
    highlightthickness=0,
    command=load_data,
    relief="flat"
)
abridata_15.place(
    x=379.0,
    y=507.0,
    width=130.0,
    height=35.0
)

# Botão para analisar dados
analyze_button = ctk.CTkButton(root, text="Analisar Dados", command=analyze_data,width=210, height=35, bg_color="#D9D9D9", fg_color="#37A376", font=("Poppins Regular", 14),corner_radius=25)
analyze_button.place(x=557, y=500)

# Labels para mostrar a localidade
label_localidade = ctk.CTkLabel(root,textvariable=localidade_var,bg_color="#4DB1C7",fg_color="#4DB1C7",font=("Poppins Regular",15))
label_localidade.pack(side=tk.LEFT, anchor=tk.N,pady=20,padx=20)
label_localidade.place(x=500.0,y=20.0)

#Função para fechar aplicação ou minimizar para bandeja do sistema
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

# Função para a tarefa principal que roda em segundo plano
def main_task():
    while True:
        print("Ainda estou a trabalhar no background")
        time.sleep(5)

butoesfunction()
task_thread = threading.Thread(target=main_task, daemon=True)
task_thread.start()

root.resizable(False, False)
root.mainloop()






