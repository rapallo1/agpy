"""
Generate a cutout image from a .fits file
"""
import pyfits
import copy
import numpy

def cutout(file,xc,yc,xw=25,yw=25,units='pixels',outfile=None):
    """
    Inputs:
        file  - .fits filename or pyfits HDUList (must be 2D)
        xc,yc - x and y coordinates in the fits files' coordinate system
        xw,yw - x and y width 
        units - specify units to use: either pixels or wcs
        outfile - optional output file
    """

    if isinstance(file,str):
        file = pyfits.open(file)
    elif isinstance(file,pyfits.HDUList):
        file = copy.copy(file)
    else:
        raise Exception("cutout: Input file is wrong type (string or HDUList are acceptable).")

    head = file[0].header
    if head['NAXIS'] > 2:
        raise Exception("Too many (%i) dimensions!" % head['NAXIS'])
    try:
        cd1 = head['CDELT1']
        cd2 = head['CDELT2']
    except:
        try:
            cd1 = head['CD1_1']
            cd2 = head['CD2_2']
        except:
            raise Exception("No CD or CDELT keywords in header")

    lonarr = ((numpy.arange(head['NAXIS1'])-head['CRPIX1'])*cd1 + head['CRVAL1'] )
    latarr = ((numpy.arange(head['NAXIS2'])-head['CRPIX2'])*cd2 + head['CRVAL2'] )

    xx = numpy.argmin(numpy.abs(xc-lonarr))
    yy = numpy.argmin(numpy.abs(yc-latarr))

    if units=='pixels':
        xmin,xmax = numpy.max([0,xx-xw]),numpy.min([head['NAXIS1'],xx+xw])
        ymin,ymax = numpy.max([0,yy-yw]),numpy.min([head['NAXIS2'],yy+yw])
    elif units=='wcs':
        xmin,xmax = numpy.max([0,xx-xw/numpy.abs(cd1)]),numpy.min([head['NAXIS1'],xx+xw/numpy.abs(cd1)])
        ymin,ymax = numpy.max([0,yy-yw/numpy.abs(cd2)]),numpy.min([head['NAXIS2'],yy+yw/numpy.abs(cd2)])
    else:
        raise Exception("Can't use units %s." % units)

    img = file[0].data[ymin:ymax,xmin:xmax]

    file[0].data = img

    head['CRPIX1']-=xmin
    head['CRPIX2']-=ymin
    head['NAXIS1']=img.shape[1]
    head['NAXIS2']=img.shape[0]

    if isinstance(outfile,str):
        file.writeto(outfile)

    return file
