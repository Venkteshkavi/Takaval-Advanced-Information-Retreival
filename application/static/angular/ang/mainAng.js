'use strict';

angular.module('takaval', ['angularFlaskServices','customFilters','ngRoute','ngSanitize','ui.bootstrap'])
	.run(function($rootScope, $templateCache) {
		 $rootScope.$on('$routeChangeStart', function(event, next, current) {
         if (typeof(current) !== 'undefined'){
             $templateCache.remove(current.templateUrl);
         }
     });

		 $rootScope.navigateOut = function(url) {
        window.location = url;
     };
	})
	.config(['$routeProvider', '$locationProvider', '$interpolateProvider', '$httpProvider', '$sceDelegateProvider',
		function($routeProvider, $locationProvider, $interpolateProvider,$httpProvider,$sceDelegateProvider) {
		$routeProvider
		.when('/dashboard', {
			templateUrl: '/static/partials/dashboard.html',
			controller: dashboardController
		})
		.when('/analytics', {
			templateUrl: '/static/partials/analytics.html',
			controller: analyticsController
		})
		.when('/crawl', {
			templateUrl: '/static/partials/crawl.html',
			controller: crawlController
		})
		.when('/crawl-index', {
			templateUrl: '/static/partials/crawl_index.html',
			controller: crawlIndexController
		})
		.when('/not-found', {
			templateUrl: '/static/partials/not-found.html'
		})
		;
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
		$locationProvider.html5Mode({
		  enabled: true,
		  requireBase: false
		});
		$httpProvider.defaults.headers.get = {};
		$httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
    $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
	}])
	.directive('onFinishRender', function ($timeout) {
	  return {
	      restrict: 'A',
	      link: function (scope, element, attr) {
	          if (scope.$last === true) {
	              $timeout(function () {
	                  scope.$emit(attr.onFinishRender);
	              });
	          }
	      }
	  }
	})
	.directive("jdenticonValue", function() {
    return {
      restrict: "A",
      link: function(scope, el, attrs){
        jdenticon.update(el[0], attrs.jdenticonValue);
      }
    };
  });
