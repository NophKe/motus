#!/usr/bin/env python3

from tty import *
from termios import *
from os import getcwd
from sys import stdin
from pathlib import Path
from time import time, sleep
from random import randrange
from string import ascii_letters
from collections import defaultdict
from contextlib import suppress


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
    mode[CC][VMIN] = 0
    mode[CC][VTIME] = 5
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

       
def creation_dictionnaire() :
	with open(getcwd() + '/dictionnaire_motus.txt', 'r') as liste_de_mots :
		words = []
		for line in liste_de_mots :
			words.append(line.replace('\n',''))
	dico = defaultdict(list)
	for word in words :
		key = len(word)
		dico[key].append(word) 	
	return dico


def choix_mode() :
	print('''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|       Choisissez le mode de jeu en appuyant sur la touche E ou C :                                 |
|                                                                                                    |
|       E => entra??nement :   Partie en une seule manche.                                            |
|                             Vous choisissez la difficult??.                                         |
|                             Vous choisissez le nombre de lettre ?? deviner                          |
|                             Vous disposez d'autant d'essai par manche que de lettres dans le mot.  |
|                                                    	                                             |
|       C => challenge :      Partie en six manches.                                                 |
|                             Vous choisissez la difficult??.                                         |
|                             Le premier mot ?? deviner sera compos?? de 5 lettres.                    |
|                             Vous disposez d'autant d'essai par manche que de lettres dans le mot.  |
|                             A chaque manche gagn??e, le mot suivant aura une lettre de plus.        |
|                             Si vous trouvez le mot de 10 lettres, vous avez gagn?? le challenge.    |
|                                                    	                                             |
|                                                    	                                             |
|                                     ALT + F4 pour quitter                                          |
 '--------------------------------------------------------------------------------------------------' 
''')
	modes = {'E' : 'entra??nement' , 'C' : 'challenge' }
	with save_stdin_state() :
		for char in visit_stdin():
			if char.upper() in modes :
				mode_choisi = modes.get(char.upper())
				break
	print('vous avez choisi le mode', mode_choisi)
	return mode_choisi


def choix_difficulte() :
	print('''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|       Choisissez la difficult?? en appuant sur la touche F, M ou D :                                |
|                                                                                                    |
|       F   => facile :     Vous disposez de 60 secondes par essai pour donner une proposition       |
|       M   => moyen :      Vous disposez de 30 secondes par essai pour donner une proposition       |
|       D   => difficile :  Vous disposez de 15 secondes par essai pour donner une proposition       |
|                                                                                                    |
|                                     ALT + F4 pour quitter                                          |
 '--------------------------------------------------------------------------------------------------' 
''')
	difficult??s = {'F' : 60 , 'M' : 30 , 'D' : 15 }
	with save_stdin_state():
		for char in visit_stdin():
			if char.upper() in difficult??s :
				max_time = difficult??s.get(char.upper())
				break	
	print('vous disposez de', max_time, 'secondes par essai')	
	return max_time

	
def timeout_input(max_time, max_len):
	start_time = time()
	USER_INPUT = []
	print("\r" +'PROPOSITION : ', end = '')
	with save_stdin_state():
		for char in visit_stdin():
			if char in ascii_letters and char != '' :
				USER_INPUT.append(char.upper())
				print("\r" + 'PROPOSITION : ' + ''.join(USER_INPUT), end='')
			if time() - start_time > max_time or len(USER_INPUT) == max_len :
				return USER_INPUT


def devine(max_len):
	a = dico.get(max_len)
	return a[randrange(len(a))]
	

def etudie_proposition(proposition, mot_a_deviner):
	final = list()
	user_input = proposition
		                        
	counter_word_to_guess = defaultdict(int)				
	for char in mot_a_deviner :						
		counter_word_to_guess[char] += 1					  
						
	dict_output_word = defaultdict(list)
	for i, char in enumerate(user_input) :
		dict_output_word[i]	= 'to define'
			
	for i, char in enumerate(user_input) :
		if char == mot_a_deviner[i] :
			dict_output_word[i] = (char, 'right place')
			counter_word_to_guess[char] -= 1
	for i, char in enumerate(user_input) :
		if counter_word_to_guess[char] > 0 and char != mot_a_deviner[i]  :
			dict_output_word[i] = (char, 'wrong place')
			counter_word_to_guess[char] -= 1
		elif counter_word_to_guess[char] <= 0 and char != mot_a_deviner[i] :
			dict_output_word[i] = (char, 'not included')		
	
	for element in dict_output_word.values() :
		char = element[0]
		state = element[1]
		if state == 'right place' :
			final.append('\x1b[32;1m' + char + '\x1b[0m')
		elif state == 'wrong place' :
			final.append('\x1b[31;1m' + char + '\x1b[0m')
		elif state == 'not included' :
			final.append('_')

	return''.join(final)


def devine_un_mot(max_len, max_time, mot_a_deviner): 
	for chances in range(max_len):
		proposition	 = timeout_input(max_time, max_len)
		print("\r",'RESULTAT   : ' + etudie_proposition(proposition, mot_a_deviner))
		if ''.join(proposition) == ''.join(mot_a_deviner) :
			return True

def victoire() :
		print( '''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|  ______ ______ _      _____ _____ _____ _______    _______ _____ ____  _   _  _____    _   _   _   |
| |  ____|  ____| |    |_   _/ ____|_   _|__   __|/\|__   __|_   _/ __ \| \ | |/ ____|  | | | | | |  |
| | |__  | |__  | |      | || |      | |    | |  /  \  | |    | || |  | |  \| | (___    | | | | | |  |
| |  __| |  __| | |      | || |      | |    | | / /\ \ | |    | || |  | | . ` |\___ \   | | | | | |  |
| | |    | |____| |____ _| || |____ _| |_   | |/ ____ \| |   _| || |__| | |\  |____) |  |_| |_| |_|  |
| |_|    |______|______|_____\_____|_____|  |_/_/    \_\_|  |_____\____/|_| \_|_____/   (_) (_) (_)  |
|                                                                                                    |
|                                                                                                    |
|   ###########################   appuyer sur ENTRER pour continuer   ###########################    |
|                                                                                                    |
|                                                                                                    |
|                                      CTRL + C pour quitter                                         |
 '--------------------------------------------------------------------------------------------------'
''')


def defaite() :
	print( '''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|                            _____  ______ _____  _____  _    _                                      |
|                           |  __ \|  ____|  __ \|  __ \| |  | |                                     |
|                           | |__) | |__  | |__) | |  | | |  | |                                     |
|                           |  ___/|  __| |  _  /| |  | | |  | |                                     |
|                           | |    | |____| | \ \| |__| | |__| |  _   _   _                          |
|                           |_|    |______|_|  \_\_____/ \____/  (_) (_) (_)                         |
|                                                                                                    |
|                                                                                                    |
|   ###########################   appuyer sur ENTRER pour continuer   ############################   |
|                                                                                                    |
|                                                                                                    |
|                                      CTRL + C pour quitter                                         |
 '--------------------------------------------------------------------------------------------------'
''')	

def choix_nb_lettres() :
	possibilit??s = dico.keys()	
	max_len = False
	while max_len not in possibilit??s :
		with suppress(ValueError) :
			max_len = int(input('''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|       Choisissez le nombre de lettres pour cette manche :                                          |
|                                                                                                    |
|       Ecrivez un nombre entre 5 et 10 et validez en appuyant sur la touche [ENTREE]                |
|                                                                                                    |
|                                                                                                    |
|                                     ALT + F4 pour quitter                                          |
 '--------------------------------------------------------------------------------------------------' 
nombres de lettres : '''))
	return max_len



if __name__ == '__main__':

	dico = creation_dictionnaire()
	while True:
	
		print( '''\n
 ,--------------------------------------------------------------------------------------------------, 
|                                                                                                    |
|                                 __  __  ____ _______ _    _  _____                                 |
|                                |  \/  |/ __ \__   __| |  | |/ ____|                                |
|                                | \  / | |  | | | |  | |  | | (___                                  |
|                                | |\/| | |  | | | |  | |  | |\___ \                                 |
|                                | |  | | |__| | | |  | |__| |____) |                                |
|                                |_|  |_|\____/  |_|   \____/|_____/                                 |
|                                                                                                    |
|                                                                                                    |
|                                                                                                    |
|                                                                                by Nophk?? & CD187   |
|                                                                                                    |
|                                                                                                    |
|   ###########################   appuyer sur ENTRER pour commencer   ############################   |
|                                                                                                    |
|                                                                                                    |
|                                      CTRL + C pour quitter                                         |
 '--------------------------------------------------------------------------------------------------'
''')

		start = input()
		while True :
			mode_choisi = choix_mode()
		
###--------------------------- entrainement ---------------------------###
		
			if mode_choisi == 'entra??nement' :
				max_time = choix_difficulte() 
				max_len = choix_nb_lettres()		
				mot_a_deviner = devine(max_len)
				gagn?? = devine_un_mot(max_len, max_time, mot_a_deviner)
				if gagn?? == True :
					victoire()
					rejouer = input()
					continue
				else :
					defaite()
					rejouer = input()
	
###---------------------------- challenge -----------------------------###

			else : 
				max_time = choix_difficulte()
				manche_gagn??e = 0
				max_len = min(dico.keys())
				while manche_gagn??e != len(dico.keys()) :		
					mot_a_deviner = devine(max_len)
					gagn?? = devine_un_mot(max_len, max_time, mot_a_deviner)
					if gagn?? == True :			
						max_len = max_len + 1
						manche_gagn??e += 1
						continue
					else :
						defaite()
						rejouer = input()
						break						
				victoire()
				rejouer = input()
