#Get dependencies
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

print("script running")
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflecting the tables
Base.prepare(autoload_with=engine)

# Saving reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create a session
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start and 'end' date should be in the format YYYYMMDD.</p>"
    )
#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #first to define last 12 months, then get the date and precipitation from data from one year ago
    last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    precipitation = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= last_12_months).all()

    session.close()

#Route to returns json precipitation data with the date as key and the precipitation as the value of a dict
    precipitation_data = {date: prcp for date, prcp in precipitation}
    return jsonify(precipitation_data)


#Stations route
@app.route("/api/v1.0/stations")
def stations():
    query_stations = session.query(Station.station).all()

    session.close()
    #convert to list
    stations = list(np.ravel(query_stations))
    #return json
    return jsonify(stations=stations)

#Route for most active station
@app.route("/api/v1.0/tobs")
def temp_monthly():
    #first get date that is a year away from last date on the data
    last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    query_tobs = session.query(Measurement.tobs).filter(Measurement.station -- \
        'USC00519281').filter(Measurement.date >= last_12_months).all()

    session.close()
    #convert to list after unravelling
    temps = list(np.ravel(query_tobs))
    #return json results
    return jsonify(temps=temps)

#routes (start, start/end)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def start_point(start=None, end=None):
    sel= [func.min(Measurement.tobs),
          func.avg(Measurement.tobs),
          func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%Y%m%d")
        #Calculations for any date greater than out start date above
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()
        
        temps = list(np.ravel(results))
        #return json results
        return jsonify(temps)
    
    #start and stop for temp calculations
    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    #convert to list after unravelling
    temps = list(np.ravel(results))
    
    #return json results
    return jsonify(temps = temps)


if __name__ == '__main__':
    app.run(debug=True)