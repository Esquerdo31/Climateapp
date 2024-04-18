#Ler em UTF-8
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import simpledialog

def localidade_action():
    localidade = simpledialog.askstring("Localidade", "Digite a localidade:")
    if localidade:
                 localidade_var.set(f"Localidade: {localidade}") #Atualiza a variável localidade
                 print(f"Localidade definida: {localidade}")
def temperatura_action():
    print("Botao Temperatura pressionado")

def humidade_action():
    print("Botao Humidade pressionado")

def velocidade_vento_action():
    print("Botao Velocidade do Vento pressionado")

def analise_dados_action():
    print("Botao Analise de Dados pressionado")

def alertas_desastres_action():
    print("Botao Alertas de Desastres Naturais pressionado")

# Cria a janela principal
root = tk.Tk()
root.title("Informacoes Meteorologicas")


# Configura o tamanho da janela
root.geometry("400x300")

localidade_var=tk.StringVar(root, "Localidade: Nenhuma")

label_localidade = tk.Label(root, textvariable=localidade_var, fg="blue")
label_localidade.pack(side=tk.TOP, anchor=tk.NE)

# Botão de Localidade
btn_localidade = tk.Button(root, text="Localidade", command=localidade_action)
btn_localidade.pack(side=tk.TOP, anchor=tk.NE)

# Botão de Temperatura
btn_temperatura = tk.Button(root, text="Temperatura", command=temperatura_action)
btn_temperatura.pack()

# Botão de Humidade
btn_humidade = tk.Button(root, text="Humidade", command=humidade_action)
btn_humidade.pack()

# Botão de Velocidade do Vento
btn_velocidade_vento = tk.Button(root, text="Velocidade do Vento", command=velocidade_vento_action)
btn_velocidade_vento.pack()

# Botão de Análise de Dados
btn_analise_dados = tk.Button(root, text="Analise de Dados", command=analise_dados_action)
btn_analise_dados.pack()

# Botão de Alertas de Desastres Naturais
btn_alertas_desastres = tk.Button(root, text="Alertas de Desastres Naturais", command=alertas_desastres_action)
btn_alertas_desastres.pack()

# Executa o loop principal da janela
root.mainloop()
