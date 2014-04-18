BaustellenChemnitz
==================

Extrahiert aktuelle Baustellen von http://chemnitz.de und stellt diese auf einer Karte dar. Entstanden beim OpenDataDay 2014 - **Work in progress**

http://morrisjobke.de/stuff/baustellen-chemnitz/

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
* Bower (npm -g install bower)

Daten extrahieren:

	./scrape.py

Daten mit Geodaten versehen:

	./retrieve.py

Daten anschauen:

	# Abhängigkeiten installieren
	bower install
	# Webserver im aktuellen Verzeichnis starten
	python3 -m http.server
	# Browser öffnen
	xdg-open http://localhost:8000/map.html


ToDo
----

 * Daten visualisieren
 * Daten-Parser zur Wiederverwendbarkeit modularisieren
