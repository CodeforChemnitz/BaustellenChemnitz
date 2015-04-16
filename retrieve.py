#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, overpy, pprint, glob, networkx as nx
from scrape import DateTimeEncoder
import matplotlib.pyplot as plt

streetCache = {}
api = overpy.Overpass()

def get_street(street):
	print('\tsearch street: %s'%street)
	if street in streetCache:
		print('\tcache hit')
		return streetCache[street]

	query = '''
		area(3600062594)->.chemnitz;
		(
		    way
			  ["name"="%s"]
			  ["highway"]
			  (area.chemnitz);
		    -
		    (
			way
			  ["highway"="service"]
			  (area.chemnitz);
			way
			  ["highway"="track"]
			  (area.chemnitz);
		    );
		);
		out body;
		>;
		out skel qt;
		'''

	data = api.query(query%street)

	if len(data.get_nodes()) == 0:
		print('street %s couldn\'t be found'%street)
		raise Exception

	print('\t\tnodes: %i, ways: %s'%(len(data.get_nodes()), len(data.get_ways())))

	streetCache[street] = data

	return data

def get_intersection(street1, street2):
	print('\tsearch intersection between: %s and %s'%(street1, street2))
	query = '''
		area(3600062594)->.chemnitz;
		(
			way[highway][name="%s"](area.chemnitz); node(w)->.n1;
			way[highway][name="%s"](area.chemnitz); node(w)->.n2;
		);
		node.n1.n2;
		out meta;
	'''

	try:
		data = api.query(query%(street1, street2))
	except overpy.exception.OverPyException as e:
		print('something bad happened: %s'%e)
		return []

	return data.get_nodes()

def get_street_section(street_name, intersections):
	street = get_street(street_name)

	graph = nx.Graph()

	pos = {}
	count = 0
	for way in street.get_ways():
		print(way.id, ':',[node.id for node in way.get_nodes()])
		previous_id = False
		for node in way.get_nodes():
			# just add edge if previous node is available
			if previous_id != False:
				graph.add_edge(previous_id, node.id)

			# set this node as previous one
			previous_id = node.id

			pos[node.id] = [int(node.lat * 10000000), int(node.lon * 10000000)]

			count += 1

			nx.draw(graph, with_labels=True)
			plt.savefig('test-%i-%i.png'%(way.id,count))
			plt.clf()



	raise SystemExit()


def extract():
	files = glob.glob('data-2*.json')
	files.sort()
	files.reverse()
	if len(files) == 0:
		raise SystemExit

	# extract date
	filename = files[1]
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
				geodata = get_intersection(street1, street2)
			elif entry['parsed']['location']['relation'] == 'between':
				street3 = entry['parsed']['location']['streets'][1]
				print('%2i/%2i process - between - %s %s %s'%(i, len(data), street1, street2, street3))
				geodata1 = get_intersection(street1, street2)
				geodata2 = get_intersection(street1, street3)
				get_street_section(street1, None)
			else:
				print('%2i/%2i skip - %s'%(i, len(data), entry['parsed']['location']['relation']))
				continue

			if len(geodata.get_nodes()) > 0:
				print('\tfound')
				entry['geodata'] = geodata
				found.append(entry)
			else:
				print('\tnot found')
				notfound.append(entry)
		else:
			print('%2i/%2i'%(i, len(data)))

		break

	f = open('data-parsed-' + date + '.json', 'w')
	json.dump(found, f, cls=DateTimeEncoder)
	f.close()
	f = open('data-parsed-' + date + '-notfound.json', 'w')
	json.dump(notfound, f, cls=DateTimeEncoder)
	f.close()

	pprint.pprint(streetCache)

	print('stats: found: %2i/%2i'%(len(found), len(data)))

if __name__ == "__main__":
	extract()
