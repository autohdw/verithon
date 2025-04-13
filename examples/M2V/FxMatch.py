###################################################################################################
# Module Name: FxMatch
# Description: This module is used to match the input data to the output data with different data width and fractional bits.
# Author: Changhan Li
# Author: Bolin Li
# Revised：Yifang Dai
# Date: 2024.12.4
# Revised Date:2025.3.24 
# Version: V0.2.1
# Doc Version: V0.1.0
# Dependency Modules: 
#     - Delay (V0.1.0)
# Release Notes: 
#     - V0.2.1: Fixed bugs in all round modes and checked results in all round modes.
###################################################################################################
import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader
import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(__file__)))
sys.path.append(dirname(__file__))
from Delay import ModuleDelay
from PyTU import QuMode, OfMode, QuType

@convert
def ModuleFxMatch(QU_IN, QU_OUT, QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, N_CLK = 0, IF_RST_N = False):
    # Parse the input arguments
    if type(IF_RST_N) == bool:
        IF_RST_N = [IF_RST_N] * N_CLK
    # End Parse the input arguments
    #/ module FxMatch(
    #/     i_data, o_data
    if N_CLK > 0:
        #/ , i_clk
        if any(IF_RST_N):
            #/ , i_rst_n
            pass
    #/ );
    #/ input wire [`QU_IN.DWT`-1:0] i_data;     // Input data
    #/ output wire [`QU_OUT.DWT`-1:0] o_data;   // Output data
    if N_CLK > 0:
        #/ input wire i_clk;                        // Clock
        if any(IF_RST_N):
            #/ input wire i_rst_n;                      // Reset, negative effective
            pass
    #/ //
    # For simplicity, unsigned input is expanded with a 0 sign bit, and for unsigned output, the sign bit is truncated.
    EQ_QU_IN = QuType()
    if QU_IN.IF_SIGNED == False:
        EQ_QU_IN.DWT = QU_IN.DWT + 1
        EQ_QU_IN.FRAC = QU_IN.FRAC
        EQ_QU_IN.IF_SIGNED = True
        #/ wire [`EQ_QU_IN.DWT`-1:0] i_data_eq;
        #/ assign i_data_eq = {1'b0, i_data};
    else:
        EQ_QU_IN = QU_IN
        #/ wire [`EQ_QU_IN.DWT`-1:0] i_data_eq;
        #/ assign i_data_eq = i_data;
    EQ_QU_OUT = QuType()
    if QU_OUT.IF_SIGNED == False:
        EQ_QU_OUT.DWT = QU_OUT.DWT + 1
        EQ_QU_OUT.FRAC = QU_OUT.FRAC
        EQ_QU_OUT.IF_SIGNED = True
    else:
        EQ_QU_OUT = QU_OUT
    # Rule out the case where only one stage is needed
    #/ wire [`EQ_QU_OUT.DWT`-1:0] o_data_eq;
    if EQ_QU_OUT.LSB() > EQ_QU_IN.MSB():
        # Quantization Stage only
        #/ // Quantization Stage
        if EQ_QU_OUT.LSB() - EQ_QU_IN.MSB() > 1:
            # Impossible to round up
            match QU_MODE:
                case QuMode.TRN.TCPL:
                    #/ assign o_data_eq = i_data_eq[`EQ_QU_IN.DWT`-1] ? {`EQ_QU_OUT.DWT`{1'b1}} : {`EQ_QU_OUT.DWT`{1'b0}};
                    pass
                case QuMode.RND.POS_INF | QuMode.TRN.SMGN | QuMode.RND.ZERO | QuMode.RND.CONV | QuMode.RND.NEG_INF | QuMode.RND.INF:
                    #/ assign o_data_eq = {`EQ_QU_OUT.DWT`{1'b0}};
                    pass
        else: # EQ_QU_OUT.LSB() - EQ_QU_IN.MSB() == 1
            # Possible to round up
            match QU_MODE:
                case QuMode.TRN.TCPL:
                    #/ assign o_data_eq = i_data_eq[`EQ_QU_IN.DWT`-1] ? {`EQ_QU_OUT.DWT`{1'b1}} : {`EQ_QU_OUT.DWT`{1'b0}};
                    pass
                case QuMode.TRN.SMGN | QuMode.RND.POS_INF | QuMode.RND.ZERO | QuMode.RND.CONV:
                    #/ assign o_data_eq = {`EQ_QU_OUT.DWT`{1'b0}};
                    pass
                case  QuMode.RND.INF  | QuMode.RND.NEG_INF:
                    #/ assign o_data_eq = (i_data_eq == {1'b1, {`EQ_QU_IN.DWT-1`{1'b0}}}) ? {`EQ_QU_OUT.DWT`{1'b1}} : {`EQ_QU_OUT.DWT`{1'b0}};
                    pass
            pass
    elif EQ_QU_OUT.MSB() < EQ_QU_IN.LSB():
        # Overflow Stage only
        #/ // Overflow Stage
        match OF_MODE:
            case OfMode.WRP.TCPL | OfMode.SAT.ZERO:
                #/ assign o_data_eq = {`EQ_QU_OUT.DWT`{1'b0}};
                pass
            case OfMode.SAT.TCPL:
                #/ assign o_data_eq = i_data_eq[`EQ_QU_IN.DWT`-1]
                #/                      ? {1'b1, {`EQ_QU_OUT.DWT-1`{1'b0}}}
                #/                      : {
                #/                          (i_data_eq == {`EQ_QU_IN.DWT`{1'b0}})
                #/                              ? {`EQ_QU_OUT.DWT`{1'b0}}
                #/                              : {1'b0, {`EQ_QU_OUT.DWT-1`{1'b1}}}
                #/                      };
                pass
            case OfMode.SAT.SMGN:
                if EQ_QU_OUT.DWT > 2:
                    #/ assign o_data_eq = i_data_eq[`EQ_QU_IN.DWT`-1]
                    #/                      ? {1'b1, {`EQ_QU_OUT.DWT-2`{1'b0}}, 1'b1}
                    #/                      : {
                    #/                          (i_data_eq == {`EQ_QU_IN.DWT`{1'b0}})
                    #/                              ? {`EQ_QU_OUT.DWT`{1'b0}}
                    #/                              : {1'b0, {`EQ_QU_OUT.DWT-1`{1'b1}}}
                    #/                      };
                    pass
                elif EQ_QU_OUT.DWT == 2:
                    #/ assign o_data_eq = i_data_eq[`EQ_QU_IN.DWT`-1]
                    #/                      ? {1'b1, 1'b1}
                    #/                      : {
                    #/                          (i_data_eq == {`EQ_QU_IN.DWT`{1'b0}})
                    #/                              ? {`EQ_QU_OUT.DWT`{1'b0}}
                    #/                              : {1'b0, {`EQ_QU_OUT.DWT-1`{1'b1}}}
                    #/                      };
                    pass
                else:
                    #/ assign o_data_eq = 1'b0;
                    pass
    else:
        # Both Quantization and Overflow Stages
        #/ // Quantization Stage
        QU_QUAN = QuType(IF_SIGNED = True)
        if EQ_QU_OUT.LSB() > EQ_QU_IN.LSB():
            # // Truncate / Round precision
            match QU_MODE:
                case QuMode.TRN.TCPL:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB(), LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ assign op_quan = i_data_eq[`EQ_QU_IN.DWT`-1:`EQ_QU_IN.DWT - QU_QUAN.DWT`];
                    pass
                case QuMode.TRN.SMGN:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB(), LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`-1:0] i_data_eq_abs;
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan_abs;
                    #/ assign i_data_eq_abs = i_data_eq[`EQ_QU_IN.DWT`-1] ? ~i_data_eq + 1'b1 : i_data_eq;
                    #/ assign op_quan_abs = i_data_eq_abs[`EQ_QU_IN.DWT`-1:`EQ_QU_IN.DWT - QU_QUAN.DWT`];
                    #/ assign op_quan = i_data_eq[`EQ_QU_IN.DWT`-1] ? ~op_quan_abs + 1'b1 : op_quan_abs;
                case QuMode.RND.POS_INF:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB()+1 , LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`:0] i_data_eq_fill;
                    #/ assign i_data_eq_fill = {i_data_eq[`EQ_QU_IN.DWT`-1] , i_data_eq};
                    comp_val = f"{EQ_QU_IN.DWT - QU_QUAN.DWT+1}'b1" + "0" * (EQ_QU_IN.DWT - QU_QUAN.DWT)
                    #/ assign op_quan = (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] >= `comp_val`)
                    #/                  ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                  : i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`];
                case QuMode.RND.NEG_INF:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB()+1 , LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`:0] i_data_eq_fill;
                    #/ assign i_data_eq_fill = {i_data_eq[`EQ_QU_IN.DWT`-1] , i_data_eq};
                    comp_val = f"{EQ_QU_IN.DWT - QU_QUAN.DWT+1}'b1" + "0" * (EQ_QU_IN.DWT - QU_QUAN.DWT)
                    #/ assign op_quan = (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] > `comp_val`)
                    #/                  ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                  : i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`];
                case QuMode.RND.ZERO: # MODIFIED CASE
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB()+1 , LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`:0] i_data_eq_fill;
                    #/ assign i_data_eq_fill = {i_data_eq[`EQ_QU_IN.DWT`-1] , i_data_eq};
                    comp_val = f"{EQ_QU_IN.DWT - QU_QUAN.DWT+1}'b1" + "0" * (EQ_QU_IN.DWT - QU_QUAN.DWT)
                    #/ assign op_quan = (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] > `comp_val`)
                    #/                  ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                  : (
                    #/                      ((i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] == `comp_val`) && (i_data_eq_fill[`EQ_QU_IN.DWT`-1]))
                    #/                          ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                          : i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] 
                    #/                  );
                    pass
                case QuMode.RND.INF:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB()+1, LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`:0] i_data_eq_fill;
                    #/ assign i_data_eq_fill = {i_data_eq[`EQ_QU_IN.DWT`-1] , i_data_eq};
                    comp_val = f"{EQ_QU_IN.DWT - QU_QUAN.DWT+1}'b1" + "0" * (EQ_QU_IN.DWT - QU_QUAN.DWT)
                    #/ assign op_quan = (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] > `comp_val`)
                    #/                  ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                  : (
                    #/                      ((i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] == `comp_val`) && (~i_data_eq_fill[`EQ_QU_IN.DWT`-1]))
                    #/                          ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                          : i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`]
                    #/                  );
                case QuMode.RND.CONV:
                    QU_QUAN.set(MSB = EQ_QU_IN.MSB()+1 , LSB = EQ_QU_OUT.LSB())
                    #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
                    #/ wire [`EQ_QU_IN.DWT`:0] i_data_eq_fill;
                    #/ assign i_data_eq_fill = {i_data_eq[`EQ_QU_IN.DWT`-1] , i_data_eq};
                    comp_val = f"{EQ_QU_IN.DWT - QU_QUAN.DWT+1}'b1" + "0" * (EQ_QU_IN.DWT - QU_QUAN.DWT)
                    #/ assign op_quan = (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] > `comp_val`)
                    #/                  ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                  : (
                    #/                      ((i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT`:0] == `comp_val`) && (i_data_eq_fill[`EQ_QU_IN.DWT - QU_QUAN.DWT+1`]))
                    #/                          ? (i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`] + 1'b1)
                    #/                          : i_data_eq_fill[`EQ_QU_IN.DWT`:`EQ_QU_IN.DWT - QU_QUAN.DWT+1`]
                    #/                  );
        elif EQ_QU_OUT.LSB() == EQ_QU_IN.LSB():
            #/ // Perfect LSB match
            QU_QUAN.set(MSB=EQ_QU_IN.MSB, LSB=EQ_QU_OUT.LSB)
            #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
            #/ assign op_quan = i_data_eq;
            pass
        else: # EQ_QU_OUT.LSB() < EQ_QU_IN.LSB()
            #/ // Pad extra LSB bits with 0
            QU_QUAN.set(MSB=EQ_QU_IN.MSB, LSB = EQ_QU_OUT.LSB)
            #/ wire [`QU_QUAN.DWT`-1:0] op_quan; // Quantization output
            #/ assign op_quan = {i_data_eq, {`QU_QUAN.DWT - EQ_QU_IN.DWT`{1'b0}}};
            pass
        #/ // Overflow Stage
        if EQ_QU_OUT.MSB() < QU_QUAN.MSB():
            #/ // Overflow protection
            match OF_MODE:
                case OfMode.WRP.TCPL:
                    #/ assign o_data_eq = op_quan[`EQ_QU_OUT.DWT`-1:0];
                    pass
                case OfMode.SAT.TCPL:
                    neg_max = f"{EQ_QU_OUT.DWT}'b1" + "0" * (EQ_QU_OUT.DWT - 1)
                    pos_max = f"{EQ_QU_OUT.DWT}'b0" + "1" * (EQ_QU_OUT.DWT - 1)
                    #/ assign o_data_eq = (op_quan[`QU_QUAN.DWT`-1:`EQ_QU_OUT.DWT`] != {`QU_QUAN.DWT - EQ_QU_OUT.DWT`{op_quan[`EQ_QU_OUT.DWT`-1]}})
                    #/                  ? (op_quan[`QU_QUAN.DWT`-1] ? `neg_max` : `pos_max`)
                    #/                  : op_quan[`EQ_QU_OUT.DWT`-1:0];
                case OfMode.SAT.SMGN:
                    if EQ_QU_OUT.DWT > 1:
                        neg_max = f"{EQ_QU_OUT.DWT}'b1" + "0" * (EQ_QU_OUT.DWT - 2) + "1"
                        pos_max = f"{EQ_QU_OUT.DWT}'b0" + "1" * (EQ_QU_OUT.DWT - 1)
                        #/ assign o_data_eq = (op_quan[`QU_QUAN.DWT`-1:`EQ_QU_OUT.DWT`] != {`QU_QUAN.DWT - EQ_QU_OUT.DWT`{op_quan[`EQ_QU_OUT.DWT`-1]}})
                        #/                  ? (op_quan[`QU_QUAN.DWT`-1] ? `neg_max` : `pos_max`)
                        #/                  : (op_quan[`EQ_QU_OUT.DWT`-1:0] == {1'b1 , {`EQ_QU_OUT.DWT-1`'b0}}) ? op_quan[`EQ_QU_OUT.DWT`-1:0] +1'b1 : op_quan[`EQ_QU_OUT.DWT`-1:0];
                    else:
                        neg_pos_max = f"{EQ_QU_OUT.DWT}'b0"
                        #/ assign o_data_eq =`neg_pos_max`;
                    
                case OfMode.SAT.ZERO:
                    #/ assign o_data_eq = (op_quan[`QU_QUAN.DWT`-1:`EQ_QU_OUT.DWT`] != {`QU_QUAN.DWT - EQ_QU_OUT.DWT`{op_quan[`EQ_QU_OUT.DWT`-1]}})
                    #/                  ? `EQ_QU_OUT.DWT`'b0
                    #/                  : op_quan[`EQ_QU_OUT.DWT`-1:0];
                    pass
        elif EQ_QU_OUT.MSB() == QU_QUAN.MSB():
            #/ // Perfect MSB match
            match OF_MODE:
                case OfMode.WRP.TCPL | OfMode.SAT.TCPL | OfMode.SAT.ZERO:
                    #/ assign o_data_eq = op_quan;
                    pass
                case OfMode.SAT.SMGN:
                    if EQ_QU_OUT.DWT >1:
                        #/ assign o_data_eq = (op_quan == {1'b1 , {`QU_QUAN.DWT-1`'b0}}) ? op_quan + 1'b1 : op_quan;
                        pass
                    else:
                        #/ assign o_data_eq = 1'b0;
                        pass
                    pass
            pass
        else: # EQ_QU_OUT.MSB() > QU_QUAN.MSB()
            #/ // Pad extra MSB bits with sign bit
            match QU_MODE:
                case QuMode.TRN.TCPL | QuMode.TRN.SMGN:
                    #/ assign o_data_eq = {{`EQ_QU_OUT.DWT - QU_QUAN.DWT`{op_quan[`QU_QUAN.DWT`-1]}}, op_quan};
                    pass
                case QuMode.RND.POS_INF | QuMode.RND.ZERO | QuMode.RND.INF | QuMode.RND.CONV | QuMode.RND.NEG_INF:
                    #/ assign o_data_eq = op_quan[`QU_QUAN.DWT`-1] ? {{`EQ_QU_OUT.DWT - QU_QUAN.DWT`{i_data_eq[`EQ_QU_IN.DWT`-1]}}, op_quan} : {{`EQ_QU_OUT.DWT - QU_QUAN.DWT`{op_quan[`QU_QUAN.DWT`-1]}}, op_quan};
                    pass
            pass

    # Truncate the sign bit for unsigned output
    #/ wire [`QU_OUT.DWT`-1:0] o_data_trunc;
    if QU_OUT.IF_SIGNED == False:
        #/ // Truncate the sign bit for unsigned output
        #/ assign o_data_trunc = o_data_eq[`EQ_QU_OUT.DWT`-2:0];
        pass
    else:
        #/ assign o_data_trunc = o_data_eq;
        pass

    # Delay the output data
    inst_ports = {
        "i_data": "o_data_trunc",
        "o_data": "o_data"
    }
    if N_CLK > 0:
        inst_ports["i_clk"] = "i_clk"
        if any(IF_RST_N):
            inst_ports["i_rst_n"] = "i_rst_n"
    ModuleDelay(DWT = EQ_QU_OUT.DWT, N_CLK = N_CLK, IF_RST_N = IF_RST_N, PORTS = inst_ports)

    #/ endmodule
    pass

if __name__ == "__main__":
    moduleloader.set_root_dir("./RTL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()

    # ModuleFxMatch(QU_IN = QuType(8, 4, True), QU_OUT = QuType(8, -2, True), QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, N_CLK = 0, IF_RST = False)
    ModuleFxMatch(QU_IN = QuType(8, 4, True), QU_OUT = QuType(8, 2, False), N_CLK = 4, IF_RST_N = False, QU_MODE=QuMode.RND.ZERO, OF_MODE=OfMode.SAT.ZERO)
