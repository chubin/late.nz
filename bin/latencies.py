# vim: fileencoding=utf-8

"""
Console port of https://people.eecs.berkeley.edu/~rcs/research/interactive_latency.html
It visualizes the most important latency values.
The output is available at https://cheat.sh/latencies

Code is available at https://github.com/chubin/latenci.es

"""

import sys
import os
import itertools
import datetime
import textwrap
import re

YEAR = datetime.datetime.now().year
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))
import data

# source of the block:
# https://www.fileformat.info/info/unicode/block/block_elements/list.htm
BLOCK = "▗▖"
HALF_BLOCK = "▗ "
LANE_SIZE = 29

COLOR = {
    'gray':     '\033[37m',
    'red':      '\033[31m',
    'green':    '\033[32m',
    'yellow':   '\033[33m',
    'blue':     '\033[34m',
    'dark_gray':'\033[38;5;242m',
    'reset':    '\033[m',
}

COLOR_BY_UNIT = {
    'ns':   'gray',
    '100ns':'blue',
    '10us': 'green',
    'ms':   'red',
}

FACTOR_BY_UNIT = {
    'ns':   1,
    '100ns':100,
    '10us': 10000,
    'ms':   1000000,
}

FOOTER = (
    "# [github.com/chubin/late.nz] [MIT License]",
    "# Console port of \"Jeff Dean's latency numbers\"",
    "# from [github.com/colin-scott/interactive_latencies]",
    "",
)

def _format_ns(time_ns):
    suffixes = ['ns', 'us', 'ms', 's']

    index = 0
    while time_ns >= 1000 and index < len(suffixes):
        index += 1
        time_ns /= 1000

    return "%s%s" % (time_ns, suffixes[index])

def _render_block(number, color=None, caption=None):

    def _single_box(text):
        # cutting off "single_box_"
        color = text.group(0)[11:]
        if color in COLOR:
            return COLOR[color] + BLOCK + COLOR['reset']
        return BLOCK

    number_int = int(number)
    if number - number_int > 0.5 or number_int == 0:
        number = number_int + 1
        last_block_is_half = True
    else:
        number = number_int
        last_block_is_half = False

    lane_size = LANE_SIZE
    size_x = 10
    answer = []

    if color and color in COLOR:
        color_on = COLOR[color]
        color_off = COLOR['reset']
    else:
        color_on = ''
        color_off = ''

    # creating block itself
    for _ in range(number // size_x):
        spaces = " "*(lane_size - size_x*2)
        answer += [BLOCK*size_x + spaces]

    spaces = " "*(lane_size - number%size_x*2)
    if last_block_is_half:
        answer += [BLOCK*(number%size_x-1)+ HALF_BLOCK + spaces]
    else:
        answer += [BLOCK*(number%size_x) + spaces]

    answer = [color_on + x + color_off for x in answer]

    # creating caption
    if 'single_box_' in caption:
        spaces = " "*(LANE_SIZE-caption.index('single_box_')-2)
        caption_block = [re.sub('single_box_[a-z]*', _single_box, caption) + spaces]
    else:
        caption_strings = caption.split('|')
        caption_strings = list(itertools.chain(*[
            textwrap.wrap(x, width=LANE_SIZE-2) for x in caption_strings]))
        caption_block = [x.ljust(lane_size) for x in caption_strings]

    answer = caption_block + answer
    return answer

def render(year=YEAR):
    """
    Render latencies for `year` and return result as a string
    """
    metrics = data.get_metrics(year)

    columns = []
    for block_unit in ['ns', '100ns', '10us', 'ms']:

        empty_line = " "*LANE_SIZE

        blocks = []
        for metric in metrics:
            value, unit, title, _, extra = metric
            if unit != block_unit:
                continue

            color = COLOR_BY_UNIT[unit]
            formatted_value = _format_ns(int(value))
            factorized_value = value/FACTOR_BY_UNIT[unit]

            if title:
                caption = "%s: %s" % (title, formatted_value)
            else:
                if extra:
                    caption = "%s = %s" % (formatted_value, extra)
                else:
                    caption = "%s" % formatted_value

            blocks += [
                _render_block(factorized_value, color=color, caption=caption)
                + [empty_line]
            ]

        columns.append(list(itertools.chain(*blocks)))

    max_column_size = max(len(column) for column in columns)
    empty_line = " "*(LANE_SIZE)
    columns = [column + [empty_line]*(max_column_size-len(column))
               for column in columns]

    footer = ["%s%s%s" % (
        COLOR['dark_gray'],
        line.ljust(LANE_SIZE*2),
        COLOR['reset'])
              for line in FOOTER]

    columns[0] = columns[0][:-6] + footer
    columns[1] = columns[1][:-6] + [""]*4

    output = [
        COLOR['dark_gray'] + "# Latency numbers every programmer should know " + COLOR['reset'],
        "",
    ] + ["".join(line) for line in zip(*columns)]

    return "".join("%s\n" % x for x in output)

if __name__ == '__main__':
    sys.stdout.write(render())
