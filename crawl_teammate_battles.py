import codecs

import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

URL_TEMPLATE = "https://www.formula1.com/en/results.html/%s/drivers.html"


class Driver:
    def __init__(self, name, team, points):
        self.name = name
        self.team = team
        self.points = points

    def __repr__(self):
        return "%s, %s PTS: %s\n" % (self.name, self.team, self.points)


class Team:
    def __init__(self, name):
        self.name = name
        self.drivers = []

    def get_battle_results(self):
        drivers = self.drivers
        drivers.sort(key=lambda x: float(x.points), reverse=True)

        if len(drivers) == 0:
            return []

        results = []
        for i in range(0, len(drivers) - 1):
            if drivers[i].points == 0 and drivers[i + 1].points == 0:
                continue

            results.append(drivers[i].name + ":" + drivers[i + 1].name)
            # results.append(drivers[i].name + drivers[i].points + ":" + drivers[i + 1].name + drivers[i + 1].points)

        return results


def get_url_for_year(year):
    return URL_TEMPLATE % str(year)


def get_page_soup(url):
    contents = requests.get(url)
    return BeautifulSoup(contents.text, "lxml")


def build_get_value_func(cells):
    def at(index):
        return re.sub("\s+", " ", cells[index].text).strip()

    return at


def get_driver_list(page_soup):
    drivers = []
    for row in page_soup.select(".table-wrap tr"):
        cells = row.select("td")
        if len(cells) == 0:  # probably the header row
            continue

        get = build_get_value_func(cells)
        drivers.append(Driver(name=get(2)[:-4], team=get(4), points=get(5)))

    return drivers


def group_teams(drivers):
    teams = {}
    for driver in drivers:
        if driver.team not in teams:
            teams[driver.team] = Team(driver.team)
        teams[driver.team].drivers.append(driver)

    return teams


def main():
    current_year = datetime.now().year
    battles = []

    for year in range(1950, current_year):
        page = get_page_soup(get_url_for_year(year))
        drivers = get_driver_list(page)
        teams = group_teams(drivers)
        for team in teams.values():
            battles = battles + team.get_battle_results()

    print(battles)

    with codecs.open("output.txt", "w", "utf8") as file:
        file.write("\n".join(battles))


if __name__ == "__main__":
    main()
