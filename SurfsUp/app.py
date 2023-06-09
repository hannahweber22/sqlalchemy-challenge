# Import the dependencies.
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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end"

    )

@app.route("/api/v1.0/precipitation")
def date_dict():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the 
    last 12 months of data) to a dictionary using date as the key and prcp as the value. 
    Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    
    # Calculate the date one year from the last date in data set.
    #Don’t pass the date as a variable to your query. ???
    

    recent_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    recent_year

    # Perform a query to retrieve the data and precipitation scores

    prep_scores = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > recent_year).all()


    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    dict_df = pd.DataFrame(prep_scores,  columns=['Measurement Date', 'Precipitation Score'])
    
    #Convert dataframe into dictionary
    date_dict = dict_df.groupby('Measurement Date')['Precipitation Score'].apply(list).to_dict()
    
    #Close session
    session.close()

    #Return JSON dictionary
    return jsonify(date_dict)

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset."""
        # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station = session.query(Station.name).all()
    station_list = list(np.ravel(station))
    
    #Close session
    session.close()
    
    #Return JSON station list
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def active_station():

    """Query the dates and temperature observations of the most-active station for the 
    previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    stat_count = func.count(Measurement.station)
    recent_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    stat = session.query(Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(stat_count.desc()).first()[0]
    active_temp = session.query(Measurement.tobs).\
                        filter(Measurement.date > recent_year).\
                        filter(Measurement.station == stat).all()

    tobs_list = list(np.ravel(active_temp))
    
    #Close session
    session.close()

    
    #Return JSON termperature list
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def user_start(start):

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start 
    end range.

    For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query lowest temp, average temp, and highest temp from date range above start date in the measurement table
    low_temp = func.min(Measurement.tobs)
    high_temp = func.max(Measurement.tobs)
    avg_temp = func.avg(Measurement.tobs)
    sel = [low_temp, high_temp, avg_temp]
    user_start = start
    user_query = session.query(*sel).\
                        filter(Measurement.date >= user_start).all()

    #Select low temp, average temp, and high temp from query result
    user_low = user_query[0][0]
    user_high = user_query[0][1]
    user_avg = user_query[0][2]
    
    #Close session
    session.close()

    #Return min temp, avg temp, high temp
    return (
    f'Minimum Temperature: {user_low}<br/>'
    f'Average Temperature: {user_avg}<br/>'
    f'Maximum Temperature: {user_high}'
    
    )


@app.route("/api/v1.0/<start>/<end>")
def user_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-
    end range.

    For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, 
    inclusive.""" 
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query lowest temp, average temp, and highest temp from date range above start date and below end date in the measurement table
    low_temp = func.min(Measurement.tobs)
    high_temp = func.max(Measurement.tobs)
    avg_temp = func.avg(Measurement.tobs)
    sel = [low_temp, high_temp, avg_temp]
    user_start = start
    user_finish = end
    user_query = session.query(*sel).\
                        filter(Measurement.date >= user_start).\
                        filter(Measurement.date <= user_finish).all()
    
    #Select low temp, average temp, and high temp from query result
    user_low = user_query[0][0]
    user_high = user_query[0][1]
    user_avg = user_query[0][2]

    #Close session
    session.close()  

    #Return min temp, avg temp, max temp
    return (
    f'Minimum Temperature: {user_low}<br/>'
    f'Average Temperature: {user_avg}<br/>'
    f'Maximum Temperature: {user_high}'
    
    )


if __name__ == "__main__":
    app.run(debug=True)


