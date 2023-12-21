from FlightRadar24 import FlightRadar24API
from time import sleep
import json
import requests
import os
FlightRadar = FlightRadar24API()

cooldown = 60

path2json = os.getcwd() + "/configuration.json"

latitude = None
longitude = None
radius = None

with open(path2json, 'r') as file:
    data = json.load(file)
    print(data)
    latitude = data["latitude"]
    longitude = data["longitude"]
    radius = data["radius"]


def GetMugHeli():
    global cooldown
    bounds = FlightRadar.get_bounds_by_point(latitude=latitude,longitude=longitude, radius=radius)
    flights = FlightRadar.get_flights(bounds=bounds)
    for aircraft in flights:
        if aircraft.registration == "F-GSMU" or aircraft.registration == "F-GMHC":
            print(aircraft)
            latitude = aircraft.latitude
            longitude = aircraft.longitude
            google_maps = f"https://www.google.com/maps?q={latitude},{longitude}"
            cooldown = 900
        else:
            cooldown = 60
            

# while True:
#     GetMugHeli()    
#     sleep(cooldown)