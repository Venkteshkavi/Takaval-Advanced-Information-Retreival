'use strict';

/* Controllers */

function dashboardController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {
	$('#sidebar-menu .waves-effect').removeClass('active');
	$('#sidebar-menu .d-nav').addClass('active');
	$rootScope.pageTitle = "Dashboard";
	$scope.counts = {};
	$scope.getDashboardData = function(){
		try{
			$http.post("/get/dashboard-data").
			success(function(data)
			{
				$scope.counts = data.counts;
				console.log($scope.counts);
				Morris.Bar({
					element: 'morris-bar-example',
					data: [
						{ y: 'The Hindu', a: $scope.counts.hindu },
						{ y: 'Times of India', a: $scope.counts.times },
						{ y: 'NDTV', a: $scope.counts.ndtv },
						{ y: 'Detik', a: $scope.counts.detik }
					],
					xkey: 'y',
					ykeys: ['a'],
					labels: ['Data Collected Per News Source'],
					hideHover: 'auto',
					resize: true, //defaulted to true
					gridLineColor: '#eeeeee',
					barSizeRatio: 0.2,
					barColors: ['#188ae2']
				});

				Morris.Donut({
					element: 'morris-donut-example',
					data: [
						{label: "Riot", value: $scope.counts.riot},
						{label: "Protest", value: $scope.counts.protest},
						{label: "Violence", value: $scope.counts.violence}
					],
					resize: true, //defaulted to true
					colors: ['#ff8acc', '#5b69bc', "#35b8e0"]
				});

				Morris.Donut({
					element: 'topic',
					data: [
						{label: "Riot", value: $scope.counts.totalRC_pred},
						{label: "Protest", value: $scope.counts.totalPC_pred},
						{label: "Violence", value: $scope.counts.totalVC_pred}
					],
					resize: true, //defaulted to true
					colors: ['#ff8acc', '#5b69bc', "#35b8e0"]
				});

				// Themes begin
				am4core.useTheme(am4themes_animated);
				// Themes end

				// Create map instance
				var chart = am4core.create("chartdiv", am4maps.MapChart);

				// Set map definition
				chart.geodata = am4geodata_continentsLow;

				// Set projection
				chart.projection = new am4maps.projections.Miller();

				chart.homeZoomLevel = 3;
				chart.homeGeoPoint = {
					latitude: 8.0376,
					longitude: 85.4563
				};

				// Create map polygon series
				var polygonSeries = chart.series.push(new am4maps.MapPolygonSeries());
				polygonSeries.exclude = ["antarctica"];
				polygonSeries.useGeodata = true;
				var polygonTemplate = polygonSeries.mapPolygons.template;
				polygonTemplate.tooltipText = "{name}";
				polygonTemplate.fill = am4core.color("#22628e");
				// Create an image series that will hold pie charts
				var pieSeries = chart.series.push(new am4maps.MapImageSeries());
				var pieTemplate = pieSeries.mapImages.template;
				pieTemplate.propertyFields.latitude = "latitude";
				pieTemplate.propertyFields.longitude = "longitude";

				var pieChartTemplate = pieTemplate.createChild(am4charts.PieChart);
				pieChartTemplate.adapter.add("data", function(data, target) {
				if (target.dataItem) {
					return target.dataItem.dataContext.pieData;
				}
				else {
					return [];
				}
				});
				pieChartTemplate.propertyFields.width = "width";
				pieChartTemplate.propertyFields.height = "height";
				pieChartTemplate.horizontalCenter = "middle";
				pieChartTemplate.verticalCenter = "middle";

				var pieTitle = pieChartTemplate.titles.create();
				pieTitle.text = "{title}";

				var pieSeriesTemplate = pieChartTemplate.series.push(new am4charts.PieSeries);
				pieSeriesTemplate.dataFields.category = "category";
				pieSeriesTemplate.dataFields.value = "value";
				pieSeriesTemplate.labels.template.disabled = true;
				pieSeriesTemplate.ticks.template.disabled = true;

				pieSeries.data = [{
					"title": "India",
					"latitude": 20.5937,
					"longitude": 78.9629,
					"width": 75,
					"height": 75,
					"pieData": [{
						"category": "Protest",
						"value": $scope.counts.indiaProtest
					}, {
						"category": "Riot",
						"value": $scope.counts.indiaRiot
					}, {
						"category": "Violence",
						"value": $scope.counts.indiaViolence
					}]
				}, {
					"title": "Indonesia",
					"latitude": 0.7893,
					"longitude": 113.9213,
					"width": 50,
					"height": 50,
					"pieData": [{
					"category": "Protest",
					"value": $scope.counts.indonesiaProtest
					}, {
					"category": "Riot",
					"value": $scope.counts.indonesiaRiot
					}, {
					"category": "Violence",
					"value": $scope.counts.indonesiaViolence
					}]
				}];
			})
			.error(function(data){
				console.warn(data);
			});
		}
		catch(err){
			console.warn(err);
		}
	}
/*
var $donutData = ;
this.createDonutChart('', $donutData, );*/
	$scope.getDashboardData();


			
}


function analyticsController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {
	$('#sidebar-menu .waves-effect').removeClass('active');
	$('#sidebar-menu .a-nav').addClass('active');
	$rootScope.pageTitle = "Analytics";
	
}

function crawlController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {

	
}

function crawlIndexController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {
	$('#sidebar-menu .waves-effect').removeClass('active');
	$('#sidebar-menu .c-nav').addClass('active');
	$rootScope.pageTitle = "Crawled Data";

	// pagination controls
	$scope.currentPage = 1;
	$scope.totalItems = 0;
	$scope.entryLimit = 100; // items per page
	$scope.noOfPages = 15;
	$scope.cdata = [];
	$scope.getCrawlIndexData = function(){
		let skip = ($scope.currentPage - 1) * $scope.entryLimit;
		$http.post("/get/crawl-index", {
			startIndex: skip,
            limit: $scope.entryLimit
		}).
		success(function(response)
		{
			console.log(response)
			$scope.cdata = response.cdata;
			$scope.totalItems = response.totalCount;
		})
		.error(function(response){
			console.warn(response);
		});
	}

	var initiailzing = true;
	// $watch to get next page data
	$scope.$watch('currentPage', function(newPage){
		if (initiailzing) {
			$timeout(function() { initiailzing = false; });
		} else {
			$scope.currentPage = newPage;
			$scope.getCrawlIndexData();
		}
	});

	$scope.getCrawlIndexData();
}



function setCookie(key, value) {
	var expires = new Date();
	expires.setTime(expires.getTime() + (1 * 24 * 60 * 60 * 1000));
	document.cookie = key + '=' + value + ';path=/' + ';expires=' + expires.toUTCString();
};

function getCookie(key) {
	var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
	return keyValue ? keyValue[2] : null;
};
