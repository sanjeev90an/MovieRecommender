from flask.app import Flask
from flask.globals import request
from flask.json import jsonify
from flask.templating import render_template
import json

from movie_recommender.app.app_controller import get_app_controller

app = Flask(__name__)
app_controller = get_app_controller()

@app.route('/getNextMovie', methods=['GET'])
def get_next_movie():
    return jsonify(app_controller.get_next_movie())


@app.route('/saveMovieRating', methods=['POST'])
def save_movie_rating():
    movie_id = request.form['movieId'].encode('utf-8')
    rating = request.form['rating'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'review', rating)
    return ok_response() 

@app.route('/skipMovie', methods=['POST'])
def skip_movie():
    movie_id = request.form['movieId'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'skip', -1)
    return ok_response()
    
@app.route('/checkoutMovie', methods=['POST'])
def checkout_movie():
    movie_id = request.form['movieId'].encode('utf-8')
    user_id = request.form['userId'].encode('utf-8')
    app_controller.capture_user_action(movie_id, user_id, 'checkout', -1)
    return ok_response()

@app.route('/getAllVisitorRatings', methods=['GET'])
def get_all_visitor_ratings():
    movie_id = request.args.get('movieId').encode('utf-8')
    all_visitor_ratings = app_controller.get_all_visitor_ratings(movie_id)  # 5222
    return json.dumps(all_visitor_ratings), 200, {'ContentType':'application/json'}

@app.route('/getAllOldRatings', methods=['GET'])
def get_all_old_ratings():
    movie_id = request.args.get('movieId').encode('utf-8')
    all_old_ratings = app_controller.get_all_old_ratings(movie_id)  # 2471
    return json.dumps(all_old_ratings), 200, {'ContentType':'application/json'}

@app.route('/')
def show_home_page():
    return render_template('index.html')

@app.route('/fb_test')
def fb_test():
    return render_template('fb_test.html')

def ok_response():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run("127.0.0.1", 9090, debug=True)
