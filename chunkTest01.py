import copy
import random

import pglib
from pglib.weights import SineWeight
from pglib import Region, RandomRegions
from nodeBoxApplication import NodeBoxApplication


class Chunk( Region ):

    def __init__( self, region, subChunks=None ):
        self.region = region
        
        # Generate some sub chunks if we don't have any.
        self.subChunks = subChunks
        if self.subChunks is None:
            self.subChunks = []
            for i in range( random.randint( 0, 3 ) ):
                self.subChunks.append( Region( 1, 1, 9, 9 ) )

    def __copy__( self ):
        return Chunk( copy.copy( self.region ), subChunks=[
            copy.copy( subChunk )
            for subChunk in self.subChunks
        ] )


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):

        chunks = []
        for i in range( 7 ):

            # Copy previous chunk if possible.
            chunk = None#
            if i < 1:
                chunk = Chunk( Region( -15, 0, -5, 10 ) )
            else:
                chunk = copy.copy( chunks[-1] )

            chunk.region.x1 += 15
            chunk.region.x2 += 15
            chunks.append( chunk )

        drawFns = []
        for chunk in chunks:
            colour = pglib.utils.getRandomColour( a=0.15 )
            drawFns.append( self.regionToRect( chunk.region, fill=colour, stroke=(1, 0, 0, 0.75), strokewidth=1 ) )
            for subChunk in chunk.subChunks:
                reg = subChunk
                reg.x1 += chunk.region.x1
                reg.x2 += chunk.region.x1
                drawFns.append( self.regionToRect( reg, fill=colour, stroke=(1, 0, 0, 0.75), strokewidth=3 ) )
        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 20
    SCREEN_WIDTH = 100 * GRID_SPACING
    SCREEN_HEIGHT = 20 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )