from playwright.sync_api import sync_playwright


URL = (
    "https://www.glassdoor.com/Job/jobs.htm"
    "?sc.keyword=Java%20Developer"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("Abrindo Glassdoor...")

    response = page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    if response:
        print("Status:", response.status)

    print("Título:", page.title())
    print("URL final:", page.url)

    page.wait_for_timeout(5000)

    input(
        "Veja o navegador. "
        "Pressione ENTER para fechar..."
    )

    browser.close()