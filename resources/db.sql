create database movie_recommender;
\c movie_recommender
create table movie_info (
id BIGSERIAL PRIMARY KEY,
movie_id integer unique, 
title varchar,
genres varchar,
imdb_id varchar,
tmdb_id integer
);

create table rating_info( 
id BIGSERIAL PRIMARY KEY,
movie_id integer, 
user_id varchar,
rating decimal, 
date_added timestamp,
unique(movie_id, user_id)
);


create table tag_info(
id BIGSERIAL PRIMARY KEY,
user_id varchar,
movie_id integer,
date_added timestamp,
tag varchar
);

create table visitor_review_history(
id BIGSERIAL PRIMARY KEY,
user_id varchar,
movie_id integer,
action_type varchar,
rating integer,
date_added timestamp
);

create table user_info(
uid bigint unique,
user_type varchar,
user_id varchar,
name varchar, 
gender varchar,
date_added timestamp,
unique(uid, user_type)
);

create index movie_info_movie_id on movie_info(movie_id);
create index rating_info_movie_id on rating_info(movie_id);
create index rating_info_user_id on rating_info(user_id);
create index tag_info_movie_id on tag_info(movie_id);
create index visitor_review_user_id on visitor_review_history(user_id);

