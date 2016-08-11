from random import randint

from movie_recommender.data_fetcher.data_collector import TABLES
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.date_utils import get_current_time_str
from movie_recommender.ml.scikit_recommender import get_scikit_recommender
from movie_recommender.ml.nimfa_recommender import get_nimfa_recommender, \
    nimfa_recommender

class AppController:
    """
        This class acts as interface to REST APIs. The business logic of various apis is implemented in this 
        class.
    """
    
    def __init__(self):
        self.db_manager = get_db_manager()
        genres = self.db_manager.get_all_values_for_attr('movie_info', 'genres')
        self.genres = set()
        for genre in genres:
            self.genres.update(genre.split('|'))
        self.genres = list(self.genres)
        
        self.all_movie_uids = self.db_manager.get_all_values_for_attr('movie_info', 'id')
        movie_infos = self.db_manager.get_all_rows('movie_info', '1=1', limit=10000)
        self.top_movies = {}
        self.other_movies = {}
        for movie_info in movie_infos:
            genres = movie_info['genres'].split('|')
            movie_uid = movie_info['id']
            if float(movie_info['imdb_rating']) > 7.5:
                for genre in genres:
                    if genre in self.top_movies:
                        self.top_movies[genre].append(movie_uid)
                    else:
                        self.top_movies[genre] = []
            else:
                for genre in genres:
                    if genre in self.other_movies:
                        self.other_movies[genre].append(movie_uid)
                    else:
                        self.other_movies[genre] = []
               
        self.movie_info_map = {movie_info['movie_id']:movie_info for movie_info in movie_infos}
        self.all_system_users = self.db_manager.get_all_values_for_attr('rating_info', 'user_id')
        self.scikit_recommender = get_scikit_recommender()
        self.nimfa_recommender = get_nimfa_recommender()
        
    def get_next_movie(self):
        # movie_uid = self.all_movie_uids[randint(0, len(self.all_movie_uids) - 1)]
        if randint(1, 100) > 80:
            genres = self.other_movies.keys()
            genre = genres[randint(0, len(genres) - 1)]
            movies = self.other_movies[genre]
            print 'Other movie type, genre:{}, total movies:{}'.format(genre, len(movies))
        else:
            genres = self.top_movies.keys()
            genre = genres[randint(0, len(genres) - 1)]
            movies = self.top_movies[genre]
            print 'Top movie type, genre:{}, total movies:{}'.format(genre, len(movies))
        movie_id = movies[randint(0, len(movies) - 1)]
        movie_data = self.db_manager.get_row('movie_info', int(movie_id))
        print 'selected movie:{},rating:{}'.format(movie_data['title'], movie_data['imdb_rating'])
        return movie_data;
    
    def capture_user_action(self, movie_id, user_id, session_id, action_type, rating):
        column_headers = TABLES['visitor_review_history']
        row = (user_id, session_id, movie_id, action_type, rating, get_current_time_str());
        self.db_manager.insert_batch('visitor_review_history', column_headers, [row])

    def get_all_visitor_ratings(self, movie_id=''):
        where_clause = '1=1'
        if movie_id:
            where_clause = 'movie_id=\'{}\''.format(movie_id) 
        
        return self.db_manager.get_all_rows(table_name='visitor_review_history', where_clause=where_clause, limit=100, order_by='date_added')
    
    def clear_all_ratings_for_user(self, user_id):
        self.db_manager.delete_batch('visitor_review_history', (user_id, ''), 'user_id')
    
    def clear_all_ratings_for_session(self, session_id):
        self.db_manager.delete_batch('visitor_review_history', (session_id, ''), 'session_id')
        
    def get_all_ratings_for_user(self, user_id, is_system_user=False):
        all_ratings = []
        if is_system_user in ('True', 'true'):
            all_ratings = self.db_manager.get_all_rows('rating_info', 'user_id=\'' + user_id + '\'', 100, order_by='date_added')
        else:
            all_ratings = self.db_manager.get_all_rows('visitor_review_history', 'user_id=\'' + user_id + '\'', 100, order_by='date_added')
        for rating in all_ratings:
            movie_info = self.movie_info_map[rating['movie_id']]
            rating['title'] = movie_info['title']
        return all_ratings
    
    def get_all_ratings_for_session(self, session_id):
        all_ratings = self.db_manager.get_all_rows('visitor_review_history', 'session_id=\'' + session_id + '\'', 100, order_by='date_added')
        for rating in all_ratings:
            movie_info = self.movie_info_map[rating['movie_id']]
            rating['title'] = movie_info['title']
        return all_ratings
    
    def get_all_old_ratings(self, movie_id):
        all_ratings = self.db_manager.get_all_rows('rating_info', 'movie_id=\'' + movie_id + '\'', 100, order_by='date_added')
        for rating in all_ratings:
            movie_info = self.movie_info_map[rating['movie_id']]
            rating['title'] = movie_info['title']
        return all_ratings
    
    def add_user(self, user_id, name, gender, uid):
        existing_user = self.db_manager.get_row('user_info', uid, 'uid')
        if not existing_user:
            row = (uid, user_id, name, gender, get_current_time_str())
            self.db_manager.insert_batch('user_info', TABLES['user_info'], [row])

    def get_recommendations_for_session(self, session_id, algo):
        return self.__get_recommendations(session_id, 'session_id', algo)

    def get_recommendations_for_user(self, user_id, algo):
        return self.__get_recommendations(user_id, 'user_id', algo)

    def __get_recommendations(self, uid, query_key, algo):
        recommender = self.__get_recommender(algo)
        recommended_ratings = recommender.get_recommended_ratings_for_visitor(uid, query_key);
        recommended_ratings = recommended_ratings[:10]
        recommended_movie_ids = [row[0] for row in recommended_ratings]
        recommended_movies = []
        if len(recommended_movie_ids) > 0:
            recommended_movies = self.db_manager.get_all_rows('movie_info', 'movie_id in {}'.format(tuple(recommended_movie_ids)))
        return recommended_movies
    
    def __get_recommender(self, algo):
        if algo == 'scikit':
            return self.scikit_recommender
        else:
            return nimfa_recommender
    
    def get_movie_info(self, movie_id):
        movie_data = self.db_manager.get_row('movie_info', movie_id, uid_column_name='movie_id')
        return movie_data;
    
    def get_recommendations_for_system_user(self):
        uid = self.all_system_users[randint(0, len(self.all_system_users) - 1)]
        scikit_recommendations = self.scikit_recommender.get_recommended_ratings_for_systemuser(uid)
        nimfa_recommendations = self.nimfa_recommender.get_recommended_ratings_for_systemuser(uid)
        all_rating_infos = self.db_manager.get_all_rows('rating_info', 'user_id = \'{}\''.format(uid), limit=10000)
        recommendations = []
        all_rating_infos.sort(key=lambda x:x['rating'], reverse=True)
        movie_ids = {int(rating_info['movie_id']) for rating_info in all_rating_infos}
        
        scikit_recommendations = [recommendation[0] for recommendation in scikit_recommendations if recommendation[0] in movie_ids]
        nimfa_recommendations = [recommendation[0] for recommendation in nimfa_recommendations if recommendation[0] in movie_ids]
        for i, rating_info in enumerate(all_rating_infos):
            movie_id = rating_info['movie_id']
            recommendation = {'title':self.movie_info_map[str(movie_id)]['title'],
                              'nimfa_rating':self.movie_info_map[str(nimfa_recommendations[i])]['title'],
                              'scikit_rating':self.movie_info_map[str(scikit_recommendations[i])]['title'],
                              'real_rating':rating_info['rating']}
            recommendations.append(recommendation)
        return recommendations, uid, self.nimfa_recommender.rmse(), self.scikit_recommender.rmse()
        
app_controller = AppController()
def get_app_controller():
    return app_controller

if __name__ == '__main__':
    app_controller = get_app_controller()
    print app_controller.get_all_ratings_for_user('7', True)
