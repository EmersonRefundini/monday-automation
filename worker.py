from playwright.sync_api import sync_playwright
import queue
import threading
import os

fila = queue.Queue()

BASE_DIR = r"C:\Users\CAM-Brutale\Desktop\busca_desenhos"
ESTADO = os.path.join(BASE_DIR, "estado.json")
BOARD_ID = "18404237753"

play = None
browser = None
context = None
page = None


def iniciar_browser():
    global play, browser, context, page

    play = sync_playwright().start()
    browser = play.chromium.launch(headless=True)
    context = browser.new_context(storage_state=ESTADO)

    context.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["image", "media", "font"]
        else route.continue_()
    )

    page = context.new_page()
    page.goto(f"https://brutale.monday.com/boards/{BOARD_ID}", wait_until="domcontentloaded", timeout=30000)
    print("🚀 Robô pronto.")

def criar_nota(titulo, corpo):
    botao_novo = page.get_by_text("Novo")
    botao_novo.wait_for(timeout=10000)
    botao_novo.click(timeout=10000)

    opcao_nota = page.get_by_text("Adicionar uma nota")
    opcao_nota.wait_for(timeout=10000)
    page.wait_for_timeout(500)
    opcao_nota.click(force=True)

    page.locator(".icon.icon-dapulse-edit").first.wait_for(timeout=10000)
    page.locator(".icon.icon-dapulse-edit").first.click(force=True)

    titulo_box = page.locator("#collaboration_area").get_by_role("textbox")
    titulo_box.wait_for(timeout=10000)
    titulo_box.click()
    titulo_box.press("ControlOrMeta+A")
    titulo_box.fill(titulo)

    editor = page.get_by_label("Editor de rich text")
    editor.wait_for(timeout=10000)
    editor.click()
    editor.fill(corpo)

    salvar = page.get_by_role("button", name="Salvar")
    salvar.wait_for(timeout=10000)
    salvar.click(force=True)

import re

def processar_item(item_id):
    url = f"https://brutale.monday.com/boards/{BOARD_ID}/pulses/{item_id}"

    print("Processando:", item_id)

    page.goto(url, wait_until="domcontentloaded", timeout=30000)

    botao_info = page.get_by_role("button", name=re.compile("Informações"))
    botao_info.wait_for(timeout=15000)
    botao_info.click(timeout=15000)

    page.wait_for_timeout(800)

    criar_nota("PASTA DA PROGRAMAÇÃO", "X")
    page.wait_for_timeout(500)

    criar_nota("HURON", "MAQ:\n\nPEDIDO:\n\nCRÍTICO:\n\nCC:")

    print("✅ Finalizado:", item_id)

def worker():
    print("WORKER INICIOU")
    iniciar_browser()

    while True:
        item_id = fila.get()
        try:
            print("Processando item:", item_id)
            processar_item(item_id)
            print("Notas criadas:", item_id)
        except Exception:
            import traceback
            print("ERRO NO WORKER:")
            traceback.print_exc()
        finally:
            fila.task_done()

threading.Thread(target=worker, daemon=True).start()