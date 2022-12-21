import requests
import urllib.request
import pandas as pd
import json
import re
from bs4 import BeautifulSoup

def zip_locations (website):
    url=website
    Locations_page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(Locations_page.content, 'html.parser')
    zipName_raw = []
    zipName = []
    zipName_raw = soup.find_all('h3')

    #parse to text
    for name in zipName_raw:
        zipName.append(name.text)

    #remove the first entry
    zipName.pop(0)

    #filter out duplicates and replace empty space with '-' for formatting
    i = 0
    name = []
    while  zipName[i] != "Select Your Preferred Zippy's":
        noSpace = zipName[i].replace(" ", '-')
        name.append(noSpace)
        i=i+1
    return (name)

def zip_scrape (names, bingKey):
    localSite = []
    results = []
    for sites in names:
        localSite.append("https://www.zippys.com/locations/"+sites+"/")
        locationPage = "https://www.zippys.com/locations/"+sites+"/"

        Location_page = requests.get(locationPage, headers={'User-Agent': 'Mozilla/5.0'})
        local = BeautifulSoup(Location_page.content, 'html.parser')

        location_raw = str(local.find('div', class_='location-address').text).split()
        address = " ".join(location_raw)

        #Check if it is on Kam
        if ('Kamehameha' in address):
            onKam = True
        else:
            onKam = False
        
        phoneNum_raw1 = str(local.find('div', class_='location-phone').text.encode("utf-8"))
        phoneMatch = re.search(r"(?<=\').+?(?=\')",str(phoneNum_raw1))

        #print(address)
        locationCor = bingKey.geocode(address)
        latitude = locationCor.latitude
        longitude = locationCor.longitude

        #print(phoneMatch.group())

        #list of services offered at location
        Services = ["fast-food", "bakery", "atm", "restaurant", "delivery"]
        avalServices = []
        for service in Services:
            temp = local.find_all('li', class_=service)
            if temp:
                avalServices.append(service)
                #print(service)

        count = 0
        Closed = local.find_all('th')
        locHours = local.find_all('td')
        #stats open, closed or none
        FastStat = ""
        RestuStat = ""
        #type of resturant or fast food 0 = fast food, 1 = restaurant, 2 = none
        resType = 0
        FastHours = []
        RestHours = []
        for hours in Closed:
            if hours.text == "Fast Food Open":
                #print("Fast Food is open")
                FastStat = "open"
            elif hours.text == "Fast Food Closed":
                #print("Fast food is closed")
                FastStat = "closed"
            elif hours.text == "Fast Food":
                #print("Fast food is not an option")
                FastStat = "none"

            elif hours.text == "Restaurant Open":
                #print("Restaurant is open")
                RestuStat = "open"
                resType = 1
            elif hours.text == "Restaurant Closed":
                #print("Restaurant is closed")
                RestuStat = "closed"
                resType = 1
            elif hours.text == "Restaurant ":
                #print("Resturant is not an option")
                RestuStat = "maybe-open"
                resType = 2
            else:
                if hours.text:
                    storeHours = str(locHours[count].text).split()
                    operationHours = str(hours.text)+" "+' '.join(storeHours)
                    #print(operationHours)
                    if resType == 0:
                        FastHours.append(operationHours)
                    elif resType == 1:
                        RestHours.append(operationHours)
                    count = count+1

        results.append([sites, address, onKam, latitude, longitude, phoneMatch.group(), avalServices, FastStat, FastHours, RestuStat, RestHours])
        zipFrame = pd.DataFrame(results, columns=['Location', 'address', 'onKam', 'latitude', 'longitude', 'phoneNumber', 'resources', 'Fast-Food_status', 'Fast_Food_Operation_Hours', 'Resturant_status', 'Resturant_Operation_Hours'])
    return (zipFrame)

def get_loc():
    response = requests.get('https://api64.ipify.org?format=json').json()
    ip6 = response["ip"]

    # parameters to retrieve from API
    params = ['query', 'status', 'country', 'countryCode', 'city', 'timezone', 'mobile', 'lat', 'lon']

    # make the response 
    resp = requests.get('http://ip-api.com/json/' + ip6, params={'fields': ','.join(params)})

    # read response as JSON (converts to Python dict)
    info = resp.json()
    myLoc = (info.get('lat'), info.get('lon'))
    return (myLoc)

def set_loc(location, bingKey):
    myLocation = bingKey.geocode(location)
    myLocBing = (myLocation.latitude, myLocation.longitude)
    return myLocation, myLocBing

def closest_kam (myLoc, zipFrame, bingMapsKey):
    longitude = myLoc[1]
    latitude = myLoc[0]
    minTrip = None
    lat = []
    lon = []
    trpDirections = []
    tripTime = ''
    minTripDistance = ''
    trPoints = []
    lowestAddress = ''
    traffic = ''
    zipCoords = None

    #check every location distance and record it if it is on Kam
    for locations in zipFrame.index:
        destination = zipFrame['address'][locations]
        encodedDest = urllib.parse.quote(str(destination), safe='')

        #attempt to find route. Invalid routes fail. Basicaly means it will only work on Oahu
        try:
            routeUrl = "http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=" + str(latitude) + "," + str(longitude) + "&wp.1=" + encodedDest + "&routePathOutput=Points" "&key=" + bingMapsKey

            request = urllib.request.Request(routeUrl)
            response = urllib.request.urlopen(request)

            r = response.read().decode(encoding="utf-8")
            result = json.loads(r)

            itineraryItems = result["resourceSets"][0]["resources"][0]["routeLegs"][0]["itineraryItems"]
            plotPoints = result["resourceSets"][0]["resources"][0]['routePath']['line']['coordinates']
            tripDistance = result["resourceSets"][0]["resources"][0]["travelDistance"]
            #set the minTrip Distance
            if minTrip is None and zipFrame['onKam'][locations] == True:
                minTrip = tripDistance
                lowestAddress = destination
                zipCoords = (zipFrame['latitude'][locations], zipFrame['longitude'][locations])
            if tripDistance < minTrip and zipFrame['onKam'][locations] == True:
                minTrip = tripDistance
                lowestAddress = destination
                zipCoords = (zipFrame['latitude'][locations], zipFrame['longitude'][locations])
                traffic = result["resourceSets"][0]["resources"][0]["trafficCongestion"]
                tripTime = result["resourceSets"][0]["resources"][0]["travelDuration"]
                lat = []
                lon = []
                trpDirections = []
                trPoints = []

                for points in plotPoints:
                    lat.append(points[0])
                    lon.append(points[1])

                for item in itineraryItems:
                    trpDirections.append(item["instruction"]["text"])
                    trPoints.append(item["maneuverPoint"]['coordinates'])
        except:
            bumper = 0

    return(trPoints, tripTime, minTrip, traffic, trpDirections, lat, lon, lowestAddress, zipCoords)