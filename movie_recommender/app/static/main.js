var currentMovieInfo;

function getData() {
	$('#submitButton').on('click', submitRating)
	$('#checkButton').on('click', checkoutMovie)
	$('#skipButton').on('click', skipMovie)
	getNextMovie();
}

function submitRating(event) {
	url = "saveMovieRating";
	rating = $("input[name=rating]:checked").val();
	successHandler = function(response) {
		getNextMovie();
	}
	userId = getUserId();
	$.ajax({
		url : url,
		type : "POST",
		data : {
			movieId : currentMovieInfo['movie_id'],
			userId : userId,
			rating : rating
		},
		success : successHandler,
		error : emptyHandler
	})
}

function getUserId() {
	// check if user is logged in
	return 'anon';
}

function skipMovie(event) {
	saveUserAction("skipMovie");
}
function checkoutMovie(event) {
	saveUserAction("checkoutMovie");
}

function saveUserAction(url) {
	successHandler = function(response) {
		getNextMovie();
	}
	userId = getUserId();
	$.ajax({
		url : url,
		type : "POST",
		data : {
			movieId : currentMovieInfo['movie_id'],
			userId : userId,
		},
		success : successHandler,
		error : emptyHandler
	})
}

emptyHandler = function() {
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