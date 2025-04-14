 module FxMatch000000000E (
     i_data, o_data
 );
 input wire [14-1:0] i_data;     // Input data
 output wire [15-1:0] o_data;   // Output data
 //
 wire [14-1:0] i_data_eq;
 assign i_data_eq = i_data;
 wire [15-1:0] o_data_eq;
 // Quantization Stage
 // Perfect LSB match
 wire [14-1:0] op_quan; // Quantization output
 assign op_quan = i_data_eq;
 // Overflow Stage
 // Pad extra MSB bits with sign bit
 assign o_data_eq = {{1{op_quan[14-1]}}, op_quan};
 wire [15-1:0] o_data_trunc;
 assign o_data_trunc = o_data_eq;
Delay000000000A  u_0000000001_Delay000000000A(.i_data(o_data_trunc), .o_data(o_data));
 endmodule
