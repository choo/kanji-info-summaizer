import os, re
import fsutils
from char_utils import is_kanji
from pprint import pprint

FILEPATH = 'joyokanjihyo.txt'


def _is_title(line):
    if (not line.startswith('\t')
        and not line.startswith('03初_改定常用漢字表')):
        line = line.strip()
        return len(line) == 1 and is_kanji(line[0])
    return False


def _is_kyujitai(line):
    line = line.strip()
    return (line.startswith('（') and
            line.endswith('）'))


def main():
    ret = []
    lines = fsutils.read_lines(FILEPATH)
    mark_indices = []
    for i, line in enumerate(lines):
        if _is_title(line):
            if len(mark_indices) > 0 and not mark_indices[-1]['end']:
                mark_indices[-1]['end'] = i
            mark_indices.append({'start': i, 'end': None})
        elif line.startswith('03初_改定常用'):
            mark_indices[-1]['end'] = i - 1
    for tmp in mark_indices:
        i = tmp['start']
        title = lines[i].strip()
        kyujitai = ''
        if _is_kyujitai(lines[i + 1]):
            kyujitai = lines[i + 1].strip()
            kyujitai = kyujitai.replace('（', '').replace('）', '')
            i += 1
        yomis, provs = [], []
        for idx in range(i + 1, tmp['end']):
            line = lines[idx]
            if line.strip() == '':
                continue
            cols = [col.strip() for col in line.split('\t')]
            n = len(cols)
            if n > 3:
                yomis.append(cols[3])
            if n > 4:
                provs.append(cols[4])
            if n > 5:
                plus = cols[5]
            #if n > 6:
            #    print(cols[6]) # nothing
        ret.append({
            'title': title,
            'kyujitai': kyujitai,
            'yomis': ','.join(yomis),
            'provs': ','.join(provs),
        })
    fsutils.write_csv(ret, 'kanji_joyo.tsv')


if __name__ == '__main__':
    main()

