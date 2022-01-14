#!/usr/bin/env python3

from random import randrange
from pathlib import Path
from sys import stdin
from string import ascii_letters
from tty import CC, VMIN, VTIME, setraw
from termios import tcgetattr, tcsetattr, TCSAFLUSH

########    terminal manipulation     #################################

def setnonblocking(fd, when=TCSAFLUSH):
	mode = tcgetattr(fd)
	mode[CC][VMIN] = 0
	mode[CC][VTIME] = 0
	tcsetattr(fd, when, mode)

def get_a_key():
	"""This function reads an only one key from the keyboard and returns it.
	if this key is the <ESCAPE> key however, it checks if there are things
	left to read in the stdin buffer. This way we read one char at a time,
	but we steal collapse escape sequences."""
	mode = tcgetattr(stdin)
	setraw(stdin)
	rv = stdin.read(1)
	if rv == '\x1b':
		setnonblocking(stdin)
		esc_seq = stdin.read()
		if esc_seq:
			rv += esc_seq
	tcsetattr(stdin, TCSAFLUSH, mode)
	return rv

########    word manipulation     ####################################

def get_lenght(mot):
    """ Cette fonction retourne une longueur une mot «normalisée»:
    toto  -> 4
    tété  -> 4
    voeux -> 5
    """
    caracteres_speciaux = [ ' ' , '-' ]
    counter_ascii_letters = 0
    counter_caracteres_speciaux = 0

    for char in mot:
        if char in string.ascii_letters :
            counter_ascii_letters = counter_ascii_letters + 1
        if char in caracteres_speciaux :
            counter_caracteres_speciaux = counter_caracteres_speciaux + 1
    return counter_ascii_letters + counter_caracteres_speciaux

def mot_au_hasard(nombre_de_lettres):
    table = Path(get_file(nombre_de_lettres)).read_text().splitlines()
    return table[randrange(len(table))]

########    game loop     ############################################

def play():
    difficulté = 2 
    while True:
#TODO Factorise la variable du IF suivant.
        if devine(nombre_de_chances, difficulté):
            if difficulté < difficulté_maximum:
                difficulté = difficulté + 1
                print("Vous entrez dans le niveau " + str(difficulté))
            else:
                print("Vous êtes au niveau maximum, Bravo !")
#TODO remplacer dans la fonction devine
        else:
            print('\n' * 30 + '-' * 30 + '\nPERDU\n' + '-' * 30)
            input('Press [ENTER]')

def proposition() :
    user_input = [] 
    while len(user_input) != len(mot_a_deviner):
        pending = get_a_key()
        '''if pending =='\x1b[55' :
            break'''
        if pending not in ascii_letters :
            continue
        else :
            user_input.append(pending.upper())
            print("\r" + ''.join(user_input), end='')
    print('')	
    return user_input

########    dictionnary infrastructure     ###########################
# TODO delete next 2 gllobal variables
difficulté_maximum = 7 #il y a un accent dans le nom de cette variable :-)
chemin = ""

def get_file(numero):
    return chemin + "mots_de_" + str(numero) + "_lettres.txt"

def create_files():
    master_list = []
    with open(chemin + "liste_francais.txt", 'r') as dico :
        for line in dico :
            master_list.append([get_lenght(line) , line])

    for List in master_list :
        word_lenght = List[0]
        word = List[1]

    # Ce bout de prog ne fonctionnait pas ici car ces fichiers n'existent
    # pas encore dans ce repertoire.
        nom_du_fichier = get_file(word_lenght)
        if not Path(nom_du_fichier).exists(): # si ce fichier n'existe pas
            Path(nom_du_fichier).touch()      # créer un fichier vide

        fichier = open(nom_du_fichier, 'a')
        fichier.write(word)
    fichier.close()

def initialize():
    """ Le but de cette fonction est de vérifier que les fichiers mots_de_*_lettres.txt
    existent bien. La fonction teste jusqu'au sixième fichier. Si les 6 premiers existent, on 
    suppose que les autres aussi. (magic !)
    Si un des fichier n'existe pas, on lance la fonction create_files().
    On finit par vider l'écran, et afficher l'écran d'acceuil.
    """
    for number in range(6,10):
        if not Path(get_file(number)).exists():
            create_files()
            break
    print('\n' * 300) #devrait être assez pour vider l'écran
    print('##### M O T U S #####')
    print('                by Nophké & XXXXXX')
    print()
    print(',---------------------,')
    print('|Ctrl + C pour quitter|')
    print('`---------------------`')
    print()


def devine(nb_chances, level): 
        mot_a_trouver = mot_au_hasard(level)
        for chances in range(nb_chances):
            print(' _' * level)
            print()
            proposition = input('votre proposition: ')
            if proposition ==  mot_a_trouver:
                print('gagné')
                return True



#TODO use get_terminal_size()
# Vu que tout est encapsulé dans des fonction notre programme devient 
# beaucoup plus simple, et se résume à ces quelques lignes:

########    LE PROGRAMME EN LUI MEME   ###############################

if __name__ == '__main__':
    initialize()
    nombre_de_chances = int(input('choisir un nombre de chances: '))
    play()

    mot_a_deviner = ['J', 'O', 'U', 'E', 'E']

    while True :

        length = len(mot_a_deviner)
        print('veuillez proposer un mot de ' + str(length) + ' lettres :')
        proposition = proposition()
        
        mauvaises_lettres = [char for char in proposition]
        for char in mot_a_deviner :
            if char in mauvaises_lettres :
                mauvaises_lettres.remove(char)
        
        final = list()
        for i, char in enumerate(proposition) :
            if char == mot_a_deviner[i] :
                final.append('\x1b[32;1m' + char + '\x1b[0m')
            elif char in mauvaises_lettres :
                final.append('_')
            else :
                final.append('\x1b[31;1m' + char + '\x1b[0m')
        print(''.join(final))
