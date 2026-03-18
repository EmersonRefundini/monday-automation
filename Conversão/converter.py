import os
import win32com.client

pasta = r"E:\DESENHOS E PROJETOS"

swApp = win32com.client.Dispatch("SldWorks.Application")
swApp.Visible = False

for root, dirs, files in os.walk(pasta):
    for file in files:

        if file.lower().endswith(".slddrw"):

            caminho = os.path.join(root, file)
            pdf = os.path.splitext(caminho)[0] + ".pdf"

            # se já existir PDF ele pula
            if os.path.exists(pdf):
                print("PDF já existe, pulando:", file)
                continue

            print("Convertendo:", file)

            model = swApp.OpenDoc6(caminho, 3, 1, "", 0, 0)

            if model:
                model.Extension.SaveAs(pdf, 0, 1, None, 0, 0)
                swApp.CloseDoc(model.GetTitle())

print("FINALIZADO")