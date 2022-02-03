#!/usr/bin/env python3

#from random import randrange
#from pathlib import Path
from sys import stdin
from time import time
from termios import *

DIFFICULTÉ_MINIMUM = 6
DIFFICULTÉ_MAXIMUM = 10

class save_stdin_state:
    def __enter__(self):
        self.mode = tcgetattr(stdin)
    def __exit__(self, *args):
        tcsetattr(stdin, TCSAFLUSH, self.mode)

def visit_stdin(vtime=0):
    IFLAG = 0
    OFLAG = 1
    CFLAG = 2
    LFLAG = 3
    ISPEED = 4
    OSPEED = 5
    CC = 6
    old_mode = tcgetattr(stdin)

    mode = old_mode[:]
    mode[IFLAG] = mode[IFLAG] & ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON)
    mode[OFLAG] = mode[OFLAG] & ~(OPOST)
    mode[CFLAG] = mode[CFLAG] & ~(CSIZE | PARENB)
    mode[CFLAG] = mode[CFLAG] | CS8
    mode[LFLAG] = mode[LFLAG] & ~(ECHO | ICANON | IEXTEN | ISIG)
    mode[LFLAG] = mode[LFLAG] | ECHO
    mode[CC][VMIN] = 0
    mode[CC][VTIME] = 1
    tcsetattr(stdin, TCSAFLUSH, mode)
    
    esc_mode = mode[:]
    esc_mode[CC][VTIME] = 0

    while True:
        ret = stdin.read(1)
        if ret == '\x1b':
            tcsetattr(stdin, TCSAFLUSH, esc_mode)
            esc_seq = stdin.read()
            if esc_seq:
                ret += esc_seq
            tcsetattr(stdin, TCSAFLUSH, mode)
        yield ret

def timeout_input(prompt, max_time, max_len):
    print(prompt, end='')
    start_time = time()
    USER_INPUT = ''
    with save_stdin_state():
        for char in visit_stdin():
            if char:
                USER_INPUT += char
            if time() - start_time > max_time or len(USER_INPUT) == max_len :
                return USER_INPUT

def mot_au_hasard(level):
    return "catfishing"[0:level]

def etudie_proposition(proposition, mot_a_deviner):
    mauvaises_lettres = [char for char in proposition if char not in mot_a_deviner]
    final = list()
    for i, char in enumerate(proposition) :
        if char == mot_a_deviner[i] :
            final.append('\x1b[32;1m' + char + '\x1b[0m')
        elif char in mauvaises_lettres :
            final.append('_')
        else :
            final.append('\x1b[31;1m' + char + '\x1b[0m')
    return ''.join(final)


def devine_un_mot(nb_chances, level, timeout): 
    mot_a_trouver = mot_au_hasard(level)
    for chances in range(nb_chances):
        proposition = timeout_input('votre proposition: ', timeout, level)
        print(etudie_proposition(proposition, mot_a_trouver))
        if proposition ==  mot_a_trouver:
            return True

if __name__ == '__main__':
    print('\n' * 300)
    print('##### M O T U S #####')
    print('                by Nophké & CD187')
    print()
    print(',---------------------,')
    print('|Ctrl + C pour quitter|')
    print('`---------------------`')
    print()

    nombre_de_chances = int(input('choisir un nombre de chances: '))

    timeout = 6 
    print(f'{timeout =} secondes',end='\r')

    difficulté = DIFFICULTÉ_MINIMUM 
    print(f'{difficulté =}')

    while True:
        manche_gagnée = devine_un_mot(nombre_de_chances, difficulté, timeout)
        if manche_gagnée:
            if difficulté < DIFFICULTÉ_MAXIMUM:
                difficulté += 1
                print("Vous entrez dans le niveau {difficulté}")
                continue
            else:
                print("Vous êtes au niveau maximum, Bravo !")
                break
        else:
            print('\n' * 30 + '-' * 30 + '\nPERDU\n' + '-' * 30)
            input('Press [ENTER]')
            break

