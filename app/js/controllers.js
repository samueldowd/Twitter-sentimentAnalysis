var myApp = angular.module('myApp', []);

myApp.controller('MyController', ['$scope', '$http', function($scope, $http) {
  $http.get('js/tweets.json').success(function(data) {
    $scope.tweets = data;  
   });
  $scope.color = function(){
  	if ($(this).text() != 0) {
  		console.log(this);
          $(this).addClass('red');
        }
        else {
        	console.log(this);
          $(this).addClass('green'); 
        }
    }  

}]);
