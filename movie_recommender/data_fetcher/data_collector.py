import csv
import itertools
import json
import os
import time
import urllib
import urllib2

from movie_recommender.utils.logging_utils import get_logger
from movie_recommender.utils.time_utils import time_it
from movie_recommender.utils.database_manager import get_db_manager
from movie_recommender.utils.date_utils import millis_to_str


TABLES = {'movie_info':('movie_id', 'title', 'genres', 'imdb_id', 'tmdb_id'),
          'rating_info':('user_id', 'movie_id', 'rating', 'date_added'),
          'tag_info':('user_id', 'movie_id', 'tag', 'date_added'),
          'visitor_review_history':('user_id', 'movie_id', 'action_type', 'rating', 'date_added')
          }

class MovieDataFetcher:
    
    MOVIE_API_URL = "http://api.myapifilms.com/imdb/idIMDB"
    API_TOKEN = "49f60ab4-8b98-47b4-86b0-73eb48ddc441"
    BATCH_SIZE = 400;
    
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


    def insert_movie_info(self):
        movie_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "movies.csv")
        links_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "links.csv")
        row_batch = []
        self.logger.info("Inserting movie info to movie_info table.")
        for movie_row, links_row in itertools.izip(movie_file_reader, links_file_reader):
            movie_id = movie_row[0]
            if int(movie_id) not in self.all_movie_ids:
                row_batch.append(((movie_id, movie_row[1].replace("'", ""), movie_row[2], links_row[1], links_row[2] or '0')))
                self.all_movie_ids.add(movie_id)
                if len(row_batch) + 1 > self.BATCH_SIZE:
                    self.db_manager.insert_batch("movie_info", TABLES['movie_info'], row_batch)
                    row_batch = []
        
        self.db_manager.insert_batch("movie_info", TABLES['movie_info'], row_batch)
        self.logger.info("Finished inserting movie info.")


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

    def insert_tag_info(self):
        row_batch = []
        self.logger.info("Going to insert tags to tag_info table")
        tag_file_reader = self.__get_csv_file_reader(self.movie_data_dir, "tags.csv")
        for tag_row in tag_file_reader:
            movie_id = tag_row[1]
            if int(movie_id) in self.all_movie_ids:
                row_batch.append((tag_row[0], movie_id, tag_row[2], millis_to_str(tag_row[3])))
                if len(row_batch) + 1 > self.BATCH_SIZE:
                    self.db_manager.insert_batch("tag_info", TABLES['tag_info'], row_batch)
        self.db_manager.insert_batch("tag_info", TABLES['tag_info'], row_batch)
        self.logger.info("Finished inserting tags")
        
    @time_it
    def filter_data(self):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        cursor.execute("Select * from movie_info")
        rows = cursor.fetchall()
        movie_ids_to_remove = []
        for row in rows:
            movie_id = row[1]
            movie_title = row[2]
            imdb_id = row[4]
            try:
                year = int(movie_title[movie_title.rfind("(") + 1:movie_title.rfind(")")])
                self.logger
            except ValueError:
                self.logger.error("Failed to find year in movie_title for title:{}, imdb_id:{}".format(movie_title, imdb_id))
                year = self.find_year_from_api(movie_title, imdb_id);
            if year < 2000:
                movie_ids_to_remove.append(movie_id)
        ids_to_remove = tuple(map(int, movie_ids_to_remove))
        if len(ids_to_remove) > 0:
            cursor.execute("delete from movie_info where movie_id in " + str(ids_to_remove))
            connection.commit();
        self.db_manager.release_connection(connection)
        self.all_movie_ids = self.all_movie_ids - set(movie_ids_to_remove)
        self.logger.info("Total movies older than 2000 : {}, new movies:{}".format(len(ids_to_remove), len(self.all_movie_ids)))
    
    def find_year_from_api(self, movie_title, imdb_id):
        params = {'title':movie_title, 'token':self.API_TOKEN}
        data = urllib.urlencode(params)
        time.sleep(1)
        try:
            response = urllib2.urlopen(self.MOVIE_API_URL + "?" + data)
            received_obj = json.loads(response.read())
            release_year = int(received_obj['data']['movies'][0]['releaseDate'])
            self.logger.info("Found release year :{} for movie:{}".format(movie_title, release_year))
            return release_year
        except BaseException:
            self.logger.error("Error while calling the api for movie, title:{}, imdb_id:{}".format(movie_title, imdb_id))
            return -1;
    
if __name__ == '__main__':
    movie_data_fetcher = MovieDataFetcher("/media/sanjeev/Work/ml-latest")
    movie_data_fetcher.insert_movie_info()
    movie_data_fetcher.filter_data()
    movie_data_fetcher.insert_rating_info()
    movie_data_fetcher.insert_tag_info()
