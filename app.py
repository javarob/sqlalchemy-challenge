# dependencies 
import numpy as np
import pandas as pd
import datetime as dt
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# DB Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

# Table References
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create session 
session = Session(engine)

###############################################
# Flask File Name
###############################################
app = Flask(__name__)

###############################################
# Routes
###############################################
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f'<br/>'
        f'Available Routes:<br/>'
        f'<br/>'
        f'*** Prior year rain totals from all stations<br/>'
        f'<a href="http://localhost:5000/api/v1.0/precipitation">  api/v1.0/precipitation</a><br/>'
        f'<br/>'
        f'*** Station numbers and names<br/>'
        f'<a href="http://localhost:5000/api/v1.0/stations">/api/v1.0/stations</a><br/>'
        f'<br/>'
        f'*** Prior year temperatures from all stations<br/>'
        f'<a href="http://localhost:5000/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
        f'<br/>'
        f'*** Provide start date (YYYY-MM-DD), gives: MIN/AVG/MAX temp for all dates <= start date<br/>'
        f'<a href="http://localhost:5000/api/v1.0/2015-05-01">/api/v1.0/start<a/><br/>'
        f'<br/>'
        f'*** Provide end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temp for dates between the start and end<br/>'
        f'<a href="http://localhost:5000/api/v1.0/2013-06-01/2013-06-25">/api/v1.0/start/end</a><br/>'
        
    )
#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain_fall = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# list of date and prcp
    rain_totals = []
    for day in rain_fall:
        row = {}
        row["date"] = day[0]
        row["prcp"] = day[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#######################################################################################
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
#######################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temps for prior year"""
#    * Query dates and temp observations over the last year.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temp_totals = []
    for day in temp:
        row = {}
        row["date"] = day[0]
        row["tobs"] = day[1]
        temp_totals.append(row)

    return jsonify(temp_totals)
#######################################################################################
@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date"""
    year, month, day = map(int, start.split('-'))
    date_start = dt.date(year,month,day)
    # Query for tobs of defined start date
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.date >= date_start).all()
    data = list(np.ravel(results))
    return jsonify(data)

#######################################################################################
@app.route("/api/v1.0/<start>/<end>")
def range_temp(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given range"""
    year, month, day = map(int, start.split('-'))
    date_start = dt.date(year,month,day)
    year2, month2, day2 = map(int, end.split('-'))
    date_end = dt.date(year2,month2,day2)
    # Query for tobs for definied date range
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.date >= date_start).filter(Measurement.date <= date_end).all()
    data = list(np.ravel(results))
    return jsonify(data)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)