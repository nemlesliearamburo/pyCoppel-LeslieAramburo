import requests
import pymongo
import json
import time
from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi


app = Flask(__name__)


BASE_URL = "http://api.tvmaze.com/search/shows?q=query"
@app.route('/getShows', methods=['GET'])
def get_shows():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        return jsonify({'error': response.json()['message']}), response.status_code
    shows = []
    for show in response.json():
        show_data = {
            'id': show['show']['id'],
            'name': show['show']['name'],
            'channel': show['show']['type'],
            'summary': show['show']['summary'],
            'genres': show['show']['genres'],
            'comments': {
                "comment": '',
                "rating": ''
            }
        }
        shows.append(show_data)
    return jsonify({'data': shows}), 200 if shows else 204

@app.route('/getShowById/<show_id>', methods=['GET'])
def getShowById(show_id):
    # connection db
    uri = "mongodb+srv://nemlesliearamburo:fmMstbqVogPy8jM6@cluster0.d7ivrsp.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["Shows"]
    collection = db["shows"]
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        datos = collection.find ( { "id" : int(show_id) } )
        show_find = ""
        for x in datos:
            show_find = x
            show_find = str(show_find)
        if show_find == "":
            BASE_URL2 = "https://api.tvmaze.com/shows"
            response = requests.get(BASE_URL2+"/"+show_id)
            data = response.json()
            show_find = data
            comments = {
                'comments': {
                    "comment": '',
                    "rating": ''
                }
            }
            show_find.update(comments)
            collection.insert_one(data)

        client.close()
    except Exception as e:
        print(e)
    return show_find

@app.route('/getRating/<show_id>', methods=['GET'])
def getRating(show_id):
    # connection db
    uri = "mongodb+srv://nemlesliearamburo:fmMstbqVogPy8jM6@cluster0.d7ivrsp.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["Shows"]
    collection = db["shows"]
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        datos = collection.find ( { "id" : int(show_id) }, { "comments.rating": 1, "_id": 0, "id": 1})
        shows = []
        for x in datos:
            show_data = {
                'id': x['id'],
                'rating_average': x['comments']['rating']
            }
            shows.append(show_data)
        client.close()
    except Exception as e:
        print(e)
    time.sleep(4)
    return show_data

if __name__ == "__main__":
    app.run(debug=True)
    
    