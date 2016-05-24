import csv
import itertools
import json
import os
import urllib
import urllib2

from movie_recommender.utils.logging_utils import get_logger
from movie_recommender.utils.time_utils import time_it
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.date_utils import millis_to_str


TABLES = {'movie_info':('movie_id', 'title', 'genres', 'imdb_id', 'tmdb_id', 'actors', 'awards',
                        'country', 'director', 'imdb_rating', 'imdb_votes', 'language', 'metascore',
                         'plot', 'poster_url', 'rated', 'release_date', 'runtime', 'writer', 'year'),
          'rating_info':('user_id', 'movie_id', 'rating', 'date_added'),
          'tag_info':('user_id', 'movie_id', 'tag', 'date_added'),
          'visitor_review_history':('user_id', 'movie_id', 'action_type', 'rating', 'date_added'),
          'user_info':('uid', 'user_id', 'name', 'gender', 'date_added')
          }

MOVIE_INFO_PROPERTY_MAP = {'imdbRating':'imdb_rating', 'imdbVotes':'imdb_votes', 'Poster':'poster_url', 'Released':'release_date'}

class MovieDataFetcher:
    """
    This class reads, filters and dumps the movie data to db.
    """
    
    MOVIE_API_URL = "http://www.omdbapi.com"
    API_TOKEN = "49f60ab4-8b98-47b4-86b0-73eb48ddc441"
    BATCH_SIZE = 200;
    
    def __init__(self, movie_data_dir):
        self.movie_data_dir = movie_data_dir
        self.db_manager = get_db_manager()
        self.all_movie_ids = set(self.db_manager.get_all_values_for_attr('movie_info', 'movie_id'))
        self.logger = get_logger()
        
    @time_it

    def __get_csv_file_reader(self, folder_name, file_name):
        file_path = os.path.join(folder_name, file_name)
        file_reader = csv.reader(open(file_path, "rb"), delimiter=',')
        next(file_reader)
        return file_reader


    """
    Reads movie and movie link data from files and saves to movie_info table.
    """
    def insert_movie_info(self):
        movie_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "movies.csv")
        links_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "links.csv")
        row_batch = []
        self.logger.info("Inserting movie info to movie_info table.")
        for movie_row, links_row in itertools.izip(movie_file_reader, links_file_reader):
            movie_id = movie_row[0]
            year = self.__get_year_from_title(movie_row[1])
            if int(movie_id) not in self.all_movie_ids and year >= 2000:
                movie_info = self.get_movieinfo_from_api(movie_row[1], links_row[1])
                complete_movie_info = self.__get_complete_movie_info(movie_row, links_row, movie_info)
                try:
                    int(complete_movie_info['year'])
                except ValueError:
                    complete_movie_info['year'] = complete_movie_info['year'][:4]
                if int(complete_movie_info['year']) >= 2000:
                    row = [complete_movie_info[key].replace("'", "") for key in TABLES['movie_info']]
                    row_batch.append(tuple(row))
                    self.all_movie_ids.add(int(movie_id))
                if len(row_batch) + 1 > self.BATCH_SIZE:
                    self.db_manager.insert_batch("movie_info", TABLES['movie_info'], row_batch)
                    row_batch = []
        
        self.db_manager.insert_batch("movie_info", TABLES['movie_info'], row_batch)
        self.logger.info("Finished inserting movie info.")

    def __get_complete_movie_info(self, movie_row, links_row, movie_info):
        row = {'movie_id': movie_row[0], 'title': movie_row[1].replace("'", ""), 'genres': movie_row[2],
                'imdb_id':links_row[1], 'tmdb_id':links_row[2] or '0'}
        for key in movie_info:
            column_name = key.lower()  if key.lower() in TABLES['movie_info'] else MOVIE_INFO_PROPERTY_MAP.get(key, '')
            if column_name:
                row[column_name] = movie_info[key].replace("N/A", '0').encode('utf-8');
        return row

    """
    Reads ratings data from file and dumps to rating_info table. 
    """
    def insert_rating_info(self):
        row_batch = []
        ratings_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "ratings.csv")
        self.logger.info("Going to insert ratings to rating_info table")
        for rating_row in ratings_file_reader:
            movie_id = rating_row[1]
            if int(movie_id) in self.all_movie_ids:
                row_batch.append((rating_row[0], movie_id, rating_row[2], millis_to_str(rating_row[3])))
                if len(row_batch) + 1 > self.BATCH_SIZE:
                    self.db_manager.insert_batch("rating_info", TABLES['rating_info'], row_batch)
                    row_batch = []
        
        self.db_manager.insert_batch("rating_info", TABLES['rating_info'], row_batch)
        self.logger.info("Finished inserting ratings")

    def __get_year_from_title(self, movie_title):
        year = 2000
        try:
            year = int(movie_title[movie_title.rfind("(") + 1:movie_title.rfind(")")])
            self.logger
        except ValueError:
            self.logger.error("Failed to find year in movie_title for title:{}.".format(movie_title))
        return year

    """
    Reads tags data from file and dumps to tag_info table. 
    """
    def insert_tag_info(self):
        row_batch = []
        self.logger.info("Going to insert tags to tag_info table")
        tag_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "tags.csv")
        for tag_row in tag_file_reader:
            movie_id = tag_row[1]
            if int(movie_id) in self.all_movie_ids:
                row_batch.append((tag_row[0], movie_id, tag_row[2].replace("'", ""), millis_to_str(tag_row[3])))
                if len(row_batch) + 1 > self.BATCH_SIZE:
                    self.db_manager.insert_batch("tag_info", TABLES['tag_info'], row_batch)
                    row_batch = []
        self.db_manager.insert_batch("tag_info", TABLES['tag_info'], row_batch)
        self.logger.info("Finished inserting tags")
        
    """
    Calls myapifilms api and gets the release year for a movie.
    """
    def get_movieinfo_from_api(self, movie_title, imdb_id):
        params = {'i':'tt' + imdb_id, 'r':'json'}
        data = urllib.urlencode(params)
#         time.sleep(1)
        movie_info = {}
        try:
            response = urllib2.urlopen(self.MOVIE_API_URL + "?" + data)
            movie_info = json.loads(response.read())
            self.logger.info("Fetched movie info for movie_title :{} and id:{}".format(movie_title, imdb_id))
        except BaseException:
            self.logger.error("Error while calling the api for movie, title:{}, imdb_id:{}".format(movie_title, imdb_id))
        return movie_info
    
if __name__ == '__main__':
    movie_data_fetcher = MovieDataFetcher("/home/sanjeev/Downloads/ml-latest-small")
    movie_data_fetcher.insert_movie_info()
    movie_data_fetcher.insert_rating_info()
    movie_data_fetcher.insert_tag_info()
