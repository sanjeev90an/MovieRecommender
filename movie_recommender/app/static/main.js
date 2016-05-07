var currentMovieInfo;
var loggedInUserInfo;

function getData() {
	$('#submitButton').on('click', submitRating)
	$('#checkButton').on('click', checkoutMovie)
	$('#skipButton').on('click', skipMovie)
	getNextMovie();
}

function getUserId() {
	// check if user is logged in
	if (loggedInUserInfo) {
		return loggedInUserInfo['email'];
	} else {
		return 'anon';
	}
}

function submitRating() {
	rating = $("input[name=rating]:checked").val();
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("saveMovieRating", currentMovieInfo['movie_id'], rating,
			'review', successHandler);
}

function skipMovie() {
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("skipMovie", currentMovieInfo['movie_id'], -1, "skip",
			successHandler);
}
function checkoutMovie() {
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("checkoutMovie", currentMovieInfo['movie_id'], -1,
			"checkout", successHandler);
}

function saveUserAction(url, movieId, rating, actionType, successHandler) {
	userId = getUserId();
	if (userId == 'anon') {
		saveMovieReviewInCookie(movieId, rating, actionType);
	}
	$.ajax({
		url : url,
		type : "POST",
		data : {
			movieId : movieId,
			userId : userId,
			rating : rating
		},
		success : successHandler,
		error : emptyHandler
	})
}

emptyHandler = function() {
}
emptySuccessHandler = function(response) {
}

function getNextMovie() {
	url = "getNextMovie"
	successHandler = function(response) {
		currentMovieInfo = response;
		renderMovieInfo(response);
		getOldRatings(response);
		getVisitorRatings(response);
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "GET",
		success : successHandler,
		error : failureHandler
	})
}

function renderMovieInfo(movieData) {
	$("#movieDetails").html(movieData['title'])
}

function getOldRatings(movieData) {
	movieId = movieData['movie_id'];
	url = "getAllOldRatings"
	successHandler = function(response) {
		renderOldRatings(JSON.parse(response));
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "GET",
		data : {
			movieId : movieId
		},
		success : successHandler,
		error : failureHandler
	})
}

function renderOldRatings(oldRatings) {
	$("#oldRatings").html("");
	$("#oldRatings").append("<h1>Old ratings</h1>");
	if (oldRatings.length > 0) {
		for ( var key in oldRatings) {
			$("#oldRatings").append(
					"<div class=smallcard>" + oldRatings[key]['rating']
							+ " by " + oldRatings[key]['user_id'] + " at "
							+ oldRatings[key]['date_added'] + "</div>")
		}
	} else {
		$("#oldRatings").append("<div class=smallcard> No ratings yet</div>");
	}
}

function getVisitorRatings(movieData) {
	movieId = movieData['movie_id'];
	url = "getAllVisitorRatings"
	successHandler = function(response) {
		renderVisitorRatings(JSON.parse(response));
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "GET",
		data : {
			movieId : movieId
		},
		success : successHandler,
		error : failureHandler
	})
}

function renderVisitorRatings(visitorRatings) {
	$("#visitorRatings").html("");
	$("#visitorRatings").append("<h1>Visitor Ratings</h1>")
	if (visitorRatings.length > 0) {
		for ( var key in visitorRatings) {
			var rating = visitorRatings[key]['rating'];
			var action;
			if (rating > 0) {
				action = rating;
			} else {
				action = visitorRatings[key]['action_type'];
			}
			$("#visitorRatings").append(
					"<div class=smallcard>" + action + " by "
							+ visitorRatings[key]['user_id'] + " at "
							+ visitorRatings[key]['date_added'] + "</div>")
		}
	} else {
		$("#visitorRatings").append(
				"<div class=smallcard> No ratings yet</div>");
	}
}

function handleUserLogin(userInfo) {
	loggedInUserInfo = userInfo;
	document.getElementById('status').innerHTML = 'Logged in as '
			+ userInfo['name'];
	addUserIfNotPresent(userInfo);
	allReviews = getReviewedMoviesFromCookie();
	for ( var key in allReviews) {
		var review = allReviews[key];
		var rating = review['rating'];
		var movieId = review['movieId'];
		switch (allReviews[key]['actionType']) {
		case 'skip':
			saveUserAction("skipMovie", movieId, rating, 'skip',
					emptySuccessHandler);
		case 'checkout':
			saveUserAction("checkoutMovie", movieId, rating, 'checkout',
					emptySuccessHandler);
		case 'review':
			saveUserAction("saveMovieRating", movieId, rating, 'review',
					emptySuccessHandler);
		}
	}
	document.cookie = 'reviewedMovies=[]';
	console.log(allReviews);
}

function addUserIfNotPresent(userInfo) {
	url = "addUser"
	$.ajax({
		url : url,
		type : "POST",
		data : {
			userId : userInfo['email'],
			name : userInfo['name'],
			gender : userInfo['gender'],
			uid : userInfo['id']
		},
		success : emptySuccessHandler,
		error : emptyHandler
	})
}

function getReviewedMoviesFromCookie() {
	var cookies = document.cookie.split(';');
	var reviews;
	for (key in cookies) {
		if (cookies[key].trim().indexOf('reviewedMovies') == 0) {
			reviews = cookies[key].split('=')[1]
			break;
		}
	}
	if (reviews) {
		return JSON.parse(reviews);
	} else {
		return [];
	}
}

function saveMovieReviewInCookie(movieId, rating, actionType) {
	reviews = getReviewedMoviesFromCookie();
	data = {
		'movieId' : movieId,
		'rating' : rating,
		'actionType' : actionType
	}
	reviews.push(data);
	document.cookie = 'reviewedMovies=' + JSON.stringify(reviews);
}

function getRecommendations() {
	var userId = getUserId();
	var successHandler = successHandler = function(response) {
		renderRecommendations(JSON.parse(response));
	}
	if (userId != 'anon') {
		$.ajax({
			url : url,
			type : "GET",
			data : {
				userId : userId,
			},
			success : successHandler,
			error : emptyHandler
		})
	}
}

function renderRecommendations(recommendedMovies) {
	$("#recommendations").html("");
	$("#recommendations").append("<h1>Recommendations</h1>")
	if (recommendedMovies.length > 0) {
		for ( var key in recommendedMovies) {
			$("#recommendations").append(
					"<div class=smallcard>" + recommendedMovies[key]['title']
							+ "</div>")
		}
	} else {
		$("#recommendations").append(
				"<div class=smallcard>No recommendations yet</div>");
	}
}