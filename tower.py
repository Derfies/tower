import copy
import random

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


class TowerChunk( object ):

    def __init__( self, regions ):
        self.regions = regions
        self.notch = None

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

        # Copy a random region, then shrink it down to a single unit in height,
        # sitting along the edge of the region it was copied from.
        notch = copy.copy( self.getRandomRegion() )
        print '   original   :', notch
        edge = TowerRegion.getRandomEdgeAttribute()
        print '   edge:', edge
        dimAttr = 'width' if 'y' in edge else 'height'
        print '   push dim:', dimAttr
        dim = getattr( notch, dimAttr ) - 1
        notch.pushEdge( edge, dim )

        print '   push:', edge, '->', dim

        print '   after push:', notch

        # Weird shit happens if the notch is the same width as the original region.
        # We probably never want the width to be less than 3 anyway, otherwise
        # pushing edges in above this chunk will be difficult.
        #dim = getattr( notch, dimAttr ) - 1
        if dim < 4:
            print '    NO RAND RANGE: chunk is too small'
            return
        amt = random.randint( 3, dim )
        adjEdge = TowerRegion.getRandomAdjacentEdgeAttribute( edge )
        # print '   ', adjEdge, ':', amt
        # notch.pushEdge( adjEdge,  amt)
        # print '    notch:', notch
        print '   adj push:', adjEdge, '->', amt
        notch.pushEdge( adjEdge, amt )
        print '   after adj push:', notch

        if notch.x2 - notch.x1 <= 0:
            return
        if notch.y2 - notch.y1 <= 0:
            return

        # Find all regions that the notch collides with.
        for region in filter( lambda r: r.intersects( notch ), self.regions ):
            print '    INT ->', region
            copyRegion = copy.copy( region )

            attrs = ['x1', 'x2', 'y1', 'y2']
            attrs = filter( lambda attr: getattr( region, attr ) == getattr( notch, attr ), attrs )
            if attrs:

                setattr( region, attrs[0], getattr( notch, TowerRegion.getOppositeEdgeAttribute( attrs[0] ) ) )

                if len( attrs ) > 1:
                    setattr( copyRegion, attrs[1], getattr( notch, TowerRegion.getOppositeEdgeAttribute( attrs[1] ) ) )

            else:
                print '    WARN: ', region, 'could not find and edges overlapping with notch'

            self.regions.append( copyRegion )

        self.notch = notch

    def cleanUp( self ):

        # Remove any region that has width or height of zero.
        for i in reversed( range( len( self.regions ) ) ):
            if not self.regions[i].width or not self.regions[i].height:
                self.regions.pop( i )


class Tower( object ):

    def __init__( self, numChunks, chunkSizeX, chunkSizeY ):
        self.numChunks = numChunks
        self.chunkSizeX = chunkSizeX
        self.chunkSizeY = chunkSizeY
        self.chunks = []

    def generate( self ):
        print '*' * 35
        for i in range( self.numChunks ):

            print i

            # Copy previous chunk if possible.
            chunk = None
            if i < 1:
                chunk = TowerChunk( [TowerRegion( 0, 0, self.chunkSizeX, self.chunkSizeY )] )
            else:
                chunk = copy.copy( self.chunks[-1] )

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