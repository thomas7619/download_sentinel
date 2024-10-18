# download_sentinel package
## Description
Python functions to download Sentinel data (time series or synthesis)
This requires an account on https://openeo.dataspace.copernicus.eu/, see https://documentation.dataspace.copernicus.eu/Registration.html

## Installation of environment



Create and install environment with conda :
```
conda env create -f environment.yml
```

**Note**: if your prefer to install with pip :
```
pip install -r requirements.txt
```

**Note**: an anvironment can be saved with
```
conda env export --no-builds > environment.yml
```
or
```
pip freeze > requirements.txt
```



## Python execution

See the notebook `ex_download_s2.ipynb`

Import library
```
import download_sentinel as S2
```

Help on the main function
```
help(S2.download_S2)
```

## Download a *synthesis* over a given period
```
# Bands to download
bands=["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"]
# Geojson file (made with  https://geojson.io/) for the area of interest
input_path = 'copacabana_ipanema.geojson'
# Folder to save data
output_folder = './outputs/copacabana_ipanema_synthesis_2024_06/'
# Start and end dates
startday = "20240601"
endday = "20240615"
# Synthesis : if True, download a synthesis, if False, fownload the complete time series
synthesis = True
# Command
S2.download_S2(input_path,output_folder,startday,endday,bands=bands,visu=True,synthesis=synthesis)
```
This saves all individual bands in output_folder

## Download a *complete time series* over a given period
```
# Bands to download
bands=["B01","B02","B03","B04","B05","B06","B07","B8A", "B09", "B11", "B12"]
# Geojson file (made with  https://geojson.io/) for the area of interest
input_path = 'copacabana_ipanema.geojson'
# Folder to save data
output_folder = './outputs/copacabana_ipanema_timeseries_2024_06/'
# Start and end dates
startday = "20240601"
endday = "20240615"
# Synthesis : if True, download a synthesis, if False, fownload the complete time series
synthesis = False
# Command
S2.download_S2(input_path,output_folder,startday,endday,bands=bands,visu=True,synthesis=synthesis)
```
This saves all individual dates in specific subfloders in output_folder
