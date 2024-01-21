import requests
import os

from bs4 import BeautifulSoup

attacks = ["water", "earth", "fire", "air", "slash", "crush", "stab"]

index_urls = {
    "water": "https://runescape.wiki/w/Category:Weak_to_water_spells",
    "earth": "https://runescape.wiki/w/Category:Weak_to_earth_spells",
    "fire": "https://runescape.wiki/w/Category:Weak_to_fire_spells",
    "air": "https://runescape.wiki/w/Category:Weak_to_air_spells",
    "slash": "https://runescape.wiki/w/Category:Weak_to_slash_attacks",
    "crush": "https://runescape.wiki/w/Category:Weak_to_crush_attacks",
    "stab": "https://runescape.wiki/w/Category:Weak_to_stab_attacks",
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


def get_index_html(attack, url):
    return get_entity_html("data", f"index_{attack}", url)


def get_npcs(soup):
    base_url = "https://runescape.wiki"
    npcs = {}

    for tag in soup.select(".mw-category-group ul li a"):
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
        npcs_file.write("Name;Attack Weakness;Combat Level;Life Points;Members Only;\n")

        for attack in attacks:
            attack_url = index_urls[attack]
            attack_index = get_index_html(attack, attack_url)

            attack_soup = BeautifulSoup(attack_index, "html.parser")
            attack_npcs = get_npcs(attack_soup)

            for attack_npc in attack_npcs:
                attack_npc_url = attack_npcs[attack_npc]
                attack_npc_html = get_npc_html(attack_npc, attack_npc_url)

                attack_npc_soup = BeautifulSoup(attack_npc_html, "html.parser")
                attack_npc_info = get_npc_info(attack_npc_soup)

                npcs_file.write(f"{attack_npc_info['name']};"
                                f"{attack};"
                                f"{attack_npc_info['combat_level']};"
                                f"{attack_npc_info['life_points']};"
                                f"{attack_npc_info['members_only']};"
                                f"\n")
