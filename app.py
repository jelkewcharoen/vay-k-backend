from flask import Flask, request
import pymysql

app = Flask(__name__)

con = pymysql.connect(host = 'vayk-database.c23p9o6zuvtv.us-east-1.rds.amazonaws.com', user = 'general', password = '[u{;J<r`{ssVb-54', database = 'VayK')
#con = pymysql.connect(host = 'localhost', user = 'root', password = '', database = 'VayK')
cursor = con.cursor()

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

@app.route("/trips/<string:trip_id>/itinerary", methods=['GET', 'POST'])
def getTrip(trip_id):
    if request.method == 'GET':
        cursor.execute(f''' SELECT distinct(day) FROM stops WHERE tripID = {trip_id}''')
        result = cursor.fetchall()
        trip = []
        for day in result:
            cursor.execute(f''' SELECT type, stopName, city, stateRegion, notes FROM stops WHERE tripID = {trip_id} and day = {day[0]}''')
            day_result = cursor.fetchall()
            places = []
            for stop in day_result:
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
    if request.method == 'POST':
        cursor.execute(''' INSERT INTO stops () VALUES ()''')

@app.route("/trips/<string:trip_id>/map")
def getTripMap(trip_id):
    json_result = {'data': ''}
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

if __name__ == "__main__":
    app.run(debug = True)