import os
import requests

from movie_recommender.utils.database_manager import get_db_manager


db_manager = get_db_manager()

movie_infos = db_manager.get_all_rows('movie_info', limit=10000)
base_dir = '/home/sanjeev/movierecommender/movie_recommender/app/static/img'

for movie_info in movie_infos:
    file_name = os.path.join(base_dir, movie_info['movie_id'] + '.jpg')
    if not os.path.isfile(file_name):
        f = open(file_name, 'wb')
        try:
            f.write(requests.get(movie_info['poster_url']).content)
        except BaseException:
            print 'error:', movie_info['movie_id']
        finally:
            f.close()
    else:
        print 'skipping:', file_name
