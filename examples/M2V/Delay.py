###################################################################################################
# Module Name: Delay
# Description: This module is used to delay the input data by N_CLK clock cycles.
# Author: Changhan Li
# Author: Bolin Li
# Date: 2025.2.22
# Version: V0.1.0
# Doc Version: V0.1.0
# Dependency Modules: None
###################################################################################################
import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader

from enum import Enum

from PyTU import QuMode, OfMode, QuType

@convert
def ModuleDelay(DWT, N_CLK = 1, IF_RST_N = False):
    # Parsing the input arguments
    if N_CLK > 0 and type(IF_RST_N) == bool:
        # Expand the boolean to a list of the same value
        IF_RST_N = [IF_RST_N] * N_CLK
    # End Parsing the input arguments
    #/ module Delay(
    #/    i_data, o_data
    if N_CLK > 0:
        #/    , i_clk
        if any(IF_RST_N):
            #/    , i_rst_n
            pass
    #/ );
    #/ // Input and output ports
    #/ input [`DWT`-1:0] i_data;
    #/ output [`DWT`-1:0] o_data;
    if N_CLK > 0:
        #/ input i_clk;
        if any(IF_RST_N):
            #/ input i_rst_n;
            pass

    if N_CLK == 0:
        #/ assign o_data = i_data;
        pass
    else: # N_CLK > 0
        #/ reg [`DWT`-1:0] data_d [0:`N_CLK`-1];
        if IF_RST_N[0]:
            #/ always @(posedge i_clk, negedge i_rst_n) begin
            #/     if (~i_rst_n) begin
            #/         data_d[0] <= `DWT`'b0;
            #/     end 
            #/     else begin
            #/         data_d[0] <= i_data;
            #/     end
            #/ end
            pass
        else:
            #/ always @(posedge i_clk) begin
            #/     data_d[0] <= i_data;
            #/ end
            pass
        # Delaying the data (if N_CLK > 1)
        for i in range(1, N_CLK):
            if IF_RST_N[i]:
                #/ always @(posedge i_clk, negedge i_rst_n) begin
                #/     if (~i_rst_n) begin
                #/         data_d[`i`] <= `DWT`'b0;
                #/     end
                #/     else begin
                #/         data_d[`i`] <= data_d[`i-1`];
                #/     end
                #/ end
                pass
            else:
                #/ always @(posedge i_clk) begin
                #/     data_d[`i`] <= data_d[`i-1`];
                #/ end
                pass
        #/ assign o_data = data_d[`N_CLK`-1];
    #/ endmodule

if __name__ == "__main__":
    moduleloader.set_root_dir(".\RTL")
    moduleloader.set_naming_mode("SEQUENTIAL")
    # moduleloader.saveParams()
    moduleloader.disEnableWarning()

    # ModuleFxMatch(QU_IN = QuType(8, 4, True), QU_OUT = QuType(8, -2, True), QU_MODE = QuMode.TRN.TCPL, OF_MODE = OfMode.WRP.TCPL, N_CLK = 0, IF_RST = False)
    ModuleDelay(DWT = 8, N_CLK = 4, IF_RST_N = [True, False, True, False])