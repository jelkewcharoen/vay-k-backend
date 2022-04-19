from flask import Flask, request
import requests
import pymysql
import json
import boto3
import uuid
from flask_cors import CORS
import os
is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:
    api_key = os.environ['GOOGLE_API_KEY']
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret = os.environ['AWS_ACCESS_SECRET']

else:
    with open('keys.txt') as f:
        api_key = f.readline()
        access_key = f.readline()
        access_key = access_key[:-1]
        access_secret = f.readline()
        f.close

bucket_name = 'vaykphotosbucket'

# Connect to S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id = access_key,
    aws_secret_access_key = access_secret
)

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#SQL set up
host = 'vayk-database.c23p9o6zuvtv.us-east-1.rds.amazonaws.com'
user = 'general'
pwd = '[u{;J<r`{ssVb-54'
database = 'VayK'

@app.route("/")
def hello():
    return "Vay-K app"

####################################################################################################
#routes for frontend
####################################################################################################

@app.route("/trips", methods=['GET', 'POST'])
def getTrips():
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    if request.method == 'GET': 
        cursor.execute(''' SELECT title, date(startDate), date(endDate), id FROM trip ''')
        result = cursor.fetchall()
        tripList = []
        for i in  range(len(result)):
            trip = result[i]
            cursor.execute(f''' SELECT city, country FROM non_us_location where tripID = {trip[3]}''')
            trip_result = cursor.fetchall()
            locations = []
            for location in trip_result:
                l = {
                    'state': 'N/A',
                    'city': location[0],
                    'country': location[1] 
                }
                locations.append(l)

            cursor.execute(f''' SELECT state, city, country FROM us_location where tripID = {trip[3]}''')
            trip_result = cursor.fetchall()
            for location in trip_result:
                l = {
                    'state': location[0],
                    'city': location[1],
                    'country': 'USA' 
                }
                locations.append(l)
            tripList.append({
                'id': trip[3],
                'title': trip[0],
                'startDate': None if trip[1] is None else trip[1].strftime("%m/%d/%y"),
                'endDate':  None if trip[2] is None else trip[2].strftime("%m/%d/%y"),
                'locations': locations
            })
        json_result = {"data": tripList}
        cursor.close()
        con.close()
        return json_result
        
    if request.method == 'POST':
        cursor.execute(''' INSERT INTO trip () VALUES ()''')
        con.commit()
        cursor.close()
        con.close()
        return "add trip"
    

@app.route("/trips/<string:trip_id>/itinerary")
def getTrip(trip_id):
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    cursor.execute(f''' SELECT distinct(day) FROM stops WHERE tripID = {trip_id}''')
    result = cursor.fetchall()
    trip = []
    #iterate through each day
    for day in result:
        cursor.execute(f''' SELECT distinct city, stateRegion, postalCode FROM stops WHERE tripID = {trip_id} and day = {day[0]} order by eventNo''')
        cities = cursor.fetchall()
        places = []
        for city in cities:
            cursor.execute(f''' SELECT type, stopName, notes, eventNo FROM stops WHERE tripID = {trip_id} and day = {day[0]} and city = "{city[0]}" and stateRegion = "{city[1]}" and postalCode = "{city[2]}" order by eventNo''')
            stops = cursor.fetchall()
            places.append({
                'city': {
                    'name':city[0],
                    'state':city[1]
                }
            })
            for stop in stops:
                places.append({
                    f"{stop[0]}" : {
                        'name' : stop[1],
                        'details' : stop[2],
                        'eventNo': stop[3]
                    }
                })

        trip.append({
            'day': day[0],
            'places': places
        })
    json_result = {'data': trip}
    cursor.close()
    con.close()
    return json_result

@app.route("/trips/<string:trip_id>/place", methods=['GET', 'POST'])
def addPlace(trip_id):
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    if request.method == 'POST':
        info = request.form
        place_type = info['type']
        day = info['tripDay']
        eventID = info['placeAt']
        placeName = info['place']['name']
        notes = info['place']['details']
        cursor.execute(f''' UPDATE stops SET eventNo = eventNo+1 where eventNo >= {eventID} and tripID = {tripID} and day = {day} order by eventID DESC''')
        cursor.execute(f''' INSERT INTO stops (tripID, day, eventNo, type, notes) VALUES ({tripID}, {day}, {eventNo}, "{place_type}", "{notes}")''')
        con.commit()
    cursor.close()
    con.close()
    return "add stop"

@app.route("/trips/<string:trip_id>/map")
def getTripMap(trip_id):
    url_begin = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    cursor.execute(f''' SELECT stopName, day, eventNo FROM stops where tripID = {trip_id}''')
    trip_result = cursor.fetchall()
    stops = []
    for stop in trip_result:
        name = stop[0].replace(" ", "%20")
        payload={}
        headers = {}
        url = url_begin+"input="+name+"&inputtype=textquery&fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&key="+api_key
        response = json.loads(requests.request("GET", url, headers=headers, data=payload).text)["candidates"][0]
       
        l = {
            'name': response["name"],
            'lat': response["geometry"]["location"]["lat"],
            'lng': response["geometry"]["location"]["lng"],
            'day':stop[1],
            'eventNo':stop[2]
        }
        stops.append(l)
    cursor.close()
    con.close()
    json_result = {'data': stops}
    return json_result

@app.route("/trips/<string:trip_id>/webpages", methods=['GET', 'POST'])
def getTripWebpages(trip_id):
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    if request.method == 'GET':
        cursor.execute(f''' SELECT title, website, description, id FROM extension_info where tripID = {trip_id} and isSaved = false''')
        result = cursor.fetchall()
        webpages = []
        for webpage in result:
            webpages.append({
                'title':webpage[0],
                'url':webpage[1],
                'description':webpage[2],
                'id':webpage[3]
            })
        json_result = {'data': webpages}
        cursor.close()
        con.close()
        return json_result
    if request.method == 'POST' :
        info = request.form
        webpage_id = info['id']
        stop_id = info['stopId']
        cursor.execute(f''' UPDATE SET isSaved = true and eventNo = {stop_id} FROM extension_info where tripID = {trip_id} and id = {webpage_id}''')
        con.commit()
        cursor.close()
        con.close()
        return "Added webpage to stop"
    

@app.route("/trips/<string:trip_id>/photos", methods=['GET', 'POST'])
def getTripPhotos(trip_id):
    con = pymysql.connect(host = host, user = user, password = pwd, database = database)
    cursor = con.cursor()
    if request.method == 'GET':
        cursor.execute(f''' SELECT url, description FROM images where tripID = {trip_id} and isSaved = false''')
        result = cursor.fetchall()
        photos = []
        for photo in result:
            photos.append({
                'url':photo[0],
                'description':photo[1]
            })
        json_result = {'data': photos}
        cursor.close()
        con.close()
        return json_result
    if request.method == 'POST':
        info = request.form
        url = info['url']
        stop_id = info['stopId']
        cursor.execute(f''' UPDATE SET isSaved = true and eventNo = {stop_id} FROM images where tripID = {trip_id} and url = {url}''')
        con.commit()
        cursor.close()
        con.close()
        return "Added photo to stop"

@app.route("/trips/<string:trip_id>/lodges")
def getTripLodges(trip_id):
    json_result = {'data': ''}
    return json_result

@app.route("/trips/<string:trip_id>/flights")
def getTripFlights(trip_id):
    json_result = {'data': ''}
    return json_result

####################################################################################################
#routes for chrome extension
####################################################################################################


@app.route("/add/photo/<string:trip_id>", methods=['GET', 'POST'])
def addPhotoBookmark(trip_id):
    result = {}
    if True:
        image_file = '/Users/jelke/Downloads/Photo.jpeg'  # TODO replace path to pass image file here
        unique_file_name = str(uuid.uuid4()) + ".png"
        s3.upload_file (image_file, bucket_name,unique_file_name, ExtraArgs={'ContentType': "image/jpeg"})

        #Save Url to db
        photo_url = "https://%s.s3.amazonaws.com/%s" % ( bucket_name, unique_file_name)
        #TODO insert statement to DB
        #format insert (tripID = not null, photo_url = not null, description, isSaved = not null, day, eventNo)
        con = pymysql.connect(host = host, user = user, password = pwd, database = database)
        cursor = con.cursor()
        cursor.execute(f''' INSERT INTO images (tripID, url) VALUES ({trip_id}, "{photo_url}")''')
        con.commit()
        cursor.close()
        con.close()
        result.update({
            'data': photo_url
        })
    return result

@app.route("/add/webpage/<string:trip_id>", methods=['GET', 'POST'])
def addWebpageBookmark(trip_id):
    if True:
        #Save Url to db
        title = "webpage"
        webpage_url = "www.something.com"
        #TODO insert statement to DB
        con = pymysql.connect(host = host, user = user, password = pwd, database = database)
        cursor = con.cursor()
        cursor.execute(f''' INSERT INTO extension_info (tripID, title, website) VALUES ({trip_id}, "{title}", "{webpage_url}")''')
        con.commit()
        cursor.close()
        con.close()
    return {'data': webpage_url}

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = True)
