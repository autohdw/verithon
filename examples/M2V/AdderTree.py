###################################################################################################
# Module Name: AdderTree
# Description: This module is used to sum multiple inputs fixed-point numbers.
# Author: Yifang Dai
# Date: 2025.4.1
# Version: V0.1.0
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
from Add import ModuleAdd
import math 

def has_non_zero(var):
    if isinstance(var, (int, float)):
        return var != 0
    elif isinstance(var, (list, tuple)):  
        return any(x != 0 for x in var)
    else:
        return True
    
# Explain Add_Tree module here
@convert
def ModuleAdderTree(QU_IN:QuType, QU_OUT:QuType, N_PIPELINES = 10, QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, IF_RST_N = False, N_INPUTS=2, CONFIG_MODE = "A"):
    
    # Parse Configuration Mode (Case Insensitive)
    CONFIG_MODE = CONFIG_MODE.lower()
    if CONFIG_MODE == "a" or CONFIG_MODE == "input-output" or CONFIG_MODE == "input_output" or CONFIG_MODE == "inout" or CONFIG_MODE == "auto":
        CONFIG_MODE = "A"
    elif CONFIG_MODE == "b" or CONFIG_MODE == "layer-wise" or CONFIG_MODE == "layer_wise":
        CONFIG_MODE = "B"
    elif CONFIG_MODE == "c" or CONFIG_MODE == "element-wise" or CONFIG_MODE == "element_wise":
        CONFIG_MODE = "C"
    else:
        CONFIG_MODE = "A"
        print("// Warning: Configuration Mode is not supported, set to default mode A")

    #----------------------------------------------------------------------------------
    n_layers = math.ceil(math.log2(N_INPUTS))

    QU_LAYERS: list[QuType] = [QuType() for _ in range(n_layers+1)]  
    
    if CONFIG_MODE == "A":
        if type(IF_RST_N) == bool:
            IF_RST_N = [IF_RST_N] * N_PIPELINES
        # Convert Mode A Input to Mode B Input
        # QMode, OMode, if_arst_n, if_rst_n, if_en are the same for all layers
        QU_MODE = [QU_MODE] * n_layers
        OF_MODE = [OF_MODE] * n_layers
        # N_PIPELINES should distribute evenly to all layers
        base_pipelines = N_PIPELINES // n_layers
        extra_pipelines = N_PIPELINES % n_layers
        N_PIPELINES = [base_pipelines if i < n_layers - extra_pipelines else base_pipelines + 1 for i in range(n_layers)]
        # dwt_layers start from dwt_in and increase by 1, except the last being dwt_out
        for i in range(n_layers):
            QU_LAYERS[i].DWT = QU_IN.DWT + i
            # QU_LAYERS.FRAC are all the same as frac_in, except the last being frac_out
            QU_LAYERS[i].FRAC = QU_IN.FRAC
            QU_LAYERS[i].IF_SIGNED = QU_IN.IF_SIGNED
        QU_LAYERS[n_layers].DWT = QU_OUT.DWT
        QU_LAYERS[n_layers].FRAC = QU_OUT.FRAC
        QU_LAYERS[n_layers].IF_SIGNED = QU_OUT.IF_SIGNED
        # Parse the Input Args:
    if CONFIG_MODE == "B":
        for i in range(n_layers):
            QU_LAYERS[i].DWT = QU_IN[i].DWT
            QU_LAYERS[i].FRAC = QU_IN[i].FRAC
            QU_LAYERS[i].IF_SIGNED = QU_IN[i].IF_SIGNED
        QU_LAYERS[n_layers].DWT = QU_OUT.DWT
        QU_LAYERS[n_layers].FRAC = QU_OUT.FRAC
        QU_LAYERS[n_layers].IF_SIGNED = QU_OUT.IF_SIGNED
        if type(IF_RST_N) == bool:
            IF_RST_N = [IF_RST_N] * sum(N_PIPELINES)
        pass

    #/ module ADDERTREE(
    #/  i_data,
    #/  o_data,
    if has_non_zero(N_PIPELINES):
        
        if any(IF_RST_N) == True:
            #/ i_rst_n,
            pass
        #/ i_clk     
    #/);

    #/ // Input and Output Ports
    #/ input wire [`QU_LAYERS[0].DWT * N_INPUTS`-1:0] i_data;
    #/ output wire [`QU_OUT.DWT`-1:0] o_data;
    if has_non_zero(N_PIPELINES):
        #/ input wire i_clk; 
        if any(IF_RST_N) == True:
            #/ input wire i_rst_n;
            pass
    #/ wire [`QU_LAYERS[0].DWT * N_INPUTS`-1:0] data0;
    #/ assign data0 = i_data;
    n_operators = N_INPUTS

    for layer in range(n_layers):
        n_remainder = n_operators % 2
        n_adders = n_operators // 2
        n_operators = n_adders + n_remainder
        
        #/ wire [`n_operators*QU_LAYERS[layer+1].DWT`-1:0] data`layer+1`;
        QU_IN_FIX = QuType()
        QU_OUT_FIX = QuType()
        QU_IN_FIX.DWT = QU_LAYERS[layer].DWT
        QU_IN_FIX.FRAC = QU_LAYERS[layer].FRAC
        QU_IN_FIX.IF_SIGNED = QU_LAYERS[0].IF_SIGNED
        QU_OUT_FIX.DWT = QU_LAYERS[layer+1].DWT
        QU_OUT_FIX.FRAC = QU_LAYERS[layer+1].FRAC
        QU_OUT_FIX.IF_SIGNED = QU_LAYERS[0].IF_SIGNED
        for adder in range(n_adders):
            inst_ports_add = {
                "i_data_1": f"data{layer}[{2*adder+1}*{QU_LAYERS[layer].DWT}-1:{2*adder}*{QU_LAYERS[layer].DWT}]",
                "i_data_2": f"data{layer}[{2*adder+2}*{QU_LAYERS[layer].DWT}-1:{2*adder+1}*{QU_LAYERS[layer].DWT}]",
                "o_data": f"data{layer+1}[{adder+1}*{QU_LAYERS[layer+1].DWT}-1:{adder}*{QU_LAYERS[layer+1].DWT}]"
            }
            if N_PIPELINES[layer] > 0:
                inst_ports_add["i_clk"] = "i_clk"
                if type(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]) == bool:
                    if(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]):
                        inst_ports_add["i_rst_n"] = "i_rst_n"
                else:
                    if any(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]):
                        inst_ports_add["i_rst_n"] = "i_rst_n"
            ModuleAdd(QU_IN_1 = QU_IN_FIX, QU_IN_2 = QU_IN_FIX, QU_OUT = QU_OUT_FIX, QU_MODE = QU_MODE[layer], OF_MODE = OF_MODE[layer], IF_RST_N=IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])], N_PIPELINES=N_PIPELINES[layer], PORTS = inst_ports_add)

        if n_remainder == 1:
            #/ wire [`QU_LAYERS[layer].DWT`-1:0] remainder_l`layer+1`;
            inst_ports_delay = {
                "i_data": f"data{layer}[{(2*n_operators-1)}*{QU_LAYERS[layer].DWT}-1:{(2*n_operators-2)}*{QU_LAYERS[layer].DWT}]",
                "o_data": f"remainder_l{layer+1}"
            }
            if N_PIPELINES[layer] > 0:
                inst_ports_delay["i_clk"] = "i_clk"
                if type(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]) == bool:
                    if(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]):
                        inst_ports_delay["i_rst_n"] = "i_rst_n"
                else:
                    if any(IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])]):
                        inst_ports_delay["i_rst_n"] = "i_rst_n"

                ModuleDelay(DWT = QU_IN_FIX.DWT, N_CLK = N_PIPELINES[layer], IF_RST_N = IF_RST_N[sum(N_PIPELINES[:layer]):sum(N_PIPELINES[:layer+1])], PORTS = inst_ports_delay)
            
                inst_ports_fxmatch_1 = {
                    "i_data": f"remainder_l{layer+1}",
                    "o_data":  f"data{layer+1}[{n_operators}*{QU_LAYERS[layer+1].DWT}-1:{(n_operators-1)}*{QU_LAYERS[layer+1].DWT}]"
                }
                ModuleFxMatch(QU_IN=QU_IN_FIX, QU_OUT=QU_OUT_FIX, QU_MODE = QU_MODE[layer], OF_MODE = OF_MODE[layer], PORTS = inst_ports_fxmatch_1)
            else:
                inst_ports_fxmatch_1 = {
                    "i_data": f"data{layer}[{(2*n_operators-1)}*{QU_LAYERS[layer].DWT}-1:{(2*n_operators-2)}*{QU_LAYERS[layer].DWT}]",
                    "o_data":  f"data{layer+1}[{n_operators}*{QU_LAYERS[layer+1].DWT}-1:{(n_operators-1)}*{QU_LAYERS[layer+1].DWT}]"
                }
                ModuleFxMatch(QU_IN=QU_IN_FIX, QU_OUT=QU_OUT_FIX, QU_MODE = QU_MODE[layer], OF_MODE = OF_MODE[layer], PORTS = inst_ports_fxmatch_1)
    
    #/ assign o_data = data`n_layers`; 
    #/ endmodule
if __name__ == "__main__":
    moduleloader.set_root_dir("./RTL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()

    # ModuleAdd(QU_IN_1=QuType(9,3,True),QU_IN_2=QuType(10,4,True),QU_OUT=QuType(9,3,True),N_PIPELINES=0) # Combinational

    ModuleAdderTree(QU_IN = [QuType(10,2,True),QuType(9,2,True)], QU_OUT = QuType(9,2,True), N_PIPELINES = [2,3],  QU_MODE = [QuMode.TRN.TCPL,QuMode.TRN.TCPL], OF_MODE = [OfMode.WRP.TCPL,OfMode.WRP.TCPL], IF_RST_N = True, CONFIG_MODE = "B") # Sequential
