import fetch
import parse
import tts_convert

if __name__ == '__main__':
    ids = fetch.fetch()
    parse.parse(ids)
    tts_convert.tts_convert()
