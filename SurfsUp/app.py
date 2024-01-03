# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)
print(Base.classes.keys())
# Save references to each table
measure = Base.classes.measurement
station_ref = Base.classes.station
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
    """All available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Route containing percipitation analysis:"
        f"/api/v1.0/precipitation<br/>"
        f"Route containing a list of all the stations:"
        f"/api/v1.0/stations<br/>"
        f"Route containing temperature observations from the most active station within the previous year:"
        f"/api/v1.0/tobs<br/>"
        f"Route to see the minimum, maximum and average temperature recorded for any time after a specific date or within a certain time period:"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"start_date and end_date should be replaced with the date you are seeking written in the following format: Day-Month-Year"
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

# Debugging
if __name__ == '__main__':
    app.run(debug=True)

