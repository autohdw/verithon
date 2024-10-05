# import pytv
from pytv import convert
from pytv import moduleloader

# import mycls
# from mycl import QuType

from enum import Enum


class QuMode:
    class TRN(Enum):
        TCPL = 0
        SMGN = 1

    class RND(Enum):
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

    def __init__(self, DWT, FRAC, IF_SIGNED):
        self.DWT = DWT
        self.FRAC = FRAC
        self.IF_SIGNED = IF_SIGNED

@convert
def ModuleEmpty1(p1):
    #/ module  Empty1()
    #/ xxxxx
    #/ reg [`p1`:0] data
    #/ endmodule
    pass

@convert
def ModuleFX_Match(QU_IN, QU_OUT, QU_MODE=QuMode.TRN.TCPL, OF_MODE=OfMode.WRP.TCPL, N_CLK=0, IF_RST=0):
    #/ module FX_MATCH(
    #/ data_in,
    #/ data_out,
    #/ clk,
    #/ rst
    #/ );
    ModuleBasic(p1=1,p2=2,PORTS=[])
    ModuleBasic(p1=-1,p2=1,PORTS=["M"])
    ModuleBasic(p1=1,p2=2,PORTS=["A","B"])
    ModuleBasic(p1=-1,p2=1)
    ModuleEmpty1(p1=5)
    #/ start of FX_MATCH
    #/ middle of FX_MATCH
    #/ end of FX_MATCH
    #/ endmodule
    pass


@convert
def ModuleBasic(p1, p2):
    #/ module BASIC(
    if p1 > 0:
        #/ portBA1,
        pass
    if p2 > 0:
        #/ portBA2,
        pass
    #/ );
    #/ start of BASIC
    #/ middle of BASIC
    #/ end of BASIC
    #/ endmodule


# if __name__ == "__main__":
moduleloader.set_root_dir(".\RTL")
moduleloader.set_naming_mode("SEQUENTIAL")
# moduleloader.saveParams()
moduleloader.disEnableWarning()

# inst_ports_dict = {'PORT1':'name_port1', 'PORT2':'name_port2'}
inst_ports_list = ['m','n','p', 'q']

ModuleBasic(p1=1, p2=2, PORTS=['A','B'])
ModuleFX_Match(QU_IN=QuType(8, 4, True), QU_OUT=QuType(8, 4, True),PORTS = inst_ports_list)
