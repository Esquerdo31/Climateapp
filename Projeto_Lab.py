import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import requests

API_KEY_WEATHER = '0a862d8a9b294adb99eb68c1c92a2365'  # Chave da API do Weatherbit
API_KEY_GEO = 'cc88a6dd1b8de7'         # Chave da API IPinfo

def fetch_initial_location():
    try:
        response = requests.get(f"https://ipinfo.io?token={API_KEY_GEO}")
        if response.status_code == 200:
            data = response.json()
            loc = data['city'] + ' - ' + data['country']
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
                resultado_var.set(f"Temperatura em {cidade}, {pais}: {temperatura}C")
            else:
                resultado_var.set("Nenhum dado de temperatura disponivel para esta localidade.")
        else:
            resultado_var.set(f"Erro ao buscar dados da API: {response.status_code}")

root = tk.Tk()
root.title("Informacoes Meteorologicas")
root.geometry("500x400")

localidade_var = tk.StringVar(root, "Localidade: Nenhuma")
resultado_var = tk.StringVar(root)

# Lista de códigos de país para o exemplo, use uma lista completa conforme necessário
country_list = ['BR', 'US', 'PT', 'ES', 'FR', 'DE', 'IT']

fetch_initial_location()

btn_localidade = tk.Button(root, text="Definir Localidade", command=set_localidade)
btn_localidade.pack(side=tk.TOP, anchor=tk.N)

btn_temperatura = tk.Button(root, text="Consultar Temperatura", command=temperatura_action)
btn_temperatura.pack(side=tk.TOP, anchor=tk.N, pady=10)

label_localidade = tk.Label(root, textvariable=localidade_var, fg="blue")
label_localidade.pack(side=tk.TOP, anchor=tk.N)

label_resultado = tk.Label(root, textvariable=resultado_var, fg="red")
label_resultado.pack(side=tk.TOP, anchor=tk.N, pady=20)

root.mainloop()
