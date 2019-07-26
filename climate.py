import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station 

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return dict of all dates and prcp"""

    # Query all dates and prcp
    prec_results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert into dict
    prec_dict = dict(prec_results)

    return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return list of all stations"""

    # Query all dates and prcp
    station_results = session.query(Station.station).all()

    # Convert into one list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return list of dates and tempatures a year from last data point"""
    # Calculate date 1 year ago from last point
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    twelve_months = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query all dates and tobs
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= twelve_months).all()
    # Convert into list 
    all_tobs = []
    for date, tobs in tobs_data:
        all_tobs.append(date)
        all_tobs.append(tobs)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return JSON of dates and tempatures greater than or equal to inputted start date"""

    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), Measurement.date).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()

    return jsonify(start_data)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    """Return JSON of dates and tempatures between inputted start and end dates"""

    start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), Measurement.date).\
        filter(Measurement.date >= start, Measurement.date <= end).\
        group_by(Measurement.date).all()

    return jsonify(start_end_data)

if __name__ == '__main__':
    app.run(debug=False)
