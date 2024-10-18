import openeo
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import os
import pandas as pd
import time

# https://documentation.dataspace.copernicus.eu/APIs/openEO/Python_Client/Python.html 

def download_S2(path_geojson, output_folder, startday, endday, bands=["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B8A", "B09", "B11", "B12"], visu=False,max_cloud_cover=35,synthesis=False,sleep_time=3,retries=5):
    """
    Parameters
    ----------
      - path_geojson:
          path to geojson for (see https://geojson.io/)
      - name folder:
          name of folder to store data
      - startday:
          starting day in format "YYYYMMDD" (ex : "20220731")
      - endday:
          ending day in format YYYYYMMDD (ex : "20220831")
      - bands:
          a list of strings among default values :
          ["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"]
      - visu:
          (def False) to visualize information on the progess of downloading
      - max_cloud_cover (def 35):
          maxium cloud coverage in %
      - synthesis:
          (def False) If True, download a synthesis over the time period
           otherwise, download all data
           
      - sleep_time and retries : for downloading time series, 
                                  multiple sollicitations to server
                                  can generate errors due to many connections
                                  
             - retries (default 5): number of trials to perform for each date
             - sleep_time (default 3) : pause between two requests to the server
        

    Returns
    -------
      - If synthesis is False
          Bands in folder output_folder/date1
                          output_folder/date2
                          ...
                          output_folder/dateN
    
      - If synthesis is True
          Bands in folder output_folder



    Example :
    ---------
    bands=["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"]

    # Download time series
    download_S2('altea.geojson','./outputs/ALTEA_Noel2023',"20231220","20240131",bands=bands,visu=True,synthesis=False)

    # Download synthesis
    download_S2('altea.geojson','./outputs/ALTEA_synthesis',"20231220","20240131",bands=bands,visu=True,synthesis=False)


    Issues : if server is not available, you should retry
    The first time : need authentification


      
    """
    if synthesis is True:
        download_S2_synthesis(path_geojson,output_folder,
                    startday,endday,
                    bands=bands,
                    visu=visu,
                    max_cloud_cover=max_cloud_cover)
    else:
        download_S2_timeseries(path_geojson, output_folder,
                               startday, endday, bands=bands,
                               visu=visu,max_cloud_cover=max_cloud_cover,sleep_time=sleep_time,retries=retries)


def download_S2_synthesis(path_geojson,output_folder,
                startday,endday,
                bands=["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"],
                visu=False,max_cloud_cover=35):
    """
    - path_geojson = path to geojson (see https://geojson.io/)
    - name folder : name of folder to store data
    - startday = starting day in format "YYYYMMDD" (ex : "20220731")
    - endday = ending day in format YYYYYMMDD (ex : "20220831")
    - bands : a list of strings among default values :
        ["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"]
    - visu : (def False) to visualize info
    - max_cloud_cover (def 35):
          maxium cloud coverage in %



    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    connection = openeo.connect("openeo.dataspace.copernicus.eu")
    connection.list_collection_ids()

    # Get detailed metadata of a certain collection
    if visu:
        connection.describe_collection("SENTINEL2_L2A")
    connection.authenticate_oidc()
    
    geojson_data=read_geojson(path_geojson)


    coordinates = geojson_data['features'][0]['geometry']['coordinates']

    
    longitudes = [coord[0] for coord in coordinates]
    latitudes = [coord[1] for coord in coordinates]

    valW = min(longitudes)  # Longitudes minimum = west
    valE = max(longitudes)  # Longitudes maximum = east
    valS = min(latitudes)   # Latitudes minimum = south
    valN = max(latitudes)   # Latitudes maximum = north

    # Créer l'étendue spatiale
    spatial_extent = {
        "west": valW,
        "south": valS,
        "east": valE,
        "north": valN
    }

    if visu:
        print("Spatial extent:", spatial_extent)
    
    datacube = connection.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=spatial_extent,
        temporal_extent = ["2021-02-01", "2021-04-30"],
        #bands=["B02", "B04", "B08"],
        bands=bands,
        max_cloud_cover=max_cloud_cover,
    )

    data=[]
    for band in bands:
        data.append(datacube.band(band)) 
    
    for i in range(len(data)):
        if visu:
            print('Downloading ... %s/%s.tif'%(output_folder,bands[i]))
        data[i].download('%s/%s.tif'%(output_folder,bands[i]))
        if visu:
            print(' ... done')
    print(' Download complete')

def download_S2_timeseries(path_geojson, output_folder, startday, endday, bands=["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B8A", "B09", "B11", "B12"], visu=False, max_cloud_cover=90,sleep_time=3,retries=5):
    """
    Télécharge des images Sentinel-2 dans un dossier pour chaque date et bande spécifiée.

    - path_geojson : chemin vers le fichier GeoJSON (ex : https://geojson.io/)
    - output_folder : dossier de sortie pour stocker les données téléchargées
    - startday : date de début au format "YYYYMMDD" (ex : "20220731")
    - endday : date de fin au format "YYYYMMDD" (ex : "20220831")
    - bands : liste des bandes à télécharger (par défaut, toutes les bandes optiques de Sentinel-2)
    - visu : si True, permet de visualiser des informations sur les téléchargements (par défaut False)
    - max_cloud_cover : couverture nuageuse maximale autorisée (par défaut 90%)
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    connection = openeo.connect("openeo.dataspace.copernicus.eu")
    connection.list_collection_ids()

    if visu:
        connection.describe_collection("SENTINEL2_L2A")
    connection.authenticate_oidc()

    geojson_data = read_geojson(path_geojson)
    coordinates = geojson_data['features'][0]['geometry']['coordinates']

    # Extraire les longitudes et latitudes
    longitudes = [coord[0] for coord in coordinates]
    latitudes = [coord[1] for coord in coordinates]

    valW = min(longitudes)  # Ouest
    valE = max(longitudes)  # Est
    valS = min(latitudes)  # Sud
    valN = max(latitudes)  # Nord

    spatial_extent = {"west": valW, "south": valS, "east": valE, "north": valN}

    # Boucle sur les dates dans l'intervalle spécifié
    for current_date in pd.date_range(start=startday, end=endday):
        temporal_extent = [current_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")]
        print('---------- Test ',current_date.strftime("%Y-%m-%d"),'-------------')

        try:
            # Charger le cube de données filtré par date et par bandes
            datacube = connection.load_collection(
                "SENTINEL2_L2A",
                spatial_extent=spatial_extent,
                temporal_extent=temporal_extent,
                bands=bands,
                max_cloud_cover=max_cloud_cover,
            )

            # Télécharger chaque bande
            for band in bands:
                data = datacube.band(band)
                if visu:
                    print(f"Check data availability for {current_date.strftime('%Y-%m-%d')} and band {band}")

                # Créer le dossier pour la date si nécessaire
                folder_date = os.path.join(output_folder, current_date.strftime('%Y%m%d'))
                if not os.path.exists(folder_date):
                    os.makedirs(folder_date)

                # Nom du fichier de sortie
                filename = f"{folder_date}/{band}.tif"

                # Utiliser la fonction de téléchargement avec retry
                download_success = download_with_retry(data, filename,sleep_time=sleep_time,retries=retries)

                if visu:
                    if download_success:
                        print(f"Downloaded : {filename}")
                
                if download_success is False:
                    if os.path.exists(folder_date) and not os.listdir(folder_date):
                        os.rmdir(folder_date)
                    print(f"miss at least one band for date {current_date.strftime('%Y-%m-%d')}. Move to next day")
                    break


        except openeo.rest.OpenEoApiError as e:
            if 'NoDataAvailable' in str(e):
                # Gérer l'erreur "NoDataAvailable" et passer à la date suivante
                print(f"Aucune donnée disponible pour la date {current_date.strftime('%Y-%m-%d')}. Passage à la date suivante.")
                # Supprimer le dossier si aucune donnée n'a été téléchargée
                folder_date = os.path.join(output_folder, current_date.strftime('%Y%m%d'))
                if os.path.exists(folder_date) and not os.listdir(folder_date):
                    os.rmdir(folder_date)
                continue
            else:
                # Pour toute autre erreur, la remonter
                raise e

    print("Download of each S2 image done !")

def download_with_retry(data, filename, retries=5, sleep_time=3):
    """
    Tentative de téléchargement avec retries et délai exponentiel en cas d'erreur 429 (trop de requêtes).
    Ignore l'erreur 400 (NoDataAvailable).
    """
    for attempt in range(retries):
        try:
            data.download(filename)
            print(f"Data downloaded after {attempt + 1} trial(s).")
            return True
            #return  # Sortir si le téléchargement réussit
        except Exception as e:
            # Capture le type d'erreur pour comprendre pourquoi ça ne marche pas
            #print(f"Erreur détectée : {e}")
            #print(f"Type d'exception : {type(e)}")
            
            if isinstance(e, openeo.rest.OpenEoApiError) and e.http_status_code == 400 and 'NoDataAvailable' in str(e):
#                print(f" ************ [Erreur 400] No DATA : {e}. Téléchargement annulé.")
                print("-- ************ [Erreur 400] No DATA.")
                return False
            else:
#                print(f"Trail {attempt + 1} failed: {e}")
                print(f"Trail {attempt + 1} failed")
                wait_time = sleep_time * (attempt + 1)
                print(f"-- [Erreur 429]. Wait {wait_time} seconds to start again...")
                time.sleep(wait_time)
    
    
    print(f"Failed to check data availability after {retries} trials.")
    return False


