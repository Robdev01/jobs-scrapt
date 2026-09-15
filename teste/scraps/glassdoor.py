from urllib.parse import quote_plus, urljoin

from playwright.sync_api import sync_playwright


BASE_URL = "https://www.glassdoor.com"


def limpar_texto(texto):
    if not texto:
        return None

    return " ".join(texto.split())


def texto_primeiro(card, seletores):
    """
    Tenta vários seletores e retorna o primeiro texto encontrado.
    """

    for seletor in seletores:
        try:
            elemento = card.locator(seletor).first

            if elemento.count() > 0:
                texto = elemento.inner_text(timeout=2000)

                if texto:
                    return limpar_texto(texto)

        except Exception:
            continue

    return None


def buscar_vagas_glassdoor(
    keyword,
    location="Brazil",
    limit=20
):

    # Monta a pesquisa
    query = quote_plus(keyword)

    url = (
        f"{BASE_URL}/Job/jobs.htm"
        f"?sc.keyword={query}"
    )

    print()
    print("=" * 60)
    print("GLASSDOOR JOB COLLECTOR")
    print("=" * 60)
    print("Keyword:", keyword)
    print("Location:", location)
    print("URL:", url)
    print("=" * 60)

    vagas = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        print("Abrindo Glassdoor...")

        response = page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        if response:
            print(
                "Status:",
                response.status
            )

        # Aguarda os resultados renderizarem
        page.wait_for_timeout(4000)

        # Se algum controle explícito impedir acesso,
        # interrompemos em vez de tentar contorná-lo.
        conteudo = page.content().lower()

        if (
            "captcha" in conteudo
            or "verify you are human" in conteudo
            or "access denied" in conteudo
        ):
            browser.close()

            raise RuntimeError(
                "O Glassdoor solicitou verificação "
                "ou bloqueou esta sessão."
            )

        # ------------------------------------------------
        # LOCALIZAR CARDS
        # ------------------------------------------------

        seletores_cards = [
            "li[data-test='jobListing']",
            "[data-test='job-card']",
            "li[class*='JobsList_jobListItem']",
            "li[class*='jobListItem']",
        ]

        cards = None

        for seletor in seletores_cards:

            encontrados = page.locator(
                seletor
            )

            quantidade = encontrados.count()

            print(
                f"{seletor}: {quantidade}"
            )

            if quantidade > 0:
                cards = encontrados
                break

        if cards is None:

            browser.close()

            raise RuntimeError(
                "Nenhum card de vaga foi encontrado."
            )

        quantidade = cards.count()

        print()
        print(
            "Cards encontrados:",
            quantidade
        )

        quantidade_processar = min(
            quantidade,
            limit
        )

        # ------------------------------------------------
        # PROCESSAR VAGAS
        # ------------------------------------------------

        for i in range(quantidade_processar):

            card = cards.nth(i)

            print()
            print("-" * 60)
            print(
                f"Processando vaga "
                f"{i + 1}/{quantidade_processar}"
            )

            # TITULO

            titulo = texto_primeiro(
                card,
                [
                    "a[data-test='job-title']",
                    "[data-test='job-title']",
                    "a[class*='jobTitle']",
                ]
            )

            # EMPRESA

            empresa = texto_primeiro(
                card,
                [
                    "[data-test='employer-name']",
                    "[class*='EmployerProfile']",
                    "[class*='employerName']",
                ]
            )

            # LOCALIZAÇÃO

            localizacao = texto_primeiro(
                card,
                [
                    "[data-test='emp-location']",
                    "[class*='location']",
                ]
            )

            # SALÁRIO

            salario = texto_primeiro(
                card,
                [
                    "[data-test='detailSalary']",
                    "[data-test='salary-estimate']",
                    "[class*='salary']",
                ]
            )

            # LINK

            link = None

            seletores_link = [
                "a[data-test='job-title']",
                "a[href*='job-listing']",
            ]

            for seletor in seletores_link:

                try:

                    elemento = card.locator(
                        seletor
                    ).first

                    if elemento.count() > 0:

                        href = elemento.get_attribute(
                            "href"
                        )

                        if href:

                            link = urljoin(
                                BASE_URL,
                                href
                            )

                            break

                except Exception:
                    continue

            print("Título:", titulo)
            print("Empresa:", empresa)
            print("Localização:", localizacao)

            # ------------------------------------------------
            # DESCRIÇÃO
            # ------------------------------------------------

            descricao = None

            try:

                link_vaga = card.locator(
                    "a[data-test='job-title']"
                ).first

                if link_vaga.count() > 0:

                    link_vaga.click()

                    # Espera o painel de detalhes atualizar
                    page.wait_for_timeout(1500)

                    seletores_descricao = [
                        "[data-test='jobDescriptionContent']",
                        "[class*='jobDescription']",
                        "#JobDescriptionContainer",
                    ]

                    for seletor in seletores_descricao:

                        elemento = page.locator(
                            seletor
                        ).first

                        if elemento.count() > 0:

                            texto = elemento.inner_text(
                                timeout=3000
                            )

                            if texto:

                                descricao = limpar_texto(
                                    texto
                                )

                                break

            except Exception as erro:

                print(
                    "Não foi possível obter "
                    "a descrição:",
                    erro
                )

            vaga = {
                "title": titulo,
                "company": empresa,
                "location": localizacao,
                "salary": salario,
                "description": descricao,
                "url": link,
                "source": "glassdoor"
            }

            vagas.append(vaga)

        browser.close()

    print()
    print("=" * 60)
    print(
        f"TOTAL COLETADO: {len(vagas)}"
    )
    print("=" * 60)

    return vagas