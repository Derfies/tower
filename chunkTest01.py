import copy
import random
from functools import partial

import nodebox.graphics as nbg

import pglib
import tower
from pglib.weights import SineWeight
from pglib import Region, RandomRegions
from nodeBoxApplication import NodeBoxApplication





class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):

        t = tower.Tower( 8, 10, 10 )
        t.generate()

        drawFns = []
        offset = 0
        for i, chunk in enumerate( t.chunks ):
            outline = Region( offset, 5, offset + 10, 15 )
            drawFns.append( self.regionToRect( outline, stroke=(0, 1, 0, 0.25), strokewidth=10 ) )

            if chunk.notch is not None:
                chunk.notch.x1 += offset
                chunk.notch.x2 += offset
                chunk.notch.y1 += 5
                chunk.notch.y2 += 5
                drawFns.append( self.regionToRect( chunk.notch, fill=(0, 0, 1, 0.3), stroke=(0, 0, 1, 0.75), strokewidth=4 ) )

            #for point in chunk.points:
            #    drawFns.append( partial( nbg.ellipse, *[(point.x + offset) * self.gridSpacing, (point.y + 5) * self.gridSpacing, 10, 10], fill=(0, 0, 1, 1) ) )


            for point in chunk.dots:
                drawFns.append( partial( nbg.ellipse, *[(point.x + offset) * self.gridSpacing, (point.y + 5) * self.gridSpacing, 5, 5], fill=(0, 1, 0, 1) ) )


            if i > 0:
                for region in t.chunks[i - 1].regions:
                    r = copy.copy( region )
                    r.x1 += 15
                    r.x2 += 15
                    drawFns.append( self.regionToRect( r, fill=(0.25, 0.25, 0, 1) ) )

           
            for region in chunk.regions:
                region.x1 += offset
                region.x2 += offset
                region.y1 += 5
                region.y2 += 5
                drawFns.append( self.regionToRect( region, fill=(1, 0, 0, 0.5), stroke=(1, 0, 0, 0.5), strokewidth=2 ) )
            offset += 15
        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 20
    SCREEN_WIDTH = 140 * GRID_SPACING
    SCREEN_HEIGHT = 20 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )