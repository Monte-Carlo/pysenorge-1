#!/usr/bin/python
# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredtext'
'''
Calculates the average and maximum wind speed and the prevailing wind direction
based on hourly wind vector data.

A netcdf file with hourly data from 07:00 to 06:00 UTC serves as data source.
The amplitude of the hourly wind vectors is calculated for each cell. 
The amplitudes are then averaged over 24h. The result is interpolated from the 
4 km UM grid to the 1 km seNorge grid.

Command line usage:
===================
    python //~/pysenorge/themes/wind_600m_daily.py YYYY-MM-DD [options]
    
Daily production usage:
=======================
    python //~/pysenorge/themes/wind_600m_daily.py YYYY-MM-DD

Todo:
=====
- Make dependent on wind direction. Read wind direction - determine 
    predominant wind direction - calculated average wind speed in predominant 
    wind direction (avg all wind speed might give false alarm). Wind directions 
    can be classified in either 4 or 8 regions (90 or 45 degrees).
- Path to clt files is hard-coded.

:Author: kmu
:Date: 14. nov. 2011

Changed:
========
- Added a test that checks that the 3-D matrix is multiplied correctly.
- Added a theme showing max wind gust last 24 h.
- Added a theme showing prevailing wind direction last 24 h.
'''

''' IMPORTS '''
# Built-in
import os, time
#import math
from datetime import timedelta
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))  

# Additional
try:
    from netCDF4 import Dataset
except ImportError:
    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
    except ImportError:
        print '''WARNING: Can not find module "netCDF4" or "Scientific.IO.NetCDF"!
        Please install for netCDF file support.'''
from numpy import sqrt, mean, flipud, zeros_like, zeros, uint16#, arctan2

# Own
from pysenorge.set_environment import netCDFin, BILout, \
                                      FloatFillValue, UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.io.png import writePNG
from pysenorge.tools.date_converters import iso2datetime, datetime2BILdate, get_hydroyear
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate
#from pysenorge.functions.lamberts_formula import LambertsFormula


def model(x_wind, y_wind):
    """
    Calculates avg. and max. wind speed and prevailing wind direction from the
    x and y vector components.
    
    Parameters:
    ===========
    - x_wind: Wind vector component in *x*-direction
    - y_wind: Wind vector component in *y*-direction
    """    
    total_wind = sqrt(x_wind**2 + y_wind**2)
#    dims = total_wind.shape
    total_wind_avg = mean(total_wind, axis=0)
    max_wind = zeros_like(total_wind_avg)
#    wind_dir_cat = zeros_like(total_wind_avg)
#    wind_dir = arctan2(y_wind, x_wind)
#    
#    for i in xrange(dims[1]):
#        for j in xrange(dims[2]):
#            max_wind[i][j] = total_wind[:,i,j].max()
#            # Init compass direction counters
#            N = 0
#            NE = 0
#            E =0
#            SE = 0
#            S = 0
#            SW = 0
#            W = 0
#            NW = 0
#            for k in xrange(dims[0]):
#                alpha = wind_dir[k,i,j]
#                degalpha = math.degrees(alpha)
#                
#                # Translate to cardinal wind direction from which wind originates.
#                # Arrow at 0 degree points towards east.
#                if degalpha >= 0.0:
#                    if degalpha >=0.0 and degalpha<22.5:
#                        W += 1 
#                    elif degalpha >=22.5 and degalpha<67.5:
#                        SW += 1
#                    elif degalpha >=67.5 and degalpha<112.5:
#                        S += 1
#                    elif degalpha >=112.5 and degalpha<157.5:
#                        SE += 1
#                    elif degalpha >=157.5 and degalpha<=180.0:
#                        E += 1 
#                if degalpha < 0.0:
#                    if degalpha <0.0 and degalpha>=-22.5:
#                        W += 1
#                    elif degalpha <-22.5 and degalpha>=-67.5:
#                        NW += 1
#                    elif degalpha <-67.5 and degalpha>=-112.5:
#                        N += 1
#                    elif degalpha <-112.5 and degalpha>=-157.5:
#                        NE += 1
#                    elif degalpha <-157.5 and degalpha>=-180.0:
#                        E += 1
#                        
#            wind_dir_cat[i][j] = LambertsFormula(N, NE, E, SE, S, SW, W, NW)
                        
    return total_wind_avg, max_wind#, wind_dir_cat


def main():
    """
    Loads and verifies input data, calls the model, and controls the output stream. 
    
    Command line usage::
    
        python //~HOME/pysenorge/themes/wind_600m_daily.py YYYY-MM-DD [options]
    """
    # Theme variables
    themedir1 = 'wind_speed_avg_600m'
    themedir2 = 'wind_speed_max_600m'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/wind_600m_daily.py YYYY-MM-DD [options]"
    
    parser = OptionParser(usage=usage)

    parser.add_option("-t", "--timerange", 
                      action="store", dest="timerange", type="string",
                      default="[2,8]",
                      help='''Time-range as "[6,30]"''')
    parser.add_option("--no-bil",
                      action="store_false", dest="bil", default=True,
                      help="Set to suppress output in BIL format")
    parser.add_option("--nc",
                      action="store_true", dest="nc", default=False,
                      help="Set to store output in netCDF format")
    parser.add_option("--png",
                      action="store_true", dest="png", default=False,
                      help="Set to store output as PNG image")
    
    # Comment to suppress help
#    parser.print_help()

    (options, args) = parser.parse_args()
    
    # Verify input parameters
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    # get current datetime
    
    #############
    
    
    ### different for prognosis files
    ### date corresponds to start, not end as in my convention
    
    
    #############
    cdt = iso2datetime(args[0]+" 06:00:00")
    ncfilename = "UM4_ml00_%s.nc" % datetime2BILdate(cdt-timedelta(days=1)) # e.g. UM4_ml_2010_11_28.nc
    
    if len(args) != 1:
        parser.error("Please provide an input file!")
    else:
        # Add full path to the filename
        ncfile = os.path.join(netCDFin, str(cdt.year), ncfilename)
    
    timerange = eval(options.timerange)
    
    if not os.path.exists(ncfile):
        parser.error("%s does not exist!" % ncfile)
    else:
        if timerange == None:
            # Load wind data from prognosis (netCDF file) for entire time-range
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][:]
            x_wind = ds.variables['x_wind_600m'][:,:,:]
            y_wind = ds.variables['y_wind_600m'][:,:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()
        else:
            # Load wind data from prognosis (netCDF file) for selected time-range
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][timerange[0]:timerange[1]]
            x_wind = ds.variables['x_wind_600m'][timerange[0]:timerange[1],:,:]
            y_wind = ds.variables['y_wind_600m'][timerange[0]:timerange[1],:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()
            
#    from netCDF4 import num2date
#    for t in wind_time:
#        print num2date(t, "seconds since 1970-01-01 00:00:00 +00:00")
    
    print "Using input data from file %s" % ncfilename
    
    # Setup outputs
    _tstart = time.gmtime(wind_time[0])
    tstruct = time.gmtime(wind_time[-1]) # or -1 if it should be the average until that date
    print "For the period %s-%s-%s:%s - %s-%s-%s:%s" % (str(_tstart.tm_year).zfill(4),
                               str(_tstart.tm_mon).zfill(2),
                               str(_tstart.tm_mday).zfill(2),
                               str(_tstart.tm_hour).zfill(2),
                               str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2),
                               str(tstruct.tm_hour).zfill(2))
    outfile1 = '%s_%s_%s_%s' % (themedir1, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    outfile2 = '%s_%s_%s_%s' % (themedir2, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    
    outdir1 = os.path.join(BILout, themedir1, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir1):
        if not os.path.exists(os.path.join(BILout, themedir1)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir1)
        os.chdir(os.path.join(BILout, themedir1))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

    outdir2 = os.path.join(BILout, themedir2, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir2):
        if not os.path.exists(os.path.join(BILout, themedir2)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir2)
        os.chdir(os.path.join(BILout, themedir2))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

    # Calculate the wind speed vector - using model()
    total_wind_avg, max_wind = model(x_wind, y_wind)
    
    # interpolate total average wind speed to seNorge grid
    total_wind_avg_intp = interpolate(rlon, rlat, total_wind_avg)
    max_wind_intp = interpolate(rlon, rlat, max_wind)
#    wind_dir_intp = interpolate(rlon, rlat, wind_dir)
    
    
    # Replace NaN values with the appropriate FillValue
    total_wind_avg_intp = nan2fill(total_wind_avg_intp)
    max_wind_intp = nan2fill(max_wind_intp)
#    wind_dir_intp = nan2fill(wind_dir_intp)
    
    if options.bil:
        from pysenorge.grid import senorge_mask
        
        mask = senorge_mask()
        
        # Write to BIL file
        
        # avg wind
        bil_avg_wind = flipud(uint16(total_wind_avg_intp*10.0))
        bil_avg_wind[mask] = UintFillValue
        
        bilfile = BILdata(os.path.join(outdir1,
                          outfile1+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_avg_wind.flatten()) # collapsed into one dimension
        print biltext
        
        #  max wind
        bil_max_wind = flipud(uint16(max_wind_intp*10.0))
        bil_max_wind[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir2,
                          outfile2+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_max_wind.flatten())
        print biltext
        
#        # wind direction
#        bil_dir_wind = flipud(uint16(wind_dir_intp))
#        bil_dir_wind[mask] = UintFillValue
#        bilfile = BILdata(os.path.join(outdir,
##                          'wind_direction_10m'+'_'+dtstr+'.bil'),
#                          outfile+'.bil'),
#                          datatype='uint16')
#        biltext = bilfile.write(bil_dir_wind.flatten())
#        print biltext
    
    if options.nc:
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir1, outfile1+'.nc'))
#        ncfile.rootgrp.info = themename
        ncfile.new(wind_time[-1])
        
        ncfile.add_variable('avg_wind_speed', total_wind_avg.dtype.str, "m s-1",
                            'Average wind speed last 24h', total_wind_avg_intp)
        ncfile.add_variable('max_wind_speed', max_wind.dtype.str, "m s-1",
                            'Maximum wind gust last 24h', max_wind_intp)
#        ncfile.add_variable('wind_direction', wind_dir.dtype.str,
#                            "cardinal direction",
#                            'Prevailing wind direction last 24h', wind_dir_intp)
        ncfile.close()
        
    if options.png:
        # Write to PNG file
        writePNG(total_wind_avg_intp[0,:,:],
                 os.path.join(outdir1, outfile1),
                 cltfile=r"Z:\tmp\wind_600m_daily\avg_wind_speed_600_no.clt"
                 )
        writePNG(max_wind_intp[0,:,:],
                 os.path.join(outdir2, outfile2),
                 cltfile=r"Z:\tmp\wind_600m_daily\max_wind_speed_600_no.clt"
                 )
#        writePNG(wind_dir_intp[0,:,:],
#                 os.path.join(outdir, 'wind_direction'+'_'+dtstr),
#                 cltfile=r"Z:\tmp\wind_600m_daily\wind_direction_600_no.clt"
#                 )
    
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"


def clt_avg_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(UintFillValue, 16,
              'Gjennomsnittlig vindhastighet',
              'Gjennomsnittlig vindhastighet i 600 m h�yde',
              'Vindstyrke')
    cltlist = [CLTitem(36.7, 300.0, (255,74,74), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (126, 0, 255), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (255,194,74), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (255,255,74), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (194,224,74), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (134,194,74), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (74,164,74), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (74,194,134), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (74,224,194), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (74,255,255), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (74,194,224), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_600m_daily\avg_wind_speed_600_no.clt")
    
    
def clt_max_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(UintFillValue, 16,
              'Maksimal vindhastighet',
              'Maksimal vindhastighet i 600 m h�yde',
              'Vindstyrke')
    cltlist = [CLTitem(36.7, 300.0, (255,74,74), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (126, 0, 255), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (255,194,74), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (255,255,74), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (194,224,74), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (134,194,74), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (74,164,74), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (74,194,134), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (74,224,194), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (74,255,255), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (74,194,224), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_600m_daily\max_wind_speed_600_no.clt")


def clt_wind_direction_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(UintFillValue, 16,
              'Hovedvindretning',
              'Hovedvindretning i 600 m h�yde',
              'Himmelretning')
    cltlist = [CLTitem(0, 1, (0,0,255), 'N'),
               CLTitem(1, 2, (126, 0, 255), 'N�'),
               CLTitem(2, 3, (255, 0, 215), '�'),
               CLTitem(3, 4, (255, 126, 0), 'S�'),
               CLTitem(4, 5, (255, 0, 0), 'S'),
               CLTitem(5, 6, (255, 245, 0), 'SV'),
               CLTitem(6, 7, (0, 255, 0), 'V'),
               CLTitem(7, 8, (0, 230, 255), 'NV'),
               CLTitem(8, 255, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_600m_daily\wind_direction_600_no.clt")

def clt_wind_direction_no_v2():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(UintFillValue, 16,
              'Hovedvindretning siste d�gn',
              'Hovedvindretning i 600 m h�yde',
              'Himmelretning')
    cltlist = [CLTitem(0, 1, (0, 16, 165), 'N'),
               CLTitem(1, 2, (0, 100, 181), 'N�'),
               CLTitem(2, 3, (15, 173, 0), '�'),
               CLTitem(3, 4, (140, 199, 0), 'S�'),
               CLTitem(4, 5, (255, 255, 20), 'S'),
               CLTitem(5, 6, (255, 148, 0), 'SV'),
               CLTitem(6, 7, (255, 40, 40), 'V'),
               CLTitem(7, 8, (197, 0, 124), 'NV'),
               CLTitem(8, UintFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\snowsim\wind_600m_daily\wind_direction_600_no.clt")


def clt_wind_direction_en():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(UintFillValue, 16,
              'Prevailing wind direction last 24h',
              'Prevailing wind direction at 600 m above ground',
              'Cardinal direction')
    cltlist = [CLTitem(0, 1, (0, 16, 165), 'N'),
               CLTitem(1, 2, (0, 100, 181), 'NE'),
               CLTitem(2, 3, (15, 173, 0), 'E'),
               CLTitem(3, 4, (140, 199, 0), 'SE'),
               CLTitem(4, 5, (255, 255, 20), 'S'),
               CLTitem(5, 6, (255, 148, 0), 'SW'),
               CLTitem(6, 7, (255, 40, 40), 'W'),
               CLTitem(7, 8, (197, 0, 124), 'NW'),
               CLTitem(8, UintFillValue, (255, 255, 255), 'No data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\snowsim\wind_600m_daily\wind_direction_600_en.clt")
    

def _test():
    """
    Test "model()" with a benchmark dataset.
    """
    # Init x and y wind components
    x_wind = zeros((3,12,10))
    y_wind = zeros((3,12,10)) 
    
    # Upper left corner blows from N with "Stiv kuling"
    y_wind[:,6:12,0:5] = -14.0
    
    # Upper right corner blows from SE with "Orkan"
    x_wind[:,6:12,5:10] = -32.0
    y_wind[:,6:12,5:10] = 32.0
    
    # Lower left corner blows from W with "Svak wind"
    x_wind[:,0:6,0:5] = 2.0
    
    # Lower right corner blows from NW with "Full storm"
    x_wind[:,0:6,5:10] = 20.0
    y_wind[:,0:6,5:10] = -20.0
    
    total_wind_avg, max_wind, wind_dir_cat = model(x_wind, y_wind)
    print total_wind_avg.shape, max_wind.shape, wind_dir_cat.shape
    
    total_wind_avg = nan2fill(total_wind_avg)
    max_wind = nan2fill(max_wind)
    wind_dir_cat = nan2fill(wind_dir_cat)
    
    testdir = r'Z:\tmp\wind_600m_daily'
    writePNG(total_wind_avg, os.path.join(testdir, 'test_avg'),
             os.path.join(testdir, 'avg_wind_speed_600_no.clt'))
    writePNG(max_wind, os.path.join(testdir, 'test_max'),
             os.path.join(testdir, 'max_wind_speed_600_no.clt'))
    writePNG(wind_dir_cat, os.path.join(testdir, 'test_dir'),
             os.path.join(testdir, 'wind_direction_600_no.clt'))


if __name__ == '__main__':
    main()

#    clt_avg_wind_speed_no()
#    clt_max_wind_speed_no()
#    clt_wind_direction_no()
#    clt_wind_direction_no_v2()
#    clt_wind_direction_en()
#    _test()