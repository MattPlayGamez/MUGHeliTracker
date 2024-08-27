import time
import json
import math
import os
import requests
from FlightRadar24 import FlightRadar24API
from time import sleep

FlightRadar = FlightRadar24API()
cooldown = 60
path2json = os.getcwd() + "/configuration.json"

self_latitude = None
self_longitude = None
radius = None
vehicle_to_track = None
topic = None
landing_radius = None

print('app started')

with open(path2json, 'r') as file:
    data = json.load(file)
    self_latitude = data["latitude"]
    self_longitude = data["longitude"]
    radius = data["radius"]
    vehicle_to_track = data["registration"]
    topic = data["NTFYtopic"]
    landing_radius = data["landing_radius"]

def getDistanceFromTwoCoords(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of Earth in kilometers
    R = 6371.0

    # Distance in kilometers
    distance = R * c
    return distance

def TrackTillLanding(registration):
    previous_altitude = 10000000
    print('Tracking till landing...')
    sendout = True

    while True:
        # Bepaal de grenzen voor de vluchtzoekopdracht
        bounds = FlightRadar.get_bounds_by_point(self_latitude, self_longitude, landing_radius)
        flights = FlightRadar.get_flights(bounds=bounds)

        # Zoek naar het vliegtuig met de juiste registratie
        for aircraft in flights:
            if aircraft.registration == registration:
                print("In landing radius")
                if aircraft.altitude < previous_altitude:
                    print(aircraft.altitude)
                    if aircraft.altitude < 165:
                        print("Below 165 feet")
                        google_maps = f"https://www.google.com/maps?q={aircraft.latitude},{aircraft.longitude}"
                        if sendout:
                            request_data = {
                                "topic": topic,
                                "message": "**MUG Heli land in de buurt, meer info als hij landt** \n",
                                "actions": [
                                    {
                                        "action": "view",
                                        "label": "Open Flight Radar",
                                        "url": "https://www.flightradar24.com/51.13,3.03/14"
                                    }
                                ]
                            }
                            requests.post('https://ntfy.sh/', data=json.dumps(request_data), headers={
                                "Markdown": "yes",
                                "Title": "Mug heli landt",
                                "Priority": "urgent",
                                "Tags": "warning, helicopter"
                            })
                            sendout = False

                    # Check of de helikopter is geland
                    if aircraft.altitude <= 60:
                        google_maps = f"https://www.google.com/maps?q={aircraft.latitude},{aircraft.longitude}"
                        afstand_van_thuis = getDistanceFromTwoCoords(self_latitude, self_longitude, aircraft.latitude, aircraft.longitude)
                        data = {
                            "topic": topic,
                            "message": f"**MUG Heli is geland op {afstand_van_thuis}km ** \n",
                            "actions": [
                                {
                                    "action": "view",
                                    "label": "Open Google Maps",
                                    "url": google_maps
                                }
                            ]
                        }
                        requests.post('https://ntfy.sh/', data=json.dumps(data), headers={
                            "Markdown": "yes",
                            "Title": f"Mug heli geland op {afstand_van_thuis}km",
                            "Priority": "urgent",
                            "Tags": "warning, helicopter, danger"
                        })
                    previous_altitude = aircraft.altitude
                    return  # Stop de functie nadat de helikopter is geland
        time.sleep(1)  # Wacht een seconde voordat je opnieuw zoekt

def GetMugHeli():
    global cooldown
    bounds = FlightRadar.get_bounds_by_point(self_latitude, self_longitude, radius)
    flights = FlightRadar.get_flights(bounds=bounds)
    for aircraft in flights:
        if aircraft.registration == vehicle_to_track:
            print(aircraft)
            latitude = aircraft.latitude
            longitude = aircraft.longitude
            speed = round(aircraft.ground_speed * 1.609344, 0)
            google_maps = f"https://www.google.com/maps?q={latitude},{longitude}"
            altitude = round(aircraft.altitude * 0.3048, 0)
            data = {
                "topic": topic,
                "message": f"**MUG Heli in de buurt ({radius}km)** \nOp een hoogte van {altitude}m\nMet een snelheid van {speed}km/h",
                "actions": [
                    {
                        "action": "view",
                        "label": "Open Flight Radar",
                        "url": "https://www.flightradar24.com/51.13,3.03/13"
                    },
                    {
                        "action": "view",
                        "label": "Open Google Maps",
                        "url": google_maps
                    }
                ]
            }
            requests.post('https://ntfy.sh/', data=json.dumps(data), headers={
                "Markdown": "yes",
                "Title": "Mug heli in de buurt",
                "Priority": "urgent",
                "Tags": "warning, helicopter"
            })
            sleep(1)
            TrackTillLanding(aircraft.registration)
            cooldown = 900
        else:
            cooldown = 60

if __name__ == "__main__":
    while True:
        GetMugHeli()
        sleep(cooldown)
