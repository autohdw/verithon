 module FxMatch000000000F (
     i_data, o_data
 );
 input wire [15-1:0] i_data;     // Input data
 output wire [15-1:0] o_data;   // Output data
 //
 wire [15-1:0] i_data_eq;
 assign i_data_eq = i_data;
 wire [15-1:0] o_data_eq;
 // Quantization Stage
 // Perfect LSB match
 wire [15-1:0] op_quan; // Quantization output
 assign op_quan = i_data_eq;
 // Overflow Stage
 // Perfect MSB match
 assign o_data_eq = op_quan;
 wire [15-1:0] o_data_trunc;
 assign o_data_trunc = o_data_eq;
Delay000000000A  u_0000000002_Delay000000000A(.i_data(o_data_trunc), .o_data(o_data));
 endmodule
