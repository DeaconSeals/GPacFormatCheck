#!/usr/bin/python3

# author: Deacon Seals

# use: python3 worldCheck.py worldFilePath0 worldFilePath1 ... worldFilePathN
# use note: Bash regex filename expressions supported

'''
Non-secret-sauce checks:
*valid characters
*valid delineation
*correct number of elements per line
*valid map dimensions
*starting location of pac-man and ghosts
*correct map orientation
*valid indexing scheme # 0 indexing 4 life
*basic bounds checking

Secret sauce checks:
*map correctness
*more complex move validation
*other secret things
'''

import sys

softErrors = []

class FormattingError(Exception):
	def __init__(self, errors):
		self.errors = errors

def printLines(lines):
	message = ""
	if len(lines) == 1:
		message = "line "+repr(lines[0]+1)
	elif len(lines) > 1:
		message = "lines "+repr(lines[0]+1)
		for i in range(1,len(lines)):
			message += ", "+repr(lines[i]+1)
	return message

def checkCharacters(text):
	errors = []
	errata = dict()
	for line in range(len(text)):
		for char in text[line]:
			if char.casefold() not in "mpwft0123456789 ":
				if char not in errata:
					errata[char] = set()
				errata[char].add(line)

	if errata:
		for char in errata:
			lines = list(errata[char])
			message = ": invalid character "+repr(char)+" found on "
			
			if len(lines) > 1:
				lines.sort()
			message += printLines(lines)
			errors.append(message)

	if errors: raise FormattingError(errors)
	
	return

def checkStructure(text):
	errors = []
	width = 0
	height = 0
	global softErrors

	# iterate over text and ignore tailing blank lines
	# note: our initial rstrip formatting clears all space-only lines
	for line in range(len(text)):
		if text[-(line+1)]:
			if line > 0:
				text = text[:-line]
			break
	
	if text:
		if text[0].isdigit() and '.' not in text[0]:
			width = int(text[0])
		else:
			errors.append(": invalid width")

		if len(text) > 1:
			if text[1].isdigit() and '.' not in text[1]:
				height = int(text[1])
			else:
				errors.append(": invalid height")

		blankLines = []
		noDelineation = set()
		tooManySpaces = set()
		tooFewElements = []
		tooManyElements = []

		for line in range(2,len(text)):
			if text[line]:
				if text[line].count(" ") == 0:
					noDelineation.add(line)
				elif text[line].count(" ") > 2:
					tooManySpaces.add(line)

				if text[line].count(" ") > 0:
					segmented = [element for element in text[line].split(" ") if element]
					if len(segmented) < 3:
						tooFewElements.append(line)
					elif len(segmented) > 3:
						tooManyElements.append(line)
						tooManySpaces.discard(line)
			else:
				blankLines.append(line)

		if blankLines:
			softErrors.append(": warning, unexpected blank line found on "+printLines(blankLines))

		noDelineation = list(noDelineation)
		tooManySpaces = list(tooManySpaces)

		if len(noDelineation) > 1:
			noDelineation.sort()
		if len(tooManySpaces) > 1:
			tooManySpaces.sort()

		if noDelineation:
			errors.append(": there is no space delineation on "+printLines(noDelineation))
		if tooManySpaces:
			errors.append(": there are too many spaces on "+printLines(tooManySpaces))
		if tooFewElements:
			errors.append(": there are too few elements on "+printLines(tooFewElements))
		if tooManyElements:
			errors.append(": there are too many elements on "+printLines(tooManyElements))
	else:
		errors.append(": file is empty")

	if errors: raise FormattingError(errors)

	return width, height

def getElements(line):
	return line[0], (int(line[1]), int(line[2]))

def getFirstLoc(piece, world):
	for line in world:
		if len(line) < 3:
			continue
		target, location = getElements(line)
		if target == piece:
			return location
	return (-1,-1)
'''
*valid map dimensions
*starting location of pac-man and ghosts
*correct map orientation
*valid indexing scheme # 0 indexing 4 life
*basic bounds checking
'''
def checkContent(text, height, width):
	errors = []
	errata = dict()
	pacStart = (0, height-1)
	ghostStart = (width-1, 0)
	invalid = (-1,-1)

	pills = set()
	walls = set()
	reduced = {"m","1","2","3","f","t"}
	validPieces = reduced | {"p","w"}

	if width < 2:
		errors.append(": width must be at least 2")
	if height < 2:
		errors.append(": height must be at least 2")

	world = [[element for element in line.split(' ') if element] for line in text]

	capitals = [line[0] for line in world[2:] if line and line[0] not in validPieces and line[0].casefold() in validPieces]
	if capitals:
		message = ": detected incorrect use of capital letters for character(s) "
		for letter in capitals:
			message += " "+repr(letter)

	location = getFirstLoc("p")
	if location == invalid:
		
	if location != pacStart:
		errors.append(": expected pac-man starting location of "+repr(pacStart)+" but got "+repr(location))

	for line in range(2,len(world)):
		
		if not world[line]:
			continue

		piece, location = getElements(world[line])
		
		if piece not in validPieces:
			if piece not in errata:
				errata[piece] = set()
			errata[piece].add(line)
		else:
			pass

def checkWorld(filename):
	worldText = []
	global softErrors

	with open(filename, 'r') as file:
		worldText = [line.rstrip() for line in file]

	if worldText:
		try:
			checkCharacters(worldText)
			width, height = checkStructure(worldText)
			checkContent(worldText, height, width)

			for error in softErrors:
				print(filename+error)
			softErrors.clear()

		except FormattingError as e:
			for error in e.errors:
				print(filename + error)


def main():
	if len(sys.argv) < 2:
		print("Please pass in a world file")
	else:
		for arg in range(1,len(sys.argv)):
			checkWorld(sys.argv[arg])

if __name__ == '__main__':
	main()