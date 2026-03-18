import os
import pandas as pd
import re

pasta = r"E:\DESENHOS E PROJETOS"

df = pd.read_excel("codigos.xlsx")

# extrai apenas os 6 números do código
codigos = df.iloc[:,0].dropna().astype(str).str.extract(r'(\d{6})')[0]

arquivos = []

for root, dirs, files in os.walk(pasta):
    for file in files:
        arquivos.append(file)

resultado = []

for codigo in codigos:

    divisoes = []
    encontrou_arquivo = False
    tem_drawing = False
    tem_part = False

    for arquivo in arquivos:

        nome = os.path.splitext(arquivo)[0]
        ext = os.path.splitext(arquivo)[1].lower()

        # procura divisão tipo 123456 - A
        match = re.match(rf"{codigo}\s*-\s*([A-Z]+)", nome)

        if match:
            encontrou_arquivo = True
            divisoes.append(match.group(1))

        elif nome.startswith(codigo):
            encontrou_arquivo = True

        if ext == ".slddrw" and nome.startswith(codigo):
            tem_drawing = True

        if ext == ".sldprt" and nome.startswith(codigo):
            tem_part = True


    if divisoes:
        divisoes = sorted(set(divisoes))
        tipo = "Dividido"

    elif encontrou_arquivo:
        tipo = "Peça única"

    else:
        tipo = "Não encontrado"

    resultado.append([
        codigo,
        tipo,
        ",".join(divisoes),
        "Sim" if tem_drawing else "Não",
        "Sim" if tem_part else "Não"
    ])

df_resultado = pd.DataFrame(
    resultado,
    columns=["Código","Tipo","Divisões","Tem Drawing","Tem Part"]
)

df_resultado.to_excel("resultado_divisoes.xlsx", index=False)

print("Finalizado")