# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
from flask import Flask
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (
        f"<h1>Welcome to the Climate App API</h1><br/>"
        f"<h3>Available routes:</h3>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stats/&lt;start&gt;<br/>"
        f"/api/v1.0/stats/&lt;start&gt;/&lt;end&gt;<br/>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_measurement_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago).all()
    
    session.close()
    
    prcp_data = []
    for date, prcp in prcp_measurement_query:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route('/api/v1.0/stations')
def stations():
    station_query = session.query(Station.station).all()

    session.close()

    station_names = list(np.ravel(station_query))

    return jsonify(station_names)


@app.route('/api/v1.0/tobs')
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs_measurement_query = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281', \
                Measurement.date > year_ago).all()

    session.close()

    tobs_list = list(np.ravel(tobs_measurement_query))

    return jsonify(tobs_list)

@app.route('/api/v1.0/stats/<start>')
@app.route('/api/v1.0/stats/<start>/<end>')
def stats(start, end=dt.date.max.isoformat()):
    sel = [func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]

    tobs_stats = session.query(*sel)\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .first()

    session.close()

    return jsonify(list(tobs_stats))


if __name__ == '__main__':
    app.run(debug=True, port=5001)