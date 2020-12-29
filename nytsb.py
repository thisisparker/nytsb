#!/usr/bin/env python3

import json
import math
import random
import re
import shutil
import textwrap
import urllib.request

class SpellingBee:
    def __init__(self):
        url = "https://www.nytimes.com/puzzles/spelling-bee"
        res = urllib.request.urlopen(url)

        pattern = re.compile('window.gameData = .*?}}')

        scripts = re.findall(pattern, res.read().decode('utf-8'))

        data = json.loads(scripts[0][len('window.gameData = '):])

        self.date = data['today']['displayDate']
        self.center = data['today']['centerLetter']
        self.outer = data['today']['outerLetters']
        self.valid = data['today']['validLetters']
        self.pangrams = data['today']['pangrams']
        self.answers = data['today']['answers']

        self.valid.insert(3, self.valid.pop(0))

        self.max_score = calculate_score(self.answers)

        self.guessed = []

    def shuffle_letters(self):
        random.shuffle(self.valid)

    @property
    def score(self):
        return calculate_score(self.guessed)

    @property
    def rank(self):

        ranks = [["Beginner",0], ["Good Start",2], ["Moving Up",5],
                 ["Good",8], ["Solid",15], ["Nice",25], ["Great",40],
                 ["Amazing",50], ["Genius",70], ["Queen Bee", 100]]

        r = max([l for l in ranks 
                    if self.score/self.max_score * 100 >= l[1]],
                    key=lambda x: x[1])[0]

        return r

    def display_letters(self):
        spaces = 7 * ' {} '
        letters = [l.lower() if l != self.center 
                             else l.upper() for l in self.valid]
        print('\n', spaces.format(*letters),'\n')

    def guessed_list(self):
        num_columns = min([3, int(get_width()/15)]) or 1
        num_rows = len(self.guessed) // num_columns

        num_rows += 1 if len(self.guessed) % num_columns else 0

        l = sorted(self.guessed)
        columnized_list = [l[s::num_rows] for s in range(num_rows)]

        rows = [(len(row)*'{:<14}').format(*row) for row in columnized_list]

        return '\n'.join(['Guessed words ({}):'.format(len(self.guessed))] + rows)


def quit():
    return 'Ok bye now'

def calculate_score(word_list):
    score = 0
    for w in word_list:
        if len(w) == 4:
            score += 1
        elif len(w) > 4:
            score += len(w)

        if len(set(w)) == 7:
            score += 7

    return score

def get_help():
    width = get_width()
 
    help_text = """\
        Create words using letters from the hive. Words must contain
        at least 4 letters, must include the center letter (shown here in 
        uppercase), and letters can be used more than once.

        At any time, you can submit the letter S to shuffle your hive,
        L to list the words you've correctly guessed, ? to view this help
        text, or Q to quit."""

    help_grafs = [textwrap.dedent(graf).replace('\n',' ') for graf in 
            help_text.split('\n\n')]

    return '\n\n'.join([textwrap.fill(graf, width=width)
                       for graf in help_grafs])

def get_width():
    return shutil.get_terminal_size().columns - 2

def main():

    bee = SpellingBee()

    entry = ''

    commands = {'q': quit,
                's': bee.shuffle_letters,
                'l': bee.guessed_list,
                '?': get_help,
                '':  get_help}

    print('\n🐝 Spelling Bee for {} 🐝\n'.format(bee.date))

    print(get_help(), '\n')

    while entry != 'q':
        print('Score:', bee.score, '({})'.format(bee.rank))
        bee.display_letters()

        entry = input('Enter a word: ').lower()

        msg = ''

        if entry in commands:
            msg = commands[entry]()
        elif len(entry) < 4:
            msg = 'Too short.'
        elif any(letter not in bee.valid for letter in entry):
            msg = 'Bad letters.'
        elif bee.center not in entry:
            msg = 'Missing center letter.'
        elif entry not in bee.answers:
            msg = 'Not in word list.'
        elif entry in bee.guessed:
            msg = 'Already found.'
        elif entry in bee.pangrams:
            msg = 'Pangram!'
            bee.guessed.append(entry)
        elif entry in bee.answers:
            msg = random.choice(['Awesome!', 'Nice!', 'Good!'])
            bee.guessed.append(entry)

        if msg:
            print('\n{msg}\n'.format(msg=msg))
        else:
            print('')

if __name__ == '__main__':
    main()
