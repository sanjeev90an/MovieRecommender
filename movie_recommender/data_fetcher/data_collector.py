import csv
import itertools
import os

from movie_recommender.utils.database_manager import DatabaseManager
from movie_recommender.utils.time_utils import time_it


class MovieDataFetcher:
    
    TABLES = {'movie_info':('movie_id', 'title', 'genres', 'imdb_id', 'tmdb_id'),
                  'rating_info':('user_id', 'movie_id', 'rating', 'date_added'),
                  'tag_info':('user_id', 'movie_id', 'tag', 'date_added') 
                  }
    MOVIE_API_URL = "http://api.myapifilms.com"
    API_TOKEN = "10025e36­e895­463b­857e­b3d63e221302"
    
    def __init__(self, movie_data_dir):
        self.movie_data_dir = movie_data_dir
        self.db_manager = DatabaseManager(db_name="movie_recommender")
        
    @time_it

    def __get_csv_file_reader(self, folder_name, file_name):
        file_path = os.path.join(folder_name, file_name)
        file_reader = csv.reader(open(file_path, "rb"), delimiter=',')
        return file_reader

    def insert_data_in_db(self):
        movie_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "movies.csv")
        links_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "links.csv")
        row_batch = []
        for movie_row, links_row in itertools.izip(movie_file_reader, links_file_reader):
            row_batch.append((movie_row[0], movie_row[1], movie_row[2], links_row[1], links_row[2]))
            self.db_manager.insert_batch("movie_info", self.TABLES['movie_info'], row_batch)
        
        ratings_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "ratings.csv")
        for rating_row in ratings_file_reader:
            self.db_manager.insert_batch("rating_info", self.TABLES['rating_info'], tuple(rating_row))
            
        tag_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "tags.csv")
        for tag_row in tag_file_reader:
            self.db_manager.insert_batch("tag_info", self.TABLES['tag_info'], tuple(tag_row))
        
        
    @time_it
    def filter_data(self):
        
        pass


if __name__ == '__main__':
    movie_data_fetcher = MovieDataFetcher("")
    movie_data_fetcher.insert_data_in_db()
    movie_data_fetcher.filter_data()
