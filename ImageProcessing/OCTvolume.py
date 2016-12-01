"""
this creates volume object

"""

import os
import ImageProcessing
import numpy as np

class OCTimage(object):
    """
    root class OCT image
    """ 
    def __init__(self, PathTiff, start=None, end=None):
        
        if type(PathTiff) is not str:
            raise TypeError("the input address must be a string!")

        elif not os.path.isdir(PathTiff):
            raise TypeError("the input string must be a valid directory!")

        else:
            self.address = PathTiff # address to access the tiff images
        self._start = start
        self._end = end
        self._volume_data = self.read()
        if start or end:
            self._state = True # False if none cropped (default), True Ohterwise
        else:
            self._state = False
        
    def read(self):
        if self._start and self._end:
            out = ImageProcessing.readPartialOCTstack(self.address, self._start, self._end)
            print "read partial the image stacks: " + str(self._start)+ " to " + str(self._end)
            print "read the image stack size: " + str(out.shape)     
    
        else:
            out = ImageProcessing.readOCTstack(self.address)
            print "read all the image stacks"
            print "read the image stack size: " + str(out.shape)
            
        ##############  output ###############
        print "the volume max: " + str(out.max())
        print "the volume min: " + str(out.min())
        print "the volume mean: " + str(out.mean())    
        return out

class RefVolume(OCTimage):
    """
    reference volume class:
        this class should read the tiff image stack and convert it into nd-arrary
        
        it should contain several class methods including:
        1) create volume from images
        2) noise reduction volume, dynamic range, ostu method
        3) create binary domain
        4) volume discretization 
        ...        
    """
    def __init__(self, address,start=None,end=None):
        """
        initialize the class
        """
        OCTimage.__init__(self, address, start, end)
        self._convex_xy = None # the list stores the x dimension of convex, the z dimension is as the index of element in list
        self._periPoint = None
        self._logicSlice = None
        self._block_volume = None
        self._denoise_volume = None
        self._binary_volume = None

    def denoise(self,size, inRange):
        """
        median_filter on the block volume
        size --- for median filter
        inRange --- for Dynamic Range 
        """
        temp_volume = ImageProcessing.medOCT(self._block_volume, size)
        self._denoise_volume = ImageProcessing.DynamicRangeImage(temp_volume, inRange)
    
    def binary(self, threshold):
        self._binary_volume = ImageProcessing.toBinary(self._denoise_volume, threshold)
  
    def points(self, number = None):
        """
        selection convex points in the image
        number --- the slice number in the volume
        """
        if number:
            PointBuilder = ImageProcessing.KeyPoints(self._volume_data[:,:,number])
        else:
            sx, sy, sz = self._volume_data.shape
            PointBuilder = ImageProcessing.KeyPoints(self._volume_data[:,:,sz//2])
                    
        return PointBuilder
        
    def segmentation(self, points, useSnake = True): 
        
        ## make ellipse
        if len(points)==0:
            print "the input points size is ZERO!"
            return None
        
        Initial_ellipsePoints = ImageProcessing.FindEllipse(points)
        
        self._convex_xy = Initial_ellipsePoints # back up the data
                
        outPoints = []
        
        if self._state == False:
            for i in range(self._volume_data.shape[2]): # iterating through the vertical stacks
                print i
                slice_snake = np.empty([Initial_ellipsePoints.shape[0],3]) # Make N by 3 points
                
                if useSnake == True:
                    snake = ImageProcessing.ActiveEllipse(self._volume_data[:,:,i], Initial_ellipsePoints)
                else:
                    snake = Initial_ellipsePoints
                    
                slice_snake[:,0] = snake[:,0] # create 3d points
                slice_snake[:,1] = snake[:,1]
                slice_snake[:,2] = i
                outPoints.append(slice_snake)
                
        elif self._state == True:
            for i in range(self._start, self._end+1): # iterating through the vertical stacks
                print i
                slice_snake = np.empty([Initial_ellipsePoints.shape[0],3]) # Make N by 3 points 
                
                if useSnake == True:
                    snake = ImageProcessing.ActiveEllipse(self._volume_data[:,:,i], Initial_ellipsePoints)
                else:
                    snake = Initial_ellipsePoints
                    
                slice_snake[:,0] = snake[:,0] # create 3d points
                slice_snake[:,1] = snake[:,1]
                slice_snake[:,2] = i
                outPoints.append(slice_snake)
                
        for i in range(len(outPoints)): # reshape the list
            if i == 0: fb = outPoints[i]  
            else: fb = np.concatenate((fb,outPoints[i]),axis=0)
            
        self._periPoint = fb
        
    def blockImage(self):
        """
        this use the perPoint to create convex hull and logical operation for each slice
        """
        self._logicSlice = ImageProcessing.LogicRegion(self._volume_data[:,:,self._volume_data.shape[2]//2], self._convex_xy)
        self._block_volume = np.empty_like(self._volume_data)
        if self._state == False:
            for i in range(self._volume_data.shape[2]):
                self._block_volume[:,:,i] = self._volume_data[:,:,i] * self._logicSlice
                
        elif self._state == True:
             for i in range(self._start, self._end+1): 
                self._block_volume[:,:,i] = self._volume_data[:,:,i] * self._logicSlice
        
    def threshold(self, block_size):
        return ImageProcessing.sliceThreshold(self._volume_data, block_size)
        
    def distImage(self):
        pass
        
    def meshSampling(self):
        pass
        
    def kltSampling(self):
        pass
        
    def getVolume(self):
        return self._volume_data
         
class DefVolume(OCTimage):
    """
    reference volume class:
        this class should read the tiff image stack and convert it into nd-arrary
        
        it should contain several class methods including:
        1) create volume from images
        2) noise reduction volume, dynamic range, ostu method
        3) create binary domain
        4) volume discretization 
        ...        
    """
    def __init__(self, address,start=None,end=None):
        """
        initialize the class
        """
        OCTimage.__init__(self, address, start, end)
        self._convex_xy = None # the list stores the x dimension of convex, the z dimension is as the index of element in list
        self._periPoint = None
        self._logicSlice = None
        self._block_volume = None
        self._denoise_volume = None
        self._binary_volume = None
        
    def denoise(self,size, inRange):
        """
        median_filter on the block volume
        size --- for median filter
        inRange --- for Dynamic Range 
        """
        temp_volume = ImageProcessing.medOCT(self._block_volume, size)
        self._denoise_volume = ImageProcessing.DynamicRangeImage(temp_volume, inRange)
        
    def binary(self, threshold):
        self._binary_volume = ImageProcessing.toBinary(self._denoise_volume, threshold)
        
    def points(self, number = None):
        """
        selection convex points in the image
        number --- the slice number in the volume
        """
        if number:
            PointBuilder = ImageProcessing.KeyPoints(self._volume_data[:,:,number])
        else:
            sx, sy, sz = self._volume_data.shape
            PointBuilder = ImageProcessing.KeyPoints(self._volume_data[:,:,sz//2])
                    
        return PointBuilder
        
    def segmentation(self, points, useSnake = True): 
        
        ## make ellipse
        if len(points)==0:
            print "the input points size is ZERO!"
            return None
        
        Initial_ellipsePoints = ImageProcessing.FindEllipse(points)
        
        self._convex_xy = Initial_ellipsePoints # back up the data

        outPoints = []
        
        if self._state == False:
            for i in range(self._volume_data.shape[2]): # iterating through the vertical stacks
                print "uncropped: " + str(i)
                slice_snake = np.empty([Initial_ellipsePoints.shape[0],3]) # Make N by 3 points
                
                if useSnake == True:
                    snake = ImageProcessing.ActiveEllipse(self._volume_data[:,:,i], Initial_ellipsePoints)
                else:
                    snake = Initial_ellipsePoints
                    
                slice_snake[:,0] = snake[:,0] # create 3d points
                slice_snake[:,1] = snake[:,1]
                slice_snake[:,2] = i
                outPoints.append(slice_snake)
                
        elif self._state == True:
            for i in range(self._start, self._end+1): # iterating through the vertical stacks
                print "cropped: " + str(i)
                slice_snake = np.empty([Initial_ellipsePoints.shape[0],3]) # Make N by 3 points 
                
                if useSnake == True:
                    snake = ImageProcessing.ActiveEllipse(self._volume_data[:,:,i], Initial_ellipsePoints)
                else:
                    snake = Initial_ellipsePoints
                    
                slice_snake[:,0] = snake[:,0] # create 3d points
                slice_snake[:,1] = snake[:,1]
                slice_snake[:,2] = i
                outPoints.append(slice_snake)
                
        for i in range(len(outPoints)): # reshape the list
            if i == 0: fb = outPoints[i]  
            else: fb = np.concatenate((fb,outPoints[i]),axis=0)
            
        self._periPoint = fb
        
    def blockImage(self):
        """
        this use the perPoint to create convex hull and logical operation for each slice
        """
        self._logicSlice = ImageProcessing.LogicRegion(self._volume_data[:,:,self._volume_data.shape[2]//2], self._convex_xy)
        self._block_volume = np.empty_like(self._volume_data)
        if self._state == False:
            for i in range(self._volume_data.shape[2]):
                self._block_volume[:,:,i] = self._volume_data[:,:,i] * self._logicSlice
                
        elif self._state == True:
             for i in range(self._start, self._end+1): 
                self._block_volume[:,:,i] = self._volume_data[:,:,i] * self._logicSlice

    def threshold(self, block_size):
        return ImageProcessing.sliceThreshold(self._volume_data, block_size)
        
    def distImage(self):
        pass
        
    def meshSampling(self):
        pass
        
    def kltSampling(self):
        pass
        
    def getOriginVolume(self):
        return self._volume_data  
        
    def getBlockVolume(self):
        return self._block_volume  
    
if __name__ == "__main__":
   print "this is a unit test!"
   import numpy as np
   import matplotlib.pyplot as plt # volume.getVolume().shape[2]//2
   from skimage.segmentation import active_contour
   import Visualization
   from scipy import ndimage
   
   Refvolume = RefVolume("/Users/junchaowei/Desktop/Python_DVC2/UP_Research/WholeRegionRealData/JunchaoFirstRun/M6_OD/M6_OD_baseline_C-scan/")
   Defvolume = RefVolume("/Users/junchaowei/Desktop/Python_DVC2/UP_Research/WholeRegionRealData/JunchaoFirstRun/M6_OD/M6_OD_125_C-scan/")

   ra = Refvolume.points()
   da = Defvolume.points()
   
   rb = Refvolume.segmentation(np.array([ra.xs[1:],ra.ys[1:]]).T, useSnake=False)
   db = Defvolume.segmentation(np.array([da.xs[1:],da.ys[1:]]).T, useSnake=False)
   
   Refvolume.blockImage()
   Defvolume.blockImage()
   
   Refvolume.denoise(10, (60,255) )
   Defvolume.denoise(10, (60,255) )
   
   Refvolume.binary(60)
   
   plot = Visualization.DataVisulization(ndimage.gaussian_filter(Refvolume._denoise_volume,1), 70)
   plot.contour3d()

   #points = np.empty([len(b)*b[0].shape[0],3]) # initlizing the point array, each slice points number is b[0].shape, the slice number is len(b)
          
   #Visualization.DataVisulization(Refvolume, 1).scatterplot(fb.T)
   
   #snake = active_contour(volume.getVolume()[:,:,40], b, w_edge=-1, w_line=1, gamma=0.001, beta=10) 
   #plt.plot(b[:,0],b[:,1])
   #plt.imshow(volume.getVolume()[:,:,40],cmap='Greys_r')
   #plt.show()

   #
   #threshold = volume.threshold(251)
   #import Visualization
   ##plot = Visualization.DataVisulization(ndimage.gaussian_filter(threshold,1), 0.3)
   ##plot.contour3d()
   #import matplotlib.pyplot as plt
   #plt.imshow(volume.getVolume()[:,:,30],cmap='Greys_r')
   #plt.imshow(threshold[:,:,30],cmap='Greys_r')
   #plt.show()