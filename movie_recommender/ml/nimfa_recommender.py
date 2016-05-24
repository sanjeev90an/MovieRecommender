import nimfa
from os.path import dirname, abspath
from os.path import join

from movie_recommender.ml.recommender import AbstractRecommender
import numpy as np

"""
    @author: code directly used from nimfa lib examples.
    
"""

class NimfaRecommender(AbstractRecommender):
    
    def __init__(self):
        super(self)
    
    def run(self):
        """
        Run SNMF/R on the MovieLens data set.
        
        Factorization is run on `ua.base`, `ua.test` and `ub.base`, `ub.test` data set. This is MovieLens's data set split 
        of the data into training and test set. Both test data sets are disjoint and with exactly 10 ratings per user
        in the test set. 
        """
        for data_set in ['ua', 'ub']:
            V = self.read(data_set)
            W, H = self.factorize(V)
            self.rmse(W, H, data_set)
    
    
    def factorize(self, V):
        """
        Perform SNMF/R factorization on the sparse MovieLens data matrix. 
        
        Return basis and mixture matrices of the fitted factorization model. 
        
        :param V: The MovieLens data matrix. 
        :type V: `numpy.matrix`
        """
        snmf = nimfa.Snmf(V, seed="random_vcol", rank=30, max_iter=30, version='r', eta=1.,
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
        return fit.basis(), fit.coef()
    
    
    def read(self, data_set):
        """
        Read movies' ratings data from MovieLens data set. 
        
        :param data_set: Name of the split data set to be read.
        :type data_set: `str`
        """
        print("Read MovieLens data set")
        fname = join(dirname(dirname(abspath(__file__))), "datasets", "MovieLens", "%s.base" % data_set)
        V = np.ones((943, 1682)) * 2.5
        for line in open(fname):
            u, i, r, _ = list(map(int, line.split()))
            V[u - 1, i - 1] = r
        return V
    
    
    def rmse(self, W, H, data_set):
        """
        Compute the RMSE error rate on MovieLens data set.
        
        :param W: Basis matrix of the fitted factorization model.
        :type W: `numpy.matrix`
        :param H: Mixture matrix of the fitted factorization model.
        :type H: `numpy.matrix`
        :param data_set: Name of the split data set to be read. 
        :type data_set: `str`
        """
        fname = join(dirname(dirname(abspath(__file__))), "datasets", "MovieLens", "%s.test" % data_set)
        rmse = []
        for line in open(fname):
            u, i, r, _ = list(map(int, line.split()))
            sc = max(min((W[u - 1, :] * H[:, i - 1])[0, 0], 5), 1)
            rmse.append((sc - r) ** 2)
        print("RMSE: %5.3f" % np.mean(rmse))
        
        
    def get_recommended_ratings_for_visitor(self, user_id):
        pass
