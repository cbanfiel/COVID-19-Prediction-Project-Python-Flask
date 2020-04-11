import plotly.graph_objects as go
import config as config

DAYS_PREDICTED = 29
COUNTY = "Detroit City"

connection = config.connect()
cursor = connection.cursor()

cursor.execute(f"SELECT infections, deaths, thedate FROM covid2020 WHERE county = '{COUNTY}' ")

dbData = cursor.fetchall()


def getCasesGrowth():
    comparisons = 0
    i=0
    growth = 0
    for i in range(1, len(dbData)):
        comparisons += 1
        growth += dbData[i][0]/dbData[i-1][0]

    growth = growth/comparisons
    return growth
 
def getDeathRate():
    comparisons = 0
    i=0
    rate = 0
    for i in range(0, len(dbData)):
        comparisons += 1
        rate += dbData[i][1]/dbData[i][0]

    rate = rate/comparisons
    return rate


casesGrowth = getCasesGrowth()
deathRate = getDeathRate()

print(casesGrowth)
print(deathRate)




dt = dbData[len(dbData)-1][2]

month = dt.month
day = dt.day


cases = []
deaths = []
dates = []

cases.append(dbData[len(dbData)-1][0])
deaths.append(dbData[len(dbData)-1][1])

last = 120

for i in range(0, DAYS_PREDICTED):
    if i > 7:
        casesGrowth -= (casesGrowth/last)

    cases.append(round(cases[i]*casesGrowth))
    deaths.append(round(cases[i]*deathRate))
    dates.append(f"{month}/{day}")
    day += 1
    if(day > 30):
        day = 1
        month += 1


fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=cases,
    name="Cases" 
))

fig.add_trace(go.Scatter(
    x=dates,
    y=deaths,
    name="Deaths" 
))

fig.update_layout(
    title=f"Predicted COVID-19 cases in {COUNTY} County, Michigan",
    xaxis_title="Dates",
    yaxis_title="Confirmed Cases"
)

fig.show()
