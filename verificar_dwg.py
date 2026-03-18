import os
import pandas as pd
import re

pasta = r"E:\DESENHOS E PROJETOS"

df = pd.read_excel("codigos.xlsx")

codigos = df.iloc[:,0].dropna().astype(int).astype(str).str.zfill(6)

arquivos = []

for root, dirs, files in os.walk(pasta):
    for file in files:
        if file.lower().endswith(".dwg"):
            arquivos.append(file)

resultado = []

for codigo in codigos:

    divisoes = []
    encontrou_arquivo = False

    for arquivo in arquivos:

        nome = arquivo.replace(".dwg","")

        # procura divisão tipo 123456 - A
        match = re.match(rf"{codigo}\s*-\s*([A-Z]+)", nome)

        if match:
            encontrou_arquivo = True
            divisoes.append(match.group(1))

        # procura peça única tipo 123456
        elif nome.startswith(codigo):
            encontrou_arquivo = True

    if divisoes:
        divisoes = sorted(set(divisoes))
        resultado.append([codigo, "Dividido", ",".join(divisoes)])

    elif encontrou_arquivo:
        resultado.append([codigo, "Peça única", ""])

    else:
        resultado.append([codigo, "Não encontrado", ""])

df_resultado = pd.DataFrame(resultado, columns=["Código","Tipo","Divisões"])

df_resultado.to_excel("resultado_divisoes.xlsx", index=False)

print("Finalizado")