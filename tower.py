import copy
import random

from pglib import Region


class TowerChunk( Region ):

    def __init__( self, regions ):
        self.regions = regions

    def addRegion( self ):

        # Randomise a region to copy.
        rIdx = random.randint( 0, len( self.regions ) - 1 )
        region = copy.copy( self.regions[rIdx] )
        self.regions.append( region )

        # Randomly pick and edge.
        eIdx = random.randint( 0, 3 )
        edge = ['x1', 'x2', 'y1', 'y2'][eIdx]
        sign = [-1, 1][random.randint( 0, 1 )]
        d = random.randint( 1, 1 )
        amt = getattr( region, edge )
        setattr( region, edge, amt + d * sign )

    def __copy__( self ):
        return TowerChunk( [
            copy.copy( region )
            for region in self.regions
        ] )


class Tower( object ):

    def __init__( self, numChunks, chunkSizeX, chunkSizeY ):
        self.numChunks = numChunks
        self.chunkSizeX = chunkSizeX
        self.chunkSizeY = chunkSizeY
        self.chunks = []

    def generate( self ):
        for i in range( self.numChunks ):

            # Copy previous chunk if possible.
            chunk = None
            if i < 1:
                chunk = TowerChunk( [Region( 0, 0, self.chunkSizeX, self.chunkSizeY )] )
            else:
                chunk = copy.copy( self.chunks[-1] )

                # Increase number of regions...?
                if True:
                    chunk.addRegion()

            self.chunks.append( chunk )