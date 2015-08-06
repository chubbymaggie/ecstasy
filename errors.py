"""
Custom error classes and helper functions for descriptive error-messages.
"""

import warnings

class EcstasyError(Exception):
	"""
	Base class for exceptions in Ecstasy.

	Attributes:
		what (str): A descriptive string regarding the cause of the error.
	"""

	def __init__(self, what):
		"""
		Initializes the EcstasyError super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""

		self.what = what

		super(EcstasyError, self).__init__(what)

class FlagError(EcstasyError):
	"""
	Raised when flag combinations are invalid.
	"""

	def __init__(self, what):
		"""
		Initializes the EcstasyError super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""

		super(FlagError, self).__init__(what)

class ParseError(EcstasyError):
	"""
	Raised when the string passed to the beautify()
	method is ill-formed and includes some syntactic
	badness such as missing closing tags.
	"""

	def __init__(self, what):
		"""
		Initializes the EcstasyError super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""

		super(ParseError, self).__init__(what)

class ArgumentError(EcstasyError):
	"""
	Raised when the positional argument for a phrase
	is either out-of-range (i.e. there were fewer positional
	arguments passed to beautify() than requested in the argument).
	"""

	def __init__(self, what):
		"""
		Initializes the EcstasyError super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""

		super(ArgumentError, self).__init__(what)

class InternalError(EcstasyError):
	"""
	Raised when something went wrong internally, i.e.
	within methods that are non-accessible via the
	API but are used for internal features or processing.
	Basically get mad at the project creator.
	"""

	def __init__(self, what):
		"""
		Initializes the EcstasyError super-class.

		Arguments:
			what (str): A descriptive string regarding the cause of the error.
		"""
		super(InternalError, self).__init__(what)

def position(string, index):
	"""
	Returns a helpful position description for an index in a
	(multi-line) string using the format line:column.

	Arguments:
		string (str): The string to which the index refers.
		index (int): The index of the character in question.

	Returns:
		A string with the format line:column where line refers to the
		1-indexed row/line in which the character is found within the
		string and column to the position of the character within
		(relative to) that  line.
	"""

	if not string:
		return None

	if index < 0 or index >= len(string):
		raise InternalError("Out-of-range index passed to errors.position!")

	lines = string.split("\n")

	# If there only is one single line the
	# line:index format wouldn't be so intuitive
	if len(lines) == 1:
		return str(index)

	before = n = 0

	for n, line in enumerate(lines):
		# Note that we really want > and not
		# >= because the length is 1-indexed
		# while the index is not, i.e. the
		# value of 'before' already includes the
		# first character of the next line when
		# speaking of its 0-indexed index
		if before + len(line) > index:
			break
		before += len(line)

	# n + 1 to have it 1-indexed
	# index - before to have only the
	# index within the relevant line
	return "{}:{}".format(n + 1, index - before)

def number(digit):
	"""
	Gets a spoken-word representation for a number.

	Arguments:
		digit (int): An integer to convert into spoken-word.

	Returns:
		A spoken-word representation for a digit,
		including an article ('a' or 'an') and a suffix,
		e.g. 1 -> 'a 1st', 11 -> "an 11th".
	"""

	digit = str(digit)

	if digit.startswith("8") or digit[:len(digit) % 3] == "11":
		article = "an "
	else:
		article = "a "

	if digit.endswith("1") and digit != "11":
		suffix = "st"
	elif digit.endswith("2") and digit != "12":
		suffix = "nd"
	elif digit.endswith("3") and digit != "13":
		suffix = "rd"
	else:
		suffix = "th"

	return article + digit + suffix

def warn(what, string, pos):

	"""
	Combines a warning with a call to errors.position().

	Simple convenience function.

	Arguments:
		string (str): The string being parsed.
		pos (int): The index of the character that caused trouble.
	"""

	pos = position(string, pos)

	warnings.warn("{} at position {}!".format(what, pos), Warning)
