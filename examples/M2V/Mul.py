###################################################################################################
# Module Name: Mul
# Description: This module is used to Multiply two fixed-point numbers.
# Author: Bolin Li
# Author: Yifang Dai
# Date: 2025.3.30
# Version: V0.2.1
# Doc Version: V0.2.1 
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

@convert
def ModuleMul(QU_IN_1:QuType, QU_IN_2:QuType, QU_OUT:QuType, N_PIPELINES=0, QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, IF_RST_N=False):
    # Clock, Resets and Enables
    if N_PIPELINES > 0 and type(IF_RST_N) == bool:
        # Expand the boolean to a list of the same value
        IF_RST_N = [IF_RST_N] * N_PIPELINES


    #/ module MUL(
    #/ i_data_1, i_data_2, o_data
    if N_PIPELINES > 0:
        #/    ,i_clk
        if any(IF_RST_N):
            #/    , i_rst_n
            pass
    #/ );

    #/ input wire [`QU_IN_1.DWT-1`:0] i_data_1;
    #/ input wire [`QU_IN_2.DWT-1`:0] i_data_2;
    #/ output wire [`QU_OUT.DWT-1`:0] o_data;
    if N_PIPELINES > 0:
        #/ input wire i_clk;
        if any(IF_RST_N):
            #/ input wire i_rst_n;
            pass
        pass


    #/ wire [`QU_IN_1.DWT-1`:0] data_1;
    #/ wire [`QU_IN_2.DWT-1`:0] data_2;




    #/ assign data_1 = i_data_1;
    #/ assign data_2 = i_data_2;


    # Calculate the Multiplier Result Quantization Parameters
    DWT_FIX = QU_IN_1.DWT + QU_IN_1.FRAC
    FRAC_FIX = QU_IN_1.FRAC + QU_IN_2.FRAC
    SIGN_FIX = QU_IN_1.IF_SIGNED or QU_IN_2.IF_SIGNED
    QU_IN_FIX = QuType(DWT_FIX, FRAC_FIX, SIGN_FIX)
    


    # Sign-Magnitude Calculation
    #/ wire [`QU_IN_1.DWT-1`:0] data_1_abs;
    #/ wire [`QU_IN_2.DWT-1`:0] data_2_abs;
    #/ wire [`QU_IN_FIX.DWT-1`:0] data_mul_ures;
    if QU_IN_1.IF_SIGNED:
        #/ assign data_1_abs = data_1[`QU_IN_1.DWT-1`] ? {~data_1[`QU_IN_1.DWT-1`:0] + 1'b1} : data_1;
        pass
    else:
        #/ assign data_1_abs =  data_1;
        pass

    if QU_IN_2.IF_SIGNED:
        #/ assign data_2_abs = data_2[`QU_IN_2.DWT-1`] ? {~data_2[`QU_IN_2.DWT-1`:0] + 1'b1} : data_2;
        pass
    else:
        #/ assign data_2_abs =  data_2;
        pass

    #/ assign data_mul_ures = data_1_abs * data_2_abs;
    #/ wire res_sign;                   
    #/ wire [`QU_IN_FIX.DWT`:0] data_mul_res;

    
    if QU_IN_1.IF_SIGNED and QU_IN_2.IF_SIGNED:
        #/ assign res_sign = data_1[`QU_IN_1.DWT-1`] ^ data_2[`QU_IN_2.DWT-1`];
        #/ assign data_mul_res = res_sign ? {~{1'b0, data_mul_ures[`QU_IN_FIX.DWT-1`:0]} + 1'b1} : {1'b0, data_mul_ures}; 
        pass
    elif QU_IN_1.IF_SIGNED:
        #/ assign res_sign = data_1[`QU_IN_1.DWT-1`];
        #/ assign data_mul_res = res_sign ? {~{1'b0, data_mul_ures[`QU_IN_FIX.DWT-1`:0]} + 1'b1} : {1'b0, data_mul_ures};  
        pass
    elif QU_IN_2.IF_SIGNED:
        #/ assign res_sign = data_2[`QU_IN_2.DWT-1`];
        #/ assign data_mul_res = res_sign ? {~{1'b0, data_mul_ures[`QU_IN_FIX.DWT-1`:0]} + 1'b1} : {1'b0, data_mul_ures};  
        pass
    else:
        #/ assign res_sign = 1'b0;
        #/ assign data_mul_res = {1'b0, data_mul_ures};
        pass

    

    # Output FxMatch
    #/ wire [`QU_OUT.DWT-1`:0] result_fixed;
    inst_ports_fxmatch = {
        "i_data": "data_mul_res",
        "o_data": "result_fixed"
    }
    ModuleFxMatch(QU_IN = QU_IN_FIX, QU_OUT = QU_OUT, QU_MODE = QU_MODE, OF_MODE = OF_MODE,IF_RST_N=IF_RST_N, PORTS = inst_ports_fxmatch)

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
    moduleloader.set_root_dir(".//RTL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()

    # Test
    ModuleMul(QU_IN_1=QuType(10, 4, True), QU_IN_2=QuType(9, 3, True), QU_OUT=QuType(9, 2, True), N_PIPELINES=2, IF_ENABLE=True, IF_RST_N=True)
