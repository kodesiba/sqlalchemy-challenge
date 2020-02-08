# import dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

# setup engine and session
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# setup flask
app = Flask(__name__)

# app routes
@app.route("/")
def home():
    return (
        f"Climate App<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"For the following endpoints, dates must be in YYYY-MM-DD format<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # get database query and return
    precipdict = {}
    response = session.query(Measurement.date,Measurement.prcp).all()
    for record in response:
        recdict = {record.date: record.prcp}
        precipdict.update(recdict)
    session.close()
    return jsonify(precipdict)

@app.route("/api/v1.0/stations")
def stations():
    # get database query and return
    stationdict = {}
    response = session.query(Station.station, Station.name).all()
    for record in response:
        recdict = {record.station: record.name}
        stationdict.update(recdict)
    session.close()
    return jsonify(stationdict)

@app.route("/api/v1.0/tobs")
def tobs():
    tempdict = {}
    # get latest date
    latestdate = session.query(func.max(Measurement.date)).first()
    for date in latestdate:
        daten = dt.datetime.strptime(date,'%Y-%m-%d').date()
    # find what one year before the latest date is
    oneyearbefore = daten - dt.timedelta(days=365)
    # query data for the data from the last year
    response = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= oneyearbefore).all()
    for record in response:
        recdict = {record.date: record.tobs}
        tempdict.update(recdict)
    session.close()
    return jsonify(tempdict)

@app.route("/api/v1.0/<start>")
def tstart(start):
    # check date format for start date
    try:
        dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return (f"Incorrect start date format, should be YYYY-MM-DD<br/>"
                f"If you are not looking for a dated endpoint, check your spelling"), 404
    # get database query and return
    response = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).first()
    respdict = {'TMIN':response[0],
                'TAVG':response[1],
                'TMAX':response[2]}
    session.close()
    return jsonify(respdict)

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):    
    # check date format for start date
    try:
        dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return (f"Incorrect start date format, should be YYYY-MM-DD<br/>"
                f"If you are not looking for a dated endpoint, check your spelling"), 404

    # check date format for end date
    try:
        dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return (f"Incorrect end date format, should be YYYY-MM-DD<br/>"
                f"If you are not looking for a dated endpoint, check your spelling"), 404
    # get database query and return
    response = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).first()
    respdict = {'TMIN':response[0],
                'TAVG':response[1],
                'TMAX':response[2]}
    session.close()
    return jsonify(respdict)


# run app
if __name__ == "__main__":
    app.run(debug=True)