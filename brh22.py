import requests
import math
from constants import *
import numpy as np

DISTTHRESHOLD = 2

def greenleaguescore(zipcode):

    zipcodeurl = "https://maps.googleapis.com/maps/api/geocode/json?address=" + zipcode + "&key=" + API_KEY

    payload = {}
    headers = {}

    zipcoderesponse = requests.request("GET", zipcodeurl, headers=headers, data=payload)
    viewport = zipcoderesponse.geometry.viewport

    center = viewport.getcenter()
    east = viewport.east
    west = viewport.west
    north = viewport.north
    south = viewport.south

    distance = math.dist(east, west, north, south)

    parkurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=park&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY
    nbhdurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=nbhd&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY
    busurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=bus&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY
    trainsurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=train&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY
    subwurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=subway&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY
    transiturl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=transit&inputtype=textquery&locationbias=circle%3A" + distance + "%" + center.lat + "%2C" + center.lon + "&fields=geometry&key=" + API_KEY

    parkresponse = requests.request("GET", parkurl, headers=headers, data=payload)
    nbhdresponse = requests.request("GET", nbhdurl, headers=headers, data=payload)
    busstations = requests.request("GET", busurl, headers=headers, data=payload)
    trainstation = requests.request("GET", trainsurl, headers=headers, data=payload)
    subwaystation = requests.request("GET", subwurl, headers=headers, data=payload)
    transitstations = requests.request("GET", transiturl, headers=headers, data=payload)
    parklocations = []
    nbhdlocations = []
    publicsystems = []

    for candidate in parkresponse.candidates:
      parklocations.append(candidate.geometry.location)

    for candidate in nbhdresponse.candidates:
      nbhdlocations.append(candidate.geometry.location)

    for candidate in busstations.candidates:
      publicsystems.append(candidate.geometry.location)

    for candidate in trainstation.candidates:
      publicsystems.append(candidate.geometry.location)

    for candidate in subwaystation.candidates:
      publicsystems.append(candidate.geometry.location)

    for candidate in transitstations.candidates:
      publicsystems.append(candidate.geometry.location)

    nbhdcount = len(nbhdlocations)
    greennbhdcount = 0

    for nbhd in nbhdlocations:
      for park in parklocations:

        if math.dist(park, nbhd) <= DISTTHRESHOLD:

          greennbhdcount += 1

      total_area_covered = 0


      for i in range(1, len(publicsystems)):

        u = np.array([publicsystems[i - 1] + 5, nbhd, 1])       

        n = np.array([publicsystems[i] + 5, nbhd, 1])       

        n_norm = np.sqrt(sum(n**2))    

        spanned_area = (np.dot(u, n)/n_norm**2)*n

        total_area_covered += u - spanned_area

    cover = total_area_covered/distance**2

    if cover > 1:
      cover = 1
      
    PARK_COVER = str(greennbhdcount/nbhdcount)

    TRANSIT_COVER = str(cover)

    TOTAL_SCORE = (greennbhdcount/nbhdcount + cover)//DISTTHRESHOLD
    

    return PARK_COVER, TRANSIT_COVER, TOTAL_SCORE

def writeontxt(zip_inputs):
  files = [open("data.txt","w")]
  for zipcode in zip_inputs:
    PARK_COVER, TRANSIT_COVER, total = greenleaguescore(zipcode)
    files.write(zipcode+"\n")
    files.write("Percent of households within walkable distances from green spaces: " + PARK_COVER+"\n")
    files.write("Percent of area within zip code covered by public transit: " + TRANSIT_COVER+"\n")
    files.write("total: " + total+"\n")

  for i in files:
      i.close()