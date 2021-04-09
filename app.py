# Importing Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setting up Database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Flask Setup
app = Flask(__name__)

# Flask Routes

# Index Route Setup
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# Route for precipitation date and amount
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and amount of precipitation using date as the key
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary for precipitation data
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

# Route for station names
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all station names
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list for station names
    station_list = list(np.ravel(results))

    return jsonify(station_list)

# Route of temperature observations for the previous year of the most active station
# Create our session (link) from Python to the DB
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query date tobs data in the last year of the most active station
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').\
        order_by(Measurement.date.asc()).all()

    session.close()

    # Create a dictionary for tobs data in the last year
    recent_active_station = []
    for station, date, tobs in results:
        active_tobs_dict = {}
        active_tobs_dict["station"] = station
        active_tobs_dict["date"] = date
        active_tobs_dict["tobs"] = tobs
        recent_active_station.append(active_tobs_dict)

    return jsonify(recent_active_station)

# Route for Min, Max, and Average Temperatures from specified start date and on
# Create our session (link) from Python to the DB
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Query data from start date
    newest_data = session.query((func.min(Measurement.tobs)), (func.max(Measurement.tobs)), (func.avg(Measurement.tobs))).\
        filter(Measurement.date >= start).all()

    session.close()
    
    # Create a list for the summary stats from the start date and on
    recent_list = list(np.ravel(newest_data))
    
    return jsonify(recent_list)
                        

# Route for Min, Max, and Average Temperatures using a specified start and an end date.
# Create our session (link) from Python to the DB
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)
    # Query data from start date to end date
    date_range_data = session.query((func.min(Measurement.tobs)), (func.max(Measurement.tobs)), (func.avg(Measurement.tobs))).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Create a list for the summary stats from the start date to the end date
    range_list = list(np.ravel(date_range_data))
      
    return jsonify(range_list)


if __name__ == '__main__':
    app.run(debug=True)


