import math
import random

import numpy as np
from direct.task import Task
import pandac.PandaModules as pm
from direct.showbase.ShowBase import ShowBase
from direct.directtools.DirectGrid import DirectGrid
from direct.gui.DirectGui import *

from nodebox.graphics import PerlinNoise

import tower


import p3d


BOARD_SIZE_X = 10
BOARD_SIZE_Y = 10
BOARD_SIZE_Z = 1
MOUSE_SPEED = 1


def shift( a, shifts, axis ):
    """
    Roll they array then set the opposite edge to zeros to remove the default
    wrapping functionality.
    """
    axes = np.core.numeric.normalize_axis_tuple( axis, a.ndim, allow_duplicate=True )
    for i, axis in enumerate( axes ):
        a = np.roll( a, shifts[i], axis )
        slc = [slice( None )] * a.ndim
        if shifts[i] < 0:
            slc[axis] = np.ma.size( a, axis ) - 1
        else:
            slc[axis] = 0
        a[slc] = 0
    return a


class Board( object ):

    def __init__( self, array ):
        self.array = array
        self.size = len( array )
        self.tiles = []

    def clear( self ):
        for tile in self.tiles:
            tile.removeNode()
        self.tile = []

    def render( self, renderNp, colour=None, size=1 ):
        if colour is None:
            colour = (1, 1, 1, 1)

        # Plot a 3D cube for each non-zero value in the matrix.
        x, y, z = self.array.nonzero()
        for m in range( len( x ) ):
            tile = pm.NodePath( p3d.geometry.Box() )
            tile.setScale( size )
            tile.setSz( 0.5 )
            tile.setColor( colour )
            if colour[-1] < 1:
                tile.setTransparency( pm.TransparencyAttrib.MAlpha )
                tile.setAlphaScale( colour[-1] )
            tile.setPos( x[m], y[m], z[m] * 0.5 )
            tile.reparentTo( renderNp )
            self.tiles.append( tile )


class MyApp( ShowBase ):
 
    def __init__( self ):
        ShowBase.__init__( self )

        self._xray = False
        self.boards = []
        self.numbers = []

        self.noiseStep = 100
        self.noiseScaleX = 1
        self.noiseScaleY = 1
        self.noiseScaleZ = 1
        self.thresh = 0.5

        self.chunks = []

        # def setStep():
        #     self.noiseStep = self.stepSlider['value']
        #     self.generateBoard()

        # def setScaleX():
        #     self.noiseScaleX = self.scaleSliderX['value']
        #     self.generateBoard()

        # def setScaleY():
        #     self.noiseScaleY = self.scaleSliderY['value']
        #     self.generateBoard()

        # def setScaleZ():
        #     self.noiseScaleZ = self.scaleSliderZ['value']
        #     self.generateBoard()

        # def setThresh():
        #     self.thresh = self.threshSlider['value']
        #     self.generateBoard()
         
        # self.stepSlider = DirectSlider( range=(0, 200), value=100, command=setStep )
        # self.stepSlider.setPos( 0, 0, .9 )
        # self.stepSlider.setSz( 0.5 )

        # self.scaleSliderX = DirectSlider( range=(0, 2), value=1, command=setScaleX )
        # self.scaleSliderX.setPos( 0, 0, .8 )
        # self.scaleSliderX.setSz( 0.5 )

        # self.scaleSliderY = DirectSlider( range=(0, 2), value=1, command=setScaleY )
        # self.scaleSliderY.setPos( 0, 0, .7 )
        # self.scaleSliderY.setSz( 0.5 )

        # self.scaleSliderZ = DirectSlider( range=(0, 2), value=1, command=setScaleZ )
        # self.scaleSliderZ.setPos( 0, 0, .8 )
        # self.scaleSliderZ.setSz( 0.5 )

        # self.threshSlider = DirectSlider( range=(0, 1), value=0.5, command=setThresh )
        # self.threshSlider.setPos( 0, 0, .7 )
        # self.threshSlider.setSz( 0.5 )

        self.accept( 'f4', self.newGenerator )
        self.accept( 'f5', self.generateBoard )
        self.accept( 'f6', self.toggleXray )
        self.setupGrid()
        self.setupCamera()
        self.setupLights()
        self.setupHelpers()
        self.newGenerator()

        self.mouse = p3d.Mouse( 'mouse' )
        self.mouse.Start()

        self.camTask = self.taskMgr.add( self.cameraRotationTask, 'camLoop' )

    def setupGrid( self ):
        """Create the grid and set up its appearance."""
        self.grid = DirectGrid( 
            gridSize=BOARD_SIZE_X,
            gridSpacing=1.0,
            planeColor=(0.5, 0.5, 0.5, 0.0),
            parent=self.render
        )
        self.grid.snapMarker.hide()
        self.grid.centerLines.setColor( (0, 0, 0, 0) )
        self.grid.centerLines.setThickness( 2 )
        self.grid.majorLines.setColor( (0.25, 0.25, 0.25, 0) )
        self.grid.majorLines.setThickness( 1 )
        self.grid.minorLines.setColor( (0.5, 0.5, 0.5, 0) )
        self.grid.updateGrid()

    def newGenerator( self ):
        self.generator = PerlinNoise()
        self.generateBoard()

    def setupCamera( self ):
        lens = pm.OrthographicLens()
        lens.setFilmSize( 40, 30 )
        self.cam.node().setLens( lens )

        self.camArm = pm.NodePath( 'camArm' )
        self.camArm.reparentTo( self.render )
        self.cam.reparentTo( self.camArm )

        base.cam.setHpr( 90, -35, 0 )
        base.cam.setPos( base.cam, 0, -30, 0 )

        self.camArm.setHpr( 45, 0, 0 )      # k = 0: Camera rotation = 45
        #self.camArm.setHpr( 135, 0, 0 )    # k = 3: Camera rotation = 135
        #self.camArm.setHpr( 225, 0, 0 )    # k = 2: Camera rotation = 225
        #self.camArm.setHpr( 315, 0, 0 )    # k = 1: Camera rotation = 315
        self.camArm.setPos( 0, 0, 8 )

    def setupLights( self ):
        dlight = pm.DirectionalLight( 'dlight1' )
        dlnp = self.render.attachNewNode( dlight )
        dlnp.setHpr( 35, -75, 0 )
        self.render.setLight( dlnp )

        dlight = pm.DirectionalLight( 'dlight1' )
        dlnp = self.render.attachNewNode( dlight )
        dlnp.setHpr( 35, -105, 0 )
        self.render.setLight( dlnp )

    def setupHelpers( self ):

        # Axes.
        box = pm.NodePath( p3d.geometry.Box() )
        box.setColor( 1, 0, 0, 1 )
        box.setPos( BOARD_SIZE_X + 2, 0, 0 )
        box.setScale( 0.5 )
        box.reparentTo( self.render )

        box = pm.NodePath( p3d.geometry.Box() )
        box.setColor( 0, 1, 0, 1 )
        box.setPos( 0, BOARD_SIZE_Y + 2, 0 )
        box.setScale( 0.5 )
        box.reparentTo( self.render )

        box = pm.NodePath( p3d.geometry.Box() )
        box.setColor( 0, 0, 1, 1 )
        box.setPos( 0, 0, BOARD_SIZE_Z + 2 )
        box.setScale( 0.5 )
        box.reparentTo( self.render )

        # Wire box to visualise board extents.
        # colour = (0.25, 0.25, 0.25, 0.25)
        # box = pm.NodePath( p3d.geometry.Box() )
        # box.setScale( BOARD_SIZE_X, BOARD_SIZE_Y, BOARD_SIZE_Z )
        # box.setPos( BOARD_SIZE_X / 2.0 - 0.5, BOARD_SIZE_Y / 2.0 - 0.5, BOARD_SIZE_Z / 2.0 - 0.5)
        # box.reparentTo( self.render )
        # box.setRenderModeWireframe()
        # box.setTwoSided( True )

    def cameraRotationTask( self, task ):
        if self.mouse.buttons[0]:
            self.camArm.setH( self.camArm, self.mouse.dx * MOUSE_SPEED )
            #self.camArm.setR( self.camArm, self.mouse.dy * MOUSE_SPEED )
            #self.camArm.setP( self.camArm, 0 )
        return Task.cont

    def setXray( self ):
        for node in self.render.getChildren():
            node.setTransparency( pm.TransparencyAttrib.MAlpha if self._xray else pm.TransparencyAttrib.M_none )
            node.setAlphaScale( 0.3 if self._xray else 1.0 )

    def toggleXray( self ):
        self._xray = not self._xray
        self.setXray()
        
    def generateBoard( self ):

        print 'generateBoard'

        for chunk in self.chunks:
            chunk.removeNode()
        self.chunks = []

        t = tower.Tower( 5, 10, 10 )
        t.generate()

        offset = 0
        for chunk in t.chunks:
            for region in chunk.regions:
                tile = pm.NodePath( p3d.geometry.Box() )

                tile.setSx( region.width )
                tile.setSy( region.height )

                tile.setX( region.x1 + region.width / 2.0 - 5 )
                tile.setY( region.y1 + region.height / 2.0 - 5 )


                tile.setSz( 5 )
                tile.setZ( offset + tile.getSz() / 2.0 )
                tile.reparentTo( base.render )
                self.chunks.append( tile )
            offset += 5





app = MyApp()
app.run()