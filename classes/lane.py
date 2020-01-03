'''
Created on Aug 11, 2018

@author: Babtu
'''
class Lane():
    '''
    A single lane, or a component of an intersection.
    Attributes:
        pts    A set of coordinates which bound the lane on the intersection's image.
        index  The index of the point which divides the top half of the lane from the bottom half.
        type   The direction which cars in the lane travel.
    '''

    def __init__(self, pts, index, type):
        self.pts = pts
        self.index = index
        self.type = type
