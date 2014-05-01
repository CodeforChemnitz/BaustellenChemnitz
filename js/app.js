var app = angular.module('RoadWorksChemnitz', ['leaflet-directive']);

app.controller('MainController', [ '$scope', '$timeout', '$http', 'leafletData', function($scope, $timeout, $http, leafletData) {
	angular.extend($scope, {
		defaults: {
			tileLayer: "http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
			tileLayerOptions: {
				attribution: '&copy; Kartendaten: <a href="http://openstreetmap.org/copyright">OpenStreetMap-Mitwirkende</a>. ' +
					'Tiles: <a href="http://hot.openstreetmap.org/">Humanitarian OpenStreetMap Team</a> ' +
					'Baustellen-Daten: <a href="http://www.chemnitz.de/chemnitz/de/aktuelles/baustellenservice/index.itl">Chemnitz</a>'
			}
		},
		center: { lat: 1, lng: 1, zoom: 1 },
		bounds: {
			northEast: {
				lat: 50.871793,
				lng: 12.9739791
			},
			southWest: {
				lat: 50.7631432,
				lng: 12.8240364
			}
		},
		markers: [],
		paths: []
	});

	$http.get('Baustellen.json').then(function(response){
		angular.forEach(response.data, function(value){
			if(value.geodata && value.geodata.length) {
				var message = 'Einschränkung: ' + value.parsed.restriction + '<br />Maßnahme: ' + value.parsed.action + '<br />Zeitraum: ' + value.parsed.date.since + ' bis ' + value.parsed.date.until;
				if(value.parsed.location.relation === 'intersection') {
					angular.forEach(value.geodata, function(geo) {
						$scope.markers.push({
							lat: geo.lat,
							lng: geo.lng,
							message: message
						});
					});
				} else if(value.parsed.location.relation === 'between') {
					angular.forEach(value.geodata, function(geo) {
						$scope.paths.push({
							color: 'red',
							latlngs: geo,
							message: message,
							weight: 2
						});
					});
					/*angular.forEach(value.geodata, function(geo) {
						var polyline = L.polyline(geo, {color: 'red'}).addTo(map)
							.bindPopup(message);
					});*/
				}
			}
		});
	});

	$scope.$on("centerUrlHash", function(event, centerHash) {
		console.log("url", centerHash);
		$location.search({ c: centerHash });
	});

	$scope.expanded = false;

	$scope.toggleExpand = function() {
		$scope.expanded = !$scope.expanded;
		leafletData.getMap().then(function(map){
			// timeout of 5 seconds is needed as the rendering isn't complete before
			$timeout(function(){
				map.invalidateSize(true);
			}, 5);
		});
	};
}]);


/*
var map = L.map('map').fitBounds([[], []]);
L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
	maxZoom: 18
}).addTo(map);

$.getJSON('data-parsed.json', function(data) {
	$.each(data, function(index, value){
		if(value.geodata && value.geodata.length) {
			var message = 'Einschränkung: ' + value.parsed.restriction + '<br />Maßnahme: ' + value.parsed.action + '<br />Zeitraum: ' + value.parsed.date.since + ' bis ' + value.parsed.date.until;
			if(value.parsed.location.relation === 'intersection') {
				$.each(value.geodata, function(index, geo) {
					L.marker([geo.lat, geo.lon]).addTo(map)
						.bindPopup(message);
				});
			} else if(value.parsed.location.relation === 'between') {
				$.each(value.geodata, function(index, geo) {
					var polyline = L.polyline(geo, {color: 'red'}).addTo(map)
						.bindPopup(message);
				});
			}

		}
	});
});*/
