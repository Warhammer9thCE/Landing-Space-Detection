import h5py
import numpy as np
from PIL import Image
from skimage.io import imread,imsave
import os
import glob

#OpenImage takes a file input and returns the numpy array with
#pixel data and the header file
def OpenImage(file):
    im = Image.open(file).convert('RGB')
    print im
    pix = np.array(im)
    return im, pix, (im.size[1],im.size[0])

#StoreData(hdf5File,group,data) opens the hdf5File, opens the
#group and appends the given data to the group in the form (b,c,0,1)
def StoreImage(hdf5File,group,data):
    with h5py.File(hdf5File, "r+") as f:
        dset = f[group]
        rdata = dset[...]
        size = rdata.shape

        #check if the b=0th elemenet has any data stored, if it does, then it appends
        #a new b element onto the list and stores the new array. Used because it will
        #initially skip over the 0th element if not.
        if dset[0].any():
            dset.resize((size[0]+1,size[1],size[2],size[3]))
        dset[size[0]-1] = data

#ConvertData(data) turns a pixel array into (b,c,0,1) format
#where b is HDF5 index, c is RGB pixel tuple, 0 is vertical
#index, 1 is horizontal index. Function returns the (c,0,1)
#submatrix for later storage into HDF5 index b
def ConvertData(data):
    data = np.swapaxes(data,1,2)
    data = np.swapaxes(data,0,1)
    return data

def ReConvertData(data):
    data = np.swapaxes(data,0,1)
    data = np.swapaxes(data,1,2)
    return data

#Initially creates the HDF5File with 2 groups, satellite and roadmap.
def Init(hdf5File,width,height):
    with h5py.File(hdf5File, "w") as f:
        sat = f.create_dataset('satellite',(1,3,width,height),maxshape=(None,None,None,None),compression="gzip")
        road = f.create_dataset('roadmap',(1,3,width,height),maxshape=(None,None,None,None),compression="gzip")
        imgData = f.create_dataset('meta',(1,2,1),maxshape=(None,None,None,None),compression="gzip")

def Debug(hdf5File,group):
    with h5py.File(hdf5File, "r") as f:
        print 'Now Debugging:'
        dset = f[group]
        data = dset[...]
        print 'HDF5 data shape:',data.shape
        pix = ReConvertData(data[0])
        print 'Pixel shape after conversion:',pix.shape
        img = Image.fromarray(pix,'RGB')
        print img
        img.save('debug.png')
        return pix

def Run(hdf5File,directory,filetype):
    search = directory+'/*.'+filetype

    #iterate through every file of filetype in the subdirectory
    for file in glob.glob(search):
        im, pix, size = OpenImage(file)
        try:
            pix = ConvertData(pix)
        except RuntimeError:
            print "Conversion of",file," has failed"
            break
        group = None
        if 'Roadmap' in file:
            group = 'roadmap'
        if 'Satellite' in file:
            group = 'satellite'
        if group is not None:
            StoreImage(hdf5File,group,pix)
        else:
            print("Non-Static API image found: ",file)

if __name__ == "__main__":

    file = 'LSD.HDF5'
    directory = 'zoom=17'
    filetype = 'png'
    sat = 'satellite'
    road = 'roadmap'
    test = 'test.jpg'
    width = 1280
    height = 1280

    # Init(file,width,height)
    # Run(file,directory,filetype)
    # Debug(file,sat)
    pixData = Debug(file,sat)
    for file2 in glob.glob(directory+'/*.'+filetype):
        if 'Satellite' in file2:
            imgSat,pixSat,sizeSat = OpenImage(file2)
            print pixSat.dtype
            print pixData.dtype
            # print pixSat==pixData
