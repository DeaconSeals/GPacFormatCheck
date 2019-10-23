#!/usr/bin/python3

# author: Deacon Seals

# use: python3 worldCheck.py worldFilePath0 worldFilePath1 ... worldFilePathN
# use note: Bash regex filename expressions supported

'''
Non-secret-sauce checks:
*valid characters
*valid delineation
*correct number of characters
*starting location of pac-man and ghosts
*correct map orientation
*valid map dimensions
*valid indexing scheme # 0 indexing 4 life
*basic bounds checking

Secret sauce checks:
*map correctness
*more complex move validation
*other secret things
'''

import sys

def checkCharacters(text):
	errata = dict()
	for line in range(len(text)):
		for char in text[line]:
			if char.casefold() not in "mpwft0123456789 ":
				if char not in errata:
					errata[char] = set()
				errata[char].add(line)
			# else:
			# 	print("looks good")

	print(errata)
	if errata:
		for char in errata:
			lines = list(errata[char])
			message = ": invalid character "+repr(char)+" found on"
			if len(lines) == 1:
				message += " line "+repr(lines[0])
			else:
				lines.sort()
				message += " lines "+repr(lines[0])
				for line in range(1,len(lines)):
					message += ", "+repr(lines[line])
		print(message)
	else:
		print("looks good")


def checkWorld(filename):
	worldText = []
	with open(filename, 'r') as file:
		worldText = [line.rstrip() for line in file]

	print(worldText)
	if worldText:
		checkCharacters(worldText)

def main():
	if len(sys.argv) < 2:
		print("Please pass in a world file")
	else:
		for arg in range(1,len(sys.argv)):
			checkWorld(sys.argv[arg])

if __name__ == '__main__':
	main()