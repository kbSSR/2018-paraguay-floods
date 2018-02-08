#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import calendar
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--psi", help="The streamfunction")
parser.add_argument("--rain", help="The streamfunction")

def main():
    """Run everything
    """
    # Read in raw data
    args = parser.parse_args()
    psi = xr.open_dataset(args.psi)
    prcp = xr.open_dataset(args.rain)

    # Plot options
    map_proj = ccrs.Orthographic(-60, -10)
    data_proj = ccrs.PlateCarree()
    months_plot = [11, 12, 1, 2]
    years_plot = [2015, 2015, 2016, 2016]
    figsize = (4 * len(months_plot), 5)

    # Initialize the plot and axes
    fig, axes = plt.subplots(
        nrows=2, ncols=len(months_plot),
        subplot_kw={'projection': map_proj}, figsize=figsize
    )
    for i, (month, year) in enumerate(zip(months_plot, years_plot)):
        def select_fun(ds):
            # Define a function to sub-set data
            ds = ds.sel(time = ds['time.month'] == month)
            ds = ds.sel(time = ds['time.year'] == year)
            return ds.mean(dim='time')

        # Plot the streamfunction
        ax = axes[0, i]
        ax.set_title('{} {}'.format(calendar.month_name[month], year))
        C0 = select_fun(psi['anomaly']).plot.contourf(
            transform=data_proj,
            ax=ax,
            cmap='PuOr',
            extend="both",
            levels=np.linspace(-6e6, 6e6, 13),
            add_colorbar=False, add_labels=False
        )

        ax = axes[1, i] # Rainfall
        C1 = select_fun(prcp['anomaly']).plot.contourf(
            transform=data_proj,
            ax=ax,
            cmap='BrBG', extend="both",
            levels=np.linspace(-10, 10, 11),
            add_colorbar=False, add_labels=False
        )

    # set up the axes
    southern_hemisphere = Region(lon=[-120, 0], lat=[-50, 5])
    south_america = Region(lon=[-85, -30], lat=[-40, -7.5])
    viz.format_axes(axes[0, :], extent = southern_hemisphere.as_extent(), border=True)
    viz.format_axes(axes[1, :], extent = south_america.as_extent(), border=True)

    # Add  color bars
    fig.tight_layout()
    fig.subplots_adjust(right=0.935)
    cax0 = fig.add_axes([0.97, 0.55, 0.01, 0.4])
    cax1 = fig.add_axes([0.97, 0.05, 0.01, 0.4])
    cbar0 = fig.colorbar(C0, cax = cax0)
    cbar0.formatter.set_powerlimits((4, 4))
    cbar0.update_ticks()
    cbar0.set_label(r'$\psi_{850}$ Anomaly [$m^2$/s]', rotation=270)
    cbar0.ax.get_yaxis().labelpad = 20
    cbar1 = fig.colorbar(C1, cax=cax1)
    cbar1.set_label('Precip. Anomaly [mm/d]', rotation=270)
    cbar1.ax.get_yaxis().labelpad = 20

    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
