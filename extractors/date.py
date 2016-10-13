#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, re, calendar


class DateExtractionException(Exception):
    pass


def extract(dateString):
    """Return an dict with following keys: since, until, note(optional)

    >>> from pprint import pprint
    >>> pprint(extract('10.05.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 5, 10)}
    >>> pprint(extract('am 10.05.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 5, 10)}
    >>> pprint(extract('17.10.2016, 08.00 - 14.00 Uhr'))
    {'notice': '08.00 - 14.00 Uhr',
     'since': datetime.date(2016, 10, 17),
     'until': datetime.date(2016, 10, 17)}

    >>> pprint(extract('von 10.05.2013 bis 15.06.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 6, 15)}
    >>> pprint(extract('ab 10.05.2013 bis 15.06.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 6, 15)}
    >>> pprint(extract('seit 10.05.2013 bis 15.06.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 6, 15)}
    >>> pprint(extract('10.05.2013 - 15.06.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': datetime.date(2013, 6, 15)}

    >>> pprint(extract('ab 10.05.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': None}
    >>> pprint(extract('seit 10.05.2013'))
    {'since': datetime.date(2013, 5, 10), 'until': None}

    >>> pprint(extract('04.07.2016 bis Ende Dezember 2016'))
    {'since': datetime.date(2016, 7, 4), 'until': datetime.date(2016, 12, 31)}
    >>> pprint(extract('seit 04.07.2016 bis Ende September 2016'))
    {'since': datetime.date(2016, 7, 4), 'until': datetime.date(2016, 9, 30)}
    >>> pprint(extract('seit 19.09.2016 (Bauphase 9) Gesamtmaßnahme: 02/2016 bis 07/2018'))
    {'notice': 'seit 19.09.2016 (Bauphase 9) Gesamtmaßnahme: 02/2016 bis 07/2018',
     'since': datetime.date(2016, 9, 19),
     'until': datetime.date(2018, 7, 31)}

    >>> pprint(extract('bis 10.05.2013'))
    {'since': None, 'until': datetime.date(2013, 5, 10)}
    """
    data = {}
    dateRegex = '(\d{1,2})\.(\d{1,2})\.(\d{2,4})'
    specificDate = re.match('^(am)?\s*' + dateRegex + '$', dateString)
    if specificDate:
        tmp = specificDate.groups()
        date = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        data['since'] = date
        data['until'] = date
        return data

    specificDateTime = re.match('^(am)?\s*' + dateRegex + ', (.*)$', dateString)
    if specificDateTime:
        tmp = specificDateTime.groups()
        date = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        data['since'] = date
        data['until'] = date
        data['notice'] = tmp[4]
        return data

    fromToDate = re.match('^(von|ab|seit)?\s*' + dateRegex + '\s*(bis|-)\s*' + dateRegex + ',?\s*(.*)$', dateString)
    if fromToDate:
        tmp = fromToDate.groups()
        sinceDate = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        untilDate = datetime.date(
                int(tmp[7]),
                int(tmp[6]),
                int(tmp[5])
        )
        data['since'] = sinceDate
        data['until'] = untilDate
        return data

    fromDate = re.match('^(ab|seit)?\s*' + dateRegex + '$', dateString)
    if fromDate:
        tmp = fromDate.groups()
        date = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        data['since'] = date
        data['until'] = None
        return data

    untilDate = re.match('^(bis)?\s*' + dateRegex + '$', dateString)
    if untilDate:
        tmp = untilDate.groups()
        date = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        data['since'] = None
        data['until'] = date
        return data

    untilEstimatedDate = re.match('^(seit)?\s*' + dateRegex + '\s*bis voraussichtlich\s*(.*)$', dateString)
    if untilEstimatedDate:
        tmp = untilEstimatedDate.groups()
        date = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )
        data['since'] = date
        data['until'] = None
        data['notice'] = 'bis voraussichtlich ' + tmp[4]
        return data

    months = "Jan|Feb|Mär|Apr|Mai|Jun|Jul|Aug|Sep|Okt|Nov|Dez"

    fromToEndDate = re.match('^(von|ab|seit)?\s*' + dateRegex + '\s*(bis|-)\s*Ende (' + months + ')\w* (\d{4})$', dateString)
    if fromToEndDate:
        tmp = fromToEndDate.groups()
        sinceDate = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )

        year = int(tmp[6])
        monthNumber = months.split('|').index(tmp[5]) + 1

        _, daysInMonth = calendar.monthrange(year, monthNumber)

        untilDate = datetime.date(
                year,
                monthNumber,
                daysInMonth
        )

        data['since'] = sinceDate
        data['until'] = untilDate
        return data



    fromToDate = re.match('^(von|ab|seit)?\s*' + dateRegex + '\s*.*(bis|-)\s*(\d{2})/(\d{4}).*$', dateString)
    if fromToDate:
        tmp = fromToDate.groups()
        sinceDate = datetime.date(
                int(tmp[3]),
                int(tmp[2]),
                int(tmp[1])
        )

        year = int(tmp[6])
        monthNumber = int(tmp[5])

        _, daysInMonth = calendar.monthrange(year, monthNumber)

        untilDate = datetime.date(
                year,
                monthNumber,
                daysInMonth
        )
        data['since'] = sinceDate
        data['until'] = untilDate
        data['notice'] = dateString
        return data

    raise DateExtractionException(dateString)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
