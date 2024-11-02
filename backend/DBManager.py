import datetime

import boto3
import json

from boto3.dynamodb.conditions import Key

from models import MovieMetadata, Comment, Review, User


class DBManager:
    def __init__(self):
        with open("secret.json") as file:
            details = json.load(file)

        self.session = boto3.Session(
            aws_access_key_id=details["1"],
            aws_secret_access_key=details["2"],
            aws_session_token=details["3"],
            region_name="ca-central-1"
        )
        self.s3_resource = self.session.resource('s3')
        self.s3_client = self.session.client('s3')

        self.ddb_client = self.session.client('dynamodb')
        self.ddb_resource = self.session.resource('dynamodb')
        
        self.movie_table = self.ddb_resource.Table('Movies')

    def create_bucket(self, bucket_name="moviebucket1comp306123"):
        try:
            location = {'LocationConstraint': "ca-central-1"}
            self.s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        except Exception as e:
            print(e)
            return False  # Bucket creation failed.
        return True  # Successful bucket creation.

    def delete_bucket(self, bucket_name="moviebucket1comp306123"):
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            bucket.objects.all().delete()
            bucket.delete()
        except Exception as e:
            print(e)

    def list_tables(self):
        return self.ddb_client.list_tables()

    def scan(self, table_name='Movies'):
        return self.ddb_resource.Table(table_name).scan()

    def create_table(self, table_name="Movies"):
        try:
            self.ddb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'movie_id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'movie_id',
                        'AttributeType': 'N'  # Number
                    },
                    {
                        'AttributeName': 'genre',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'rating',
                        'AttributeType': 'N'  # Number
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                },
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'GenreIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'genre',
                                'KeyType': 'HASH'  # Partition key
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'  # Include all attributes
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'RatingIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'rating',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ]
            )
            print("Movies Table Created.")
        except Exception as e:
            print(f"Table creation error: {e}")

    def search_by_genre(self, genre):
        table = self.movie_table
        results = table.query(IndexName='GenreIndex',KeyConditionExpression=Key('Genre').eq(genre))
        return results

    def search_by_rating(self, rating, option):
        results = None
        table = self.movie_table
        if option == 0:
            results = table.query(IndexName='RatingIndex', FilterExpression=Key('rating').gte(rating))
        if option == 1:
            results = table.query(IndexName='RatingIndex', FilterExpression=Key('rating').gt(rating))
        elif option == 2:
            results = table.query(IndexName='RatingIndex', FilterExpression=Key('rating').eq(rating))
        elif option == 3:
            results = table.query(IndexName='RatingIndex', FilterExpression=Key('rating').lt(rating))
        elif option == 4:
            results = table.query(IndexName='RatingIndex', FilterExpression=Key('rating').lte(rating))
        return results

    def list_movies(self, bucket_name="moviebucket1comp306123"):
        try:
            object_list = []
            objects = self.s3_client.list_objects(Bucket=bucket_name)
            if objects.get('Contents'):
                for i in objects.get('Contents'):
                    object_list.append(i)
                return object_list
            else:
                return f"NO ITEMS IN BUCKET {bucket_name}"
        except Exception as e:
            print(e)

    def get_movie(self, key, bucket_name="moviebucket1comp306123"):
        try:
            objects = self.s3_client.list_objects(Bucket=bucket_name)
            if objects.get('Contents'):
                for i in objects.get('Contents'):
                    if i['Key'] == key:
                        return i
                    else:
                        return None
            else:
                return f"NO ITEMS IN BUCKET {bucket_name}"
        except Exception as e:
            print(e)

    def upload_movie(self, movie_path, movie_name=None, bucket_name="moviebucket1comp306123"):
        self.s3_client.upload_file(movie_path, bucket_name, movie_name) # UPLOADS THE FILE NOT THE METADATA

    def upload_metadata(self, metadata):
        self.movie_table.put_item(Item=metadata)
    
    def upload_movie_and_metadata(self, movie_path, bucket_name, metadata:MovieMetadata):
        movie_name = metadata.movie_id
        self.upload_movie(movie_path, movie_name, bucket_name)
        self.upload_metadata(metadata)

    def upload_comment(self, comment):
        response = self.movie_table.update_item(
            Key={
                'movie_id': comment.movie_id
            },
            UpdateExpression="SET comments = list_append(if_not_exists(comments, :empty_list), :new_comment)",
            ExpressionAttributeValues={
                ':new_comment': [comment],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )
        return response

    def get_comment_index(self, movie_id, comment:Comment):
        movie = self.get_movie_metadata(movie_id)
        if movie is not None and movie['comments'] is not None:
            object_list = movie['comments']
            for i in range(len(object_list)):
                if object_list[i]['comment_id'] == comment.comment_id:
                    return i
            else:
                return None

    def edit_comment(self, comment:Comment):
        if ((comment.timestamp - datetime.datetime.now(datetime.UTC)).total_seconds() / 3600) < 24:
            # only if within 24 hrs
            index = self.get_comment_index(comment.movie_id, comment)
            if index:
                output = self.movie_table.update_item(
                    Key={
                        'movie_id': comment.movie_id
                    },
                    UpdateExpression= f"SET comments[{index}].content = :new_content",
                    ExpressionAttributeValues={':new_content': comment.content}
                )
                return output
            else:
                return None

    def delete_comment(self, comment:Comment):
        if ((comment.timestamp - datetime.datetime.now(datetime.UTC)).total_seconds() / 3600) < 24:
            # only if within 24 hrs
            index = self.get_comment_index(comment.movie_id, comment)
            new_list = self.get_movie_metadata(comment.movie_id)['comments']
            new_list.pop(index)
            if index:
                output = self.movie_table.update_item(
                    Key={
                        'movie_id': comment.movie_id
                    },
                    UpdateExpression=f"SET comments = :new_list",
                    ExpressionAttributeValues={':new_list': new_list}
                )
                return output
            else:
                return None

    def add_review(self, review):
        response = self.movie_table.update_item(
            Key={
                'movie_id': review.movie_id
            },
            UpdateExpression="SET reviews = list_append(if_not_exists(reviews, :empty_list), :new_review)",
            ExpressionAttributeValues={
                ':new_review': [review],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )
        return response

    def get_review_index(self, movie_id, review:Review):
        movie = self.get_movie_metadata(movie_id)
        if movie is not None and movie['reviews'] is not None:
            object_list = movie['reviews']
            for i in range(len(object_list)):
                if object_list[i]['review_id'] == review.review_id:
                    return i
            else:
                return None

    def edit_review(self, review:Review):
        index = self.get_review_index(review.movie_id, review)
        average_score = 0.0
        review_list = self.get_movie_metadata(review.movie_id)['reviews']
        average_score += sum(review_list['score']) / len(review_list['score'])
        if index:
            output = self.movie_table.update_item(
                Key={
                    'movie_id': review.movie_id
                },
                UpdateExpression=f"SET reviews[{index}].score = :new_score,"
                                 f"SET rating = :new_rating",
                ExpressionAttributeValues={':new_score': review.score, ':new_rating': average_score}
            )
            return output
        else:
            return None

    def delete_review(self, review:Review):
        index = self.get_review_index(review.movie_id, review)
        new_list = self.get_movie_metadata(review.movie_id)['reviews']
        new_list.pop(index)
        if index:
            output = self.movie_table.update_item(
                Key={
                    'movie_id': review.movie_id
                },
                UpdateExpression=f"SET reviews = :new_list",
                ExpressionAttributeValues={':new_list': new_list}
            )
            return output
        else:
            return None

    def login(self):
        pass

    def logout(self):
        pass

    def get_movie_metadata(self, movie_id):
        return self.movie_table.get_item(Key={'movie_id': movie_id})['Item']