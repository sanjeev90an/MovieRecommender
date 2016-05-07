import csv
from scipy import sparse

from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.logging_utils import get_logger
import nimfa


class Recommender:
    
    DATA_MATRIX_FILE = "../../resources/data_matrix"
    USER_ID_FILE = "../../resources/user_ids_test"
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.logger = get_logger()
        
    def read_data(self):
        user_ids = open(self.USER_ID_FILE).read().split("\n")
        user_ids = map(int, user_ids)
        training_user_ids, test_user_ids = self.split_user_ids(user_ids)
        self.training_user_ids = training_user_ids;
        self.test_user_ids = test_user_ids
        reverse_user_id_map = {}
        for i in xrange(len(training_user_ids)):
            reverse_user_id_map[training_user_ids[i]] = i
        movie_ids = self.db_manager.get_all_values_for_attr('movie_info', 'movie_id')
        rows = []
        columns = []
        data = []
        for i in xrange(500):
            movie_id = movie_ids[i]
            ratings = self.db_manager.get_all_rows('rating_info', 'movie_id = ' + str(movie_id), limit=10000);
            self.logger.info("Fetched ratings for movie_id:{}, ratings:{}".format(movie_id, ratings))
            for row in ratings:
                user_id = int(row['user_id'])
                if user_id in reverse_user_id_map:
                    columns.append(i)
                    rows.append(reverse_user_id_map[user_id])
                    data.append(row['rating'])
        
        self.write_matrix_data_to_file([columns, rows, data])
    
    def write_matrix_data_to_file(self, rows):
        f = open(self.DATA_MATRIX_FILE, 'wb')
        wr = csv.writer(f)
        wr.writerows(rows)
        
    def split_user_ids(self, user_ids):
        training_data_size = int(len(user_ids) * .5)
        training_user_ids = user_ids[:training_data_size]
        test_user_ids = user_ids[training_data_size:]
        return training_user_ids, test_user_ids
        
    def build_data_matrix(self):
        file_reader = csv.reader(open(self.DATA_MATRIX_FILE, "rb"), delimiter=',')
        columns = next(file_reader)
        rows = next(file_reader)
        data = next(file_reader)
        data = map(float, data)
        self.data_matrix = sparse.csr_matrix((data, (rows, columns)), shape=(17900, 500))
            
    def factorize_data_matrix(self):
        self.logger.info("Going to factorize matrix")
        snmf = nimfa.Snmf(self.data_matrix, seed="random_vcol", rank=19, max_iter=30, version='r', eta=1.,
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
        
    
    def get_recommended_ratings(self, user_id):
        pass
    
recommender = Recommender()

def get_recommender():
    return recommender


if __name__ == '__main__':
    recommender = Recommender()
#     Recommender.read_data()
    recommender.build_data_matrix()
    recommender.factorize_data_matrix()
    
