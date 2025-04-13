# PyTU Version 0.0.2
from enum import Enum

class QuMode:

    class TRN(Enum):# Truncate Method
        TCPL = 0 
        SMGN = 1
    
    class RND(Enum):# Round Method
        POS_INF = 0
        NEG_INF = 1
        ZERO = 2
        INF = 3
        CONV = 4

class OfMode:

    class WRP(Enum):
        TCPL = 0
    
    class SAT(Enum):
        TCPL = 0
        SMGN = 1
        ZERO = 2


class QuType:
    DWT = 8
    FRAC = 4
    IF_SIGNED = True
    def __init__(self, DWT = 8, FRAC = 4, IF_SIGNED = True):
        self.DWT = DWT
        self.FRAC = FRAC
        self.IF_SIGNED = IF_SIGNED
    def MSB(self):
        return self.DWT - self.FRAC - 1
    def LSB(self):
        return - self.FRAC
    
    def set_dwt_frac(self, msb, lsb):
        self.DWT = msb - lsb + 1
        self.FRAC = - lsb

    def set(self,**kwargs):
        '''
        No conflict will occur even if you write MSB=... and LSB=... in set function.
        '''
        msb_helper = kwargs.get('MSB')
        lsb_helper = kwargs.get('LSB')
        if msb_helper is not None and lsb_helper is not None:
            msb_value = msb_helper() if callable(msb_helper) else msb_helper
            lsb_value = lsb_helper() if callable(lsb_helper) else lsb_helper
            self.set_dwt_frac(msb_value, lsb_value)
        else:
            print("MSB or LSB is missing")

    