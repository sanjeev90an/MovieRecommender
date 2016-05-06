import json
from random import randint

from movie_recommender.data_fetcher.data_collector import TABLES
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.date_utils import get_current_time_str


class AppController:
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.all_movie_uids = self.db_manager.get_all_values_for_attr('movie_info', 'id')
        
    def get_next_movie(self):
        movie_uid = self.all_movie_uids[randint(0, len(self.all_movie_uids) - 1)]
        movie_data = self.db_manager.get_row('movie_info', movie_uid)
        return movie_data;
    
    def capture_user_action(self, movie_id, user_id, action_type, rating):
        column_headers = TABLES['visitor_review_history']
        row = (user_id, movie_id, action_type, rating, get_current_time_str());
        self.db_manager.insert_batch('visitor_review_history', column_headers, [row])

    def get_all_visitor_ratings(self, movie_id):
        return self.db_manager.get_all_rows('visitor_review_history', 'movie_id=\'' + movie_id + '\'', 10)
    
    def get_all_old_ratings(self, movie_id):
        return self.db_manager.get_all_rows('rating_info', 'movie_id=\'' + movie_id + '\'', 10)

app_controller = AppController()
def get_app_controller():
    return app_controller

if __name__ == '__main__':
    app_controller = get_app_controller()
    print app_controller.get_next_movie()
    print get_current_time_str()
    rows = app_controller.get_all_visitor_ratings('147342')
    print json.dumps(rows)