 module Delay0000000008 (
    i_data, o_data
    , i_clk
 );
 // Input and output ports
 input [12-1:0] i_data;
 output [12-1:0] o_data;
 input i_clk;
 reg [12-1:0] data_d [0:1-1];
 always @(posedge i_clk) begin
     data_d[0] <= i_data;
 end
 assign o_data = data_d[1-1];
 endmodule
