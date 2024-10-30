from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import boto3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash


dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
ssm = boto3.client('ssm')


def get_parameter(param_name):
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response['Parameter']['Value']


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = get_parameter('/movie-app/db-connection')
app.config['SECRET_KEY'] = get_parameter('/movie-app/secret-key')
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


movie_table = dynamodb.Table('Movies')
comment_table = dynamodb.Table('Comments')


def create_dynamodb_tables():
    movie_table = dynamodb.create_table(
        TableName='Movies',
        KeySchema=[
            {'AttributeName': 'movie_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'movie_id', 'AttributeType': 'S'},
            {'AttributeName': 'rating', 'AttributeType': 'N'},
            {'AttributeName': 'genre', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'RatingIndex',
                'KeySchema': [
                    {'AttributeName': 'rating', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'GenreIndex',
                'KeySchema': [
                    {'AttributeName': 'genre', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    comment_table = dynamodb.create_table(
        TableName='Comments',
        KeySchema=[
            {'AttributeName': 'comment_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'comment_id', 'AttributeType': 'S'},
            {'AttributeName': 'movie_id', 'AttributeType': 'S'},
            {'AttributeName': 'user_id', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'MovieIndex',
                'KeySchema': [
                    {'AttributeName': 'movie_id', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'UserIndex',
                'KeySchema': [
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'error': 'Invalid credentials'}), 401


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
