import copy
import random

from geometry import Point
from pglib import Region


class TowerRegion( Region ):

    @staticmethod
    def getRandomAdjacentEdgeAttribute( edge ):
        idx = random.randint( 0, 1 )
        if edge.startswith( 'x' ):
            return ['y1', 'y2'][idx]
        else:
            return ['x1', 'x2'][idx]

    @staticmethod
    def getRandomEdgeAttribute():
        return ['x1', 'x2', 'y1', 'y2'][random.randint( 0, 3 )]

    @staticmethod
    def getOppositeEdgeAttribute( edge ):
        idx = '2' if edge[-1] == '1' else '1'
        return edge[0] + str( idx )

    # @staticmethod
    # def getEdgeAttribute( edge ):
    #     idx = '2' if edge[-1] == '1' else '1'
    #     return edge[0] + str( idx )

    def getRandomCorner( self ):
        xIdx = random.randint( 1, 2 )
        yIdx = random.randint( 1, 2 )
        return (getattr( self, 'x' + str( xIdx ) ), getattr( self, 'y' + str( yIdx ) ))
    
    def pushEdge( self, edge, amount=1 ):
        if edge in ['x2', 'y2']:
            amount *= -1
        setattr( self, edge, getattr( self, edge ) + amount )

    def pullEdge( self, edge, amount=1 ):
        if edge in ['x1', 'y1']:
            amount *= -1
        setattr( self, edge, getattr( self, edge ) + amount )

    def getPoints( self ):
        points = []
        for xIdx in range( 1, 3 ):
            for yIdx in range( 1, 3 ):
                point = Point( 
                    getattr( self, 'x' + str( xIdx ) ), 
                    getattr( self, 'y' + str( yIdx ) ) 
                )
                points.append( point )
        return points


class TowerChunk( object ):

    def __init__( self, regions ):
        self.regions = regions
        self.notch = None

        self.dots = []
        self.points = []

    def __copy__( self ):
        return TowerChunk( [
            copy.copy( region )
            for region in self.regions
        ] )

    def addRegion( self ):

        # Randomise a region to copy.
        rIdx = random.randint( 0, len( self.regions ) - 1 )
        region = copy.copy( self.regions[rIdx] )

        for i in range( random.randint( 1, 2 ) ):
        
            # Randomly pick and edge of the copied region.
            eIdx = random.randint( 0, 3 )
            edge = ['x1', 'x2', 'y1', 'y2'][eIdx]
            region.pushEdge( edge )

            # Push the edge, then push the adjacent edge to make a hole.
            for oRegion in self.regions:
                adjEdge = TowerRegion.getRandomAdjacentEdge( edge )
                oRegion.pushEdge( adjEdge )

        self.regions.append( region )

    def getRandomRegion( self ):
        idx = random.randint( 0, len( self.regions ) - 1 )
        return self.regions[idx]

    def split( self ):

        # Map all points against their regions.
        regionPoints = {
            region: region.getPoints()
            for region in self.regions
        }

        # Find all valid starting points and the regions they belong to. A point
        # is valid if it does not touch any other region, or if it does - that
        # it is also a member of that region's set of points.
        pointRegions = {}
        for region in regionPoints.keys():
            for point in regionPoints[region]:
                if not any( [
                    oRegion.touches( point ) and point not in regionPoints[oRegion]
                    for oRegion in regionPoints.keys()
                    if oRegion is not region
                ] ):
                    pointRegions[point] = region
        if not pointRegions:
            print 'Cannot find start region!'
            return
        startPoints = pointRegions.keys()
        startPoint = startPoints[random.randint( 0, len( startPoints ) - 1 )]
        startRegion = pointRegions[startPoint]
        
        # Find the two edges which describe the directions we can scale the 
        # notch.
        pullVector = startRegion.centre - startPoint
        if pullVector.x == 0 or pullVector.y == 0:
            print 'Tried to notch region with no width or height'
            return
        xEdge = 'x' + str( 1 if pullVector.x < 0 else 2 )
        yEdge = 'y' + str( 1 if pullVector.y < 0 else 2 )

        # Create a region to define as the "notch". Pull the two edges so it
        # is a 1x1 square.
        notch = TowerRegion( startPoint.x, startPoint.y, startPoint.x, startPoint.y )
        notch.pullEdge( xEdge )
        notch.pullEdge( yEdge )

        # Randomise a length for the notch.
        edge = [xEdge, yEdge][random.randint( 0, 1 )]
        dimAttr = 'width' if 'y' in edge else 'height'
        maxDim = getattr( region, dimAttr ) - 3
        if maxDim > -1:
            notch.pullEdge( edge, random.randint( 0, maxDim ) )

        # Find all regions that the notch collides with.
        for region in filter( lambda r: r.intersects( notch ), self.regions ):
            attrs = ['x1', 'x2', 'y1', 'y2']
            attrs = filter( lambda attr: getattr( region, attr ) == getattr( notch, attr ), attrs )
            if not attrs:
                return

            # Push the region's edges back to create a hole the size of the 
            # notch.
            copyRegion = copy.copy( region )
            setattr( region, attrs[0], getattr( notch, TowerRegion.getOppositeEdgeAttribute( attrs[0] ) ) )
            if len( attrs ) > 1:
                setattr( copyRegion, attrs[1], getattr( notch, TowerRegion.getOppositeEdgeAttribute( attrs[1] ) ) )
            self.regions.append( copyRegion )

        self.dots = list( startPoints )
        self.notch = notch

    def cleanUp( self ):

        # Remove any region that has width or height of zero.
        for i in reversed( range( len( self.regions ) ) ):
            if self.regions[i].width < 1 or self.regions[i].height < 1:
                self.regions.pop( i )
            else:
                print '    KEEP:', self.regions[i]


class Tower( object ):

    def __init__( self, numChunks, chunkSizeX, chunkSizeY ):
        self.numChunks = numChunks
        self.chunkSizeX = chunkSizeX
        self.chunkSizeY = chunkSizeY
        self.chunks = []

    def generate( self ):
        print '*' * 35
        for i in range( self.numChunks ):
            print ''
            print i

            # Copy previous chunk if possible.
            chunk = None
            if i < 1:
                chunk = TowerChunk( [TowerRegion( 0, 0, self.chunkSizeX, self.chunkSizeY )] )
            else:
                try:
                    chunk = copy.copy( self.chunks[-1] )
                except:
                    print '*' * 35
                    for region in self.chunks[-1].regions:
                        print region
                    raise

                # Increase number of regions...?
                #if True:
                #    chunk.addRegion()
                if i % 2:
                    chunk.split()
                else:

                    # Create a balcony all the way around the edge.
                    map( lambda r: TowerRegion.inflate( r, -1 ), chunk.regions )

                # Clean up regions.
                chunk.cleanUp()

            self.chunks.append( chunk )