import os
import uuid
import jwt
import hashlib
import boto3
import datetime
from flask_cors import CORS
from functools import wraps
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, request, jsonify

app = Flask(__name__)
cors = CORS(app)
app.config['SECRET_KEY'] = 'thisissecret'

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
usertable = ddb.Table('datausers')
bookstable = ddb.Table('data')


@app.route('/get_books', methods=['POST'])
# @token_required
def get_books(**kwargs):
    try:
        query = bookstable.query(
            IndexName='title',
            KeyConditionExpression=Key('title').eq(request.form['filtername'])
        )
        if query['Items']:
            page = request.form['start_page']
            size = request.form['page_size']

            if page == '' or page == '0':
                page = 1
            else:
                page = int(page)
            if size == '' or size == '0':
                size = 50
            else:
                size = int(size)
            first_index = size * (page - 1)
            return jsonify(query['Items'][first_index:first_index+size]), 200
        else:
            return jsonify({'message': 'No matches on filter', 'error_code': 'No Match'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/get_book', methods=['GET'])
# @token_required
def get_book(**kwargs):
    try:
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.args.get('bookID'))
        )
        if query['Items']:
            return query['Items'][0], 200
        return jsonify({'message': 'No Matching Id', 'error_code': 'Book not found'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/add_book', methods=['POST'])
# @token_required
def add_book(**kwargs):
    try:
        bookstable.put_item(
            Item={
              "bookID": uuid.uuid4().hex,
              "title": request.form['addtitle'],
              "authors": request.form['addauthor'],
              "average_rating": request.form['addrating'],
              "isbn": request.form['isbn'],
              "language_code": request.form['langcode'],
              "ratings_count": request.form['ratingcount'],
              "price": request.form['price']
            }
        )
        return jsonify({'message': 'added book'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


if __name__ == '__main__':
    app.run(debug=True)
