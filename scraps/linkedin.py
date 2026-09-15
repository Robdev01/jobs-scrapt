from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.linkedin.com/jobs/search/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def buscar_descricao_vaga(url):
    """
    Acessa a página individual da vaga e tenta obter
    a descrição completa.
    """

    if not url:
        return None

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # O LinkedIn pode utilizar diferentes estruturas
        # dependendo da página/versão.
        seletores = [
            "div.show-more-less-html__markup",
            "div.description__text",
            "section.show-more-less-html",
        ]

        for seletor in seletores:
            descricao = soup.select_one(seletor)

            if descricao:
                return descricao.get_text(
                    separator="\n",
                    strip=True
                )

        return None

    except requests.RequestException as exc:
        print(f"Erro ao buscar descrição: {url}")
        print(exc)

        return None


def buscar_vagas_linkedin(keyword, location, limit=20):

    params = {
        "keywords": keyword,
        "location": location,
    }

    url = f"{BASE_URL}?{urlencode(params)}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    vagas = []

    cards = soup.select("div.base-card")

    for card in cards:

        if len(vagas) >= limit:
            break

        titulo = card.select_one(
            "h3.base-search-card__title"
        )

        empresa = card.select_one(
            "h4.base-search-card__subtitle"
        )

        localizacao = card.select_one(
            "span.job-search-card__location"
        )

        link_element = card.select_one(
            "a.base-card__full-link"
        )

        if not titulo:
            continue

        link = (
            link_element.get("href")
            if link_element
            else None
        )

        print(
            f"Buscando descrição: "
            f"{titulo.get_text(strip=True)}"
        )

        descricao = buscar_descricao_vaga(link)

        vaga = {
            "title": titulo.get_text(
                strip=True
            ),

            "company": (
                empresa.get_text(strip=True)
                if empresa
                else None
            ),

            "location": (
                localizacao.get_text(strip=True)
                if localizacao
                else None
            ),

            "description": descricao,

            "url": link,

            "source": "linkedin",
        }

        vagas.append(vaga)

    return vagas