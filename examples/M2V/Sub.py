###################################################################################################
# Module Name: Sub
# Description: This module is used to subtract two fixed-point numbers.
# Author: Bolin Li
# Author: Yifang Dai
# Date: 2025.3.30
# Version: V0.2.1
# Doc Version: V0.1.0
# Dependency Modules: 
#   - Delay (V 0.1.0)
#   - FxMatch (V 0.2.1)
###########################################################################
import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
sys.path.append(dirname(__file__))

import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader

from enum import Enum

from PyTU import QuMode, OfMode, QuType
from Delay import ModuleDelay
from FxMatch import ModuleFxMatch

# Explain SUB module here
@convert
def ModuleSub(QU_IN_1, QU_IN_2, QU_OUT, N_PIPELINES = 0, QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, IF_RST_N = False):
    # Parse the Input Args:
    if type(IF_RST_N) == bool:
        IF_RST_N = [IF_RST_N] * N_PIPELINES
        pass


    

    #/ module SUB(
    #/ i_data_1,
    #/ i_data_2,
    #/ o_data
    if N_PIPELINES > 0:
        
        if any(IF_RST_N) == True:
            #/ , i_rst_n
            pass

        #/ , i_clk     
    #/);

    #/ // Input and Output Ports
    #/ input wire [`QU_IN_1.DWT`-1:0] i_data_1;
    #/ input wire [`QU_IN_2.DWT`-1:0] i_data_2;
    #/ output wire [`QU_OUT.DWT`-1:0] o_data;

    #/ // Internal interface
    #/ wire [`QU_IN_1.DWT`-1:0] data_1;
    #/ wire [`QU_IN_2.DWT`-1:0] data_2;
    if N_PIPELINES > 0:
        #/ input wire i_clk; 
        if any(IF_RST_N) == True:
            #/ input wire i_rst_n;
            pass

    
    #/ assign data_1 = i_data_1;       
    #/ assign data_2 = i_data_2;


    #/ // Minus data_2_minus

    #/ wire [`QU_IN_2.DWT`:0] data_2_minus;
    if QU_IN_2.IF_SIGNED == True:
        #/ assign data_2_minus =  ~{data_2[`QU_IN_2.DWT`-1], data_2} + 1'b1;
        pass
    else:
        #/ assign data_2_minus = ~{1'b0, data_2} + 1'b1;
        pass

    QU_IN_FIX = QuType()
    
    LSB_FIX = -max(QU_IN_1.FRAC, QU_IN_2.FRAC)
    MSB_FIX = max(QU_IN_1.DWT - QU_IN_1.FRAC, QU_IN_1.DWT - QU_IN_2.FRAC+1)

    QU_IN_FIX.DWT = MSB_FIX - LSB_FIX + 1
    QU_IN_FIX.FRAC = -LSB_FIX
    QU_IN_FIX.IF_SIGNED = QU_IN_1.IF_SIGNED or QU_IN_2.IF_SIGNED
    
    QU_IN_2_MINUS = QuType()
    QU_IN_2_MINUS.DWT = QU_IN_2.DWT+1
    QU_IN_2_MINUS.FRAC = QU_IN_2.FRAC
    QU_IN_2_MINUS.IF_SIGNED = QU_IN_2.IF_SIGNED
    #/ wire [`QU_IN_FIX.DWT`-1:0] data_1_fixed;
    #/ wire [`QU_IN_FIX.DWT`-1:0] data_2_fixed;

    # FxMatch
    inst_ports_fxmatch_1 = {
        "i_data": "data_1",
        "o_data": "data_1_fixed"
    }
    ModuleFxMatch(QU_IN = QU_IN_1, QU_OUT = QU_IN_FIX, QU_MODE = QU_MODE, OF_MODE = OF_MODE,IF_RST_N=IF_RST_N, PORTS = inst_ports_fxmatch_1)

    inst_ports_fxmatch_2 = {
        "i_data": "data_2_minus",
        "o_data": "data_2_fixed"
    }
    ModuleFxMatch(QU_IN=QU_IN_2_MINUS, QU_OUT=QU_IN_FIX, QU_MODE = QU_MODE, OF_MODE = OF_MODE,IF_RST_N=IF_RST_N, PORTS = inst_ports_fxmatch_2)

    # Adder

    #/ wire [`QU_IN_FIX.DWT`-1:0] result_unfixed;
    #/ wire [`QU_OUT.DWT`-1:0] result_fixed;
    #/ assign result_unfixed = data_1_fixed + data_2_fixed;
    # Output Fix
    inst_ports_fxmatch_3 = {
        "i_data": "result_unfixed",
        "o_data": "result_fixed"
    }
    ModuleFxMatch(QU_IN = QU_IN_FIX, QU_OUT = QU_OUT, QU_MODE = QU_MODE, OF_MODE = OF_MODE,IF_RST_N=IF_RST_N, PORTS = inst_ports_fxmatch_3)

    # Delay Module
    inst_ports = {
         "i_data": "result_fixed",
         "o_data": "o_data" 
    }
    if N_PIPELINES > 0:
        inst_ports["i_clk"] = "i_clk"
        if any(IF_RST_N):
            inst_ports["i_rst_n"] = "i_rst_n"

    ModuleDelay(DWT = QU_OUT.DWT, N_CLK = N_PIPELINES, IF_RST_N = IF_RST_N, PORTS = inst_ports)
    #/ endmodule
if __name__ == "__main__":
    moduleloader.set_root_dir("./RTL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()

    # ModuleAdd(QU_IN_1=QuType(9,3,True),QU_IN_2=QuType(10,4,True),QU_OUT=QuType(9,3,True),N_PIPELINES=0) # Combinational

    ModuleSub(QU_IN_1 = QuType(10,4,True), QU_IN_2 = QuType(9,3,True), QU_OUT = QuType(9,2,True), N_PIPELINES = 2, IF_ENABLE = True, IF_RST_N = True) # Sequential

