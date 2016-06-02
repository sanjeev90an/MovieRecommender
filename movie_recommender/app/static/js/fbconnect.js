function statusChangeCallback(response) {
	if (response.status === 'connected') {
		// Logged into your app and Facebook.
		FB.api('/me', 'get', {
			fields : 'id,name,gender,email'
		}, function(response) {
			console.log(response);
			handleUserLogin(response);
		});
	} else {
		// The person is not logged into Facebook, so we're not sure if
		// they are logged into this app or not.
		document.getElementById('status').innerHTML = 'Please log '
				+ 'into Facebook.';
	}
//	FB.Event.subscribe('auth.logout', handleUserLogout);
}

function checkLoginState() {
	FB.getLoginStatus(function(response) {
		statusChangeCallback(response);
	});
}

/* initializes FB connect */
function initFBConnect() {
	window.fbAsyncInit = function() {
		FB.init({
			appId : '121574618250077',
			xfbml : true,
			version : 'v2.5'
		});
		FB.getLoginStatus(function(response) {
			statusChangeCallback(response)
		});
	};


	(function(d, s, id) {
		var js, fjs = d.getElementsByTagName(s)[0];
		if (d.getElementById(id)) {
			return;
		}
		js = d.createElement(s);
		js.id = id;
		js.src = "//connect.facebook.net/en_US/sdk.js";
		fjs.parentNode.insertBefore(js, fjs);
	}(document, 'script', 'facebook-jssdk'));

}

/** * User Login/logout event handling * */

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
	fetchData();
}

/*
 * 1. Clear Session from cookie. 2. Clear user login info.
 * 
 */
function handleUserLogout() {
	console.log('User logged out.')
	removeKeyFromCookie('sessionId');
}
