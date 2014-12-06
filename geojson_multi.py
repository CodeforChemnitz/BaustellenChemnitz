#!/usr/bin/python

import json

result_p = []
result_l = []


def writePoint(node):
    geodata = node['geodata'][0]
    #print("Point", geodata, "\n")
    result_p.append({
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [geodata['lng'], geodata['lat']]
        },
        'properties': {
            'name': getNameFromParsed(node)
        }
    })


def writeLineString(node):
    for path in node['geodata']:
        poslist = []
        for geodata in path:
            #print("LineString", path, "\n")
            if geodata is not None and geodata['lat'] is not None and geodata['lng'] is not None:
                poslist.append([geodata['lng'], geodata['lat']])

        result_l.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': poslist
            },
            'properties': {
                'name': getNameFromParsed(node)
            }
        })

def getNameFromParsed(node):
    return node['parsed']['restriction'] + ": " + ', '.join(node['parsed']['location']['streets'])


f = open('data-parsed-2014-12-05.21-27.json')
data = json.load(f)

nodes = [node for node in data if node['geodata']]

for node in nodes:
    if isinstance(node['geodata'][0], dict):
        writePoint(node)
    else:
        writeLineString(node)

result_p = {
	'type': 'FeatureCollection',
	'features': result_p
}
result_l = {
	'type': 'FeatureCollection',
	'features': result_l
}

f = open('baustellen-lines.geo.json', 'w')
json.dump(result_l, f, indent=4)
f.close()

f = open('baustellen-points.geo.json', 'w')
json.dump(result_p, f, indent=4)
f.close()

