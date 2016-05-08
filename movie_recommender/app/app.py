from flask.app import Flask
from flask.globals import request
from flask.json import jsonify
from flask.templating import render_template
import json

from movie_recommender.app.app_controller import get_app_controller

"""
The REST APIs are defined in this file.
"""

app = Flask(__name__)
app_controller = get_app_controller()

"""
 Called to display movie details on webpage. It returns a random movie from list of movies.
"""
@app.route('/getNextMovie', methods=['GET'])
def get_next_movie():
    return jsonify(app_controller.get_next_movie())


"""
 Called to save a rating submitted by user in the db.
"""
@app.route('/saveMovieRating', methods=['POST'])
def save_movie_rating():
    movie_id = request.form['movieId'].encode('utf-8')
    rating = request.form['rating'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'review', rating)
    return ok_response() 

"""
 Called to save skip action by user in the db.
"""
@app.route('/skipMovie', methods=['POST'])
def skip_movie():
    movie_id = request.form['movieId'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'skip', -1)
    return ok_response()

"""
 Called to save checkout action by user in the db.
"""    
@app.route('/checkoutMovie', methods=['POST'])
def checkout_movie():
    movie_id = request.form['movieId'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'checkout', -1)
    return ok_response()

"""
 Called to fetch all actions taken by website visitors. Currently it returns only 20 
 ratings as pagination is not  implemented in UI.
"""
@app.route('/getAllVisitorRatings', methods=['GET'])
def get_all_visitor_ratings():
    movie_id = request.args.get('movieId').encode('utf-8')
    all_visitor_ratings = app_controller.get_all_visitor_ratings(movie_id)  # 5222
    return json.dumps(all_visitor_ratings), 200, {'ContentType':'application/json'}

"""
 Returns the ratings of a movie from MovieLens dataset.
"""
@app.route('/getAllOldRatings', methods=['GET'])
def get_all_old_ratings():
    movie_id = request.args.get('movieId').encode('utf-8')
    all_old_ratings = app_controller.get_all_old_ratings(movie_id)  # 2471
    return json.dumps(all_old_ratings), 200, {'ContentType':'application/json'}

"""
    Adds a user to system. This is called when a new user logs in with facebook.
"""
@app.route('/addUser', methods=['POST'])
def add_user():
    user_id = request.form['userId'].encode('utf-8')
    name = request.form['name'].encode('utf-8')
    gender = request.form['gender'].encode('utf-8')
    uid = request.form['uid'].encode('utf-8')
    app_controller.add_user(user_id, name, gender, uid)
    return ok_response()

"""
    Returns recommended movies for a user. It returns 10 recommended movies. This function 
    only returns recommendations if the user has rated at least 10 movies.
"""
@app.route('/getRecommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('userId').encode('utf-8')
    recommended_movies = app_controller.get_recommendations(user_id)
    return json.dumps(recommended_movies), 200, {'ContentType':'application/json'}

@app.route('/')
def show_home_page():
    return render_template('index.html')

def ok_response():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run("127.0.0.1", 9090, debug=True)
