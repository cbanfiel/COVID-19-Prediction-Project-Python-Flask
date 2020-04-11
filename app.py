from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime, timedelta
import config as config
import plotly.graph_objects as go
import json
import plotly
app = Flask(__name__)


class County():
    def __init__(self, name):
        self.name = name
        self.confirmed = []

    def setConfirmed(self, confirmed):
        self.confirmed = confirmed


def getCountyList():
    connection = config.connect()
    cursor = connection.cursor()
    cursor.execute(f"SELECT county FROM covid2020")
    dbData = cursor.fetchall()
    removeDupe = list(dict.fromkeys(dbData))
    counties = []

    for county in removeDupe:
        counties.append(County(county[0]))


    counties = sorted(counties, key=lambda x: x.name)
    return counties

def predictions(data):
    DAYS_PREDICTED = 15
    print(len(data))
    comparisons = 0
    i=0
    growth = 0
    for i in range(1, len(data)):
        comparisons += 1
        growth += data[i].get('cases')/data[i-1].get('cases')
    growth = growth/comparisons
    
    date = data[len(data)-1].get('date')


    cases = []
    deaths = []
    dates = []

    deathRate = data[len(data)-1].get('deaths') / data[len(data)-1].get('cases')

    cases.append(data[len(data)-1].get('cases'))
    deaths.append(data[len(data)-1].get('deaths'))

    last = 120

    for i in range(0, DAYS_PREDICTED):
        if i > 7:
            growth -= (growth/last)

        currentCases = round(cases[i]*growth)
        cases.append(currentCases)
        deaths.append(round(currentCases*deathRate))
        dates.append(date)
        date = date + timedelta(days = 1)
        
    predictions = []

    
    for i in range(0, len(dates)):
        predictions.append({
            "date": dates[i],
            "cases": cases[i],
            "deaths": deaths[i]
        })
    predictions.pop(0)
    
    
    return predictions


@app.route('/', methods=['POST', 'GET'])
def index():
        if request.method == 'POST':
            selection = request.form.get('countylist')
            counties = getCountyList()
            connection = config.connect()
            cursor = connection.cursor()
            cursor.execute("SELECT thedate, infections, deaths FROM covid2020 where county = %s", (selection,))
            dbData = cursor.fetchall()
            chartData = []
            cases = []
            dates = []
            for data in dbData:
                chartData.append({
                    "date": data[0],
                    "cases": data[1],
                    "deaths": data[2]
                })
      
            
            county = {
                "name": selection,
                "data": chartData,
                "predictions": predictions(chartData)
            }


            for prediction in county['predictions']:
                cases.append(prediction['cases'])
                dates.append(f"{str(prediction['date'].month)}/{str(prediction['date'].day)}")

            
            cases = json.dumps(cases)
            dates = json.dumps(dates)
            return render_template('index.html', counties = counties, county=county, cases=cases, dates=dates)
        else:
            counties = getCountyList()
            return render_template('index.html', counties = counties, county = None)


if __name__ == "__main__":
    app.run(debug=True)