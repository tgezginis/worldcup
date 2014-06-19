import sys
import json
import urllib
import datetime

import colorama
import humanize
import dateutil.parser
import dateutil.tz


FUTURE = "future"
NOW = "now"
PAST = "past"
SCREEN_WIDTH = 68


def progress_bar(percentage, separator="o", character="-"):
    """
    Creates a progress bar by given percentage value
    """
    filled = colorama.Fore.GREEN + colorama.Style.BRIGHT
    empty = colorama.Fore.WHITE + colorama.Style.BRIGHT

    if percentage == 100:
        return filled + character * SCREEN_WIDTH

    if percentage == 0:
        return empty + character * SCREEN_WIDTH

    completed = int((SCREEN_WIDTH / 100.0) * percentage)

    return (filled + (character * (completed - 1)) +
            separator +
            empty + (character * (SCREEN_WIDTH - completed)))


def prettify(match):
    """
    Prettifies given match object
    """
    diff = (datetime.datetime.now(tz=dateutil.tz.tzlocal()) -
            dateutil.parser.parse(match['datetime']))

    seconds = diff.total_seconds()

    if seconds > 0:
        if seconds > 60 * 90:
            status = PAST
        else:
            status = NOW
    else:
        status = FUTURE

    if status in [PAST, NOW]:
        color = colorama.Style.BRIGHT + colorama.Fore.GREEN
    else:
        color = colorama.Style.NORMAL + colorama.Fore.WHITE

    home = match['home_team']
    away = match['away_team']

    if status == NOW:
        minute = int(seconds / 60)
        match_status = "Being played now: %s minutes gone" % minute
    elif status == PAST:
        if match['winner'] == 'Draw':
            result = 'Draw'
        else:
            result = "%s won" % (match['winner'])
        match_status = "Played %s. %s" % (humanize.naturaltime(diff),
                                                  result)
    else:
        match_status = "Will be played %s" % humanize.naturaltime(diff)

    if status == NOW:
        match_percentage = int(seconds / 60 / 90 * 100)
    elif status == FUTURE:
        match_percentage = 0
    else:
        match_percentage = 100

    return """
    {} {:<30} {} - {} {:>30}
    {}
    \xE2\x9A\xBD  {}
    """.format(
        color,
        home['country'],
        home['goals'],
        away['goals'],
        away['country'],
        progress_bar(match_percentage),
        colorama.Fore.WHITE + match_status
    )

def prettify_group(group, order):
    """
    Prettifies given group object
    """
    played = group['wins'] + group['draws'] + group['losses']
    points = group['wins']*3 + group['draws']

    if order in (1, 2):
        color = colorama.Style.BRIGHT + colorama.Fore.GREEN
    else:
        color = colorama.Style.NORMAL + colorama.Fore.WHITE

    return color +"{}. {}\t{} {} {} {} {} {} {}".format(
        order,
        format(group['country']).ljust(30),
        format(played).ljust(2),
        format(group['wins']).ljust(2),
        format(group['draws']).ljust(2),
        format(group['losses']).ljust(2),
        format(group['goals_for']).ljust(2),
        format(group['goals_against']).ljust(2),
        format(points).ljust(2)
    )


def is_valid(match):
    """
    Validates the given match object
    """
    return (
        isinstance(match, dict) and
        isinstance(match.get('home_team'), dict) or
        isinstance(match.get('away_team'), dict)
    )


def fetch(endpoint):
    """
    Fetches match results by given endpoint
    """
    url = "http://worldcup.sfg.io/matches/%(endpoint)s" % {
        "endpoint": endpoint
    }

    data = urllib.urlopen(url)
    matches = json.load(data)

    for match in matches:
        if is_valid(match):
            yield match

def fetch_group_results():
    """
    Fetches group results
    """
    url = "http://worldcup.sfg.io/group_results"

    data = urllib.urlopen(url)
    groups = json.load(data)

    for group in groups:
        yield group


def main():
    colorama.init()
    endpoint = ''.join(sys.argv[1:])
    if endpoint == "groups":
        for i, group in enumerate(fetch_group_results()):
            if i % 4 == 0:
                order = 1
                print colorama.Style.BRIGHT + "\nGroup %s" % chr(group["group_id"]-1 + ord('A')) + " " * 32 + " MP W  D  L  GF GO P"
                print "-" * 60
            print prettify_group(group, order)
            order = order + 1
    else:
        for match in fetch(endpoint):
            print prettify(match)


if __name__ == "__main__":
    main()
