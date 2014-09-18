#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, json, urllib.parse
from collections import deque
from helper.listConcat import listConcat

from scrape import DateTimeEncoder
import glob

streetCache = {}

def searchStreet(street):
	if street in streetCache:
		print('cache hit: %s '%street)
		return streetCache[street]

	a = '%3Cosm-script%20output%3D%22json%22%20timeout%3D%2225%22%3E%0A%20%20%20%20%3Cid-query%20type%3D%22area%22%20ref%3D%223600062594%22%20into%3D%22area%22%2F%3E%0A%20%20%20%20%3Cunion%3E%0A%20%20%20%20%20%20%20%20%3Cquery%20type%3D%22way%22%3E%0A%20%20%20%20%20%20%3Chas-kv%20k%3D%22name%22%20v%3D%22'
	b = '%22%2F%3E%0A%20%20%20%20%20%20%3Carea-query%20from%3D%22area%22%2F%3E%0A%20%20%20%20%3C%2Fquery%3E%0A%20%20%3C%2Funion%3E%0A%20%20%3C%21--%20print%20results%20--%3E%0A%20%20%3Cprint%20mode%3D%22body%22%2F%3E%0A%20%20%3Crecurse%20type%3D%22down%22%2F%3E%0A%20%20%3Cprint%20mode%3D%22skeleton%22%20order%3D%22quadtile%22%2F%3E%0A%3C%2Fosm-script%3E'

	data = '<osm-script>' + \
		'<osm-script output="json" timeout="25">' + \
			'<id-query into="area" {{nominatimArea:Chemnitz}} type="area"/>' + \
			'<union>' + \
				'<query type="way">' + \
					'<has-kv k="name" v="PLACEHOLDER"/>' + \
					'<area-query from="area"/>' + \
				'</query>' + \
			'</union>' + \
			'<print mode="body"/>' + \
			'<recurse type="down"/>' + \
			'<print mode="skeleton" order="quadtile"/>' + \
		'</osm-script>' + \
	'</osm-script>'

	response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street) + b )
	content = response.read()
	data = json.loads(content.decode('utf8'))

	if len(data['elements']) == 0:
		print('street %s couldn\'t be found'%street)
		raise Exception

	nodes = []
	ways = []
	detailedNodes = {}
	for d in data['elements']:
		if d['type'] == 'way':
			nodes = nodes + d['nodes']
			ways.append(d['nodes'])
		if d['type'] == 'node':
			detailedNodes[d['id']] = {'lng': d['lon'], 'lat': d['lat']}

	if len(nodes) == 0:
		print('no nodes for street %s'%street)
		raise Exception

	result = { 'nodes': set(nodes), 'detailed': detailedNodes, 'ways': ways }

	streetCache[street] = result

	return result

def findIntersection(street1, street2, street3=False):

	try:
		data1 = searchStreet(street1)
		data2 = searchStreet(street2)
	except Exception:
		return []


	sameNodes = list(data2['nodes'].intersection(data1['nodes']))
	if len(sameNodes) == 0:
		print('sameNodes empty')

	allNodes = {}
	allNodes.update(data1['detailed'])
	allNodes.update(data2['detailed'])

	result = []
	if street3:
		# specifc way
		try:
			data3 = searchStreet(street3)
		except Exception:
			return []

		allNodes.update(data3['detailed'])

		mergedWays = listConcat()
		for way in data1['ways']:
			mergedWays.add(way)

		ways = mergedWays.get()

		sameNodes2 = list(data3['nodes'].intersection(data3['nodes']))

		if len(sameNodes2) == 0:
			print('sameNodes2 empty')

		for node1 in sameNodes:
			for node2 in sameNodes2:
				for way in ways:
					if node1 in way and node2 in way:
						result.append([allNodes[n] for n in way])
	else:
		for node in sameNodes:
			result.append(allNodes[node])

	return result

def extract():
	files = glob.glob('data-2*.json')
	files.sort()
	files.reverse()
	if len(files) == 0:
		raise SystemExit

	# extract date
	filename = files[0]
	date = filename[5:-5]

	print('file used: %s'%filename)

	f = open(filename)
	data = json.load(f)

	found = []
	notfound = []
	i = 0
	for entry in data:
		i += 1
		if 'location' in entry['parsed']:
			street1 = entry['street']
			street2 = entry['parsed']['location']['streets'][0]
			# remove "
			street2 = street2.replace('"', '')
			if entry['parsed']['location']['relation'] == 'intersection':
				print('%2i/%2i process - intersection - %s %s'%(i, len(data), street1, street2))
				geodata = findIntersection(street1, street2)
			elif entry['parsed']['location']['relation'] == 'between':
				street3 = entry['parsed']['location']['streets'][1]
				print('%2i/%2i process - between - %s %s %s'%(i, len(data), street1, street2, street3))
				geodata = findIntersection(street1, street2, street3)
			else:
				print('%2i/%2i skip - %s'%(i, len(data), entry['parsed']['location']['relation']))
				continue

			if len(geodata) > 0:
				print('\tfound')
				entry['geodata'] = geodata
				found.append(entry)
			else:
				print('\tnot found')
				notfound.append(entry)
		else:
			print('%2i/%2i'%(i, len(data)))

	f = open('data-parsed-' + date + '.json', 'w')
	json.dump(found, f, cls=DateTimeEncoder)
	f.close()
	f = open('data-parsed-' + date + '-notfound.json', 'w')
	json.dump(notfound, f, cls=DateTimeEncoder)
	f.close()

	print('stats: found: %2i/%2i'%(len(found), len(data)))

if __name__ == "__main__":
	extract()
