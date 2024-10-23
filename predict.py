from datetime import datetime
import math
from pyorbital.orbital import Orbital
from math import *
from rtlsdr import RtlSdr
import wave
import numpy as np
elevation_threshold=0
def footprint(satellite):
    Re=6378
    orb = Orbital(satellite)
    lon, lat, alt = orb.get_lonlatalt(datetime.utcnow())
    return Re*math.acos(Re/(Re+alt))
def delta(satellite, station):
    orb = Orbital(satellite)
    lon, lat, alt = orb.get_lonlatalt(datetime.utcnow())
    lat_sat_rad = math.radians(lat)
    lon_sat_rad = math.radians(lon)
    lat_station_rad = math.radians(station[0])
    lon_station_rad = math.radians(station[1])
    return math.acos(
    math.sin(lat_station_rad) * math.sin(lat_sat_rad) +
    math.cos(lat_station_rad) * math.cos(lat_sat_rad) * math.cos(lon_sat_rad - lon_station_rad))
def distance(satellite,station):
    orb = Orbital(satellite)
    lon, lat, alt = orb.get_lonlatalt(datetime.utcnow())
    Re=6378
    distance_to_sat = math.sqrt((Re + alt)**2 - (Re**2 * math.cos(delta(satellite,station))**2))
    return (distance_to_sat)
def elevation_angle(satellite,station):
    orb = Orbital(satellite)
    lon, lat, alt = orb.get_lonlatalt(datetime.utcnow())
    Re=6378
    elevation_angle = math.degrees(math.asin(((Re + alt) - Re * math.cos(delta(satellite,station))) / distance(satellite,station)))
def prochain_passage(satellite1,satellite2,satellite3,station):
    orb1 = Orbital(satellite1)
    lon1, lat1, alt1 = orb1.get_lonlatalt(datetime.utcnow())
    orb2 = Orbital(satellite2)
    lon2, lat2, alt2 = orb2.get_lonlatalt(datetime.utcnow())
    orb3 = Orbital(satellite3)
    lon3, lat3, alt3 = orb3.get_lonlatalt(datetime.utcnow())
    s=[satellite1,satellite2,satellite3]
    d=[distance(satellite1,station),distance(satellite2,station),distance(satellite3,distance)]
    return s[min(distance).index],freqs[min(distance).index]
def est_detectable(satellite,station):
    return(elevation_angle(satellite,station)>elevation_threshold)
satellite1="NOAA 15"
satellite2="NOAA 18"
satellite3="NOAA 19"
freqs=[137.620, 137.9125, 137.100]
station=[48.36071142457538, -4.571863963872921]
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Fréquence d'échantillonnage
sdr.gain = 'auto'
def record_signal(output_file,orb):
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16 bits par échantillon
        wf.setframerate(int(sdr.sample_rate))
        while True:
            satellite, freq =prochain_passage(satellite1,satellite2,satellite3,station)
            orb=Orbital(satellite)
            # Récupérer la position du satellite (latitude, longitude, altitude)
            lon_sat, lat_sat, alt = orb.get_lonlatalt(datetime.utcnow())
            
            # Calcul de l'élévation du satellite
            elevation_angle = elevation_angle(satellite,station)
            
            # Si le satellite descend en dessous du seuil d'élévation, arrêter l'enregistrement
            if elevation_angle < elevation_threshold:
                print(f"Satellite en-dessous de {elevation_threshold}°, arrêt de l'enregistrement.")
                break
            
            # Capturer les échantillons SDR
            samples = sdr.read_samples(2048)
            
            #Convertir en format audio et enregistrer
            data = (np.real(samples) * 32767).astype(np.int16)
            wf.writeframes(data.tobytes())
while True:
    satellite, sdr.center_freq =prochain_passage(satellite1,satellite2,satellite3,station)
    i=0
    if est_detectable(satellite,station):
        orb = Orbital(satellite)
        i+=1
        print(f"Satellite détecté avec une élévation de {elevation_angle(satellite,station):.2f}°, démarrage de l'enregistrement.")
        output_filename = "prise_de_vue_n°{i}.wav"
        record_signal(output_filename,orb)
        

