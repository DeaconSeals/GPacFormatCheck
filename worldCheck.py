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
		wrongFormat = []

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
						if segmented[0].casefold() not in {"m","1","2","3","f","t","p","w"} or \
						not(segmented[1].isdigit() and '.' not in segmented[1]) or \
						not(segmented[2].isdigit() and '.' not in segmented[2]):
							wrongFormat.append(line) 
			else:
				blankLines.append(line)

		if blankLines:
			softErrors.append(": [warning] unexpected blank line found on "+printLines(blankLines))

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
		if wrongFormat:
			errors.append(": correct format of 'indicator integer integer' was not followed on "+printLines(wrongFormat))
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

def inWidth(location, width):
	return location[0] >= 0 and location[0] < width
def inHeight(location, height):
	return location[1] >= 0 and location[1] < height
'''
*valid map dimensions DONE
*starting location of pac-man and ghosts DONE
*correct map orientation
*valid indexing scheme # 0 indexing 4 life
*basic bounds checking
'''
def checkContent(text, height, width):
	errors = []
	errata = dict()
	pacStart = (0, height-1)
	ghostStart = (width-1, 0)
	missing = (-1,-1)
	critical = False
	declarations = True

	walls = set()
	pills = set()
	reduced = {"m","1","2","3","f","t"}
	validPieces = reduced | {"p","w"}

	# check for reasonable dimensions
	if width < 2:
		errors.append(": width must be at least 2")
	if height < 2:
		errors.append(": height must be at least 2")

	# separate text into non-uniform 2D list
	world = [[element for element in line.split(' ') if element] for line in text]

	# check for errors relating to character capitalization
	capitals = [line[0] for line in world[2:] if line and line[0] not in validPieces and line[0].casefold() in validPieces]
	if capitals:
		message = ": detected incorrect use of capital letters for character(s) "
		for letter in capitals:
			message += " "+repr(letter)
		errors.append(message)

	if errors: raise FormattingError(errors)

	# check starting position of pac-man and ghosts
	location = getFirstLoc("m", world)
	if location == missing:
		errors.append(": couldn't find expected pac-man character 'm'")
		critical = True
	elif location != pacStart:
		errors.append(": expected pac-man starting location of "+repr(pacStart)+" but got "+repr(location))
	
	location = getFirstLoc("1", world)
	if location == missing:
		errors.append(": couldn't find expected ghost character '1'")
		critical = True
	elif location != ghostStart:
		errors.append(": expected ghost starting location of "+repr(pacStart)+" but got "+repr(location))

	location = getFirstLoc("2", world)
	if location == missing:
		errors.append(": couldn't find expected ghost character '2'")
		critical = True
	elif location != ghostStart:
		errors.append(": expected ghost starting location of "+repr(pacStart)+" but got "+repr(location))

	location = getFirstLoc("3", world)
	if location == missing:
		errors.append(": couldn't find expected ghost character '3'")
		critical = True
	elif location != ghostStart:
		errors.append(": expected ghost starting location of "+repr(pacStart)+" but got "+repr(location))
	# finished looking at starting position

	# live to squawk another day unless players are missing
	if errors and critical: raise FormattingError(errors)

	for line in range(2,len(world)):
		
		# skip blank lines
		if not world[line]:
			continue

		piece, location = getElements(world[line])
		
		if piece not in validPieces:
			errors.append(": invalid first element "+repr(piece)+" on line "+repr(line+1))
		else:
			if piece in {"m","1","2","3","f","p","w"}:
				horizontal = inWidth(location, width)
				vertical = inHeight(location, height)
				if not horizontal or not vertical:
					message = ": "+piece+" went out of bounds "
					if not horizontal and not vertical:
						message += "horizontally and vertically "
					elif not horizontal:
						message += "horizontally "
					else:
						message += "vertically "
					message += " at location "+repr(location)+" on line "+repr(line+1)
					errors.append(message)
					raise FormattingError(errors)

			if piece == "w":
				if declarations and location not in walls:
					walls.add(location)
				elif not declarations:
					errors.append(": unexpected wall declaration after game start on line "+repr(line+1))
					raise FormattingError(errors)
				else:
					errors.append(": wall on line "+repr(line+1)+" is defined already")
			elif piece == "p":
				if declarations and location not in pills:
					pills.add(location)
				elif not declarations:
					errors.append(": unexpected pill declaration after game start on line "+repr(line+1))
					raise FormattingError(errors)
				else:
					errors.append(": pill on line "+repr(line+1)+" is defined already")
			elif piece in {"m", "1", "2", "3"}:
				if piece == "m":
					message = ": pac-man"
				else:
					message = ": ghost "+piece
				
				if location in walls:
					errors.append(message+" ran into a wall at location "+repr(location)+" on line "+repr(line+1))
					raise FormattingError(errors)
			elif piece == "f":
				if location in walls:
					errors.append(": fruit spawned into a wall at location "+repr(location)+" on line "+repr(line+1))
					raise FormattingError(errors)
			elif piece == "t":
				if declarations:
					if list(pills & walls):
						message = ": intersection between pills ans walls at game location(s)"
						for loc in list(pills & walls):
							message += " "+repr(loc)
					declarations = False


	if errors: raise FormattingError(errors)
	return

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