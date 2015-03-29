## @package MapClasses
# Package containing functions regarding converting image data into classified
# probabilities, Subdividing images, converting images to float format

from skimage.io import imread, imsave
from skimage import img_as_float, img_as_ubyte,img_as_uint
import numpy as np

#define the classes for the maps, and their relevant pixel data for the roadmap
#classes are as follows
#1: Park
#2: Yard
#3: Roof
#4: roadmap
#5: Highway
#6: Water
#7: Other

#define dictionary to handle all the classes with RGB pixel colour as key, and
#class number as value, ie key:value
# MapClasses = { (R,G,B):1, (R,G,B):2 }

##
# Converts an array of image pixel data to it's float representation with values
# between 0 and 1
# @param pixels The array of pixels to convert
# @return Pixels converted to float
def ConvertFloat(pixels):
    try:
        pixels = img_as_float(pixels)
        print "Data successfully converted"
    except RuntimeError:
        print "File Could not be converted to float"
    return pixels

##
# Opens an image file and loads the pixel data, converting it to float notation
# @param file name of file to be opened
# @return pixel data in float notation
def GenData(file):
    pixData = imread(file)
    print file, "has been loaded... Shape:", pixData.shape, "\t",
    pixData = ConvertFloat(pixData)
    return pixData
##
# Subdivides a square image into a smaller subset of images of the form (b,x,y,c)
# where b is image index, x is width, y is height, c is RGB pixel triplet
# @param image array of (x,y,c) pixel data
# @param divider pixel division of wanted subdivided images, must be a factor of x,y
# @return (b,x,y,c) array of new image data.
def Subsection(image,divider):
    size = image.shape
    fac = Factor(size[0])
    if not divider in fac:
        raise Exception ("Divider must be a factor of image size")

    sections = size[0]/divider
    data = np.zeros(((sections**2),divider,divider,3),dtype=float)
    count = 0
    try:
        for i in range(0,sections):
            for j in range(0,sections):
                np.copyto(data[count],image[(i*divider):((i+1)*divider),(j*divider):((j+1)*divider),:])
                count = count + 1
        print "Image successfully divided. New array size:",data.shape
    except RuntimeError:
        print "Image could not be divided"
    return data



##
# Finds all factors of a given number
# @param size Integer value to factorize
# @return array of all factors
def Factor(size):
    return [x for x in range(1,size+1) if size%x == 0]

#define function that takes an image, converts it into sub-images and finds
#the relevant classes in the sub-images. Then save the sub-image class data
#as a 3d matrix. Height x width x depth being image-grid x image-grid x classes
#respectively. One layer of depth per class. Function needs to be moddable
#as well as the class creation. Save this data with relevant image information
#so data can be recaptured later for the satellite imagery.

#Seperate function to save the class matrix

#function to either input classes, or read classes from init file
