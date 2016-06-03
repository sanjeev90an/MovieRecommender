from random import randint

from movie_recommender.data_fetcher.data_collector import TABLES
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.date_utils import get_current_time_str
from movie_recommender.ml.scikit_recommender import get_recommender

class AppController:
    """
        This class acts as interface to REST APIs. The business logic of various apis is implemented in this 
        class.
    """
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.all_movie_uids = self.db_manager.get_all_values_for_attr('movie_info', 'id')
        self.recommender = get_recommender()
        
    def get_next_movie(self):
        movie_uid = self.all_movie_uids[randint(0, len(self.all_movie_uids) - 1)]
        movie_data = self.db_manager.get_row('movie_info', movie_uid)
        return movie_data;
    
    def capture_user_action(self, movie_id, user_id, action_type, rating):
        column_headers = TABLES['visitor_review_history']
        row = (user_id, movie_id, action_type, rating, get_current_time_str());
        self.db_manager.insert_batch('visitor_review_history', column_headers, [row])

    def get_all_visitor_ratings(self, movie_id):
        return self.db_manager.get_all_rows(table_name='visitor_review_history', limit=20)
    
    def clear_all_ratings_for_user(self, user_id):
        self.db_manager.delete_batch('visitor_review_history', (user_id, ''), 'user_id')
    
    def clear_all_ratings_for_session(self, session_id):
        self.db_manager.delete_batch('visitor_review_history', (session_id, ''), 'session_id')
        
    def get_all_ratings_for_user(self, user_id, is_system_user=False):
        all_ratings = []
        if is_system_user in ('True', 'true'):
            all_ratings = self.db_manager.get_all_rows('rating_info', 'user_id=\'' + user_id + '\'', 100)
        else:
            all_ratings = self.db_manager.get_all_rows('visitor_review_history', 'user_id=\'' + user_id + '\'', 100)
        return all_ratings
    
    def get_all_ratings_for_session(self, session_id):
        return self.db_manager.get_all_rows('visitor_review_history', 'session_id=\'' + session_id + '\'', 100)
    
    def get_all_old_ratings(self, movie_id):
        return self.db_manager.get_all_rows('rating_info', 'movie_id=\'' + movie_id + '\'', 10)
    
    def add_user(self, user_id, name, gender, uid):
        existing_user = self.db_manager.get_row('user_info', uid, 'uid')
        if not existing_user:
            row = (uid, user_id, name, gender, get_current_time_str())
            self.db_manager.insert_batch('user_info', TABLES['user_info'], [row])

    def get_recommendations(self, user_id):
        recommended_ratings = self.recommender.get_recommended_ratings_for_visitor(user_id);
        recommended_ratings.sort(key=lambda x:x[1])
        recommended_ratings = recommended_ratings[:10]
        recommended_movie_ids = [row[0] for row in recommended_ratings]
        recommended_movies = []
        if len(recommended_movie_ids) > 0:
            recommended_movies = self.db_manager.get_all_rows('movie_info', 'movie_id in {}'.format(tuple(recommended_movie_ids)))
        return recommended_movies
        
        
app_controller = AppController()
def get_app_controller():
    return app_controller

if __name__ == '__main__':
    app_controller = get_app_controller()
    print app_controller.get_all_ratings_for_user('7', True)
