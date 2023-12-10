import requests
import os

from bs4 import BeautifulSoup

elements = ["water", "earth", "fire", "air"]

index_urls = {
    "water": "https://runescape.wiki/w/Category:Weak_to_water_spells",
    "earth": "https://runescape.wiki/w/Category:Weak_to_earth_spells",
    "fire": "https://runescape.wiki/w/Category:Weak_to_fire_spells",
    "air": "https://runescape.wiki/w/Category:Weak_to_air_spells",
}


def get_entity_html(base_dir, name, url):
    file_path = f"{base_dir}/{name}.html"

    os.makedirs(base_dir, exist_ok=True)

    # Cache the received html to a file
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        response = requests.get(url)
        index = response.text

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(index)
            return index


def get_index_html(elem, url):
    return get_entity_html("data", f"index_{elem}", url)


def get_npcs(elem_soup):
    base_url = "https://runescape.wiki"
    npcs = {}

    for tag in elem_soup.select(".mw-category-group ul li a"):
        name = tag.text
        url = f"{base_url}{tag.get('href')}"
        npcs[name] = url

    return npcs


def get_npc_html(npc, url):
    return get_entity_html("data/npcs", npc, url)


def get_npc_info(npc_soup):
    info = {}

    for tag in npc_soup.select(".infobox-bonuses tr"):
        name = tag.select_one("th").text
        value = tag.select_one("td").text
        info[name] = value

    return info


def get_npc_info(npc_soup):
    return {
        "name": npc_soup.select_one(".infobox-header").text,
        "members_only": npc_soup.select_one("[data-attr-param=\"members\"]").text == "Yes",
        "combat_level": npc_soup.select_one("[data-attr-param=\"level\"]").text,
        "life_points": npc_soup.select_one("[data-attr-param=\"lifepoints\"]").text,
    }


if __name__ == "__main__":
    with open(f"data/npcs.csv", "a", encoding="utf-8") as npcs_file:
        npcs_file.write("Name;Element Weakness;Combat Level;Life Points;Members Only;\n")

        for element in elements:
            element_url = index_urls[element]
            element_index = get_index_html(element, element_url)

            element_soup = BeautifulSoup(element_index, "html.parser")
            element_npcs = get_npcs(element_soup)

            for element_npc in element_npcs:
                element_npc_url = element_npcs[element_npc]
                element_npc_html = get_npc_html(element_npc, element_npc_url)

                element_npc_soup = BeautifulSoup(element_npc_html, "html.parser")
                element_npc_info = get_npc_info(element_npc_soup)

                npcs_file.write(f"{element_npc_info['name']};"
                                f"{element};"
                                f"{element_npc_info['combat_level']};"
                                f"{element_npc_info['life_points']};"
                                f"{element_npc_info['members_only']};"
                                f"\n")
