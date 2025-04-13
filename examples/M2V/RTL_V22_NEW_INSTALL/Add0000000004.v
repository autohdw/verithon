 module Add0000000004 (
  i_data_1,
  i_data_2,
  o_data,
);
 // Input and Output Ports
 input wire [14-1:0] i_data_1;
 input wire [14-1:0] i_data_2;
 output wire [15-1:0] o_data;
 wire [14-1:0] data_1;
 wire [14-1:0] data_2;
 assign data_1 = i_data_1;
 assign data_2 = i_data_2;
 wire [15-1:0] data_1_fixed;
 wire [15-1:0] data_2_fixed;
FxMatch000000000E  u_0000000001_FxMatch000000000E(.i_data(data_1), .o_data(data_1_fixed));
FxMatch000000000E  u_0000000002_FxMatch000000000E(.i_data(data_2), .o_data(data_2_fixed));
 wire [15-1:0] result_unfixed;
 wire [15-1:0] result_fixed;
 assign result_unfixed = data_1_fixed + data_2_fixed;
FxMatch000000000F  u_0000000001_FxMatch000000000F(.i_data(result_unfixed), .o_data(result_fixed));
Delay000000000A  u_0000000003_Delay000000000A(.i_data(result_fixed), .o_data(o_data));
 endmodule
