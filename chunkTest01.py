import copy
import random

import pglib
import tower
from pglib.weights import SineWeight
from pglib import Region, RandomRegions
from nodeBoxApplication import NodeBoxApplication





class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):

        t = tower.Tower( 5, 10, 10 )
        t.generate()

        drawFns = []
        offset = 5
        for chunk in t.chunks:
            outline = Region( offset, 5, offset + 10, 15 )
            drawFns.append( self.regionToRect( outline, stroke=(0, 1, 0, 0.75), strokewidth=10 ) )

            colour = pglib.utils.getRandomColour( a=0.15 )
            for region in chunk.regions:
                region.x1 += offset
                region.x2 += offset
                region.y1 += 5
                region.y2 += 5
                drawFns.append( self.regionToRect( region, fill=colour, stroke=(1, 0, 0, 0.75), strokewidth=2 ) )
            offset += 15
        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 20
    SCREEN_WIDTH = 100 * GRID_SPACING
    SCREEN_HEIGHT = 20 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )