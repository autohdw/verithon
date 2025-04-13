###################################################################################################
# Module Name: M2V
# Description: This module performs matrix and vector multiplication.
# Author: Changhan Li
# Date: 2025.04.02
# Version: V0.1.0
# Doc Version: V0.1.0
# Dependency Modules:
#     - AdderTree (V0.1.0)
#     - Mul (V0.2.1) 
#     - Add (V0.2.1)
#     - PyTU (V0.0.2)
#     - FxMatch (V0.2.1)
#     - Delay (V0.1.0)
# Release Notes: 
#     - V0.1.0: Initial Draft
###################################################################################################

import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader
import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(__file__)))
sys.path.append(dirname(__file__))
from PyTU import QuMode, OfMode, QuType


moduleloader.set_look_ahead_speedup(True)
import math

from Delay import ModuleDelay
from FxMatch import ModuleFxMatch
from Mul import ModuleMul
from Add import ModuleAdd
from Sub import ModuleSub
from AdderTree import ModuleAdderTree


@convert
def ModuleMyPrint(a,b,c=1):
    #/ reg AAAA `a+b+c`
    pass

@convert
def ModuleM2V(M:int, V:int, QU_M:QuType, QU_V:QuType, QU_M_V:QuType, QU_OUT:QuType, QU_MODE:QuMode, OF_MODE:OfMode, TYPE="REAL", N_PIPELINES = [1, 1]):

    # Parse the input arguments
    # print(f"LINE42")
    # print(f"{N_PIPELINES}")
    N_CLK = sum(N_PIPELINES)
    # print(f"LINE44")
    #/ module M2V(
    #/     i_matrix, i_vector, o_result,
    #/     i_clk
    #/ );
    # Port Declaration
    # for i in range(0,100):
    #     ModuleMyPrint(a=i,b=3,OUTMODE='PRINT')
    if TYPE == "REAL":
        # Matrix is stored in col-major order
        #/ input wire [`M`*`V`*`QU_M.DWT`-1:0] i_matrix;
        #/ input wire [`V`*`QU_V.DWT`-1:0] i_vector;
        #/ output wire [`M`*`QU_OUT.DWT`-1:0] o_result;
        pass
    else: # TYPE == "COMPLEX"
        # Complex number form: MSB[Complex, Real]LSB
        #/ input wire [2*`M`*`V`*`QU_M.DWT`-1:0] i_matrix;
        #/ input wire [2*`V`*`QU_V.DWT`-1:0] i_vector;
        #/ output wire [2*`M`*`QU_OUT.DWT`-1:0] o_result;
        pass
    # print(f"LINE62")
    #/ input wire i_clk;
    
    if TYPE == "REAL":
        #========= Multiplication ========#
        #/ wire [`QU_M_V.DWT`-1:0] mult_result [0:`M`-1][0:`V`-1];
        for m in range(M):
            for v in range(V):
                inst_ports = {
                    "i_data_1": f"i_matrix[{v*M+m}*{QU_M.DWT}+:{QU_M.DWT}]",
                    "i_data_2": f"i_vector[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                    "o_data": f"mult_result[{m}][{v}]",
                    "i_clk": "i_clk"
                }
                ModuleMul(QU_IN_1=QU_M, QU_IN_2=QU_V, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[0], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=inst_ports)
                pass
        #========= Reduction ========#
        if V == 1:
            for m in range(M):
                #/ assign o_result[`m`*`QU_OUT.DWT`+:`QU_OUT.DWT`] = mult_result[`m`][0];
                pass
        else: # V > 1
            for m in range(M):
                i_data_str = "{" + ",".join([f"mult_result[{m}][{v}]" for v in range(V-1, -1, -1)]) + "}"
                inst_ports = {
                    "i_data": i_data_str,
                    "o_data": f"o_result[{m}*{QU_OUT.DWT}+:{QU_OUT.DWT}]"
                }
                if N_PIPELINES[1] > 0:
                    inst_ports["i_clk"] = "i_clk"
                ModuleAdderTree(QU_IN=QU_M_V, QU_OUT=QU_OUT, N_PIPELINES=N_PIPELINES[1], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, N_INPUTS=V, CONFIG_MODE="A", PORTS=inst_ports)
                pass
        
    else: # TYPE == "COMPLEX"
        #/ wire [`M`*`V`*`QU_M.DWT`-1:0] matrix_r, matrix_i;
        #/ wire [`V`*`QU_V.DWT`-1:0] vector_r, vector_i;
        #/ assign matrix_r = i_matrix[`M`*`V`*`QU_M.DWT`-1:0];
        #/ assign matrix_i = i_matrix[2*`M`*`V`*`QU_M.DWT`-1:`M`*`V`*`QU_M.DWT`];
        #/ assign vector_r = i_vector[`V`*`QU_V.DWT`-1:0];
        #/ assign vector_i = i_vector[2*`V`*`QU_V.DWT`-1:`V`*`QU_V.DWT`];
        
        #/ // Layer 1: Add and Sub
        QU_L1V = QuType(DWT=QU_V.DWT+1, FRAC=QU_V.FRAC, IF_SIGNED=QU_V.IF_SIGNED)
        QU_L1M = QuType(DWT=QU_M.DWT+1, FRAC=QU_M.FRAC, IF_SIGNED=QU_M.IF_SIGNED)
        #/ wire [`QU_L1V.DWT`-1:0] a_plus_b [0:`V`-1];
        #/ wire [`QU_L1V.DWT`-1:0] b_minus_a [0:`V`-1];
        #/ wire [`QU_L1M.DWT`-1:0] c_plus_d [0:`M`-1][0:`V`-1];
        for v in range(V):
            a_plus_b_ports = {
                "i_data_1": f"vector_r[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                "i_data_2": f"vector_i[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                "o_data": f"a_plus_b[{v}]"
            }
            b_minus_a_ports = {
                "i_data_1": f"vector_i[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                "i_data_2": f"vector_r[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                "o_data": f"b_minus_a[{v}]"
            }
            if N_PIPELINES[0] > 0:
                a_plus_b_ports["i_clk"] = "i_clk"
                b_minus_a_ports["i_clk"] = "i_clk"
            ModuleAdd(QU_IN_1=QU_V, QU_IN_2=QU_V, QU_OUT=QU_L1V, N_PIPELINES=N_PIPELINES[0], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=a_plus_b_ports)
            ModuleSub(QU_IN_1=QU_V, QU_IN_2=QU_V, QU_OUT=QU_L1V, N_PIPELINES=N_PIPELINES[0], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=b_minus_a_ports)
            # print(f"FINISHED GENERATING MODULE SUB [LINE124]")
            for m in range(M):
                c_plus_d_ports = {
                    "i_data_1": f"matrix_r[{v*M+m}*{QU_M.DWT}+:{QU_M.DWT}]",
                    "i_data_2": f"matrix_i[{v*M+m}*{QU_M.DWT}+:{QU_M.DWT}]",
                    "o_data": f"c_plus_d[{m}][{v}]"
                }
                if N_PIPELINES[0] > 0:
                    c_plus_d_ports["i_clk"] = "i_clk"
                ModuleAdd(QU_IN_1=QU_M, QU_IN_2=QU_M, QU_OUT=QU_L1M, N_PIPELINES=N_PIPELINES[0], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=c_plus_d_ports)
                pass
        #     print(f"FINISHED GENERATING MODULE ADD [LINE134]")
        # print(f"FINISHED GENERATING MODULE ADD AND SUB [LINE136]")
        #/ // L1 Pipeline Registers
        #/ wire [`M`*`V`*`QU_M.DWT`-1:0] matrix_r_d, matrix_i_d;
        #/ wire [`V`*`QU_V.DWT`-1:0] vector_i_d;
        matrix_r_d_ports = {
            "i_data": "matrix_r",
            "o_data": "matrix_r_d"
        }
        matrix_i_d_ports = {
            "i_data": "matrix_i",
            "o_data": "matrix_i_d"
        }
        vector_i_d_ports = {
            "i_data": "vector_i",
            "o_data": "vector_i_d"
        }
        if N_PIPELINES[0] > 0:
            matrix_r_d_ports["i_clk"] = "i_clk"
            matrix_i_d_ports["i_clk"] = "i_clk"
            vector_i_d_ports["i_clk"] = "i_clk"
        ModuleDelay(DWT=M*V*QU_M.DWT, N_CLK=N_PIPELINES[0], IF_RST_N=False, PORTS=matrix_r_d_ports)
        ModuleDelay(DWT=M*V*QU_M.DWT, N_CLK=N_PIPELINES[0], IF_RST_N=False, PORTS=matrix_i_d_ports)
        ModuleDelay(DWT=V*QU_V.DWT, N_CLK=N_PIPELINES[0], IF_RST_N=False, PORTS=vector_i_d_ports)
        
        #/ // Layer 2: Multiply
        #/ wire [`QU_M_V.DWT`-1:0] A [0:`M`-1][0:`V`-1];
        #/ wire [`QU_M_V.DWT`-1:0] B [0:`M`-1][0:`V`-1];
        #/ wire [`QU_M_V.DWT`-1:0] C [0:`M`-1][0:`V`-1];
        for m in range(M):
            for v in range(V):
                A_ports = {
                    "i_data_1": f"a_plus_b[{v}]",
                    "i_data_2": f"matrix_r_d[{v*M+m}*{QU_M.DWT}+:{QU_M.DWT}]",
                    "o_data": f"A[{m}][{v}]"
                }
                B_ports = {
                    "i_data_1": f"c_plus_d[{m}][{v}]",
                    "i_data_2": f"vector_i_d[{v}*{QU_V.DWT}+:{QU_V.DWT}]",
                    "o_data": f"B[{m}][{v}]"
                }
                C_ports = {
                    "i_data_1": f"b_minus_a[{v}]",
                    "i_data_2": f"matrix_i_d[{v*M+m}*{QU_M.DWT}+:{QU_M.DWT}]",
                    "o_data": f"C[{m}][{v}]"
                }
                if N_PIPELINES[1] > 0:
                    A_ports["i_clk"] = "i_clk"
                    B_ports["i_clk"] = "i_clk"
                    C_ports["i_clk"] = "i_clk"
                ModuleMul(QU_IN_1=QU_L1V, QU_IN_2=QU_M, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[1], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=A_ports)
                ModuleMul(QU_IN_1=QU_L1M, QU_IN_2=QU_V, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[1], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=B_ports)
                ModuleMul(QU_IN_1=QU_L1V, QU_IN_2=QU_M, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[1], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=C_ports)
        
        #/ // Layer 3: Subtraction
        #/ wire [`QU_M_V.DWT`-1:0] mult_result_r [0:`M`-1][0:`V`-1];
        #/ wire [`QU_M_V.DWT`-1:0] mult_result_i [0:`M`-1][0:`V`-1];
        for m in range(M):
            for v in range(V):
                mult_result_r_ports = {
                    "i_data_1": f"A[{m}][{v}]",
                    "i_data_2": f"B[{m}][{v}]",
                    "o_data": f"mult_result_r[{m}][{v}]"
                }
                mult_result_i_ports = {
                    "i_data_1": f"B[{m}][{v}]",
                    "i_data_2": f"C[{m}][{v}]",
                    "o_data": f"mult_result_i[{m}][{v}]"
                }
                if N_PIPELINES[2] > 0:
                    mult_result_r_ports["i_clk"] = "i_clk"
                    mult_result_i_ports["i_clk"] = "i_clk"
                ModuleSub(QU_IN_1=QU_M_V, QU_IN_2=QU_M_V, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[2], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=mult_result_r_ports)
                ModuleSub(QU_IN_1=QU_M_V, QU_IN_2=QU_M_V, QU_OUT=QU_M_V, N_PIPELINES=N_PIPELINES[2], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, PORTS=mult_result_i_ports)
                
        #========= Reduction ========#
        #/ wire [`M`*`QU_OUT.DWT`-1:0] result_r;
        #/ wire [`M`*`QU_OUT.DWT`-1:0] result_i;
        #/ assign o_result = {result_i, result_r};
        
        if V == 1:
            #/ assign result_r[`m`*`QU_OUT.DWT`+:`QU_OUT.DWT`] = mult_result_r[`m`][0];
            #/ assign result_i[`m`*`QU_OUT.DWT`+:`QU_OUT.DWT`] = mult_result_i[`m`][0];
            pass
        else: # V > 1
            for m in range(M):
                inst_ports_r = {
                    "i_data": "{" + ",".join([f"mult_result_r[{m}][{v}]" for v in range(V-1, -1, -1)]) + "}",
                    "o_data": f"result_r[{m}*{QU_OUT.DWT}+:{QU_OUT.DWT}]"
                }
                inst_ports_i = {
                    "i_data": "{" + ",".join([f"mult_result_i[{m}][{v}]" for v in range(V-1, -1, -1)]) + "}",
                    "o_data": f"result_i[{m}*{QU_OUT.DWT}+:{QU_OUT.DWT}]"
                }
                if N_PIPELINES[3] > 0:
                    inst_ports_r["i_clk"] = "i_clk"
                    inst_ports_i["i_clk"] = "i_clk"
                ModuleAdderTree(QU_IN=QU_M_V, QU_OUT=QU_OUT, N_PIPELINES=N_PIPELINES[3], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, N_INPUTS=V, CONFIG_MODE="A", PORTS=inst_ports_r)
                ModuleAdderTree(QU_IN=QU_M_V, QU_OUT=QU_OUT, N_PIPELINES=N_PIPELINES[3], QU_MODE=QU_MODE, OF_MODE=OF_MODE, IF_RST_N=False, N_INPUTS=V, CONFIG_MODE="A", PORTS=inst_ports_i)
                pass
        pass
    #/ endmodule
    pass
    

if __name__ == "__main__":
    moduleloader.set_root_dir("./RTL_V22_NEW_INSTALL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    moduleloader.set_debug_mode(True)
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()
    # print(f"IN MAIN FUNCTION")
    M =  256
    V =  4
    QU_M = QuType(DWT=12, FRAC=4, IF_SIGNED=True)
    QU_V = QuType(DWT=12, FRAC=4, IF_SIGNED=True)
    QU_M_V = QuType(DWT=12, FRAC=6, IF_SIGNED=True)
    QU_OUT = QuType(DWT=12, FRAC=8, IF_SIGNED=True)
    QU_MODE = QuMode.TRN.TCPL
    OF_MODE = OfMode.WRP.TCPL
    # TYPE = "REAL"
    # N_PIPELINES = [1, 1]
    
    TYPE = "COMPLEX"
    N_PIPELINES = [1, 1, 1, 1]
    # moduleloader.set_debug_mode(False)
    import time

    start = time.perf_counter()
    ModuleM2V(M=M, V=V, QU_M=QU_M, QU_V=QU_V, QU_M_V=QU_M_V, QU_OUT=QU_OUT, QU_MODE=QU_MODE, OF_MODE=OF_MODE, TYPE = TYPE, N_PIPELINES=N_PIPELINES)
    end = time.perf_counter()
    print(f"Total time is {end-start: 6f}s")


