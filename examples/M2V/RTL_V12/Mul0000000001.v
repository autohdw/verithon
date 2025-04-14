 module Mul0000000001 (
 i_data_1, i_data_2, o_data
    ,i_clk
 );
 input wire [12:0] i_data_1;
 input wire [11:0] i_data_2;
 output wire [11:0] o_data;
 input wire i_clk;
 wire [12:0] data_1;
 wire [11:0] data_2;
 assign data_1 = i_data_1;
 assign data_2 = i_data_2;
 wire [12:0] data_1_abs;
 wire [11:0] data_2_abs;
 wire [16:0] data_mul_ures;
 assign data_1_abs = data_1[12] ? {~data_1[12:0] + 1'b1} : data_1;
 assign data_2_abs = data_2[11] ? {~data_2[11:0] + 1'b1} : data_2;
 assign data_mul_ures = data_1_abs * data_2_abs;
 wire res_sign;
 wire [17:0] data_mul_res;
 assign res_sign = data_1[12] ^ data_2[11];
 assign data_mul_res = res_sign ? {~{1'b0, data_mul_ures[16:0]} + 1'b1} : {1'b0, data_mul_ures};
 wire [11:0] result_fixed;
FxMatch0000000006  u_0000000001_FxMatch0000000006(.i_data(data_mul_res), .o_data(result_fixed));
Delay0000000008  u_0000000001_Delay0000000008(.i_data(result_fixed), .o_data(o_data), .i_clk(i_clk));
 endmodule
