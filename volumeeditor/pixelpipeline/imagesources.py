from PyQt4.QtCore import QObject, QRect, pyqtSignal, QMutex
from PyQt4.QtGui import QImage
from qimage2ndarray import gray2qimage, array2qimage, alpha_view, rgb_view
from asyncabcs import SourceABC, RequestABC
from volumeeditor.slicingtools import is_bounded, slicing2rect, rect2slicing, slicing2shape, is_pure_slicing
import numpy as np

#*******************************************************************************
# I m a g e S o u r c e                                                        *
#*******************************************************************************

class ImageSource( QObject ):
    '''Partial implemented base class for image sources

    Signals:
    isDirty -- a rectangular region has changed; transmits
               an empty QRect if the whole image is dirty

    '''

    isDirty = pyqtSignal( QRect )

    def request( self, rect ):
        raise NotImplementedError

    def cancel( self ):
        raise NotImplementedError

    def setDirty( self, slicing ):
        '''Mark a region of the image as dirty.

        slicing -- if one ore more slices in the slicing
                   are unbounded, the whole image is marked dirty;
                   since an image has two dimensions, only the first
                   two slices in the slicing are used

        '''
        if not is_pure_slicing(slicing):
            raise Exception('dirty region: slicing is not pure')
        if not is_bounded( slicing ):
            self.isDirty.emit(QRect()) # empty rect == everything is dirty
        else:
            self.isDirty.emit(slicing2rect( slicing ))
assert issubclass(ImageSource, SourceABC)

#*******************************************************************************
# G r a y s c a l e I m a g e S o u r c e                                      *
#*******************************************************************************

class GrayscaleImageSource( ImageSource ):
    def __init__( self, arraySource2D, layer ):
        assert isinstance(arraySource2D, SourceABC), 'wrong type: %s' % str(type(arraySource2D))
        super(GrayscaleImageSource, self).__init__()
        self._arraySource2D = arraySource2D
        
        self._layer = layer
        
        self._arraySource2D.isDirty.connect(self.setDirty)

    def request( self, qrect ):
        assert isinstance(qrect, QRect)
        s = rect2slicing(qrect)
        req = self._arraySource2D.request(s)
        return GrayscaleImageRequest( req, self._layer.thresholding )
assert issubclass(GrayscaleImageSource, SourceABC)

class GrayscaleImageRequest( object ):
    def __init__( self, arrayrequest, normalize=None ):
        self._mutex = QMutex()
        self._canceled = False
        self._arrayreq = arrayrequest
        self._normalize = normalize

    def wait( self ):
        a = self._arrayreq.wait().squeeze()
        if self._normalize is not None:
            a = a.astype(np.float32)
            a = (a - self._normalize[0])*255.0 / (self._normalize[1]-self._normalize[0])
            a[a > 255] = 255
            a[a < 0]   = 0
            a = a.astype(np.uint8)
        img = gray2qimage(a)
        return img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
            
    def notify( self, callback, **kwargs ):
        self._arrayreq.notify(self._onNotify, package = (callback, kwargs))
    
    def cancelLock(self):
        self._mutex.lock()
    def cancelUnlock(self):
        self._mutex.unlock()
    def canceled(self):
        return self._canceled
    
    def cancel( self ):
        self.cancelLock()
        self._arrayreq.cancel()
        self._canceled = True
        self.cancelUnlock()
    
    def _onNotify( self, result, package ):
        img = self.wait()
        callback = package[0]
        kwargs = package[1]
        callback( img, **kwargs )
assert issubclass(GrayscaleImageRequest, RequestABC)

#*******************************************************************************
# A l p h a M o d u l a t e d I m a g e S o u r c e                            *
#*******************************************************************************

class AlphaModulatedImageSource( ImageSource ):
    def __init__( self, arraySource2D, layer ):
        assert isinstance(arraySource2D, SourceABC), 'wrong type: %s' % str(type(arraySource2D))
        super(AlphaModulatedImageSource, self).__init__()
        self._arraySource2D = arraySource2D
        self._layer = layer
        self._arraySource2D.isDirty.connect(self.setDirty)

    def request( self, qrect ):
        assert isinstance(qrect, QRect)
        s = rect2slicing(qrect)
        req = self._arraySource2D.request(s)
        return AlphaModulatedImageRequest( req, self._layer.tintColor, self._layer._normalize )
assert issubclass(AlphaModulatedImageSource, SourceABC)

class AlphaModulatedImageRequest( object ):
    def __init__( self, arrayrequest, tintColor, normalize=None ):
        self._mutex = QMutex()
        self._canceled = False
        self._arrayreq = arrayrequest
        self._normalize = normalize
        self._tintColor = tintColor

    def wait( self ):
        a = self._arrayreq.wait().squeeze()
        if self._normalize is not None:
            a = (a - self._normalize[0])*255 / (self._normalize[1]-self._normalize[0])
        
        shape = a.shape + (4,)
        d = np.empty(shape, dtype=np.uint8)
        d[:,:,0] = a[:,:]*self._tintColor.redF()
        d[:,:,1] = a[:,:]*self._tintColor.greenF()
        d[:,:,2] = a[:,:]*self._tintColor.blueF()
        d[:,:,3] = a[:,:]
        img = array2qimage(d)
        return img.convertToFormat(QImage.Format_ARGB32_Premultiplied)        
            
    def notify( self, callback, **kwargs ):
        self._arrayreq.notify(self._onNotify, package = (callback, kwargs))
    
    def cancelLock(self):
        self._mutex.lock()
    def cancelUnlock(self):
        self._mutex.unlock()
    def canceled(self):
        return self._canceled
    
    def cancel( self ):
        self.cancelLock()
        self._arrayreq.cancel()
        self._canceled = True
        self.cancelUnlock()
    
    def _onNotify( self, result, package ):
        img = self.wait()
        callback = package[0]
        kwargs = package[1]
        callback( img, **kwargs )
assert issubclass(AlphaModulatedImageRequest, RequestABC)

#*******************************************************************************
# C o l o r t a b l e I m a g e S o u r c e                                    *
#*******************************************************************************

class ColortableImageSource( ImageSource ):
    def __init__( self, arraySource2D, colorTable ):
        assert isinstance(arraySource2D, SourceABC), 'wrong type: %s' % str(type(arraySource2D))
        super(ColortableImageSource, self).__init__()
        self._arraySource2D = arraySource2D
        self._arraySource2D.isDirty.connect(self.setDirty)
        self._colorTable = colorTable
        
    def request( self, qrect ):
        assert isinstance(qrect, QRect)
        s = rect2slicing(qrect)
        req = self._arraySource2D.request(s)
        return ColortableImageRequest( req , self._colorTable)  
assert issubclass(ColortableImageSource, SourceABC)

class ColortableImageRequest( object ):
    def __init__( self, arrayrequest, colorTable):
        self._mutex = QMutex()
        self._canceled = False
        self._arrayreq = arrayrequest
        self._colorTable = colorTable
        
    def wait( self ):
        a = self._arrayreq.wait()
        a = a.squeeze()
        img = gray2qimage(a)
        img.setColorTable(self._colorTable)# = img.convertToFormat(QImage.Format_ARGB32_Premultiplied, self._colorTable)
        img = img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
        return img 
            
    def notify( self, callback, **kwargs ):
        self._arrayreq.notify(self._onNotify, package = (callback, kwargs))
    
    def cancelLock(self):
        self._mutex.lock()
    def cancelUnlock(self):
        self._mutex.unlock()
    def canceled(self):
        return self._canceled
    
    def cancel( self ):
        self.cancelLock()
        self._arrayreq.cancel()
        self._canceled = True
        self.cancelUnlock()
    
    def _onNotify( self, result, package ):
        img = self.wait()
        callback = package[0]
        kwargs = package[1]
        callback( img, **kwargs )
assert issubclass(ColortableImageRequest, RequestABC)

#*******************************************************************************
# R G B A I m a g e S o u r c e                                                *
#*******************************************************************************

class RGBAImageSource( ImageSource ):
    def __init__( self, red, green, blue, alpha, layer ):
        '''
        If you don't want to set all the channels,
        a ConstantSource may be used as a replacement for
        the missing channels.

        red, green, blue, alpha - 2d array sources

        '''
        self._layer = layer
        channels = [red, green, blue, alpha]
        for channel in channels: 
                assert isinstance(channel, SourceABC) , 'channel has wrong type: %s' % str(type(channel))

        super(RGBAImageSource, self).__init__()
        self._channels = channels
        for arraySource in self._channels:
            arraySource.isDirty.connect(self.setDirty)

    def request( self, qrect ):
        assert isinstance(qrect, QRect)
        s = rect2slicing( qrect )
        r = self._channels[0].request(s)
        g = self._channels[1].request(s)
        b = self._channels[2].request(s)
        a = self._channels[3].request(s)
        shape = []
        for t in slicing2shape(s):
            if t > 1:
                shape.append(t)
        assert len(shape) == 2
        return RGBAImageRequest( r, g, b, a, shape, *self._layer._normalize )
assert issubclass(RGBAImageSource, SourceABC)

class RGBAImageRequest( object ):
    def __init__( self, r, g, b, a, shape,
                  normalizeR=None, normalizeG=None, normalizeB=None, normalizeA=None ):
        self._mutex = QMutex()
        self._canceled = False
        self._requests = r, g, b, a
        self._normalize = [normalizeR, normalizeG, normalizeB, normalizeA]
        shape.append(4)
        self._data = np.empty(shape, dtype=np.uint8)
        self._requestsFinished = 4 * [False,]

    def wait( self ):
        for i, req in enumerate(self._requests):
            a = self._requests[i].wait()
            a = a.squeeze()
            if self._normalize[i] is not None:
                a = a.astype(np.float32)
                a = (a - self._normalize[i][0])*255.0 / (self._normalize[i][1]-self._normalize[i][0])
                a[a > 255] = 255
                a[a < 0]   = 0
                a = a.astype(np.uint8)
            self._data[:,:,i] = a
        img = array2qimage(self._data)
        return img.convertToFormat(QImage.Format_ARGB32_Premultiplied)        
    def notify( self, callback, **kwargs ):
        for i in xrange(4):
            self._requests[i].notify(self._onNotify, package = (i, callback, kwargs))

    def cancelLock(self):
        self._mutex.lock()
    def cancelUnlock(self):
        self._mutex.unlock()
    def canceled(self):
        return self._canceled

    def cancel( self ):
        self.cancelLock()
        for r in self._requests:
            r.cancel()
        self._canceled = True
        self.cancelUnlock()

    def _onNotify( self, result, package ):
        channel = package[0]
        self._requestsFinished[channel] = True
        if all(self._requestsFinished):
            img = self.wait()
        
            callback = package[1]
            kwargs = package[2]
            callback( img, **kwargs )
assert issubclass(RGBAImageRequest, RequestABC)
