#!/bin/python3

from datetime import date
import numpy as np
import pandas as pd
import xarray

data_path = ''
bm_ais_path = 'BedMachineAntarctica_2020-07-15_v02.nc'
bm_gis_path = 'BedMachineGreenland-v5.nc'

domain = 'Helheim'
# Cut out Thwaites ice shelf
if domain == 'Thwaites_Ice_Shelf':
    bm_path = bm_ais_path
    xmin = -1.6052e6
    xmax = -1.5326e6
    ymin = -490156
    ymax = -402706
elif domain == 'Thwaites_Shear_Zone':
    bm_path = bm_ais_path
    xmin = -1.57112e6
    xmax = xmin + 5.e3
    ymin = -462383
    ymax = ymin + 5.e3
elif domain == 'Kangerlussuaq':
    bm_path = bm_gis_path
    xmin = 488725.
    xmax = 497575.
    ymin = -2.29632e6
    ymax = -2.28972e6
elif domain == 'Helheim':
    bm_path = bm_gis_path
    xmin = 307225.
    xmax = 312615.
    ymin = -2.58162e6
    ymax = -2.57248e6

bm_data = xarray.open_dataset(bm_path)

thin_ice = 50.
x = bm_data.variables['x'].values
y = bm_data.variables['y'].values
thk = bm_data.variables['thickness'].values
thk *= thk > thin_ice  # Remove thin ice
bed = bm_data.variables['bed'].values
surf = bm_data.variables['surface'].values
# Mask values differ slightly  between AIS and GIS, but the values
# relevant to our purposes are the same as of BM-AIS-v2/BM-GIS-v5.
# AIS: 0=ocean 1=ice_free_land 2=grounded_ice 3=floating_ice 4=lake_vostok
# GIS: 0=ocean, 1=ice-free land, 2=grounded ice, 3=floating ice, 4=non-Greenland land
mask =  bm_data.variables['mask'].values

bm_data.close()
xgrid, ygrid = np.meshgrid(x,y)
ind = np.where(np.logical_and(
          np.logical_and(xgrid >= xmin, xgrid <=xmax),
          np.logical_and(ygrid >= ymin, ygrid <= ymax)))

x_out, y_out, thk_out, bed_out, surf_out, mask_out = \
    xgrid[ind], ygrid[ind], thk[ind], bed[ind], surf[ind], mask[ind]

# Domain must include (0,0) or you’ll get 
# an immediate segfault with no error message!
x_out -= np.min(x_out)
y_out -= np.min(y_out)
# Use the ice mask to determine the base for floating ice.
# Base is equal to bed for grounded ice
base_out = bed_out.copy()
base_out[mask_out==3] = surf_out[mask_out==3] - thk_out[mask_out==3] 
base_out[mask_out==0] = 0.0

geom = pd.DataFrame(
           { 'dummy': None,
             'x': x_out.astype(np.float64),
             'y': y_out.astype(np.float64),
             'surface': surf_out.astype(np.float64),
             'base': base_out.astype(np.float64),
             'bed': bed_out.astype(np.float64),
             'friction': 1.e10 # arbitrary friction value for now
            })

geom.to_csv(domain + '_' + str(date.today()) + '.csv', sep='\t', index=False, header=False, float_format="%10.7f")

