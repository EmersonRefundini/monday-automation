from playwright.sync_api import sync_playwright
import queue
import threading
import os
import traceback
import re

fila = queue.Queue()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(BASE_DIR, "estado.json")
BOARD_ID = "18404237753"

play = None
browser = None
context = None
page = None


def iniciar_browser():
    global play, browser, context, page

    print("WORKER INICIOU")
    print("BASE_DIR =", BASE_DIR)
    print("ESTADO =", ESTADO)
    print("estado.json existe?", os.path.exists(ESTADO))

    if not os.path.exists(ESTADO):
        raise FileNotFoundError(f"estado.json não encontrado em {ESTADO}")

    play = sync_playwright().start()
    browser = play.chromium.launch(headless=True)

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

    page = context.new_page()
    print("🚀 Robô pronto.")


def recriar_page():
    global page

    try:
        if page:
            page.close()
    except:
        pass

    page = context.new_page()
    print("🔄 Página recriada")


def criar_nota(titulo, corpo):
    global page

    botao_novo = page.get_by_text("Novo", exact=True).last
    botao_novo.wait_for(timeout=6000)
    botao_novo.click(timeout=6000)

    opcao_nota = page.get_by_text("Adicionar uma nota", exact=True)
    opcao_nota.wait_for(timeout=4000)
    page.wait_for_timeout(200)
    opcao_nota.click(force=True)

    icone_editar = page.locator(".icon.icon-dapulse-edit").first
    icone_editar.wait_for(timeout=4000)
    icone_editar.click(force=True)

    titulo_box = page.locator("#collaboration_area").get_by_role("textbox")
    titulo_box.wait_for(timeout=4000)
    titulo_box.click()
    titulo_box.press("ControlOrMeta+A")
    titulo_box.fill(titulo)

    editor = page.get_by_label("Editor de rich text")
    editor.wait_for(timeout=4000)
    editor.click()
    editor.fill(corpo)

    salvar = page.get_by_role("button", name="Salvar")
    salvar.wait_for(timeout=4000)
    salvar.click(force=True)


def processar_item(item_id):
    global page

    url_item = f"https://brutale.monday.com/boards/{BOARD_ID}/pulses/{item_id}"
    url_board = f"https://brutale.monday.com/boards/{BOARD_ID}"

    print("Processando:", item_id)

    for tentativa in range(2):
        try:
            # 1) tenta abrir direto no item
            page.goto(url_item, wait_until="domcontentloaded", timeout=20000)

            botao_info = page.get_by_role("button", name=re.compile("Informações"))

            try:
                botao_info.wait_for(timeout=4000)
            except:
                print("Informações não apareceu direto. Tentando abrir pela linha do board...")

                # 2) fallback: abre o board
                page.goto(url_board, wait_until="domcontentloaded", timeout=20000)

                # 3) acha a linha do item
                linha_item = page.get_by_test_id(f"item-{item_id}")
                linha_item.wait_for(timeout=15000)

                # 4) clica no botão correto (Selecionar elemento)
                botao_abrir_item = linha_item.get_by_role(
                    "button",
                    name=re.compile(r"^Selecionar elemento:")
                )
                botao_abrir_item.wait_for(timeout=10000)
                botao_abrir_item.click(timeout=10000)

                # 5) agora espera o botão Informações aparecer
                botao_info.wait_for(timeout=10000)

            # 6) clica em Informações
            try:
                botao_info.click(timeout=5000)
            except:
                print(f"Tentativa {tentativa + 1}: clique normal falhou, tentando force=True")
                botao_info.click(timeout=5000, force=True)

            page.wait_for_timeout(800)

            # 7) cria as notas
            page.get_by_text("Novo", exact=True).last.wait_for(timeout=10000)

            criar_nota("PASTA DA PROGRAMAÇÃO", "X")
            page.wait_for_timeout(300)
            criar_nota("HURON", "MAQ:\n\nPEDIDO:\n\nCRÍTICO:\n\nCC:")

            print("✅ Finalizado:", item_id)
            return

        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou para item {item_id}: {e}")

            msg = str(e).lower()
            if "page crashed" in msg or "target page, context or browser has been closed" in msg:
                print("💥 Página crashou, recriando...")
                recriar_page()

            if tentativa == 1:
                raise

            page.wait_for_timeout(1000)

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
            print("✅ Finalizado:", item_id)

        except Exception:
            print("ERRO NO PROCESSAMENTO:")
            traceback.print_exc()

            try:
                recriar_page()
            except:
                print("Erro ao recriar página")

            try:
                page.screenshot(path="/app/erro_online.png", full_page=True)
                print("📸 Screenshot salva em /app/erro_online.png")
            except:
                print("Erro ao tirar screenshot")

        finally:
            fila.task_done()


threading.Thread(target=worker, daemon=True).start()