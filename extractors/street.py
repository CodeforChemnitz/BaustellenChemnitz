#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class StreetExtractionException(Exception):
	pass


def extract(locationString):
	"""Return an dict with following keys: since, until, note(optional)

	>>> from pprint import pprint
	>>> pprint(extract('zwischen Lange Straße und Leipziger Weg'))
	{'relation': 'between', 'streets': ['Lange Straße', 'Leipziger Weg']}

	>>> pprint(extract('Einmündung Lange Straße/Leipziger Weg'))
	{'relation': 'intersection', 'streets': ['Lange Straße', 'Leipziger Weg']}
	>>> pprint(extract('in Höhe Lange Straße/Leipziger Weg'))
	{'relation': 'intersection', 'streets': ['Lange Straße', 'Leipziger Weg']}
	>>> pprint(extract('Kreuzung Lange Straße/Leipziger Weg'))
	{'relation': 'intersection', 'streets': ['Lange Straße', 'Leipziger Weg']}

	>>> pprint(extract('stadtwärts nach Lange Straße'))
	{'relation': 'townwards-after', 'streets': 'Lange Straße'}
	>>> pprint(extract('landwärts vor Lange Straße'))
	{'relation': 'townwards-after', 'streets': 'Lange Straße'}

	>>> pprint(extract('stadtwärts vor Lange Straße'))
	{'relation': 'townwards-before', 'streets': 'Lange Straße'}
	>>> pprint(extract('landwärts nach Lange Straße'))
	{'relation': 'townwards-before', 'streets': 'Lange Straße'}
	>>> pprint(extract('landwärts Höhe Lange Straße'))
	{'relation': 'townwards-before', 'streets': 'Lange Straße'}

	"""

	data = {}
	between = re.match('^zwischen\s*(.*) und (.*)\s*$', locationString)
	if between:
		data['streets'] = list(between.groups())
		data['relation'] = 'between'
		return data

	intersection = re.match('^(Einmündung|in Höhe|Kreuzung)\s*(.*)\s*$', locationString)
	if intersection:
		data['streets'] = intersection.group(2).split('/')
		data['relation'] = 'intersection'
		return data

	townwards = re.match('^(stadtwärts nach|landwärts vor)\s*(.*)\s*$', locationString)
	if townwards:
		data['streets'] = townwards.group(2)
		data['relation'] = 'townwards-after'
		return data

	countrywards = re.match('^(stadtwärts vor|landwärts nach|landwärts Höhe)\s*(.*)\s*$', locationString)
	if countrywards:
		data['streets'] = countrywards.group(2)
		data['relation'] = 'townwards-before'
		return data

	raise StreetExtractionException(locationString)

if __name__ == "__main__":
	import doctest
	doctest.testmod()
