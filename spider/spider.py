import scrapy
from datetime import datetime


class SpectreSpider(scrapy.Spider):
    name = 'Spectrespider'
    date = datetime.now().strftime('%d-%m-%Y')
    start_urls = ['https://poedb.tw/us/Monster']
    allowed_domains = ['poedb.tw']
    used_urls = []
    custom_settings = {
        'FEEDS': {'./scraped_data/%(name)s/%(name)s_batch_%(date)s.json': {'format': 'json', 'overwrite': True}},
        'CONCURRENT_REQUESTS': 100,
    }

    def parse(self, response):
        if response.url in self.used_urls:
            return

        self.used_urls.append(response.url)

        if (response.url == 'https://poedb.tw/us/Monster'):
            league_links = response.selector.xpath(
                "//h5[contains(text(), 'Monster')]/following-sibling::div[1]/div/a")

            for link in league_links:
                yield response.follow(link, self.parse)

            # reliable base spectre
            # yield response.follow(league_links[23], self.parse)

            # reliable non-varied spectre
            # yield response.follow(league_links[1], self.parse)

        elif ('_monsters' in response.url):
            monster_links = response.selector.xpath(
                "//tr[td/span[contains(text(), 'Y')]]/td/a")

            for link in monster_links:
                yield response.follow(link, self.parse)

            # reliable base spectre
            # yield response.follow(monster_links[0], self.parse)

            # reliable non-varied spectre
            # yield response.follow(monster_links[1], self.parse)

        else:

            spectrable_tabs = response.selector.xpath(
                "//div[contains(@role, 'main')]/div[contains(@class, 'tab-content')]/div[contains(@class, 'tab-pane')]")

            if (not spectrable_tabs):
                spectrable_tabs = response.selector.xpath(
                    "//div[contains(@role, 'main')]")

            spectre = {"name": response.url.split(
                '/')[-1], "varieties": [], "meta": {
                    "target_url": response.url,
                    "timestamp": f"{datetime.now()}"
            }}

            for monster_element in spectrable_tabs:
                result = monster_element.xpath(
                    ".//table/tr/th[contains(text(),'Spectre')]/following-sibling::td[1]/span/text()").get()

                if (result != 'Y'):
                    continue
                else:
                    variety_name = monster_element.xpath('./@id').get()

                    variety = {
                        "name": variety_name or 'base',
                        "levels": []
                    }

                    spectre["varieties"].append(variety)

                    lvl_tabs = monster_element.xpath(
                        ".//div[contains(@class, 'tab-content')]/div[contains(@class, 'tab-pane')]")

                    for spectre_element in lvl_tabs:
                        monster = {
                            "name": spectre_element.xpath('./@id').get(),
                            "areas": [],
                            "stats": {},
                            "skills": []
                        }

                        monster['areas'] = set(monster_element.xpath(
                            ".//th[contains(text(), 'Area')]/following-sibling::td[1]/a/text()").getall())

                        monster["stats"] = {
                            "Life": spectre_element.xpath(".//div[contains(text(), 'Life')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Armour": spectre_element.xpath(
                                ".//div[contains(text(), 'Armour')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Evasion": spectre_element.xpath(
                                ".//div[contains(text(), 'Evasion')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Energy_Shield": spectre_element.xpath(
                                ".//div[contains(text(), 'Energy Shield')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Damage": spectre_element.xpath(
                                ".//div[contains(text(), 'Damage')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Spell_Damage": spectre_element.xpath(
                                ".//div[contains(text(), 'Spell Damage')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Accuracy": spectre_element.xpath(
                                ".//div[contains(text(), 'Accuracy')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Attack_Time": spectre_element.xpath(
                                ".//div[contains(text(), 'Attack Time')]/span/span[contains(@data-bs-toggle, 'tooltip')]/text()").get(),
                            "Crit_chance": monster_element.xpath(
                                ".//div[contains(text(), 'Critical Strike Chance')]/span/text()").get(),
                            "Crit_multi": monster_element.xpath(
                                ".//div[contains(text(), 'Critical Strike Multiplier')]/span/text()").get(),
                            "Range": monster_element.xpath(
                                ".//div[contains(text(), 'Attack Distance')]/span/text()").get(),
                            "Damage_Spread": monster_element.xpath(
                                ".//div[contains(text(), 'Damage Spread')]/span/text()").get(),
                            "Resistance": {
                                "fire": monster_element.xpath(
                                    ".//div[contains(text(), 'Resistance')]/span/span/text()").getall()[0],
                                "cold": monster_element.xpath(
                                    ".//div[contains(text(), 'Resistance')]/span/span/text()").getall()[1],
                                "lightning": monster_element.xpath(
                                    ".//div[contains(text(), 'Resistance')]/span/span/text()").getall()[2],
                                "chaos": monster_element.xpath(
                                    ".//div[contains(text(), 'Resistance')]/span/span/text()").getall()[3],
                            }
                        }

                        skills = spectre_element.xpath(
                            ".//div[contains(@class, 'itemPopup')]")

                        for skill_element in skills:

                            stats = skill_element.xpath(
                                ".//span[contains(@class, 'Stats')]/text()[normalize-space()]").getall()

                            filtered_stats = list(filter(
                                lambda stat: stat != ', ', stats))

                            skill = {
                                "name": skill_element.xpath(".//div[contains(@class, 'TitleBar')]/span/text()").get(),
                                "stats": {"tags": skill_element.xpath(".//span[contains(@class, 'tags')]/text()").getall(), "stats": filtered_stats},
                                "detail": skill_element.xpath(".//span[contains(@class, 'explicitMod')]/descendant-or-self::text()[normalize-space()]").getall()
                            }

                            monster["skills"].append(skill)

                        variety["levels"].append(monster)

            yield spectre
