from playwright.sync_api import sync_playwright
import queue
import threading
import os
import traceback
import re
import time

fila = queue.Queue()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(BASE_DIR, "estado.json")
BOARD_ID = "18404237753"

play = None
browser = None


def iniciar_browser():
    global play, browser

    print("WORKER INICIOU")
    print("BASE_DIR =", BASE_DIR)
    print("ESTADO =", ESTADO)
    print("estado.json existe?", os.path.exists(ESTADO))

    if not os.path.exists(ESTADO):
        raise FileNotFoundError(f"estado.json não encontrado em {ESTADO}")

    play = sync_playwright().start()
    browser = play.chromium.launch(headless=True)

    print("🚀 Browser base pronto.")


def criar_contexto():
    context = browser.new_context(
        storage_state=ESTADO,
        viewport={"width": 1600, "height": 1200}
    )

    context.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["image", "media", "font"]
        else route.continue_()
    )

    return context


def criar_nota(page, titulo, corpo):
    botao_novo = page.get_by_text("Novo", exact=True).last
    botao_novo.wait_for(timeout=15000)
    botao_novo.click(timeout=15000)

    opcao_nota = page.get_by_text("Adicionar uma nota", exact=True)
    opcao_nota.wait_for(timeout=10000)
    page.wait_for_timeout(300)
    opcao_nota.click(force=True)

    icone_editar = page.locator(".icon.icon-dapulse-edit").first
    icone_editar.wait_for(timeout=10000)
    icone_editar.click(force=True)

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


def abrir_item_via_board(page, item_id):
    url_board = f"https://brutale.monday.com/boards/{BOARD_ID}"
    page.goto(url_board, wait_until="domcontentloaded", timeout=30000)

    linha_item = page.get_by_test_id(f"item-{item_id}")
    linha_item.wait_for(timeout=20000)

    botao_abrir_item = linha_item.get_by_role(
        "button",
        name=re.compile(r"^Selecionar elemento:")
    )
    botao_abrir_item.wait_for(timeout=10000)
    botao_abrir_item.click(timeout=10000)


def processar_item(item_id):
    url_item = f"https://brutale.monday.com/boards/{BOARD_ID}/pulses/{item_id}"
    print("Processando:", item_id)

    # pequeno atraso para itens vindos de formulário terminarem de aparecer/renderizar
    time.sleep(3)

    context = None
    page = None

    try:
        context = criar_contexto()
        page = context.new_page()

        # tentativa 1: abrir direto pela URL do item
        try:
            page.goto(url_item, wait_until="domcontentloaded", timeout=25000)

            botao_info = page.get_by_role("button", name=re.compile("Informações"))
            botao_info.wait_for(timeout=5000)

        except Exception:
            print("Informações não apareceu direto. Tentando abrir pela linha do board...")
            abrir_item_via_board(page, item_id)
            botao_info = page.get_by_role("button", name=re.compile("Informações"))
            botao_info.wait_for(timeout=10000)

        try:
            botao_info.click(timeout=5000)
        except Exception:
            print("Clique normal em Informações falhou, tentando force=True")
            botao_info.click(timeout=5000, force=True)

        page.wait_for_timeout(800)

        page.get_by_text("Novo", exact=True).last.wait_for(timeout=10000)

        criar_nota(page, "PASTA DA PROGRAMAÇÃO", "X")
        page.wait_for_timeout(300)
        criar_nota(page, "HURON", "MAQ:\n\nPEDIDO:\n\nCRÍTICO:\n\nCC:")

        print("✅ Finalizado:", item_id)

    except Exception:
        print("ERRO NO PROCESSAMENTO:")
        traceback.print_exc()

        try:
            if page:
                page.screenshot(path="/app/erro_online.png", full_page=True)
                print("📸 Screenshot salva em /app/erro_online.png")
        except Exception:
            print("Erro ao tirar screenshot")

        raise

    finally:
        try:
            if page:
                page.close()
        except Exception:
            pass

        try:
            if context:
                context.close()
        except Exception:
            pass


def worker():
    try:
        iniciar_browser()
    except Exception:
        print("ERRO AO INICIAR O BROWSER:")
        traceback.print_exc()
        return

    while True:
        item_id = fila.get()
        print("Item entrou na fila:", item_id)

        try:
            processar_item(item_id)
        except Exception:
            print("Falha final no item:", item_id)
        finally:
            fila.task_done()


threading.Thread(target=worker, daemon=True).start()