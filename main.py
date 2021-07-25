import fetch
import parse

if __name__ == '__main__':
    ids = fetch.fetch()
    parse.parse(ids)
