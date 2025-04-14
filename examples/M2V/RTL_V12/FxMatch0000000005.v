 module FxMatch0000000005 (
     i_data, o_data
 );
 input wire [14-1:0] i_data;     // Input data
 output wire [13-1:0] o_data;   // Output data
 //
 wire [14-1:0] i_data_eq;
 assign i_data_eq = i_data;
 wire [13-1:0] o_data_eq;
 // Quantization Stage
 // Perfect LSB match
 wire [14-1:0] op_quan; // Quantization output
 assign op_quan = i_data_eq;
 // Overflow Stage
 // Overflow protection
 assign o_data_eq = op_quan[13-1:0];
 wire [13-1:0] o_data_trunc;
 assign o_data_trunc = o_data_eq;
Delay0000000004  u_0000000001_Delay0000000004(.i_data(o_data_trunc), .o_data(o_data));
 endmodule
