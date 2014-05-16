#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, json, urllib.parse
from collections import deque
from helper.listConcat import listConcat

from scrape import DateTimeEncoder

def findIntersection(street1, street2, street3=False):

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

	response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street1) + b )
	content = response.read()
	data1 = json.loads(content.decode('utf8'))

	response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street2) + b )
	content = response.read()
	data2 = json.loads(content.decode('utf8'))

	if street3:
		response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + a + urllib.parse.quote(street3) + b )
		content = response.read()
		data3 = json.loads(content.decode('utf8'))
		if len(data3['elements']) == 0:
			print('street3 couldn\'t be found')
			return []

	if len(data1['elements']) == 0:
		print('street1 couldn\'t be found')
		return []
	if len(data2['elements']) == 0:
		print('street2 couldn\'t be found')
		return []

	nodes1 = []
	for d in data1['elements']:
		if d['type'] == 'way':
			nodes1 = nodes1 + d['nodes']

	if len(nodes1) == 0:
		print('nodes1 empty')

	nodes2 = []
	for d in data2['elements']:
		if d['type'] == 'way':
			nodes2 = nodes2 + d['nodes']

	if len(nodes2) == 0:
		print('nodes2 empty')

	if street3:
		nodes3 = []
		for d in data3['elements']:
			if d['type'] == 'way':
				nodes3 = nodes3 + d['nodes']
		nodes3 = set(nodes3)

		if len(nodes3) == 0:
			print('nodes3 empty')

	nodes1 = set(nodes1)
	nodes2 = set(nodes2)

	sameNodes = list(nodes2.intersection(nodes1))

	if len(sameNodes) == 0:
		print('sameNodes empty')

	tmp = data1['elements'] + data2['elements']

	if street3:
		tmp = tmp + data3['elements']

	allNodes = {}
	for node in tmp:
		if node['type'] == 'node':
			allNodes[node['id']] = {'lat': node['lat'], 'lng': node['lon']}

	result = []
	if street3:
		# specifc way
		mergedWays = listConcat()
		for d in data1['elements']:
			if d['type'] == 'way':
				mergedWays.add(d['nodes'])

		ways = mergedWays.get()

		sameNodes2 = list(nodes3.intersection(nodes1))

		if len(sameNodes2) == 0:
			print('sameNodes2 empty')

		for node1 in sameNodes:
			for node2 in sameNodes2:
				for way in ways:
					if node1 in way and node2 in way:
						result.append([allNodes[n] for n in way])
	else:
		# specific point
		for node in data2['elements']:
			if node['type'] == 'node' and node['id'] in sameNodes:
				result.append({'lat': node['lat'], 'lng': node['lon']})

	return result

def extract():
	f = open('data-2014-05-15.19-07.json')
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

	f = open('data-parsed.json', 'w')
	json.dump(found, f, cls=DateTimeEncoder)
	f.close()
	f = open('data-parsed-notfound.json', 'w')
	json.dump(notfound, f, cls=DateTimeEncoder)
	f.close()

if __name__ == "__main__":
	extract()
