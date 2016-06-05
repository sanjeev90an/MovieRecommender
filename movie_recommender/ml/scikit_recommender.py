import numpy
import os
from sklearn.decomposition.nmf import NMF
from sklearn.decomposition.truncated_svd import TruncatedSVD

from movie_recommender.ml.recommender import AbstractRecommender
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.time_utils import time_it


class ScikitRecommender(AbstractRecommender):
    """
    This class builds the scikit_recommender by factorizing the data_matrix of user vs movies. It also provide methods
    for fetching movie recommendations for a user.
    """
    
    """
    Performs SVD decompostion of the data matrix . 
    """
    @time_it
    def factorize_data_matrix(self):
        self.logger.info("Going to factorize matrix")
        DM_W_FILE = '../../resources/scikit_dm_W.npy'
        DM_H_FILE = '../../resources/scikit_dm_H.npy'
        if os.path.isfile(DM_W_FILE) and os.path.isfile(DM_H_FILE):
            self.W = numpy.load(DM_W_FILE)
            self.H = numpy.load(DM_H_FILE)
        else:
            svd = NMF(n_components=25);
            self.W = svd.fit_transform(self.data_matrix)
            self.H = svd.components_
            self.rmse()
            numpy.save(DM_W_FILE, self.W)
            numpy.save(DM_H_FILE, self.H)
        return self.W, self.H
    
    
scikit_recommender = ScikitRecommender()
scikit_recommender.build_data_matrix()
scikit_recommender.factorize_data_matrix()


def get_scikit_recommender():
    return scikit_recommender


if __name__ == '__main__':
    scikit_recommender = get_scikit_recommender()
#     nimfa_recommender = get_nimfa_recommender()
    uid = 567
    recommended_movies = scikit_recommender.get_recommended_ratings_for_systemuser(uid)
#     db_manager = get_db_manager()
#     ratings_for_user = db_manager.get_all_rows('rating_info', 'user_id in {}'.
#                                                         format(str((str(uid), ''))), 10000)
#     movie_rating_d = {movie_rating[0]:movie_rating[1] for movie_rating in recommended_movies}
#     for rating_info in ratings_for_user:
#         movie_id = int(rating_info['movie_id'])
#         rating = rating_info['rating']
#         print "movie_id:{} original rating:{} predicted rating:{}".format(movie_id, rating, movie_rating_d[movie_id])
#         
        
    for movie in recommended_movies[:10]:
        print movie[0]
#     recommended_movies = nimfa_recommender.get_recommended_ratings_for_systemuser(uid)
#     print recommended_movies[:10]
