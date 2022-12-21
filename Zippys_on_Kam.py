import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import math
from dash import dcc
from dash import html
from zipFunctions import*
from geopy import geocoders
from dash.dependencies import Input, Output

file1 = open('api.txt', 'r')
Lines = file1.readlines()
ApiKeys = []
for line in Lines:
    ApiKeys.append(line.strip())

name = zip_locations("https://www.zippys.com/locations/")
bingMapsKey = ApiKeys[0]
mapbox_access_token = ApiKeys[1]
bing = geocoders.Bing(bingMapsKey)

zipFrame = zip_scrape(name, bing)
kamFrame = zipFrame[(zipFrame['address'].str.contains('Kamehameha'))]

zipFrame['dummy_size'] = 1

def generate_tags(dirText):
    return html.H4(
        children=str(dirText),
        style={"color": "rgb(135, 206, 235)"},
    )

app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])

app.layout =dbc.Row(
    [
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.H3("These are the directions:", style={"color": "rgb(241, 211, 2)"})
                    ]),
                    dcc.Loading([
                        dbc.Col(id = "directions")], type='circle')
                    ], style={'marginTop': '5%','paddingLeft': '1%'}),
            dbc.Col([
                dcc.Store(id='store'),
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.H1("Zippys on Kam"),style={'marginTop': '1%', 'width' : '100%'}),
                        dbc.Col([
                            dcc.Input(
                                id="address_change",
                                type = 'text',
                                placeholder="Your address",
                                debounce=True
                        )],style={'marginTop': '2%', 'width': '10%'}),
                        dbc.Col(dbc.Col(id = "return-status"),style={'marginTop': '2%', 'width': '30%'}),
                        dbc.Col(dbc.Col(id = "return-statusRoute"),style={'marginTop': '2%', 'width': '30%'})
                    ]),
                ]),
                dcc.Loading([
                    dcc.Graph(id = 'Zippys Map'),
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.H3("This trip will take about:", style={"color": "rgb(241, 211, 2)"}),
                                html.H3("The travel distance is:", style={"color": "rgb(241, 211, 2)"}),
                                html.H3("The level of traffic is:", style={"color": "rgb(241, 211, 2)"}),
                                ]),
                            dbc.Col([
                                html.H3(id="trip-time", style={"color": "rgb(135, 206, 235)", "text-align": "left"}),
                                html.H3(id="trip-distance", style={"color": "rgb(135, 206, 235)", "text-align": "left"}),
                                html.H3(id="traffic-level", style={"color": "rgb(135, 206, 235)", "text-align": "left"})]),
                        ])
                    ])
                ])
            ])
        ])
    ],
)

@app.callback(
    Output("trip-time", "children"),
    Output("trip-distance", "children"),
    Output("traffic-level", "children"),
    Output("directions", "children"),
    Output("Zippys Map", "figure"),
    Output("return-status", "children"),
    Output("return-statusRoute", "children"),
    Input("address_change", "value"),
)
def update_fig(address):

    valid_address = 0
    #set default value
    if address == None:
        address = ""

    try:
        returnText = "Valid Location"
        returnColor = "rgb(57, 255, 0)"
        myLocation, myLocBing = set_loc(address, bing)
        valid_address = 1
    except:
        returnText = "Invalid Address"
        returnColor = "rgb(255, 0, 0)"
        valid_address = 0

    try:
        returnTextRoute = "Valid Route"
        returnColorRoute = "rgb(57, 255, 0)"
        trPoints, tripTime, minTripDistance, traffic, trpDirections, lat, lon, lowestAddress, zipCoords = closest_kam(myLocBing, kamFrame, bingMapsKey)
        valid_Route = 1
    except:
        returnTextRoute = "Invalid Route"
        returnColorRoute = "rgb(255, 0, 0)"
        valid_Route = 0   

    try:
        if tripTime:
            chart_title = "Routing from "+str(myLocation)+" to the nearest Zippys on Kam"
        else:
            chart_title = "No valid Route to a Zippys on Kam from: "+str(myLocation)
            valid_Route = 0
    except:
        chart_title = "Zippys locations on Kamehameha Highway"

    zipMap = px.scatter_mapbox(zipFrame,
        lon = zipFrame['longitude'],
        lat = zipFrame['latitude'],
        color = 'onKam',
        size = 'dummy_size',
        size_max=10,
        hover_name = 'Location',
        labels={
            "Location": "Location",
            "address": 'address',
            'Fast-Food-status': 'Take-out status',
            'Resturant_status': 'Resturant status',
        },
        hover_data=['address', 'phoneNumber', 'Fast-Food_status','Resturant_status'],
        zoom = 9,
        width = 1350,
        height = 720,
        title = chart_title,
    )

    try:
        zipMap.add_trace(go.Scattermapbox(
            lon = [str(zipCoords[1])],
            lat = [str(zipCoords[0])],
            mode='markers',
            marker = {'size': 20, 'color': 'Red', 'opacity': 1}, #'symbol': ["information"]*8
            name = "Closest On Kam",
            ),
        ),

        zipMap.add_trace(go.Scattermapbox(
            lon = [str(myLocBing[1])],
            lat = [str(myLocBing[0])],
            mode='markers',
            marker = {'size': 20, 'color': 'Yellow', 'opacity': 1}, #'symbol': ["information"]*8
            name = "Your Location",
            ),
        ),

        zipMap.add_trace(go.Scattermapbox(
            lon = lon,
            lat = lat,
            mode = 'lines',
            line = dict(width = 1,color = 'red'),
            opacity = 0.5,
            name = "bing Route"
        ))
    except:
        if valid_Route == 0:
            returnTextRoute = "Invalid Route"
            returnColorRoute = "rgb(255, 0, 0)"
        else:
            returnTextRoute = "Valid Route"
            returnColorRoute = "rgb(57, 255, 0)"
        if valid_address == 0:
            returnText = "Invalid address"
            returnColor = "rgb(255, 0, 0)"
        else:
            returnText = "Valid address"
            returnColor = "rgb(57, 255, 0)"
        

    if address == '':
        returnText = ""
        returnTextRoute = ""
        returnColor = "rgb(57, 255, 0)"
        returnColorRoute = "rgb(57, 255, 0)"

    zipMap.update_layout(
        #width = 1350,
        #height = 720,
        font =dict(
            size=20
        ),
        hovermode='closest',
        margin={"r":0,"t":60,"l":0,"b":0},
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=21.4892855,
                lon=-157.943801
            ),
            style="dark",
            pitch=0,
            zoom=9.8,
        ),
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor='left',
        x=0.01),
        paper_bgcolor='Black',
        colorscale_sequential='hot')

    if (valid_address == 1) and (valid_Route == 1):
        block_info_tripTime = str(math.ceil(tripTime/60))+" minutes"
        block_info_tripDistance = str(round((minTripDistance/1.609),1))+" miles"
        block_info = []

        for direction in trpDirections:
            block_info.append(direction)
        children=[generate_tags(i) for i in block_info if i]
    else:
        block_info_tripTime = "No-Route"
        block_info_tripDistance = "No-Route"
        block_info = []
        traffic = "No-Route"
        nullTrp = ['No-Route']

        for direction in nullTrp:
            block_info.append(direction)
        children=[generate_tags(i) for i in block_info if i]    

    returnStatus = html.H4(children=str(returnText),style={"color": returnColor, "text-align": 'left'})
    returnStatusRoute = html.H4(children=str(returnTextRoute),style={"color": returnColorRoute, "text-align": 'left'})

    return(block_info_tripTime, block_info_tripDistance, traffic, children, zipMap, returnStatus, returnStatusRoute)

if __name__ == '__main__':
    app.run_server(debug=True)