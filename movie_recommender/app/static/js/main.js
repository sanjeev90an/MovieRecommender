// This contains functions which are used for calling server APIs and taking actions on user actions.

var currentMovieInfo; /* Details about the movie being displayed on the page. */
var loggedInUserInfo; /* Details about the logged user, null otherwise. */
var SESSION_ID;
/* Called on page load to fetch movie info, ratings and recommendations. */
function getData() {
	$('#submitButton').on('click', submitRating)
	$('#checkButton').on('click', checkoutMovie)
	$('#skipButton').on('click', skipMovie)
	$('#clearRatingButton').on('click', clearCurrentUserRatings)
	createSession();
	initFBConnect();
}

function fetchData() {
	getNextMovie();
}

/* Creates a session id for visitor if none exists */
function createSession() {
	var sessionId = getKeyValueFromCookie('sessionId');
	if (!sessionId) {
		SESSION_ID = getUId();
		insertInCookie('sessionId', SESSION_ID);
	} else {
		SESSION_ID = sessionId;
	}
}

// returns the user id if visitor is logged in
function getUserId() {
	var userId;
	if (loggedInUserInfo) {
		userId = loggedInUserInfo['email'];
	}
	return userId;
}

function getSessionId() {
	return SESSION_ID;
}

function isUserLoggedIn() {
	if (loggedInUserInfo) {
		return true;
	} else {
		return false;
	}
}

function getUId() {
	var d = new Date().getTime();
	var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
			function(c) {
				var r = (d + Math.random() * 16) % 16 | 0;
				d = Math.floor(d / 16);
				return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
			});
	return uuid;
}

/* Called when a user submits rating for a movie on website. */
function submitRating() {
	rating = $("input[name=rating]:checked").val();
	if (rating) {
		successHandler = function(response) {
			getNextMovie();
		}
		saveUserAction("saveMovieRating", currentMovieInfo['movie_id'], rating,
				'review', successHandler);
	}
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
	sessionId = getSessionId();
	if (!isUserLoggedIn()) {
		saveMovieReviewInCookie(movieId, rating, actionType);
	}
	$.ajax({
		url : url,
		type : "POST",
		data : {
			movieId : movieId,
			userId : userId,
			rating : rating,
			sessionId : sessionId
		},
		success : successHandler,
		error : emptyHandler
	});
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
		getMyRatings();
		getRecommendations('scikit');
		getRecommendations('nimfa');
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
	$('input[name=rating]').attr('checked', false);
	$("#movieTitle").append(
			'<a href=showMovieRatings?movieId=' + movieData['movie_id'] + '>'
					+ movieData['title'] + '</a>')
	$("#moviePoster").attr('src', movieData['poster_url']);
	$("#movieGenre").html(movieData['genres'])
	$("#movieActors").html(movieData['actors'])
	$("#movieDirector").html(movieData['director'])
	$("#moviePlot").html(movieData['plot'])
	$("#imdbRating").html(movieData['imdb_rating'])
	$("#imdbVotes").html(movieData['imdb_votes'])

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

/* Fetches all ratings for visiting user. */
function getMyRatings() {
	var data;
	if (isUserLoggedIn()) {
		url = 'getRatingsForUser'
		data = {
			userId : getUserId(),
			systemUser : false
		}
	} else {
		url = 'getRatingsForSession'
		data = {
			sessionId : getSessionId()
		}
	}
	successHandler = function(response) {
		renderVisitorRatings(JSON.parse(response));
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "GET",
		data : data,
		success : successHandler,
		error : failureHandler
	})
}

/* Renders visiting user's ratings on page. */
function renderVisitorRatings(visitorRatings) {
	$('#myRatings').html('')
	if (visitorRatings.length > 0) {
		for ( var key in visitorRatings) {
			var rating = visitorRatings[key]['rating'];
			var action;
			if (rating > 0) {
				action = rating;
			} else {
				action = visitorRatings[key]['action_type'];
			}
			$('#myRatings').append('<hr>')
			$("#myRatings").append(
					"<div class=row><div class=col-md-12><div><strong>"
							+ action + "</strong> by "
							+ visitorRatings[key]['user_id']
							+ "<span class=pull-right>"
							+ visitorRatings[key]['date_added']
							+ "</span></div></div></div>")
		}
	} else {
		$('#myRatings').append('<hr>')
		$("#myRatings").append("<div class=text-warning> No ratings yet</div>");
	}
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
	var reviews = getKeyValueFromCookie('reviewedMovies');
	if (reviews) {
		return JSON.parse(reviews);
	} else {
		return [];
	}
}

function getKeyValueFromCookie(keyName) {
	var cookies = document.cookie.split(';');
	var keyValue;
	for (key in cookies) {
		if (cookies[key].trim().indexOf(keyName) == 0) {
			keyValue = cookies[key].split('=')[1]
			break;
		}
	}
	return keyValue;
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
	insertInCookie('reviewedMovies', JSON.stringify(reviews))
}

function removeKeyFromCookie(key) {
	insertInCookie(key, '');
}

function insertInCookie(key, value) {
	document.cookie = key + '=' + value;
}

/* Fetches recommended movies for a user from server. */
function getRecommendations(algo) {
	console.log("Going to fetch recommendations for " + algo)
	var url, data;
	var successHandler = successHandler = function(response) {
		renderRecommendations(algo, JSON.parse(response));
	}
	if (isUserLoggedIn()) {
		url = 'getRecommendationsForUser';
		data = {
			userId : getUserId(),
			algo : algo
		};
	} else {
		url = 'getRecommendationsForSession'
		data = {
			sessionId : getSessionId(),
			algo : algo
		};
	}
	$.ajax({
		url : url,
		type : "GET",
		data : data,
		success : successHandler,
		error : emptyHandler
	})
}
/* Updates the movie recommendations on the page. */
function renderRecommendations(algo, recommendedMovies) {
	var divId = '#' + algo + 'Recommendations'; // #scikitRecommendations or
	// #nimfaRecommendations
	$(divId).html('')
	if (recommendedMovies.length > 0) {
		$(divId).append('<hr>')
		for ( var key in recommendedMovies) {
			$(divId)
					.append(
							'<div class="row"><div class="col-md-12">'
									+ '<img class="img-rounded" width="70" height="100" src="'
									+ recommendedMovies[key]['poster_url']
									+ '" alt=""><strong>'
									+ recommendedMovies[key]['title']
									+ "</strong></div</div>")
		}
	} else {
		$(divId).append('<hr>')
		$(divId).append("<div class=text-warning>No recommendations yet</div>");
	}
}

function clearCurrentUserRatings() {
	if (isUserLoggedIn()) {
		clearRatingsForUser(getUserId())
	} else {
		clearRatingsForSession(getSessionId())
	}
	failureHandler = emptyHandler
	$.ajax({
		url : url,
		type : "POST",
		data : data,
		success : successHandler,
		error : failureHandler
	})
}

function clearRatingsForSession(sessionId) {
	successHandler = function(response) {
		getMyRatings();
	}
	$.ajax({
		url : 'clearRatingsForSession',
		type : "POST",
		data : {
			sessionId : sessionId
		},
		success : successHandler,
		error : emptyHandler
	})
}

function clearRatingsForUser(userId) {
	successHandler = function(response) {
		getMyRatings();
	}
	$.ajax({
		url : 'clearRatingsForUser',
		type : "POST",
		data : {
			userId : userId
		},
		success : successHandler,
		error : emptyHandler
	})
}