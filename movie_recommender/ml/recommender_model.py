import csv
import numpy
from scipy import sparse
from sklearn.decomposition.truncated_svd import TruncatedSVD

from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.logging_utils import get_logger
from movie_recommender.utils.time_utils import time_it


class Recommender:
    """
    This class builds the recommender by factorizing the data_matrix of user vs movies. It also provide methods
    for fetching movie recommendations for a user.
    """
    
    DATA_MATRIX_FILE = "../../resources/data_matrix_1"
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.logger = get_logger()
        self.movie_ids = self.db_manager.get_all_values_for_attr('movie_info', 'movie_id')
        self.movie_ids.sort()
        self.reverse_movie_id_map = {}
        for i in xrange(len(self.movie_ids)):
            self.reverse_movie_id_map[self.movie_ids[i]] = i
        self.user_ids = self.db_manager.get_all_values_for_attr('rating_info', 'user_id')
        self.training_user_ids, self.test_user_ids = self.__split_training_data(self.user_ids)
    
    """
    Reads data values required build data matrix from db and dumps in a file.
    """
    def read_data_matrix(self):
        self.logger.info("Using training users:{}, test users:{}".format(len(self.training_user_ids), len(self.test_user_ids)))
        reverse_user_id_map = {}
        for i in xrange(len(self.training_user_ids)):
            reverse_user_id_map[self.training_user_ids[i]] = i
        rows = []
        columns = []
        data = []
        for i in xrange(len(self.movie_ids)):
            movie_id = self.movie_ids[i]
            ratings = self.db_manager.get_all_rows('rating_info', 'movie_id = ' + str(movie_id), limit=10000);
            self.logger.info("Fetched ratings for movie_id:{}, ratings:{}".format(movie_id, ratings))
            for row in ratings:
                user_id = row['user_id']
                if user_id in reverse_user_id_map:
                    columns.append(i)
                    rows.append(reverse_user_id_map[user_id])
                    data.append(row['rating'])
        
        self.__write_matrix_data_to_file([columns, rows, data])
    
    def __write_matrix_data_to_file(self, rows):
        f = open(self.DATA_MATRIX_FILE, 'wb')
        wr = csv.writer(f)
        wr.writerows(rows)
        
    def __split_training_data(self, user_ids):
        training_data_size = int(len(user_ids) * .9)
        training_user_ids = user_ids[:training_data_size]
        test_user_ids = user_ids[training_data_size:]
        return training_user_ids, test_user_ids
        
    """
    Builds data matrix from file.
    """
    def build_data_matrix(self):
        file_reader = csv.reader(open(self.DATA_MATRIX_FILE, "rb"), delimiter=',')
        columns = next(file_reader)
        rows = next(file_reader)
        data = next(file_reader)
        data = map(float, data)
        self.data_matrix = sparse.csr_matrix((data, (rows, columns)), shape=(len(self.training_user_ids), len(self.movie_ids)))
            
    """
    Performs SVD decompostion of the data matrix. 
    """
    @time_it
    def factorize_data_matrix(self):
        self.logger.info("Going to factorize matrix")
        svd = TruncatedSVD(n_components=19);
        svd.fit(self.data_matrix)
        self.H = svd.components_
    
    """
    It returns the predicted value of ratings for a user.
    """
    @time_it
    def get_recommended_ratings_for_visitor(self, user_id):
        rating_vector = [0] * len(self.movie_ids)
        ratings_for_user = self.db_manager.get_all_rows('visitor_review_history', 'user_id in {} and action_type in {}'.
                                                        format(str((str(user_id), '')), str(('review', ''))), 10000)
        recommended_movies = []
        if len(ratings_for_user) < 10:
            self.logger.warn("User:{} does not have enough ratings for recommendations".format(user_id))
        else:
            for row in ratings_for_user:
                movie_id = int(row['movie_id'])
                movie_id_index = self.reverse_movie_id_map[movie_id]
                rating_vector[movie_id_index] = float(row['rating'])
            rating_vector = numpy.array(rating_vector)
            result = numpy.dot(self.H, rating_vector)
            result = numpy.dot(numpy.transpose(self.H), result)
            for i in xrange(len(result)):
                recommended_movies.append((self.movie_ids[i], result[i]))
        return recommended_movies
    
recommender = Recommender()
recommender.build_data_matrix()
recommender.factorize_data_matrix()


def get_recommender():
    return recommender


if __name__ == '__main__':
    recommender = Recommender()
    recommender.get_recommended_ratings_for_visitor('sanjeev90an@gmail.com')
#     recommender.read_data_matrix()
#     recommender.build_data_matrix()
#     recommender.factorize_data_matrix()
    
