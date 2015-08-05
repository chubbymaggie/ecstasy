# -*- coding: utf-8 -*-

"""
The heart of the ecstasy package, containing the main Parser class.

The MIT License (MIT)

Copyright (c) 2015 Peter Goldsborough

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without LIMITation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import re
import warnings
import collections

from . import flags
from . import errors

class Phrase(object):
	"""
	Class describing a single parsed phrase.

	When a string is parsed in ecastasy, specially-marked regions of
	text are converted taken note of and converted into Phrase objects,
	which are later then used to replace the parsed strings (including any
	tags or arguments) with the string itself as well as the formatting
	codes specified by the arguments passed to Parser.beautify(), which
	are then interpreted by the command line.

	Attributes:
		string (str): The text of the phrase (between opening and closing tags).
		opening (int): The index of the opening tag.
		closing (int): The index of the closing tag.
		style (int): The formatting/style flag-combination of the phrase.
		nested (list): A list of nested Phrase objects (children).
		override (bool): The phrase's override specification.
	"""

	def __init__(self,
				 opening=None,
				 closing=None,
				 string=None,
				 style=None):

		self.string = string

		self.opening = opening
		self.closing = closing

		self.style = style

		self.arguments = []

		self.nested = []

		self.override = False

	def __str__(self):
		return self.string

class Parser:
	def __init__(self, args, kwargs):

		self.always = kwargs

		self.positional = self.get_flags(args)

		self.tags = re.compile(r"[<>]")

		# For positional arguments
		self.argument = re.compile(r"^(-?\d,?)+!?$")

		# Used in self.stringify
		self.counter = 0

	def get_flags(self, args):

		positional = []

		for argument in args:
			# A flag is an instance of a subclass of
			# flags.MetaEnum if it was passed alone
			if isinstance(argument, flags.MetaEnum):
				positional.append(argument)

			# or is an integer if it was (bitwise) OR'd
			# with another flag (a "flag combination")
			elif isinstance(argument, int):
				if argument < 0 or argument >= flags.LIMIT:
					raise errors.FlagError("Flag value '{}' is out of range "
						"!".format(argument))
				positional.append(argument)

			# Dictionaries store 'always'-arguments
			elif isinstance(argument, dict):
				for key, value in argument.items():
					# Simple 'always'-argument where one string
					# is mapped to one formatting flag-combination
					if isinstance(key, str):
						self.always[key] = value

					# Complex 'always'-argument with a
					# tuple containing strings, each with the same
					# flag-combination (same value)
					elif isinstance(key, tuple):
						for i in key:
							self.always[i] = value
					else:
						raise TypeError("Key '{}' in dictionary "
										"argument passed is neither "
										"a string nor a tuple "
										"of strings!".format(key))

			elif isinstance(argument, collections.Iterable):
				for element in argument:
					try:
						element = int(element)
					except TypeError:
						raise TypeError("Element {} is neither a flag nor a "
										"(bitwise) OR'd flag-combination"
										"!".format(element))

					if element < 0 or element >= flags.LIMIT:
						raise errors.FlagError("Flag value '{}' is out of "
										   	   "range !".format(element))
					positional.append(element)
			else:
				raise TypeError("Argument '{}' is neither a flag, a "
								"(bitwise) OR'd flag-combination, a "
								"dictionary nor an  iterable of positional "
								"arguments!".format(argument))

		return positional

	def beautify(self, string):

		string, phrases = self.parse(string)

		if not phrases:
			return string

		return self.stringify(string, phrases)

	def parse(self, string, root=None):
		
		# When parent is None (at the first call)
		# we return a list of phrase, else this
		# function will return a phrase object
		# this is because there is no 'root' phrase
		if not root:
			phrases = []

		tag = self.tags.search(string)

		while tag:
			if tag.group() == "<":
				opening = tag.start()

				# Check for escaping
				if string[opening - 1] == "\\":
					# Remove the escape character
					string = string[:opening - 1] + string[opening:]

					# When removing the escape character, the
					# opening tag index is pushed one back
					opening -= 1

					# If the escape character was not itself (double)
					# escaped we can look for the next tag
					if opening == 0 or string[opening - 1] != "\\":

						tag = self.tags.search(string, tag.start())
						continue

				child = Phrase(opening)

				escaped, child = self.parse(string[opening + 1:], child)

				if root:
					root.nested.append(child)
				else:
					phrases.append(child)

				string = string[:opening + 1] + escaped

				tag = self.tags.search(string, child.closing + 1)

			# tag is closing ('>')
			elif root:

				# Whatever is between the opening tag and this closing tag
				substring = string[: tag.start()]

				# Positional argument <^(-?\d,?)+$>
				if self.argument.match(substring):

					# Override mode (overrides 'always' style)
					if substring.endswith("!"):
						root.override = True
						substring = substring[:-1]

					root.arguments = [int(i) for i in substring.split(",")]

					string = string[tag.end():]

					tag = self.tags.search(string)
					continue

				# Escape-character to escape the closing tag (/>)
				elif substring.endswith("\\"):

					# Get rid of the escape character either way
					string = string[:tag.start() - 1] + string[tag.start():]

					if not substring[:-1].endswith("\\"):
						# tag.start() is now one index passed the closing tag
						tag = self.tags.search(string, tag.start())
						continue

					# Double-escape means this is really supposed to be a
					# closing tag and thus we can return the phrase.
					else:
						# The closing position should be in the same scope
						# as the scope of the opening position (scope in
						# the sense of to which phrase the positions are
						# relative to). -1 due to the escaped character but
						# + 1 because index 0 is phrase.opening + 1
						root.closing = root.opening + tag.start()
						root.string = string[: tag.start() - 1]
				else:
					root.closing = root.opening + 1 + tag.start()
					root.string = string[: tag.start()]

				return string, root

			else:
				# Replace escape character
				if tag.start() > 0 and string[tag.start() - 1] == "\\":
					string = string[:tag.start() - 1] + string[tag.start():]
				else:
					# When the phrase is None at the start, there should not
					# be a closing tag because none was ever opened. This is
					# not actually an error, but we should warn about it.
					position = errors.position(string, tag.start())
					warnings.warn("Un-escaped '>' character at "
							 	  "position {}".format(position),
								  Warning)

				tag = self.tags.search(string, tag.end())

		if not root:
			return string, phrases

		# If this is not the first stack-depth the function should
		# have returned upon finding a non-argument closing tag,
		# i.e. we should never have gotten here.
		word = re.search(r"([\w\s]+)(?![\d]*>[\w\s]+>)", string)

		raise errors.ParseError("No closing tag found for "
								"opening tag after expression '{}'"
								"!".format(word.group()))

	def stringify(self, string, phrases, parent=None):

		last_tag = 0

		beauty = ""

		for phrase in phrases:

			beauty += string[last_tag : phrase.opening]

			if phrase.arguments:
				combination = 0
				for n, i in enumerate(phrase.arguments):
					try:
						combination |= self.positional[i]
					except IndexError:
						raise errors.ArgumentError("Positional argument '{}' "
							 					   "(index {}) is out of"
							 					   "range!".format(i, n))

				# If override-mode is on (turned on by ! operator) the
				# positional arguments should override the 'always'-style
				if phrase.string in self.always and not phrase.override:
					combination |= self.always[phrase.string]

				phrase.style = self.codify(combination)

			elif phrase.string in self.always:
				phrase.style = self.codify(self.always[phrase.string])

			else:
				try:
					phrase.style = self.codify(self.positional[self.counter])
					self.counter += 1
				except IndexError:
					requested = errors.number(self.counter + 1)
					available = len(self.positional)
					raise errors.ArgumentError("Requested {} formatting "
											   "argument for '{}' but only "
											   "were supplied {} were supplied"
											   "!".format(requested,
											   			  phrase.string,
											   			  available))
			if phrase.nested:
				phrase.string = self.stringify(phrase.string,
											   phrase.nested,
											   phrase)

			reset = parent.style if parent else ""

			beauty += "\033[{}m{}\033[0;{}m".format(phrase.style,
													phrase,
													reset)
			last_tag = phrase.closing + 1

		if last_tag < len(string):
			beauty += string[last_tag:]

		return beauty

	def codify(self, combination):

		codes = []

		for enum in (flags.Format, flags.Color, flags.Fill):
			for flag in enum:
				if combination & flag:
					codes.append(str(flag))

		return ";".join(codes)
