BaustellenChemnitz
==================

Extrahiert aktuelle Baustellen von http://chemnitz.de und stellt diese auf einer Karte dar. Entstanden beim OpenDataDay 2014 - **Work in progress**

http://codeforchemnitz.de/BaustellenChemnitz/

Was kann es bis jetzt?
----------------------

 * Daten von chemnitz.de extrahieren
 * Daten semantisch parsen
    * Datum (von *Datum* bis *Datum*, ab *Datum*, seit *Datum*, bis (voraussichtlich) *Datum*, etc.)
    * Lokalität (*Straße* zwischen *A* und *B*, *Straße* land-/stadtwärts vor *A*, etc.)

Selbst ausprobieren
-------------------

* Python 3.x
* Python beautifulsoup4 (pip install beautifulsoup4)

Daten extrahieren:

	./scrape.py

Daten mit Geodaten versehen:

	./retrieve.py

Tests laufen lassen:

	cd extractors
	./date.py
	./street.py

ToDo
----

 * Daten visualisieren
 * Daten-Parser zur Wiederverwendbarkeit modularisieren
