 module Add0000000003 (
  i_data_1,
  i_data_2,
  o_data,
 i_clk
);
 // Input and Output Ports
 input wire [13-1:0] i_data_1;
 input wire [13-1:0] i_data_2;
 output wire [12-1:0] o_data;
 input wire i_clk;
 wire [13-1:0] data_1;
 wire [13-1:0] data_2;
 assign data_1 = i_data_1;
 assign data_2 = i_data_2;
 wire [14-1:0] data_1_fixed;
 wire [14-1:0] data_2_fixed;
FxMatch000000000C  u_0000000001_FxMatch000000000C(.i_data(data_1), .o_data(data_1_fixed));
FxMatch000000000C  u_0000000002_FxMatch000000000C(.i_data(data_2), .o_data(data_2_fixed));
 wire [14-1:0] result_unfixed;
 wire [12-1:0] result_fixed;
 assign result_unfixed = data_1_fixed + data_2_fixed;
FxMatch000000000D  u_0000000001_FxMatch000000000D(.i_data(result_unfixed), .o_data(result_fixed));
Delay0000000008  u_0000001401_Delay0000000008(.i_data(result_fixed), .o_data(o_data), .i_clk(i_clk));
 endmodule
