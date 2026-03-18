from playwright.sync_api import sync_playwright
import os

BASE_DIR = r"C:\Users\CAM-Brutale\Desktop\busca_desenhos"
ARQUIVO_ESTADO = os.path.join(BASE_DIR, "estado.json")

print("Vai salvar em:", ARQUIVO_ESTADO)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://brutale.monday.com", wait_until="domcontentloaded")
    print("Navegador aberto. Faça login no Monday.")

    input("Depois de entrar totalmente no Monday, aperte ENTER aqui... ")

    context.storage_state(path=ARQUIVO_ESTADO)

    print("Sessão salva com sucesso em:")
    print(ARQUIVO_ESTADO)

    input("Aperte ENTER para fechar o navegador... ")
    browser.close()