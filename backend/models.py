import datetime


class User:
    def __init__(self, email, username, password, user_id):
        self.email = email
        self.username = username
        self.password = password
        self.user_id = user_id

class MovieMetadata:
    def __init__(self, title, genre, user_id, movie_id, ):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.user_id = user_id
        self.rating = 0.0
        self.comments = []
        self.reviews = []

class MovieVideo:
    def __init__(self, movie, movie_id):
        self.movie_id = movie_id
        self.movie = movie

class Comment:
    def __init__(self, content, movie_id, user_id):
        self.content = content
        self.movie_id = movie_id
        self.user_id = user_id
        self.timestamp = datetime.datetime.now(datetime.UTC)

class Review:
    def __init__(self, score, movie_id, user_id):
        self.score = score
        self.movie_id = movie_id
        self.user_id = user_id