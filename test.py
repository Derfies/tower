from functools import partial

import nodebox.graphics as nbg

import pglib
from pglib.weights import SineWeight
from pglib import Region, RandomRegions
from nodeBoxApplication import NodeBoxApplication


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):

        drawFns = []

        # Create tower base.
        roomNode = RandomRegions()
        roomNode.inputs['region'] = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        roomNode.inputs['minSize'] = 10
        roomNode.inputs['maxSize'] = 10
        roomNode.inputs['maxIterations'] = 1
        roomNode.inputs['intersect'] = True

        sineWeight = SineWeight()
        sineWeight.inputs['amplitude'] = 10000
        sineWeight.inputs['invert'] = False
        roomNode.inputs['centerWeight'] = sineWeight

        for region in roomNode.outputs['regions']:
            colour = pglib.utils.getRandomColour( a=0.5 )
            drawFns.append( self.regionToRect( region, fill=colour, stroke=(1, 0, 0, 0.75), strokewidth=5 ) )

        # roomNode = RandomRegions()
        # roomNode.inputs['region'] = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        # roomNode.inputs['minSize'] = 10
        # roomNode.inputs['maxSize'] = 20
        # roomNode.inputs['maxIterations'] = 100
        # roomNode.inputs['intersect'] = True

        # sineWeight = SineWeight()
        # sineWeight.inputs['amplitude'] = 1
        # sineWeight.inputs['invert'] = False
        # roomNode.inputs['centerWeight'] = sineWeight


        # for region in roomNode.outputs['regions']:
        #     colour = pglib.utils.getRandomColour( a=0.5 )
        #     rectArgs = [region.x1 * self.gridSpacing, region.y1 * self.gridSpacing, region.x2 * self.gridSpacing, region.y2 * self.gridSpacing]
        #     drawFns.append( partial( nbg.rect, *rectArgs, fill=colour, stroke=(1, 0, 0, 0.75) ) )

        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 20
    SCREEN_WIDTH = 20 * GRID_SPACING
    SCREEN_HEIGHT = 20 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )