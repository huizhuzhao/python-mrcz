# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 09:44:09 2016

@author: Robert A. McLeod
"""

import mrcz
import numpy as np
import numpy.testing as npt
import os, os.path, sys
import subprocess as sub
import tempfile
import unittest
from logging import Logger
log = Logger(__name__)
        
def which( program ):
    # Tries to locate a program 
    import os
    if os.name == 'nt':
        program_ext = os.path.splitext( program )[1]
        if program_ext == "":
            prog_exe = which( program + ".exe" )
            if prog_exe != None:
                return prog_exe
            return which( program + ".com" )
            
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
    

float_dtype = 'float32'
fftw_dtype = 'complex64'
tmpDir = tempfile.gettempdir()

#==============================================================================
# ioMRC Test
# 
# Internal python-only test. Build a random image and save and re-load it.
#==============================================================================
class PythonMrczTests(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def compReadWrite(self, testMage, casttype=None, compressor=None, clevel = 1 ):
        # This is the main functions which reads and writes from disk.
        mrcName = os.path.join( tmpDir, "testMage.mrc" )
        pixelsize = np.array( [1.2, 2.6, 3.4] )

        mrcz.writeMRC( testMage, mrcName, dtype=casttype,
                           pixelsize=pixelsize, pixelunits=u"\AA",
                           voltage=300.0, C3=2.7, gain=1.05,
                           compressor=compressor, clevel=clevel )
        
        rereadMage, rereadHeader = mrcz.readMRC( mrcName, pixelunits=u"\AA")
        try: os.remove( mrcName )
        except IOError: log.info( "Warning: file {} left on disk".format(mrcName) )
        
        npt.assert_array_almost_equal( testMage, rereadMage )
        npt.assert_array_equal( rereadHeader['voltage'], 300.0 )
        npt.assert_array_almost_equal( rereadHeader['pixelsize'], pixelsize )
        npt.assert_array_equal( rereadHeader['pixelunits'], u"\AA" )
        npt.assert_array_equal( rereadHeader['C3'], 2.7 )
        npt.assert_array_equal( rereadHeader['gain'], 1.05 )
    
    def test_MRC_uncompressed(self):
        log.info( "Testing uncompressed MRC, float-32" )
        testMage0 = np.random.normal( size=[2,128,96] ).astype( float_dtype )
        self.compReadWrite( testMage0, compressor=None )
        log.info( "Testing uncompressed MRC, uint-4" )
        testMage1 = np.random.randint( 10, size=[2,128,96], dtype='int8' )
        self.compReadWrite( testMage1, casttype='uint4', compressor=None )
        log.info( "Testing uncompressed MRC, int-8" )
        testMage2 = np.random.randint( 10, size=[2,128,96], dtype='int8' )
        self.compReadWrite( testMage2, compressor=None )
        log.info( "Testing uncompressed MRC, int-16" )
        testMage3 = np.random.randint( 10, size=[2,128,96], dtype='int16' )
        self.compReadWrite( testMage3, compressor=None )
        log.info( "Testing uncompressed MRC, uint-16" )
        testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
        self.compReadWrite( testMage4, compressor=None )
        log.info( "Testing uncompressed MRC, complex-64" )
        testMage5 = np.random.uniform( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.uniform( 10, size=[2,128,96]  ).astype('float32')
        self.compReadWrite( testMage5, compressor=None )
        
        
    def test_MRCZ_zstd1(self):
        log.info( "Testing 'zstd_1' MRC, float-32" )
        testMage0 = np.random.normal( size=[2,128,96] ).astype( float_dtype )
        self.compReadWrite( testMage0, compressor='zstd', clevel=1 )
        log.info( "Testing 'zstd_1' MRC, int-8" )
        testMage2 = np.random.randint( 10, size=[2,128,96], dtype='int8' )
        self.compReadWrite( testMage2, compressor='zstd', clevel=1 )
        log.info( "Testing 'zstd_1' MRC, int-16" )
        testMage3 = np.random.randint( 10, size=[2,128,96], dtype='int16' )
        self.compReadWrite( testMage3, compressor='zstd', clevel=1 )
        log.info( "Testing zstd_1 MRC, uint-16" )
        testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
        self.compReadWrite( testMage4, compressor='zstd', clevel=1 )
        log.info( "Testing 'zstd_1' MRC, complex-64" )
        testMage5 = np.random.normal( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.normal( 10, size=[2,128,96]  ).astype('float32')
        self.compReadWrite( testMage5, compressor='zstd', clevel=1 )
        
    
    def test_MRCZ_lz9(self):
        log.info( "Testing 'lz4_9' MRC, float-32" )
        testMage0 = np.random.normal( size=[2,128,96] ).astype( float_dtype )
        self.compReadWrite( testMage0, compressor='lz4', clevel=9 )
        log.info( "Testing 'lz4_9' MRC, int-8" )
        testMage2 = np.random.randint( 10, size=[2,128,96], dtype='int8' )
        self.compReadWrite( testMage2, compressor='lz4', clevel=9 )
        log.info( "Testing 'lz4_9' MRC, int-16" )
        testMage3 = np.random.randint( 10, size=[2,128,96], dtype='int16' )
        self.compReadWrite( testMage3, compressor='lz4', clevel=9 )
        log.info( "Testing lz4_9 MRC, uint-16" )
        testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
        self.compReadWrite( testMage4, compressor='lz4', clevel=9 )
        log.info( "Testing 'lz4_9' MRC, complex-64" )
        testMage5 = np.random.normal( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.normal( 10, size=[2,128,96]  ).astype('float32')
        self.compReadWrite( testMage5, compressor='lz4', clevel=9 )
        
    def test_JSON(self):
        testMage = np.random.uniform( high=10, size=[3,128,64] ).astype( 'int8' )
        meta = {'foo': 5, 'bar': 42}
        mrcName = os.path.join( tmpDir, "testMage.mrcz" )
                
        pixelsize = [1.2, 5.6, 3.4]
        
        mrcz.writeMRC( testMage, mrcName, meta=meta,
                                pixelsize=pixelsize, pixelunits=u"\AA",
                                voltage=300.0, C3=2.7, gain=1.05,
                                compressor='zstd', clevel=1, n_threads=4 )
                                
        rereadMage, rereadHeader = mrcz.readMRC( mrcName, pixelunits=u"\AA" )

        try: os.remove( mrcName )
        except IOError: log.info( "Warning: file {} left on disk".format(mrcName) )
        
        assert( np.all(testMage.shape == rereadMage.shape) )
        assert( testMage.dtype == rereadMage.dtype )
        for key in meta:
            assert( meta[key] == rereadHeader[key] )

        npt.assert_array_almost_equal( testMage, rereadMage )
        npt.assert_array_equal( rereadHeader['voltage'], 300.0 )
        npt.assert_array_almost_equal( rereadHeader['pixelsize'], pixelsize )
        npt.assert_array_equal( rereadHeader['pixelunits'], u"\AA" )
        npt.assert_array_equal( rereadHeader['C3'], 2.7 )
        npt.assert_array_equal( rereadHeader['gain'], 1.05 )
        pass

    def test_Async(self):
        testMage = np.random.uniform( high=10, size=[3,128,64] ).astype( 'int8' )
        meta = {'foo': 5, 'bar': 42}
        mrcName = os.path.join( tmpDir, "testMage.mrcz" )
                
        pixelsize = [1.2, 5.6, 3.4]
        
        worker = mrcz.asyncWriteMRC( testMage, mrcName, meta=meta,
                                pixelsize=pixelsize, pixelunits=u"\AA",
                                voltage=300.0, C3=2.7, gain=1.05,
                                compressor='zstd', clevel=1, n_threads=4 )
                                
        worker.result() # Wait for write to finish

        worker = mrcz.asyncReadMRC( mrcName, pixelunits=u"\AA" )
        rereadMage, rereadHeader = worker.result()

        try: os.remove( mrcName )
        except IOError: log.info( "Warning: file {} left on disk".format(mrcName) )
        
        assert( np.all(testMage.shape == rereadMage.shape) )
        assert( testMage.dtype == rereadMage.dtype )
        for key in meta:
            assert( meta[key] == rereadHeader[key] )

        npt.assert_array_almost_equal( testMage, rereadMage )
        npt.assert_array_equal( rereadHeader['voltage'], 300.0 )
        npt.assert_array_almost_equal( rereadHeader['pixelsize'], pixelsize )
        npt.assert_array_equal( rereadHeader['pixelunits'], u"\AA" )
        npt.assert_array_equal( rereadHeader['C3'], 2.7 )
        npt.assert_array_equal( rereadHeader['gain'], 1.05 )
        pass
    
cmrczProg = which( 'mrcz' )
if cmrczProg is None:
    log.debug( "NOTE: mrcz not found in system path, not testing python-mrcz to c-mrcz cross-compatibility" )

else:

    class PythonToCMrczTests(unittest.TestCase):
        #==============================================================================
        # python-mrcz to c-mrcz tests
        #
        # mrcz executable must be found within the system path.
        # 
        # Cross-compatibility tests between c-mrcz and python-mrcz. Build a random 
        # image, load and re-save it with c-mrcz, and then reload in Python.
        #==============================================================================
        def setUp(self):
            pass
    
        def crossReadWrite(self, testMage, casttype=None, compressor=None, clevel = 1 ):
            mrcInput = os.path.join( tmpDir, "testIn.mrcz" )
            mrcOutput = os.path.join( tmpDir, "testOut.mrcz" )
            compressor = None
            blocksize = 64
            clevel = 1
            pixelsize = [1.2, 2.6, 3.4]
        
            mrcz.writeMRC( testMage, mrcInput,
                                    pixelsize=pixelsize, pixelunits=u"\AA",
                                    voltage=300.0, C3=2.7, gain=1.05,
                                    compressor=compressor )
                                 
            sub.call( cmrczProg + " -i %s -o %s -c %s -B %d -l %d" 
                %(mrcInput, mrcOutput, compressor, blocksize, clevel ), shell=True )
            
            rereadMage, rereadHeader = mrcz.readMRC( mrcOutput, pixelunits=u"\AA" )
            
            os.remove( mrcOutput )
            os.remove( mrcInput )
            
            
            assert( np.all(testMage.shape == rereadMage.shape) )
            assert( testMage.dtype == rereadMage.dtype )
            npt.assert_array_almost_equal( testMage, rereadMage )
            npt.assert_array_equal( rereadHeader['voltage'], 300.0 )
            npt.assert_array_almost_equal( rereadHeader['pixelsize'], pixelsize )
            npt.assert_array_equal( rereadHeader['pixelunits'], u"\AA" )
            npt.assert_array_equal( rereadHeader['C3'], 2.7 )
            npt.assert_array_equal( rereadHeader['gain'], 1.05 )
            
        def test_crossMRC_uncompressed(self):
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, uncompressed, int-8" )
            testMage0 = np.random.randint( 10, size=[2,128,64], dtype='int8' )
            self.crossReadWrite( testMage0, compressor=None, clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, uncompressed, int-16" )
            testMage1 = np.random.randint( 10, size=[2,128,64], dtype='int16' )
            self.crossReadWrite( testMage1, compressor=None, clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, uncompressed, float32" )
            testMage1 = np.random.normal( size=[2,128,64] ).astype( 'float32' )
            self.crossReadWrite( testMage1, compressor=None, clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, uncompressed, uint-16" )
            testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
            self.crossReadWrite( testMage4, compressor=None, clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, uncompressed, complex-64" )
            testMage5 = np.random.normal( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.normal( 10, size=[2,128,96]  ).astype('float32')
            self.crossReadWrite( testMage5, compressor=None, clevel=1 )
        
        def test_crossMRC_zstd1(self):
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, zstd_1, int-8" )
            testMage0 = np.random.randint( 10, size=[2,128,64], dtype='int8' )
            self.crossReadWrite( testMage0, compressor='zstd', clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, zstd_1, int-16" )
            testMage1 = np.random.randint( 10, size=[2,128,64], dtype='int16' )
            self.crossReadWrite( testMage1, compressor='zstd', clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, zstd_1, float32" )
            testMage1 = np.random.normal( size=[2,128,64] ).astype( 'float32' )
            self.crossReadWrite( testMage1, compressor='zstd1', clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, zstd_1, uint-16" )
            testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
            self.crossReadWrite( testMage4, compressor='zstd', clevel=1 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, zstd_1, complex-64" )
            testMage5 = np.random.normal( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.normal( 10, size=[2,128,96]  ).astype('float32')
            self.crossReadWrite( testMage5, compressor='zstd', clevel=1 )
            
        def test_crossMRC_lz4_9(self):
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, lz4_9, int-8" )
            testMage0 = np.random.randint( 10, size=[2,128,64], dtype='int8' )
            self.crossReadWrite( testMage0, compressor='lz4', clevel=9 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, lz4_9, int-16" )
            testMage1 = np.random.randint( 10, size=[2,128,64], dtype='int16' )
            self.crossReadWrite( testMage1, compressor='lz4', clevel=9 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, lz4_9, float32" )
            testMage1 = np.random.normal( size=[2,128,64] ).astype( 'float32' )
            self.crossReadWrite( testMage1, compressor='lz4', clevel=9 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, lz4_9, uint-16" )
            testMage4 = np.random.randint( 10, size=[2,128,96], dtype='uint16' )
            self.crossReadWrite( testMage4, compressor='lz4', clevel=9 )
            log.info( "Testing cross-compatibility c-mrcz and python-mrcz, lz4_9, complex-64" )
            testMage5 = np.random.normal( 10, size=[2,128,96] ).astype('float32') + \
                   1j * np.random.normal( 10, size=[2,128,96]  ).astype('float32')
            self.crossReadWrite( testMage5, compressor='lz4', clevel=9 )
    pass

def test(verbosity=2):
    '''
    test(verbosity=2)

    Run ``unittest`` suite for ``mrcz`` package.
    '''

    from mrcz import __version__
    log.info( "MRCZ TESTING FOR VERSION %s " % __version__ )
    
    theSuite = unittest.TestSuite()

    theSuite.addTest(unittest.makeSuite(PythonMrczTests))
    if cmrczProg is not None:
        theSuite.addTest(unittest.makeSuite(PythonToCMrczTests))

    return unittest.TextTestRunner(verbosity=verbosity).run(theSuite)
    
if __name__ == "__main__":
    # Should generally call "python -m unittest -v mrcz.test" for continuous integration
    test()
    

    



                     
