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

    print("=" * 60)
    print("ABRINDO GLASSDOOR")
    print("=" * 60)

    response = page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    if response:
        print("Status:", response.status)

    print("Título:", page.title())
    print("URL:", page.url)

    # Dá tempo para os resultados renderizarem
    page.wait_for_timeout(5000)

    # Tentamos localizar estruturas comuns de cards
    seletores = [
        "li[data-test='jobListing']",
        "[data-test='job-card']",
        "li[class*='JobsList_jobListItem']",
        "li[class*='jobListItem']",
        "a[data-test='job-title']",
    ]

    print()
    print("=" * 60)
    print("PROCURANDO CARDS")
    print("=" * 60)

    for seletor in seletores:

        quantidade = page.locator(
            seletor
        ).count()

        print(
            f"{seletor}: {quantidade}"
        )

    print()
    print("=" * 60)
    print("TÍTULOS ENCONTRADOS")
    print("=" * 60)

    titulos = page.locator(
        "a[data-test='job-title']"
    )

    quantidade = titulos.count()

    print(
        "Quantidade:",
        quantidade
    )

    for i in range(
        min(quantidade, 10)
    ):

        elemento = titulos.nth(i)

        try:

            print()
            print(
                i + 1,
                elemento.inner_text()
            )

            print(
                elemento.get_attribute(
                    "href"
                )
            )

        except Exception as erro:

            print(
                "Erro:",
                erro
            )

    input(
        "\nPressione ENTER para fechar..."
    )

    browser.close()