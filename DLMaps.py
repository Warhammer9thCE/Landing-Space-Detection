from cStringIO import StringIO
import math
from PIL import Image
import urllib
import os.path
## @package DLMaps
# A package for the downloading of Google Maps Static API Images, containing functions
#that generate API URL's, downloading single images, dual roadmap and satellite images
#and the Mass downloading of bulk images over a large area

##---------------------------------------------------------------------------------------
#Generates a Style URL for the Google Maps Static API, to be appended on the base URL
#@param style (array): Takes a string array of Google-Maps Static API
#features in groups of 3 as in below Example
#[feature1, element1, style1...] eg ['all', 'labels', 'visibility:off']
#@return (string): Static Maps style String to be appended to the
#base google static maps URL
def StyleURL(style):
    temp = '&'
    #iterate through the entire array, generating feature list string
    #of form Feature|element|style
    for i in range(len(style)):
        if i%3 == 0:
            temp = temp + 'style=feature:' + style[i]
        if i%3 == 1:
            temp = temp + 'element:' + style[i]
        if i%3 == 2:
            temp = temp + style[i]
            #if end of array hasn't been reached, more features to add
            #add '&' for more features via Google API
            if i+1 != len(style):
                temp = temp + '&'
        #Seperate parts of feature, as per google API
        #Feature|element|style&
        if i%3 != 2:
            temp = temp + '|'
    return temp

##---------------------------------------------------------------------------------------
#Generates a full Google Static Maps API with all parameters listed
#@param lat (float): Latitude (degree) value of Geo-location
#@param lon (float): Longitude (degree) value of Geo-location
#@param zoom (int): Zoom level of Google Static Maps API, default = 17
#@param style (array): Takes a string array of Google-Maps Static API
#features in groups of 3 as in below Example,
#[feature1, element1, style1,...] eg ['all', 'labels', 'visibility:off'], default = None
#@param api (string): String with Google Static Maps API Key, default = None
#@param size (int): Image size in pixels, default = 640
#@param scale (int): Scale of Google Static Maps API, default = 2
#@param form (string): Image type to download, default = 'png'
#@param maptype (string): Map type to download, default = 'roadmap'
#@return (string): Full Google Static Maps URL for Image download
def GenerateURL(lat,lon, zoom = 17, style = None,api = None, size = 640, scale = 2, form = 'png', maptype = 'roadmap'):
    #Base URL for Google Static Maps API
    url = 'https://maps.googleapis.com/maps/api/staticmap?'

    #Append Lat + Lon co-ordiantes
    center = ','.join((str(lat), str(lon)))

    #Append the Given Features to the string
    urlPar = urllib.urlencode({'center': center,
                    'zoom': str(zoom),
                    'size': '%dx%d' % (size,size),
                    'maptype': maptype,
                    'scale': str(scale),
                    'format':str(form)})
    #Append the features list and API keys
    url = url + urlPar
    if style != None:
    	url = url + StyleURL(style)
    if api != None:
    	url = url + '&key=' + api
    return url

##---------------------------------------------------------------------------------------
#Downloads and saves a Google Maps Static API image
#@param  fileName (string): Filename to save to
#@param         subdirectory (string): Subdirectory to save in
#@param                  url (string): Google Static Maps URL to download from
#@param                form (string): Image type to save as
#@return NONE: Downloads Image via URL parameter and saves it in subdirectory/filename.form
def DLImage(fileName, subdirectory, url,form = 'png'):
    if os.path.isdir(subdirectory) == False:
        try:
            os.mkdir(subdirectory)
        except Exception:
            pass

    buffer = StringIO(urllib.urlopen(url).read())
    image = Image.open(buffer)
    fileName = os.path.join(subdirectory,fileName)
    image.save(fileName + '.' + form)

##---------------------------------------------------------------------------------------
#Computes the distance per pixel of a Google Maps Static API Image
#@param zoom (int): Zoom level of Google Static Maps API, default = 17
#@param scale (int): Scale of Google Static Maps API, default = 2
#@return (float): Distance per pixel of G-Maps Image (Km)
def PixDist(zoom=17,scale=2):
    earthCirc = 40075.0 #in Km's
    base = 256 #size of google maps at zoom = 0
    return earthCirc/(base*scale*(2**zoom)) #each zoom level is double the precision of previous

##---------------------------------------------------------------------------------------
#Computes the Total Pixel Distance between 2 identically sized Google Maps Static API Images
#@param distpp (float): Distance per pixel (Km), from PixDist function
#@param scale (int): Scale of Google Static Maps API, default = 2
#@param size (int): Image size in pixels, default = 640
#@return (float): Total Distance (Km) between 2 identically featured
#G-Maps Images
def DistNextImage(distpp, scale=2, size=640):
    return distpp*scale*size

##---------------------------------------------------------------------------------------
#Computes the New Latitude and Longitude co-ordinates given a direction and distance
#using the Mercator Projection Method, complete accuracy not assured
#@param lat (float): Latitude (degree) value of Geo-location
#@param lon (float): Longitude (degree) value of Geo-location
#@param dist (float): Distance (Km) to travel in new direction
#@param direction (int): Direction to travel, takes integer value
#North = 1, East = 2, South = 3, West = 4
#@return (float): New latitude co-ordinate
#@return (float): New longitude co-ordinate
def NewLatLon(lat,lon, dist, direction):
    LAT_Constant = 110.54 #Km distance per change in latitude degree
    LON_Constant = 110.32 #Km distance per change in longitude degree
    if direction==1:
        dist = dist/LAT_Constant #approximate change in latitude mercator projection
        lat = lat + dist #heading north
    elif direction == 2:
        dist = dist/(LON_Constant * math.cos(math.pi*lat/180.0)) #approx change in lon
        lon = lon + dist #heading east
    elif direction==3:
        dist = dist/LAT_Constant #approximate change in latitude mercator projection
        lat = lat - dist #heading south
    elif direction ==4:
        dist = dist/(LON_Constant * math.cos(math.pi*lat/180.0)) #approx change in lon
        lon = lon - dist #heading west
    return lat, lon


##---------------------------------------------------------------------------------------
#Downloads a mass amount of images using a spiral arm extension method. Using a centre point and
#a maximum width, it will continue to download images until the max width is reached.
#@param lat (float): Starting Latitude (degree) value of Geo-location
#@param lon (float): Starting Longitude (degree) value of Geo-location
#@param user (string): String with Google Static Maps API Key
#@param style (array): Takes a string array of Google-Maps Static API
#features in groups of 3 as in below Example,
#[feature1, element1, style1,...] eg ['all', 'labels', 'visibility:off'], default = None
#@param subdirectory (string): Subdirectory to save in, default = "GMAPS"
#@param zoom (int): Zoom level of Google Static Maps API, default = 17
#@param width (float): Max Latitude change (km), default = 10
#@return NONE: Initiates a Mass Dual Maps download with Given (lat,lon)
#Co-Ordinates, continuing in spiral pattern until width variable has been reached
def SpiralDl(lat,lon, user=None, style=None, subdirectory='GMAPS',zoom=17,width=10):
    direction = 1 #initial Direction (North), clockwise mod4 directions
    startLat = lat #store the starting latitude for comparison with max latitude change
    distpp = PixDist(zoom) #save distance per pixel with given zoom level
    dImage = DistNextImage(distpp) #save approx Km change between images
    count = 0
    #generate the first as a starting point
    DualMapDL(lat,lon,zoom,subdirectory,style,user)
    print '\n',
    while width>0: #while Change in Latitude is less than desired
        if count >0:
            width = width - dImage
        count = count + 1 #Slowly extending length of spiral arm
        #With starting position already downloaded, spiral arm continues out
        #by increasing the arm length every second iteration
        for i in range(1,2): #Loop until new arm length needed
            #Compute new arm length direction, clockwise mod4
            if direction != 4:
                direction = direction + 1
            else:
                direction = 1
            #Download maps over length of arm
            for j in range(1,count):
                lat, lon = NewLatLon(lat,lon,dImage,direction)
                DualMapDL(lat,lon,zoom,subdirectory,style,user)
                print '\tKm Left to go:',width

##---------------------------------------------------------------------------------------
#Downloads a Dual Pair of images from the Google Maps Static API, both the roadmap and satellite images
#corresponding to the given co-ordinates
#@param lat (float): Latitude (degree) value of Geo-location
#@param lon (float): Longitude (degree) value of Geo-location
#@param zoom (int): Zoom level of Google Static Maps API
#@param directory (string): Subdirectory to save in
#@param style (array): Takes a string array of Google-Maps Static API
#features in groups of 3 as in below Example,
#[feature1, element1, style1,...] eg ['all', 'labels', 'visibility:off'], default = None
#@param api (string): String with Google Static Maps API Key, default = None
#@param scale (int): Scale of Google Static Maps API, default = 2
#@param size (int): Image size in pixels, default = 640
#@param form (string): Image type to save as, default = 'png'
#@return NONE: Downloads Both the Roadmap and Satellite map, given the
#above parameters and saves them in directory/*.form
def DualMapDL(lat,lon,zoom,directory,style=None,api=None,size=640,scale=2,form ='png'):
	#Generate the Roadmap URL for download, and filename to save as
    try:
        url = GenerateURL(lat,lon,zoom, style, api, size,scale,form)
        fileName = 'zoom=' + str(zoom) +':'+ ','.join((str(lat), str(lon))) + ':Roadmap'
        DLImage(fileName,directory,url,form)
    	#Generate the Satellite URL for download, and filename to save as
        url = GenerateURL(lat,lon,zoom, style, api,size,scale,form, maptype = 'satellite')
        fileName = 'zoom=' + str(zoom) +':'+ ','.join((str(lat), str(lon))) + ':Satellite'
        DLImage(fileName,directory,url,form)
        print 'Dual Download Success: (Lat,Long) = (%.6f,%.6f)' %(lat,lon),
        # print 'Dual Download Success: (Lat,Lon) = (' + str(lat) + ' , ' + str(lon) +')',
    except RuntimeError:
        print 'Dual Download Failure: (Lat,Long) = (%.6f,%.6f)' %(lat,lon),
