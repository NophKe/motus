

from termios import tcgetattr, tcsetattr, TCSAFLUSH
from tty import CC, VMIN, VTIME, setraw
from sys import stdin


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
	





while True :
	
	mot_a_deviner = ['J', 'O', 'U', 'E', 'E']

	


###--------------------------------------------------------------------------------------------------###
###------------------------------------------ proposition -------------------------------------------###
###--------------------------------------------------------------------------------------------------###
	
	def proposition() :
	
		import string	
		
		user_input = [] 
		while len(user_input) != len(mot_a_deviner):
			pending = get_a_key()
			'''if pending =='\x1b[55' :
				break'''
			if pending not in string.ascii_letters :
				continue
			else :
				user_input.append(pending.upper())
				print("\r" + ''.join(user_input), end='')
		print('')	

		return user_input
 
	
	length = len(mot_a_deviner)
	print('veuillez proposer un mot de ' + str(length) + ' lettres :')
	
	proposition = proposition()
	

	
###--------------------------------------------------------------------------------------------------###
###----------------------------- analyse de la proposition et resultat ------------------------------###
###--------------------------------------------------------------------------------------------------###


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
