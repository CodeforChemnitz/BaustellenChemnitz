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
        print('cache hit: %s ' % street)
        return streetCache[street]

    data = '<osm-script output="json" timeout="25">' + \
           '<id-query into="area" ref="3600062594" type="area"/>' + \
           '<difference>' + \
           '<query type="way">' + \
           '<has-kv k="name" v="PLACEHOLDER"/>' + \
           '<has-kv k="highway" />' + \
           '<area-query from="area"/>' + \
           '</query>' + \
           '<union>' + \
           '<query type="way">' + \
           '<has-kv k="highway" v="service"/>' + \
           '<area-query from="area"/>' + \
           '</query>' + \
           '<query type="way">' + \
           '<has-kv k="highway" v="track"/>' + \
           '<area-query from="area"/>' + \
           '</query>' + \
           '</union>' + \
           '</difference>' + \
           '<print mode="body"/>' + \
           '<recurse type="down"/>' + \
           '<print mode="skeleton" order="quadtile"/>' + \
           '</osm-script>'

    data = data.replace('PLACEHOLDER', street)

    response = urllib.request.urlopen("http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote_plus(data))
    content = response.read()
    data = json.loads(content.decode('utf8'))

    if len(data['elements']) == 0:
        print('street %s couldn\'t be found' % street)
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
        print('no nodes for street %s' % street)
        raise Exception

    result = {'nodes': set(nodes), 'detailed': detailedNodes, 'ways': ways}

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


def findStreet(street):
    data = searchStreet(street)
    result = []
    for way in data['ways']:
        result.append([data['detailed'][n] for n in way])
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

    print('file used: %s' % filename)

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
                print('%2i/%2i process - intersection - %s %s' % (i, len(data), street1, street2))
                geodata = findIntersection(street1, street2)
            elif entry['parsed']['location']['relation'] == 'between':
                street3 = entry['parsed']['location']['streets'][1]
                print('%2i/%2i process - between - %s %s %s' % (i, len(data), street1, street2, street3))
                geodata = findIntersection(street1, street2, street3)
            else:
                print('%2i/%2i skip - %s' % (i, len(data), entry['parsed']['location']['relation']))
                continue

            if len(geodata) > 0:
                print('\tfound')
                entry['geodata'] = geodata
                found.append(entry)
            else:
                print('\tnot found')
                notfound.append(entry)
        else:
            print('%2i/%2i' % (i, len(data)))

    f = open('data-parsed-' + date + '.json', 'w')
    json.dump(found, f, cls=DateTimeEncoder)
    f.close()
    f = open('data-parsed-' + date + '-notfound.json', 'w')
    json.dump(notfound, f, cls=DateTimeEncoder)
    f.close()

    print('stats: found: %2i/%2i' % (len(found), len(data)))


if __name__ == "__main__":
    extract()
