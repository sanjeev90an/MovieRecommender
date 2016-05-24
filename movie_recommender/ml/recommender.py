from abc import ABCMeta, abstractmethod


class AbstractRecommender(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    
    @abstractmethod
    def get_recommended_ratings_for_visitor(self, user_id):
        pass