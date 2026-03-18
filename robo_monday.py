from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys
import os

if len(sys.argv) < 2:
    print("Uso: python robo_monday.py <item_id>")
    sys.exit(1)

ITEM_ID = sys.argv[1]
BOARD_ID = "18404237753"
ITEM_URL = f"https://brutale.monday.com/boards/{BOARD_ID}/pulses/{ITEM_ID}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(BASE_DIR, "estado.json")
SCREENSHOT_ERRO = os.path.join(BASE_DIR, "erro_robo.png")


def abrir_item(page):
    page.goto(ITEM_URL, wait_until="domcontentloaded", timeout=30000)
    page.get_by_role("button", name="Informações").wait_for(timeout=10000)
    page.get_by_role("button", name="Informações").click()


def criar_nota(page, titulo, corpo):
    page.get_by_text("Novo").wait_for(timeout=10000)
    page.get_by_text("Novo").click()

    page.get_by_text("Adicionar uma nota").wait_for(timeout=10000)
    page.get_by_text("Adicionar uma nota").click()

    page.locator(".icon.icon-dapulse-edit").first.wait_for(timeout=10000)
    page.locator(".icon.icon-dapulse-edit").first.click()

    titulo_box = page.locator("#collaboration_area").get_by_role("textbox")
    titulo_box.wait_for(timeout=10000)
    titulo_box.click()
    titulo_box.press("ControlOrMeta+A")
    titulo_box.fill(titulo)

    editor = page.get_by_label("Editor de rich text")
    editor.wait_for(timeout=10000)
    editor.click()
    editor.fill(corpo)

    page.get_by_role("button", name="Salvar").click()


def criar_notas():
    if not os.path.exists(ESTADO):
        print("Arquivo estado.json não encontrado.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=ESTADO)

        context.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["image", "media", "font"]
            else route.continue_()
        )

        page = context.new_page()

        try:
            print("Abrindo item:", ITEM_URL)
            abrir_item(page)

            criar_nota(page, "PASTA DA PROGRAMAÇÃO", "X")
            criar_nota(page, "HURON", "MAQ:\n\nPEDIDO:\n\nCRÍTICO:\n\nCC:")

            print("Notas criadas com sucesso.")

        except PlaywrightTimeoutError as e:
            print("Timeout:", e)
            page.screenshot(path=SCREENSHOT_ERRO, full_page=True)
            print("Screenshot salva em:", SCREENSHOT_ERRO)

        except Exception as e:
            print("Erro:", e)
            page.screenshot(path=SCREENSHOT_ERRO, full_page=True)
            print("Screenshot salva em:", SCREENSHOT_ERRO)

        finally:
            browser.close()


if __name__ == "__main__":
    criar_notas()