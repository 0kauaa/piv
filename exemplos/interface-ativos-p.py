import yfinance as yf
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import Label, Entry, Button
from PIL import Image, ImageTk
import os

def calcular_pesos():
    try:
        tickers = []

        if entrada1.get().strip():
            tickers.append(entrada1.get().strip().upper())
        if entrada2.get().strip():
            tickers.append(entrada2.get().strip().upper())
        if entrada3.get().strip():
            tickers.append(entrada3.get().strip().upper())

        qtde = len(tickers)

        if qtde not in [2, 3]:
            recomendacoes_label.config(text=" Digite 2 ou 3 ativos (preencha as caixas).")
            return

        # Baixando dados e calculando retornos
        retornos = []
        for t in tickers:
            dados = yf.Ticker(t).history(period='3y', interval='1d').Close.pct_change().dropna()
            retornos.append(dados)

        # Alinhar os retornos
        aligned_df = pd.concat(retornos, axis=1)
        aligned_df.columns = [f'ativo{i+1}' for i in range(qtde)]
        aligned_df.dropna(inplace=True)

        # Calcular matriz de covariância
        cov_matrix = np.cov([aligned_df[col] for col in aligned_df.columns])
        lista_2d = cov_matrix.tolist()

        # Criar matriz ajustada: diagonal², fora da diagonal * 2
        nova_matriz = []
        for i in range(qtde):
            linha = []
            for j in range(qtde):
                if i == j:
                    linha.append(lista_2d[i][j] ** 2)
                else:
                    linha.append(lista_2d[i][j] * 2)
            nova_matriz.append(linha)

        A = np.array(nova_matriz)
        b = np.array([1] * qtde)

        w = np.linalg.solve(A, b)
        w_normalizado = w / np.sum(w)

        resultado = "Pesos normalizados:\n\n"
        for i in range(qtde):
            resultado += f"{tickers[i]}: {w_normalizado[i]*100:.2f}%\n"
        resultado += f"\nSoma: {np.sum(w_normalizado):.2f}%"

        recomendacoes_label.config(text=resultado)

    except Exception as e:
        recomendacoes_label.config(text=f" Erro: {str(e)}")

# GUI
root = tk.Tk()

# icon
caminho_icone = os.path.join(os.path.dirname(__file__), "icon.png")
icone = Image.open(caminho_icone)
icone = ImageTk.PhotoImage(icone)
root.iconphoto(True, icone)

# Fundo
caminho_imagem = os.path.join(os.path.dirname(__file__), "fundo.jpg")
imagem_fundo = Image.open(caminho_imagem)
imagem_fundo = imagem_fundo.resize((1000, 563))
imagem_fundo = ImageTk.PhotoImage(imagem_fundo)

label_fundo = Label(root, image=imagem_fundo)
label_fundo.place(x=0, y=0, relwidth=1, relheight=1)

# Frame
frame = tk.Frame(root, bg="gray", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

Label(frame, text="Ativo 1:", font=("Arial", 12), bg="gray").grid(row=0, column=0, sticky="w")
entrada1 = Entry(frame, width=20, font=("Arial", 12))
entrada1.grid(row=0, column=1, pady=5)

Label(frame, text="Ativo 2:", font=("Arial", 12), bg="gray").grid(row=1, column=0, sticky="w")
entrada2 = Entry(frame, width=20, font=("Arial", 12))
entrada2.grid(row=1, column=1, pady=5)

Label(frame, text="Ativo 3 (opcional):", font=("Arial", 12), bg="gray").grid(row=2, column=0, sticky="w")
entrada3 = Entry(frame, width=20, font=("Arial", 12))
entrada3.grid(row=2, column=1, pady=5)

botao_calcular = Button(frame, text="Calcular Distribuição de Capital ", font=("Arial", 12), command=calcular_pesos)
botao_calcular.grid(row=3, column=0, columnspan=2, pady=10)

recomendacoes_label = Label(frame, text="", font=("Arial", 14), wraplength=400, bg="gray")
recomendacoes_label.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()