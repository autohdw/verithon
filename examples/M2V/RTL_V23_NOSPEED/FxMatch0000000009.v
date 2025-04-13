 module FxMatch0000000009 (
     i_data, o_data
 );
 input wire [14-1:0] i_data;     // Input data
 output wire [12-1:0] o_data;   // Output data
 //
 wire [14-1:0] i_data_eq;
 assign i_data_eq = i_data;
 wire [12-1:0] o_data_eq;
 // Quantization Stage
 // Perfect LSB match
 wire [14-1:0] op_quan; // Quantization output
 assign op_quan = i_data_eq;
 // Overflow Stage
 // Overflow protection
 assign o_data_eq = op_quan[12-1:0];
 wire [12-1:0] o_data_trunc;
 assign o_data_trunc = o_data_eq;
Delay0000000007  u_0000000002_Delay0000000007(.i_data(o_data_trunc), .o_data(o_data));
 endmodule
