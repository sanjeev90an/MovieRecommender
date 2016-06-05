"""
    @author: code directly used from nimfa lib examples.
    
"""

import nimfa
import numpy
import os
from sklearn.decomposition.nmf import NMF
from sklearn.decomposition.truncated_svd import TruncatedSVD

from movie_recommender.ml.recommender import AbstractRecommender


class NimfaRecommender(AbstractRecommender):
    
    def factorize_data_matrix(self):
        """
        Perform SNMF/R factorization on the sparse MovieLens data matrix. 
        
        Return basis and mixture matrices of the fitted factorization model. 
        
        :param V: The MovieLens data matrix. 
        :type V: `numpy.matrix`
        """
        DM_W_FILE = '../../resources/numpy_dm_W.npy'
        DM_H_FILE = '../../resources/numpy_dm_H.npy'
        if os.path.isfile(DM_W_FILE) and os.path.isfile(DM_H_FILE):
            self.W = numpy.load(DM_W_FILE)
            self.H = numpy.load(DM_H_FILE)
        else:
            snmf = nimfa.Snmf(self.data_matrix, seed="random_vcol", rank=25, max_iter=30, version='r', eta=1.,
                              beta=1e-4, i_conv=10, w_min_change=0)
            print("Algorithm: %s\nInitialization: %s\nRank: %d" % (snmf, snmf.seed, snmf.rank))
            fit = snmf()
            sparse_w, sparse_h = fit.fit.sparseness()
            print("""Stats:
                    - iterations: %d
                    - Euclidean distance: %5.3f
                    - Sparseness basis: %5.3f, mixture: %5.3f""" % (fit.fit.n_iter,
                                                                    fit.distance(metric='euclidean'),
                                                                    sparse_w, sparse_h))
            self.W = numpy.asarray(fit.basis())
            self.H = numpy.asarray(fit.coef())
            numpy.save(DM_W_FILE, self.W)
            numpy.save(DM_H_FILE, self.H)
            
        return self.W, self.H

nimfa_recommender = NimfaRecommender()
nimfa_recommender.build_data_matrix()
nimfa_recommender.factorize_data_matrix()
 
def get_nimfa_recommender():
    return nimfa_recommender


def factorize(data_matrix):
    """
    Perform SNMF/R factorization on the sparse MovieLens data matrix. 
    
    Return basis and mixture matrices of the fitted factorization model. 
    
    :param V: The MovieLens data matrix. 
    :type V: `numpy.matrix`
    """
    snmf = nimfa.Snmf(data_matrix, seed="random_vcol", rank=2, max_iter=30, version='r', eta=1.,
                      beta=1e-4, i_conv=10, w_min_change=0)
    print("Algorithm: %s\nInitialization: %s\nRank: %d" % (snmf, snmf.seed, snmf.rank))
    fit = snmf()
    sparse_w, sparse_h = fit.fit.sparseness()
    print("""Stats:
            - iterations: %d
            - Euclidean distance: %5.3f
            - Sparseness basis: %5.3f, mixture: %5.3f""" % (fit.fit.n_iter,
                                                            fit.distance(metric='euclidean'),
                                                            sparse_w, sparse_h))
    W = numpy.asarray(fit.basis())
    H = numpy.asarray(fit.coef())
        
    return W, H

def a():
    data_matrix = numpy.ones((7, 5)) * 2.5
    data_matrix[0, 0] = data_matrix[0, 1] = data_matrix[0, 2] = 1
    data_matrix[1, 0] = data_matrix[1, 1] = data_matrix[1, 2] = 3
    data_matrix[2, 0] = data_matrix[2, 1] = data_matrix[2, 2] = 4
    data_matrix[3, 0] = data_matrix[3, 1] = data_matrix[3, 2] = 5
    data_matrix[4, 3] = data_matrix[4, 4] = 4
    data_matrix[4, 1] = 2
    data_matrix[5, 3] = data_matrix[5, 4] = 5
    data_matrix[6, 3] = data_matrix[6, 4] = 2
    print data_matrix
    W, H = factorize(data_matrix)
    print 'nimfa', numpy.dot(W, H)
    rating_vector = numpy.zeros((5, 1)) * 2.5
    rating_vector[0, 0] = 4
    result = numpy.dot(H, rating_vector)
    result = numpy.dot(numpy.transpose(H), result)
    print result
    svd = NMF(n_components=2);
    W = svd.fit_transform(data_matrix)
    H = svd.components_
    print numpy.dot(W, H)
    rating_vector = numpy.ones((5, 1)) * 2.5
    rating_vector[0, 0] = 4
    result = numpy.dot(H, rating_vector)
    result = numpy.dot(numpy.transpose(H), result)
    
    print result
    print result.max()

if __name__ == '__main__':
    nimfa_recommender = get_nimfa_recommender()
    uid = 567
    recommended_movies = nimfa_recommender.get_recommended_ratings_for_systemuser(uid)
    for movie in recommended_movies[:10]:
        print movie[0]
#     a();
    

