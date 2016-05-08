// This contains functions which are used for calling server APIs and taking actions on user actions.

var currentMovieInfo; /* Details about the movie being displayed on the page. */
var loggedInUserInfo; /* Details about the logged user, null otherwise. */

/* Called on page load to fetch movie info, ratings and recommendations. */
function getData() {
	$('#submitButton').on('click', submitRating)
	$('#checkButton').on('click', checkoutMovie)
	$('#skipButton').on('click', skipMovie)
	getNextMovie();
}

// check if user is logged in
function getUserId() {
	if (loggedInUserInfo) {
		return loggedInUserInfo['email'];
	} else {
		return 'anon';
	}
}

/* Called when a user submits rating for a movie on website. */
function submitRating() {
	rating = $("input[name=rating]:checked").val();
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("saveMovieRating", currentMovieInfo['movie_id'], rating,
			'review', successHandler);
}

/* Called when user click on Skip movie. */
function skipMovie() {
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("skipMovie", currentMovieInfo['movie_id'], -1, "skip",
			successHandler);
}

/* Called when user clicks on checkout movie. */
function checkoutMovie() {
	successHandler = function(response) {
		getNextMovie();
	}
	saveUserAction("checkoutMovie", currentMovieInfo['movie_id'], -1,
			"checkout", successHandler);
}

/*
 * Save the user action in db by calling an API and also saving the action in
 * cookie if user is not logged in.
 */
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

/* Fetches next random movie title from server. */
function getNextMovie() {
	url = "getNextMovie"
	successHandler = function(response) {
		currentMovieInfo = response;
		renderMovieInfo(response);
		getOldRatings(response);
		getVisitorRatings(response);
		getRecommendations();
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "GET",
		success : successHandler,
		error : failureHandler
	})
}

/* Updates ui components with fetched movie data. */
function renderMovieInfo(movieData) {
	$("#movieDetails").html(movieData['title'])
	$("#movieGenre").html(movieData['genres'])
}

/* Fetches ratings from MovieLens dataset by calling API. */
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

/* Renders the old ratings on page. */
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

/* Fetches the actions taken by website visitors from server. */
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

/* Renders visitor ratings on page. */
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

/*
 * Called when a user logs in using facebook or a logged in user visits the page
 * again. A new user is created on server if the user logs in for first time.
 * All reviewed, skipped movies of the user are fetched from cookies and saved
 * on the server. Cookies are flushed after saving on server.
 */
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
	getRecommendations(); // if user login event is received after execution
	// of loadData, the recommendations will not be
	// fetched.
}

/* Adds a user on server by calling the api. */
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

/* Returns the movies reviewed by anonymous user which are saved in the cookies. */
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

/*
 * Saves a new skipped, reviewed, checkedout movie in the cookies if user is not
 * logged in.
 */
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

/* Fetches recommended movies for a user from server. */
function getRecommendations() {
	console.log("Going to fetch recommendations")
	var userId = getUserId();
	var url = "getRecommendations"
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
/* Updates the movie recommendations on the page. */
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