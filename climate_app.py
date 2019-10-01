import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite" , connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
recentDate = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())
recentDate = list(np.ravel(recentDate))[0]
recentDate = dt.datetime.strptime(recentDate, '%Y-%m-%d')
#recentDate
recentyear = int(dt.datetime.strftime(recentDate, '%Y'))
#recentyear
recentmonth = int(dt.datetime.strftime(recentDate, '%m'))
recentday = int(dt.datetime.strftime(recentDate, '%d'))
prevyear = dt.date(recentyear, recentmonth, recentday) - dt.timedelta(days=365)




@app.route("/")
def welcome():
    """List all available api routes."""
    return (f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
            f"Available Routes:<br/>"
            f" The latest year of preceipitation data:<br/>"
            f"/api/v1.0/precipitaton <br/>"
            f" List of all weather observation stations:<br/>"
            f"/api/v1.0/stations <br/>"
            f" The latest year of temperature data<br/>"
            f"/api/v1.0/tobs <br/>"
            f"List of the minimum temperature, the average temperature, and the max temperature for a given start(i.e.2017-1-1):<br/>"
            f"/api/v1.0/<start> <br/>"
            f"List of the minimum temperature, the average temperature, and the max temperature for a given start and end(i.e.2017-01-01/2017-01-07):<br/>"
            f"/api/v1.0/<start>/<end> <br/>"
    )

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station).all()
    stationsdata = []
    for result in results:
        station_dict ={}
        station_dict['Station'] = result.station
        station_dict["Station Name"] = result.name
        station_dict["Latitude"] = result.latitude
        station_dict["Longitude"] = result.longitude
        station_dict["Elevation"] = result.elevation
        stationsdata.append(station_dict)

    return jsonify({'Data':stationsdata})

@app.route("/api/v1.0/precipitaton")
def precipitaton():
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                .filter(Measurement.date > prevyear)
                .order_by(Measurement.date)
                .all())
               
    precipdata = []
    for result in results:
        precip_dict = {"date":result.date,"precipitaton": result.prcp, "Station": result.station}
        precipdata.append(precip_dict)

    return jsonify(precipdata)

@app.route("/api/v1.0/tobs")
def tobs(): 
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                .filter(Measurement.date > prevyear)
                .order_by(Measurement.date)
                .all())
               
    tobsdata = []
    for result in results:
        tobs_dict = {"date":result.date, "temperature":result.tobs, "Station": result.station}
        tobsdata.append(tobs_dict)

    return jsonify(tobsdata) 
@app.route("/api/v1.0/<start>")
def start_date(start):   
    sel = [Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]   
    results = (session.query(*sel).filter(Measurement.date >= start)\
              .group_by(Measurement.date)\
              .all())
    datedata = []
    for result in results:
        date_dict = {}
        
        date_dict["Date"] = result[0]
        date_dict["Min Temp"] = result[1]
        date_dict["Avg temp"] = result[2]
        date_dict["Max Temp"] = result[3]
        
        datedata.append(date_dict) 
    return jsonify({'Data':datedata})  
@app.route("/api/v1.0/<start>/<end>")
def range_date(start, end): 
    sel = [Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]   
    results = (session.query(*sel).filter(Measurement.date >= start)\
              .filter(Measurement.date <= end)
              .group_by(Measurement.date)\
              .all())   
    rangedata = []
    for result in results:
        range_dict = {}
        
        range_dict["Date"] = result[0]
        range_dict["Min Temp"] = result[1]
        range_dict["Avg temp"] = result[2]
        range_dict["Max Temp"] = result[3]
        
        rangedata.append(range_dict) 
    return jsonify({'Data':rangedata})  






if __name__ == '__main__':
    app.run(debug=True)    

