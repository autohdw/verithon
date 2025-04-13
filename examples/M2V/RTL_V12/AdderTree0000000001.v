 module AdderTree0000000001 (
  i_data,
  o_data,
 i_clk
);
 // Input and Output Ports
 input wire [48-1:0] i_data;
 output wire [12-1:0] o_data;
 input wire i_clk;
 wire [48-1:0] data0;
 assign data0 = i_data;
 wire [26-1:0] data1;
Add0000000002  u_0000000001_Add0000000002(.i_data_1(data0[1*12-1:0*12]), .i_data_2(data0[2*12-1:1*12]), .o_data(data1[1*13-1:0*13]));
Add0000000002  u_0000000002_Add0000000002(.i_data_1(data0[3*12-1:2*12]), .i_data_2(data0[4*12-1:3*12]), .o_data(data1[2*13-1:1*13]));
 wire [12-1:0] data2;
Add0000000003  u_0000000001_Add0000000003(.i_data_1(data1[1*13-1:0*13]), .i_data_2(data1[2*13-1:1*13]), .o_data(data2[1*12-1:0*12]), .i_clk(i_clk));
 assign o_data = data2;
 endmodule
