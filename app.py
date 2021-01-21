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
bookstable = ddb.Table('data2')


@app.route('/get_books', methods=['POST'])
# @token_required
def get_books(**kwargs):
    try:
        # get book by title
        query = bookstable.query(
            IndexName='title',
            KeyConditionExpression=Key('title').eq(request.form['filtername'])
        )
        if query['Items']:
            # getting pagination
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
        # get book by ID
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.args.get('bookID'))
        )
        # check if response is not empty
        if query['Items']:
            return query['Items'][0], 200
        return jsonify({'message': 'No Matching Id', 'error_code': 'Book not found'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/add_book', methods=['POST'])
# @token_required
def add_book(**kwargs):
    try:
        # build book info dict and add to bookstable
        bookstable.put_item(
            Item={
              "bookID": uuid.uuid4().hex,
              "title": request.form['addtitle'],
              "authors": request.form['addauthor'],
              "average_rating": request.form['addrating'],
              "isbn": request.form['addisbn'],
              "language_code": request.form['addlangcode'],
              "ratings_count": request.form['addratingcount'],
              "price": request.form['addprice']
            }
        )
        return jsonify({'message': 'added book'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/update', methods=['POST'])
# @token_required
def update_book(**kwargs):
    try:
        # get book by ID
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.form['updatebookID'])
        )

        if not query['Items']:
            return jsonify({'message': 'No Matching Id', 'error_code': 'Book not found'}), 200

        #build update dict
        updatedict = {
            ":newtitle": request.form['uptitle'] if request.form['uptitle']!='' else query['Items'][0]['title'],
            ":auth": request.form['upauthor'] if request.form['upauthor']!='' else query['Items'][0]['authors'],
            ":rat": request.form['uprating'] if request.form['uprating']!='' else query['Items'][0]['average_rating'],
            ":isbn": request.form['upisbn'] if request.form['upisbn']!='' else query['Items'][0]['isbn'],
            ":lang": request.form['uplangcode'] if request.form['uplangcode']!='' else query['Items'][0]['language_code'],
            ":ratcnt": request.form['upratingcount'] if request.form['upratingcount']!='' else query['Items'][0]['ratings_count'],
            ":price": request.form['upprice'] if request.form['upprice']!='' else query['Items'][0]['price']
        }

        # update item
        bookstable.update_item(
            Key={
                'bookID': request.form['updatebookID']
            },
            UpdateExpression='SET authors=:auth, average_rating=:rat, isbn=:isbn, language_code=:lang, price=:price, '
                             'ratings_count=:ratcnt, title=:newtitle',
            ExpressionAttributeValues=updatedict
        )

        return jsonify({'message': 'updated book'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500





if __name__ == '__main__':
    app.run()
