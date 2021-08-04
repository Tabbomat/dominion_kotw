import json
import re

function_template = """function getRandomKotw(sets)
    local _sets = sets or {}
    local sets = {}
    local numSets = 0
    for _, item in ipairs(_sets) do
        sets[item] = true
        numSets = numSets + 1
    end
    local kotwData = {##REPLACE_WITH_DATA##}
    -- just return any kotw
    if numSets == 0 then
        local result = kotwData[math.random(#kotwData)]
        result._usedSets = nil
        return result
    end
    -- filter by sets
    local validKotw = {}
    for _, kotw in pairs(kotwData) do
        local isValid = true
        for _, s in pairs(kotw._usedSets) do
            if sets[s] == nil then
                isValid = false
                break
            end
        end
        if isValid then
            validKotw[#validKotw + 1] = kotw
        end
    end
    if #validKotw > 0 then
        local result = validKotw[math.random(#validKotw)]
        result._usedSets = nil
        return result
    end
    -- no valid set, return nil
    return nil
end"""


def to_lua(o):
    if isinstance(o, bool):
        return str(o).lower()
    if isinstance(o, str):
        return f"'{re.escape(o)}'"
    if isinstance(o, (list, set)):
        return f"{{ {', '.join(to_lua(i) for i in o)} }}"
    if isinstance(o, dict):
        temp = ', '.join(f'{k} = {to_lua(v)}' for k, v in o.items())
        return f"{{ {temp} }}"
    return str(o)


def translate(cards_data, card):
    return cards_data[card]['German']['name'].replace(' ', '')


def tts_convert(debug=False):
    with open('data/kotw.json') as kotw_file:
        kotw_data = json.load(kotw_file)
    with open('data/cards.json') as card_file:
        cards_data = json.load(card_file)
    set_strings = []
    for kotw in kotw_data.values():  # type:dict
        kotw['_usedSets'] = sorted({cards_data[c]['set'].replace(' ', '') for c in kotw['cards']})
        kotw['cards'] = sorted(translate(cards_data, c) for c in kotw['cards'])
        if 'bane' in kotw:
            kotw['baneCard'] = translate(cards_data, kotw.pop('bane'))
        if 'colony_platinum' in kotw:
            kotw['colony'] = kotw.pop('colony_platinum')
        for card_list in ('events', 'landmarks', 'boons', 'projects', 'ways'):
            if card_list in kotw:
                kotw[card_list] = sorted(translate(cards_data, c) for c in kotw[card_list])
        set_strings.append(to_lua(kotw))
    set_str = '\n        ' + ',\n        '.join(set_strings) + '\n    ' if debug else ', '.join(set_strings)
    with open('data/random_kotw.ttslua', 'w', encoding='utf8') as output_file:
        output_file.write(function_template.replace('##REPLACE_WITH_DATA##', set_str))


if __name__ == '__main__':
    tts_convert(True)
