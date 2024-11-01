import datetime
from dataclasses import dataclass


@dataclass
class User:
    email: str
    username: str
    password: str
    user_id: int
    timestamp: datetime.datetime

    def __init__(self, email, username, password, user_id):
        self.email = email
        self.username = username
        self.password = password
        self.user_id = user_id
        self.timestamp = datetime.datetime.now(datetime.UTC)


@dataclass
class MovieMetadata:
    movie_id: int
    title: str
    genre: str
    user_id: int
    rating: float
    comments = list
    reviews = list

    def __init__(self, title, genre, movie_id, rating, comments, reviews):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.rating = rating
        self.comments = comments
        self.reviews = reviews


@dataclass
class MovieVideo:
    movie_id: int
    movie: MovieMetadata

    def __init__(self, movie_id, movie):
        self.movie_id = movie_id
        self.movie = movie


@dataclass
class Comment:
    content: str
    movie_id: int
    user_id: int
    timestamp: datetime.datetime

    def __init__(self, content, movie_id, user_id):
        self.content = content
        self.movie_id = movie_id
        self.user_id = user_id
        self.timestamp = datetime.datetime.now(datetime.UTC)


@dataclass
class Review:
    rating: int
    movie_id: int
    user_id: int
    timestamp: datetime.datetime

    def __init__(self, rating, movie_id, user_id):
        self.rating = rating
        self.movie_id = movie_id
        self.user_id = user_id
        self.timestamp = datetime.datetime.now(datetime.UTC)
