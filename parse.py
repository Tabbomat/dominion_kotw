import json
import re
from typing import Optional

typos = {'smuggler': 'smugglers', 'night guardian': 'night watchman', 'stewart': 'steward', 'watch tower': 'watchtower', 'candlestick': 'candlestick maker', 'dominion': 'dominate', 'scouting part': 'scouting party',
         'bath': 'baths'}


def parse(ids: list = None):
    try:
        with open('data/raw.json') as raw_file:
            raw_data = json.load(raw_file)
    except (FileNotFoundError, json.JSONDecodeError):
        raw_data = {}
    try:
        with open('data/cards.json') as card_file:
            cards_data = json.load(card_file)
    except (FileNotFoundError, json.JSONDecodeError):
        cards_data = {}
    # try:
    #     with open('data/kotw.json') as kotw_file:
    #         kotw = json.load(kotw_file)
    # except (FileNotFoundError, json.JSONDecodeError):
    #     kotw = {}
    kotw = {}

    def check_type(card_name: str, type_: str) -> bool:
        card = cards_data.get(card_name)
        if not card:
            return False
        return type_.capitalize() in card['types']

    keywords = ('event', 'landmark', 'project', 'colony', 'platinum', 'shelter')
    if not ids:
        ids = raw_data.keys()
    for post_id in sorted(ids):
        if post_id in kotw.keys():
            continue
        title: str = raw_data.get(post_id).lower()
        if not title:
            continue
        # remove set list
        set_string_start = title.rfind('[')
        if set_string_start > 0:
            title = title[:set_string_start].strip()
        title = re.sub(r'^".*"', '', title)
        # fix col.
        title = title.replace('col./plat', 'colony/platinum')
        kingdom = {}
        # Bane
        if match := re.search(r'\s*\(bane: ?([\w\s]+)\)\s*', title):
            kingdom['bane'] = match.group(1)
            title = title.replace(match.group(0), '')
        if match := re.search(r'\s*\(([\w\s]+) as bane\)\s*', title):
            kingdom['bane'] = match.group(1)
            title = title.replace(match.group(0), '')
        projects = []
        boons = []
        way: Optional[str] = None
        items = [typos.get(item, item) for i in re.split(r'[,.:;]', title) if (item := i.strip(' \r\n\t\\*'))]
        kingdom_cards = []

        def pop_and_check() -> str:
            _i = items.pop(0)
            if _i in cards_data.keys():
                return _i
            raise ValueError(f"{post_id =}, card = {_i}")

        while items:
            # remove spaces
            item = items.pop(0)
            if not item:
                print("empty")
                continue
            if len(kingdom_cards) < 10:
                # current item must be kingdom card
                # if split pile, use name of top card
                index = item.find('/')
                if index > 0:
                    item = item[:index]
                if item in cards_data.keys() and cards_data[item]['kingdom']:
                    kingdom_cards.append(item)
                else:
                    raise ValueError(f"{post_id =}, {item =}")
                continue
            # at this point, we have events, landmarks, ...
            if item in ('no colony/platinum or shelters', 'no colony/platinum/shelters'):
                kingdom['colony_platinum'] = False
                kingdom['shelter'] = False
            elif item == 'colony/platinum/no shelters':
                kingdom['colony_platinum'] = True
                kingdom['shelter'] = False
            elif 'colony' in item or 'platin' in item:
                kingdom['colony_platinum'] = 'no ' not in item
            elif 'shelter' in item:
                kingdom['shelter'] = 'no ' not in item
            elif item == 'bane':
                kingdom['bane'] = pop_and_check()
            elif re.match(r'events?', item):
                kingdom['events'] = []
                while items and check_type(items[0], 'Event'):
                    kingdom['events'].append(pop_and_check())
            elif re.match(r'landmark?', item):
                kingdom['landmarks'] = []
                # fix for obelisk (naming throne room)
                items[0] = re.sub(r'\s*\([\w\s]+\)\s*', '', items[0])
                while items and check_type(items[0], 'Landmark'):
                    kingdom['landmarks'].append(pop_and_check())
                    if items:
                        items[0] = re.sub(r'\s*\([\w\s]+\)\s*', '', items[0])
            elif item == 'boons':
                kingdom['boons'] = []
                while items and check_type(boon := f"the {items[0]}'s gift", 'Boon'):
                    kingdom['boons'].append(boon)
                    items.pop(0)
            elif item.startswith('project'):
                kingdom['projects'] = []
                while items and check_type(items[0], 'Project'):
                    kingdom['projects'].append(pop_and_check())
            elif item.startswith('way'):
                kingdom['ways'] = []
                while items and check_type(items[0], 'Way'):
                    kingdom['ways'].append(pop_and_check())
            elif card := cards_data.get(item):
                if 'Event' in card['types']:
                    kingdom.setdefault('events', []).append(item)
                elif 'Landmark' in card['types']:
                    kingdom.setdefault('landmarks', []).append(item)
                elif 'Project' in card['types']:
                    kingdom.setdefault('projects', []).append(item)
                else:
                    print(f"{post_id =}, {item =}")
            elif item not in ('no events',):
                print(f"{post_id =}, {item =}")
        kingdom['cards'] = kingdom_cards
        kotw[post_id] = kingdom

    with open('data/kotw.json', 'w') as kotw_file:
        json.dump(kotw, kotw_file, indent=2, sort_keys=True)


if __name__ == '__main__':
    parse()
