from flask import Flask, request
import requests
import pymysql
import json
import boto3
import uuid

access_key = 'AKIA3URWUJLY3UCV3S6C'
access_secret = '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'
bucket_name = 'vaykphotosbucket'

# Connect to S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id = access_key,
    aws_secret_access_key = access_secret
)

app = Flask(__name__)

con = pymysql.connect(host = 'vayk-database.c23p9o6zuvtv.us-east-1.rds.amazonaws.com', user = 'general', password = '[u{;J<r`{ssVb-54', database = 'VayK')
cursor = con.cursor()
with open('keys.txt') as f:
    api_key = f.readline()
    f.close

@app.route("/")
def hello():
    return "Vay-K app"

@app.route("/trips", methods=['GET', 'POST'])
def getTrips():
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
        return json_result
    if request.method == 'POST':
        cursor.execute(''' INSERT INTO trip () VALUES ()''')

@app.route("/trips/<string:trip_id>/itinerary")
def getTrip(trip_id):
    cursor.execute(f''' SELECT distinct(day) FROM stops WHERE tripID = {trip_id}''')
    result = cursor.fetchall()
    trip = []
    for day in result:
        cursor.execute(f''' SELECT type, stopName, city, stateRegion, notes FROM stops WHERE tripID = {trip_id} and day = {day[0]}''')
        day_result = cursor.fetchall()
        print(day_result)
        places = []
        for stop in day_result:
            print(stop[0])
            places.append({
                f"{stop[0]}" : {
                    'name' : stop[1],
                    'city' : stop[2],
                    'state' : stop[3],
                    'notes' : stop[4]
                }
            })
        trip.append({
            'day': day[0],
            'places': places
        })
    json_result = {'data': trip}
    return json_result

@app.route("/trips/<string:trip_id>/place", methods=['GET', 'POST'])
def addPlace(trip_id):
    if request.method == 'POST':
        cursor.execute(''' INSERT INTO stops () VALUES ()''')
        return redirect(url_for(f'trips/{trip_id}'))

@app.route("/trips/<string:trip_id>/map")
def getTripMap(trip_id):
    url_begin = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    
    cursor.execute(f''' SELECT stopName, day, eventNo FROM stops where tripID = {trip_id}''')
    trip_result = cursor.fetchall()
    print(trip_result)
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


    json_result = {'data': stops}
    return json_result

@app.route("/trips/<string:trip_id>/webpages")
def getTripWebpages(trip_id):
    json_result = {'data': ''}
    return json_result

@app.route("/trips/<string:trip_id>/photos")
def getTripPhotos(trip_id):
    json_result = {'data': ''}
    return json_result

@app.route("/trips/<string:trip_id>/lodges")
def getTripLodges(trip_id):
    json_result = {'data': ''}
    return json_result

@app.route("/trips/<string:trip_id>/flights")
def getTripFlights(trip_id):
    json_result = {'data': ''}
    return json_result

@app.route("/bookmark/add", methods=['GET', 'POST'])
def addBookmark():
    if True:
        json_result = {'data': ''}
        image_file = '/Users/jelke/Downloads/photo.jpeg'  # TODO replace path to pass image file here
        unique_file_name = str(uuid.uuid4()) + ".png"
        s3.upload_file (image_file, bucket_name,unique_file_name, ExtraArgs={'ContentType': "image/jpeg"})

        #Save Url to db
        photo_url = "https://%s.s3.amazonaws.com/%s" % ( bucket_name, unique_file_name)
        #TODO insert statement to DB
        #format insert (tripID = not null, photo_url = not null, description, isSaved = not null, day, eventNo)
        #cursor.execute(''' INSERT INTO images () VALUES ()''')
        print(photo_url)
    return {}

if __name__ == "__main__":
    app.run(debug = True)