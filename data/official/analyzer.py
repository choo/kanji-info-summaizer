import os, re
import fsutils
from char_utils import is_kanji
from pprint import pprint

FILEPATH = 'joyokanjihyo.txt'
OUTPUT_FILE = 'kanji_joyo.json'


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


def calc_line_ranges(lines):
    ret = []
    for i, line in enumerate(lines):
        if _is_title(line):
            if len(ret) > 0 and not ret[-1][1]:
                ret[-1][1] = i
            ret.append([i, None])
        elif line.startswith('03初_改定常用'):
            ret[-1][1] = i - 1
    return ret


def main():
    ret = []
    lines = fsutils.read_lines(FILEPATH)
    line_ranges = calc_line_ranges(lines)

    for i, end in line_ranges:
        tmp = {'title': lines[i].strip(), 'joyo_yomis': [], 'remarks': ''}
        if _is_kyujitai(lines[i + 1]):
            kyujitai = lines[i + 1].strip()
            kyujitai = kyujitai.replace('（', '').replace('）', '')
            tmp['kyujitai'] = kyujitai
            i += 1

        for idx in range(i + 1, end):
            ''' rest of lines '''
            line = lines[idx]
            if line.strip() == '':
                continue

            ''' 読みが記載されている行はタブで区切られているカラム数が 3 以上となる '''
            cols = [col.strip() for col in line.split('\t')]
            n = len(cols)
            if n > 4:
                tmp['joyo_yomis'].append({'yomi': cols[3], 'prov': cols[4]})
            elif n > 3:
                ''' there's no line with this condition '''
                tmp['joyo_yomis'].append({'yomi': cols[3]})
                print(line)

            if n > 5:
                tmp['remarks'] += cols[5]
            if n > 6:
                ''' there's no line with this condition '''
                print(cols[6]) # nothing
        ret.append(tmp)

    fsutils.write_json(ret, OUTPUT_FILE)
    print('{} kanjis information were written to {}'.format(len(ret), OUTPUT_FILE))


if __name__ == '__main__':
    main()
