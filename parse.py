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
    keywords = ('event', 'landmark', 'project', 'colony', 'platinum', 'shelter')
    if not ids:
        ids = raw_data.keys()
    for post_id in ids:
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
        bane: Optional[str] = None
        way: Optional[str] = None
        items = [typos.get(item, item) for i in re.split(r'[,.:;]', title) if (item := i.strip(' \r\n\t\\*'))]
        kingdom_cards = []
        while items:
            # remove spaces
            item = items.pop(0)
            if not item:
                continue
            if len(kingdom_cards) < 10:
                # current item must be kingdom card
                # if split pile, use name of top card
                index = item.find('/')
                if index > 0:
                    item = item[:index]
                if item in cards_data.keys():
                    kingdom_cards.append(item)
                else:
                    raise ValueError(f"{post_id =}, {item =}")
                continue
            # at this point, we have events, landmarks, ...
            if 'colony' in item or 'platin' in item:
                kingdom['colony_platinum'] = 'no ' not in item
            if 'shelter' in item:
                kingdom['shelter'] = 'no ' not in item
            if 'event' in item:
                kingdom['events'] = []
                while items and not any(k in items[0] for k in keywords) and not items[0] in ('way',):
                    event = items.pop(0)
                    if event in cards_data.keys():
                        kingdom['events'].append(event)
                    else:
                        raise ValueError(f"{post_id =}, {event =}")
            if 'landmark' in item:
                kingdom['landmarks'] = []
                while items and not any(k in items[0] for k in keywords) and not items[0] in ('way',):
                    event = items.pop(0)
                    # fix for obelisk (naming throne room)
                    event = re.sub(r'\s*\([\w\s]+\)\s*', '', event)
                    if event in cards_data.keys():
                        kingdom['landmarks'].append(event)
                    else:
                        raise ValueError(f"{post_id =}, {event =}")

        kingdom['cards'] = kingdom_cards
        kotw[post_id] = kingdom

    with open('data/kotw.json', 'w') as kotw_file:
        json.dump(kotw, kotw_file, indent=2, sort_keys=True)


if __name__ == '__main__':
    parse()
