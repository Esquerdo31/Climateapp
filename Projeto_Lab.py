from ast import NotEq, Param
from ctypes.wintypes import SIZE
import tkinter as tk
from tkinter import ANCHOR, simpledialog, messagebox, ttk
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


API_KEY_WEATHER = '6de9d4c574f54850af113b86005202b2'  # Chave da API do Weatherbit
API_KEY_GEO = 'cc88a6dd1b8de7'  # Chave da API IPinfo
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
EMAIL_FILE = 'emails.txt'

#Variável para guardar a email
selected_email=""
warning= 0

def fetch_initial_location():
    try:
        response = requests.get(f"https://ipinfo.io?token={API_KEY_GEO}")
        if response.status_code == 200:
            data = response.json()
            loc = data['city'] + ' - ' + data['country']
            lat, lon = data['loc'].split(',')
            coordenadas = f"{lat} - {lon}"
            cor_var.set(f"Latitude: {lat} - Longitude: {lon}")
            localidade_var.set(f"Localidade: {loc}")

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
            localidade_window.destroy()

    confirm_button = ctk.CTkButton(localidade_window, text="Confirmar", command=confirm_action)
    confirm_button.pack()

def temperatura_action():
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/current?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        print(f"url: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"data: {data}")
            if 'data' in data and len(data['data']) > 0:
                temperatura = data['data'][0]['temp']
                cidade = data['data'][0]['city_name']
                latitude = data['data'][0]['lat']
                lon = data['data'][0]['lon']
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
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
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
                lat = data['data'][0]['lat']
                lon = data['data'][0]['lon']
                resultado_var.set(f"Humidade em {cidade}, {pais}: {humidade}%")
            else:
                resultado_var.set("Nenhum dado de humidade disponível para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

def fetch_temperature_data():
    try:
        coordenadas = cor_var.get().replace("Latitude: ", "").replace("Longitude: ", "").split(" - ")
        if len(coordenadas) != 2:
            raise ValueError("Formato de coordenadas inválido. Esperado: 'Latitude: X - Longitude: Y'")

        lat, lon = coordenadas

        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

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

def previsao_temperatura():
    full_localidade = localidade_var.get().split(': ')[1]
    previsaobutton = ctk.CTkToplevel(root)
    previsaobutton.title("Previsão de Temperatura")
    previsaobutton.geometry("300x600")

    button_font = font.Font(family="Helvetica", size=12, weight="bold")
    label_font = font.Font(family="Helvetica", size=10)

    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/forecast/daily?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        print(f"url: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                for i in range(7):
                    dia = data['data'][i]
                    icon_code = dia['weather']['code']
                    image_path = map_weather_codes_to_images().get(str(icon_code),'C:\\Users\\costi\\Desktop\\Uni\\Cadeiras2semestre1ano\\lab\\Trabalho2\\icons\\default.png')
                    print(f"image_path: {image_path}")
                    # Verificar se o caminho da imagem existe
                    if not os.path.exists(image_path):
                        image_path = 'icons/default.png'  # Caminho para uma imagem padrão ou substituta

                    img = Image.open(image_path)
                    img = img.resize((30, 30), Image.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                    temp = dia['temp']
                    date_str = dia['datetime']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')
                    button_text = f"{day_of_week}: {temp}°C"
                    button = ctk.CTkButton(previsaobutton, text=button_text, image=img, compound=tk.LEFT,
                                           command=lambda d=dia: mostrar_detalhes(d))
                    button.image = img  # keep a reference to avoid garbage collection
                    button.pack(pady=5)
            else:
                ctk.CTkLabel(previsaobutton, text="Nenhum dado de previsão disponível para esta localidade.")
                             
        else:
            ctk.CTkLabel(previsaobutton, text=f"Erro ao buscar dados da API: {response.status_code}")

def mostrar_detalhes(dia):
    detalhes_janela = ctk.CTkToplevel(root)
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
    ctk.CTkLabel(detalhes_janela, text=detalhes_texto, justify=tk.LEFT).pack(pady=10)

def load_emails():
    """Ler e-mails a partir do arquivo de texto."""
    if not os.path.exists(EMAIL_FILE):
        return []
    with open(EMAIL_FILE, 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    return emails

def save_email(new_email):
    """Salvar um novo e-mail no arquivo de texto."""
    with open(EMAIL_FILE, 'a') as file:
        file.write(new_email + '\n')
        
def emailconfirma():
    """Função para carregar e-mails e enviar notificação."""
    global selected_email  # Declarar a variável global
    emails = load_emails()

    def choose_email():
        email_list_window = ctk.CTkToplevel(root)
        email_list_window.title("Escolher E-mail")
        email_list_window.geometry("300x200")

        listbox = tk.Listbox(email_list_window)
        for email in emails:
            listbox.insert(tk.END, email)
        listbox.pack()

        def on_select():
            global selected_email
            selected_email = listbox.get(tk.ACTIVE)
            
           
            if selected_email:
                email_list_window.destroy()

        select_button = ctk.CTkButton(email_list_window, text="Selecionar", command=on_select)
        select_button.pack()

        def add_new_email():
            global selected_email
            new_email = simpledialog.askstring("Novo E-mail", "Digite o novo e-mail:")
            if new_email:
                save_email(new_email)
                selected_email = new_email
                
                email_list_window.destroy()

        new_email_button = ctk.CTkButton(email_list_window, text="Adicionar Novo E-mail", command=add_new_email)
        new_email_button.pack()

    choose_email()
    
def usar_email_selecionado():
    global selected_email
    global warning
    if selected_email:
            if warning == 0:
                send_notification(selected_email)
                messagebox.showinfo("Aviso", "Caso seja detetado um aviso será envidado para o teu email!")
                warning = 1
                agendar_checagem()
            else:
                send_notification(selected_email)
                agendar_checagem()
    else:
         messagebox.showinfo("Informação", "Nenhum e-mail selecionado.")
    

def agendar_checagem():
    usar_email_selecionado()
    root.after(30000, agendar_checagem)  # 300000 milissegundos = 5 minutos

# Função para enviar e-mail
def send_email(subject, body, to_email):
    """Enviar e-mail usando smtplib."""
    from_email = "contadeavisos@gmail.com"  # Substitua pelo seu e-mail
    from_password = "contadeavisos123"  # Substitua pela sua senha

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Substitua pelo servidor SMTP do seu provedor de e-mail
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        
def send_notification(to_email):
   
    full_localidade = localidade_var.get().split(': ')[1]
    if full_localidade and full_localidade != "Nenhuma":
        cidade, pais = full_localidade.split(' - ')
        url = f"https://api.weatherbit.io/v2.0/alerts?city={cidade}&country={pais}&key={API_KEY_WEATHER}"
        print(f"url: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"data: {data}")
            if 'alerts' in data and len(data['alerts']) > 0:
                alerta = data['alerts'][0]['severity']
                if alerta in ["Advisory", "Watch", "Warning"]:
                    alertatit = data['alerts'][0]['title']
                    alertadesc = data['alerts'][0]['description']
                    subject = f"Alerta Meteorológico: {alertatit}"
                    body = f"Título: {alertatit}\n\nDescrição: {alertadesc}"
                    send_email(subject, body, to_email)
                    notif = Notification(app_id="Aplicação Meteorológica",title="Aviso de Desastres",msg=alerta , duration="short", icon=r"C:\Users\costi\Desktop\Uni\Cadeiras2semestre1ano\lab\Trabalho2\iconmestre.png")
                    notif.set_audio(audio.Default, loop=False)
                    notif.add_actions(label="Alerta Detetado!",launch="https://gmail.com/" )
                    notif.show()
                else:
                    print("Nenhum alerta relevante encontrado.")
            else:
                print("Nenhum alerta disponível para esta localidade.")
        else:
            print(f"Erro ao buscar dados da API: {response.status_code}")
               
    # notif = Notification(app_id="Aplicação Meteorológica",title="Aviso de Desastres",msg="Teste de notifcação", duration="short", icon=r"C:\Users\costi\Desktop\Uni\Cadeiras2semestre1ano\lab\Trabalho2\iconmestre.png")
    # notif.set_audio(audio.Default, loop=False)
    # notif.add_actions(label="Alerta Detetado!",launch="https://gmail.com/" )
    # notif.show()

def create_image():
    # Create an image with PIL
    width = 64
    height = 64
    icon_path = "C:\\Users\\costi\\Desktop\\Uni\\Cadeiras2semestre1ano\\lab\\Trabalho2\\iconmestre.png"
    image = Image.open(icon_path)
    return image

def on_quit(icon, item):
    icon.stop()
    root.quit()
    root.destroy()

def open_main_window(icon, item):
    root.after(0, root.deiconify)
    icon.stop()

def minimize_to_tray():
    global icon
    icon = pystray.Icon("test_icon", create_image(), "Background Script", menu=pystray.Menu(
        item('Open', open_main_window),
        item('Quit', on_quit)
    ))
    icon.run()


root = ctk.CTk()
root.title("Informações Meteorológicas")
root.geometry("500x400")

# Defina o ícone da janela principal

icon_path = "C:\\Users\\costi\\Desktop\\Uni\\Cadeiras2semestre1ano\\lab\\Trabalho2\\iconmestre.png"
img = Image.open(icon_path)
photo = ImageTk.PhotoImage(img)
root.iconphoto(True,photo)
root.iconbitmap(icon_path)

cor_var = tk.StringVar(root, "Latitude: Nenhuma - Longitude: Nenhuma")
localidade_var = tk.StringVar(root, "Localidade: Nenhuma")
resultado_var = tk.StringVar(root)

# Lista de códigos de país para o exemplo, use uma lista completa conforme necessário
country_list = ['BR', 'US', 'PT', 'ES', 'FR', 'DE', 'IT']

fetch_initial_location()

# Container for buttons
button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(side=tk.TOP, pady=10)

btn_localidade = ctk.CTkButton(button_frame, text="Definir Localidade", command=set_localidade)
btn_localidade.pack(side=tk.TOP, pady=10)

btn_temperatura = ctk.CTkButton(button_frame, text="Temperatura", command=temperatura_action)
btn_temperatura.pack(side=tk.LEFT, padx=5)

btn_humidade = ctk.CTkButton(button_frame, text="Humidade", command=get_humidade)
btn_humidade.pack(side=tk.LEFT, padx=5)

btn_vv = ctk.CTkButton(button_frame, text="Velocidade do Vento", command=get_velocidade)
btn_vv.pack(side=tk.LEFT, padx=5)

btn_show_graph = ctk.CTkButton(root, text="Mostrar Gráfico de Temperaturas", command=show_temperature_graph)
btn_show_graph.pack(pady=10)

btn_prev = ctk.CTkButton(root, text="Previsão de Temperatura", command=previsao_temperatura)
btn_prev.pack(pady=10)

label_localidade = ctk.CTkLabel(root, textvariable=localidade_var, fg_color="blue")
label_localidade.pack(side=tk.TOP, anchor=tk.N)

label_resultado = ctk.CTkLabel(root, textvariable=resultado_var)
label_resultado.pack(side=tk.TOP, anchor=tk.N, pady=20)

btn_aviso = ctk.CTkButton(root, text="⚠️Avisar desastres!⚠️", command=usar_email_selecionado, fg_color="red")
btn_aviso.pack(side=ctk.BOTTOM, anchor=tk.SE, pady=20, padx=10)

btn_email= ctk.CTkButton(root, text="Inserir email",command= emailconfirma,fg_color="green")
btn_email.pack(side=tk.BOTTOM, anchor=tk.SE, pady=10, padx=10)

def on_close():
    if messagebox.askokcancel("Quit", "Do you want to minimize to tray instead of quitting?"):
        root.withdraw()
        minimize_to_tray()
    else:
        root.quit()
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)


def main_task():
    while True:
        print("Script is running in the background...")
        time.sleep(5)


# Run the main task in a separate thread
task_thread = threading.Thread(target=main_task, daemon=True)
task_thread.start()

root.mainloop()
