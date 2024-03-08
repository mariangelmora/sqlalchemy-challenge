from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create engine
engine = create_engine("sqlite:///C:/Users/maria/Desktop/Bootcamp/SQL/CHALLENGE 10/Starter_Code/Resources/hawaii.sqlite")

# Reflect database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    """Homepage"""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()
    stations = [station for station, in results]
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the previous year."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    temperature_data = {date: tobs for date, tobs in results}
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Return TMIN, TAVG, and TMAX for all dates greater than or equal to the start date."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    """Return TMIN, TAVG, and TMAX for the given date range."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)