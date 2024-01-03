# Import dependencies and packages
from statistics import mean
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

# Engine Creation
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Remodel existing database and refrence tables
Base = automap_base()
Base.prepare(autoload_with=engine)
print(Base.classes.keys())
measure = Base.classes.measurement
station_ref = Base.classes.station

# Create a session link
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"Start and end date should be written in the following format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    year_ago = datetime(2017, 8, 23) - timedelta(days=365)
    prcp_results = session.query(measure.date, measure.prcp).filter(measure.date >= year_ago).all()
    session.close()

    prcp_data = {}
    for date, prcp in prcp_results:
        prcp_data[date] = prcp

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
  
    stat_results = session.query(station_ref.name).all()

    session.close()

    all_stations = list(np.ravel(stat_results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago = datetime(2017, 8, 23) - timedelta(days=365)
    tobs_results = session.query(measure.tobs).filter(measure.station == "USC00519281").filter(measure.date >= year_ago).all()

    session.close()
    active_stat = list(np.ravel(tobs_results))
    return jsonify(active_stat)
  
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start = None, end = None):
    session = Session(engine)
    sel = [func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)]
    
    if not end:
        start = datetime.strptime(start, "%d-%m-%Y")
        res = session.query(*sel).\
            filter(measure.date >= start).all()
        session.close()
        s_stat = list(np.ravel(res))
        return jsonify(s_stat)
    
    start = datetime.strptime(start, "%d-%m-%Y")
    end = datetime.strptime(end, "%d-%m-%Y")

    res = session.query(*sel).\
        filter(measure.date >= start).\
        filter(measure.date <= end).all()
    session.close()
    se_stat = list(np.ravel(res))
    return jsonify(se_stat)

# Debug
if __name__ == '__main__':
    app.run(debug=True)

