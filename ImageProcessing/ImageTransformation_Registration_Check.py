"""
this module creates image transformation or project for two images' registration

"""
import SaveLoad
import Visulization
from scipy import ndimage
from scipy import interpolate
import numpy as np
import scipy.ndimage as ndimage

inputDVC = SaveLoad.DVCdata("location of data") # import the DVC database

################### save the displacement, and create interpolation ##############
inter_x = interpolate.LinearNDInterpolator(inputDVC.getPoints1(), inputDVC.getDisplacementX()[0], fill_value=0.0, rescale=True) 
inter_y = interpolate.LinearNDInterpolator(inputDVC.getPoints1(), inputDVC.getDisplacementY()[0], fill_value=0.0, rescale=True) 
inter_z = interpolate.LinearNDInterpolator(inputDVC.getPoints1(), inputDVC.getDisplacementZ()[0], fill_value=0.0, rescale=True) 

image1 = inputDVC.getImage1()
image2 = inputDVC.getImage2()

sx, sy = image1[:,:,0].shape  # get dimensionality of image
mx, my = np.meshgrid(np.linspace(1,sx,sx),np.linspace(1,sy,sy))
# meshgrid change the orientation of x,y: x becomes the horizontal axis, y becomes the vertical
# this change would affect the return statement of reshape.
Cord_xy = np.vstack([mx.flatten(), my.flatten()]) # column major vector

displacementDataX = np.zeros([sy,sx, image1.shape[2]]) 
displacementDataY = np.zeros([sy,sx, image1.shape[2]])
displacementDataZ = np.zeros([sy,sx, image1.shape[2]])

imageData = np.zeros([sy,sx,image1.shape[2]])
imageData2 = np.zeros([sy,sx,image1.shape[2]])

# coordinator index
x_coor = np.zeros((sy,sx,image1.shape[2]))
y_coor = np.zeros((sy,sx,image1.shape[2]))
z_coor = np.zeros((sy,sx,image1.shape[2]))

# creating initial non-displacement group
for i in range(sy):
    for j in range(sx):
        for k in range(image1.shape[2]):
            x_coor[i,j,k] = i
            y_coor[i,j,k] = j
            z_coor[i,j,k] = k
        
# applying the displacement to index
for i in range(image1.shape[2]):
    selected = i
    xy = np.concatenate((Cord_xy, selected*np.ones([1,Cord_xy.shape[1]])), axis=0)
    extrapo_x_layer = inter_x.__call__(xy.T)
    extrapo_y_layer = inter_y.__call__(xy.T)
    extrapo_z_layer = inter_z.__call__(xy.T)
    
    ## smoothing or non-smoothing the displacement field
    reshape_extrapo_x_layer = ndimage.gaussian_filter(extrapo_x_layer.reshape(sy,sx),1) # gaussian smoother
    reshape_extrapo_y_layer = ndimage.gaussian_filter(extrapo_y_layer.reshape(sy,sx),1) # gaussian smoother
    reshape_extrapo_z_layer = ndimage.gaussian_filter(extrapo_z_layer.reshape(sy,sx),1) # gaussian smoother  

    #######################  x, y, z displacement using the interpolation  #####################
    displacementDataX[:,:,i] = reshape_extrapo_x_layer
    displacementDataY[:,:,i] = reshape_extrapo_y_layer
    displacementDataZ[:,:,i] = reshape_extrapo_z_layer
    
    #imageData[:,:,i] = im2[:,:,i]
    #imageData2[:,:,i] = im3[:,:,i]
    
finX = displacementDataX + x_coor
finY = displacementDataY + y_coor  
finZ = displacementDataZ + z_coor    
  
simage1 = np.swapaxes(image1,0,1)
simage2 = np.swapaxes(image2,0,1)
        
image3 = ndimage.map_coordinates(simage2, [finX, finY, finZ], order=1)

# showing the images' comparison
vl = Visulization.DataVisulization(simage1,1000) # initial reference image
vl.contour3d()
vl = Visulization.DataVisulization(simage2,1000) # deformed image
vl.contour3d()
vl = Visulization.DataVisulization(image3,1000) # registrated image
vl.contour3d()
        