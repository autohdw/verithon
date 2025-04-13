 module Sub0000000002 (
 i_data_1,
 i_data_2,
 o_data
 , i_clk
);
 // Input and Output Ports
 input wire [12-1:0] i_data_1;
 input wire [12-1:0] i_data_2;
 output wire [12-1:0] o_data;
 // Internal interface
 wire [12-1:0] data_1;
 wire [12-1:0] data_2;
 input wire i_clk;
 assign data_1 = i_data_1;
 assign data_2 = i_data_2;
 // Minus data_2_minus
 wire [12:0] data_2_minus;
 assign data_2_minus =  ~{data_2[12-1], data_2} + 1'b1;
 wire [14-1:0] data_1_fixed;
 wire [14-1:0] data_2_fixed;
FxMatch0000000007  u_0000000001_FxMatch0000000007(.i_data(data_1), .o_data(data_1_fixed));
FxMatch0000000008  u_0000000001_FxMatch0000000008(.i_data(data_2_minus), .o_data(data_2_fixed));
 wire [14-1:0] result_unfixed;
 wire [12-1:0] result_fixed;
 assign result_unfixed = data_1_fixed + data_2_fixed;
FxMatch0000000009  u_0000000001_FxMatch0000000009(.i_data(result_unfixed), .o_data(result_fixed));
Delay0000000008  u_0000000002_Delay0000000008(.i_data(result_fixed), .o_data(o_data), .i_clk(i_clk));
 endmodule
