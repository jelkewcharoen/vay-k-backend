from flask import Flask, request
import pymysql

app = Flask(__name__)

con = pymysql.connect(host = 'localhost', user = 'root', password = '', database = 'VayK')
cursor = con.cursor()

@app.route("/")
def hello():
    return "Vay-K app"

@app.route("/trips", methods=['GET', 'POST'])
def getTrips():
    if request.method == 'GET': 
        cursor.execute(''' SELECT trip_name, date(start_date), date(end_date) FROM trip ''')
        result = cursor.fetchall()
        tripList = []
        for i in  range(len(result)):
            trip = result[i]
            cursor.execute(f''' SELECT city, country FROM non_us_destination where trip_name = "{trip[0]}"''')
            trip_result = cursor.fetchall()
            locations = []
            for location in trip_result:
                l = {
                    'state': '',
                    'city': location[0],
                    'country': location[1] 
                }
                locations.append(l)

            cursor.execute(f''' SELECT state, city, country FROM us_destination where trip_name = "{trip[0]}"''')
            trip_result = cursor.fetchall()
            for location in trip_result:
                l = {
                    'state': location[0],
                    'city': location[1],
                    'country': location[2] 
                }
                locations.append(l)
            
            tripList.append({
                'id': i,
                'title': trip[0],
                'startDate': trip[1].strftime("%m/%d/%y"),
                'endDate': trip[2].strftime("%m/%d/%y"),
                'locations': locations
            })
        
        json_result = {"data": tripList}
        return json_result
    if request.method == 'POST':
        cursor.execute(''' INSERT INTO trip () VALUES ()''')

@app.route("/trips/<string:trip_id>/itinerary", methods=['GET', 'POST'])
def getTrip(trip_id):
    if request.method == 'GET':
        #cursor.execute(f''' SELECT distinct(day) FROM stops WHERE trip_id = {trip_id}''')
        cursor.execute(f''' SELECT distinct(day) FROM stops''')
        result = cursor.fetchall()
        trip = []
        for day in result:
            #cursor.execute(f''' SELECT type, stop_name, city, state, notes FROM stops WHERE trip_id = {trip_id}, day = {day}''')
            cursor.execute(f''' SELECT type, stop_name, city, state_region, notes FROM stops WHERE day = {day[0]}''')
            day_result = cursor.fetchall()
            places = []
            print(day_result)
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