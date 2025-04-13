 module Delay0000000002 (
    i_data, o_data
    , i_clk
 );
 // Input and output ports
 input [13-1:0] i_data;
 output [13-1:0] o_data;
 input i_clk;
 reg [13-1:0] data_d [0:1-1];
 always @(posedge i_clk) begin
     data_d[0] <= i_data;
 end
 assign o_data = data_d[1-1];
 endmodule
