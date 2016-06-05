from abc import ABCMeta
import numpy

from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.logging_utils import get_logger
from movie_recommender.utils.time_utils import time_it


class AbstractRecommender(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.db_manager = get_db_manager()
        self.logger = get_logger()
        self.movie_ids = self.db_manager.get_all_values_for_attr('rating_info', 'movie_id')
        self.movie_ids.sort()
        self.reverse_movie_id_map = {}
        self.reverse_movie_id_map = {movie_id:i for i, movie_id in enumerate(self.movie_ids)}
        self.user_ids = self.db_manager.get_all_values_for_attr('rating_info', 'user_id')
        self.user_ids.sort()
        self.reverse_uid_map = {}
        self.reverse_uid_map = {user_id:i for i, user_id in enumerate(self.user_ids)}
    
    
    def build_data_matrix(self):
        connection = self.db_manager.get_connection()
        query = 'select * from rating_info'
        data_matrix = numpy.ones((len(self.user_ids), len(self.movie_ids))) * 2.5
        
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                movie_id, user_id, rating = row[1], row[2], row[3]
                data_matrix[self.reverse_uid_map[user_id], self.reverse_movie_id_map[movie_id]] = rating
        finally:
            self.db_manager.release_connection(connection)
            
        self.data_matrix = data_matrix
        
    def rmse(self):
        self.__rmse = numpy.mean(numpy.square(numpy.subtract(self.data_matrix, numpy.dot(self.W, self.H))))
        self.logger.info("Decomposition rmse:{}".format(self.rmse))
        return self.__rmse
    
    """
    It returns the predicted value of ratings for a user.
    """
    @time_it
    def get_recommended_ratings_for_visitor(self, uid, query_key='user_id'):
        ratings_for_user = self.db_manager.get_all_rows('visitor_review_history', '{} in {} and action_type in {}'.
                                                        format(query_key, str((str(uid), '')), str(('review', ''))), 10000)
        return self.__get_recommended_ratings(ratings_for_user)
    
    @time_it
    def get_recommended_ratings_for_systemuser(self, uid):
        ratings_for_user = self.db_manager.get_all_rows('rating_info', 'user_id in {}'.
                                                        format(str((str(uid), ''))), 10000)
        return self.__get_recommended_ratings(ratings_for_user)
    
    
    def __get_recommended_ratings(self, ratings_for_user):
        rating_vector = numpy.ones((len(self.movie_ids), 1)) * 2.5
        recommended_movies = []
        if len(ratings_for_user) < 10:
            self.logger.warn("User does not have enough ratings for recommendations")
        else:
            for row in ratings_for_user:
                movie_id = int(row['movie_id'])
                movie_id_index = self.reverse_movie_id_map[movie_id]
                rating_vector[movie_id_index] = float(row['rating'])
            result = numpy.dot(self.H, rating_vector)
            result = numpy.dot(numpy.transpose(self.H), result)
            for i in xrange(len(result)):
                recommended_movies.append((self.movie_ids[i], result[i][0]))
        recommended_movies.sort(key=lambda x:x[1], reverse=True)
        return recommended_movies

    
    def factorize_data_matrix(self):
        pass

    
