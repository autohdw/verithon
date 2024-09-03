from utils import convert_new
from utils import parseVerilog_inst_block

import vModule

def ModuleMUL(param1, param2, paramN):  # Params (called by the python script) are placed in the python function definition.
   #/ module MUL #(vparam1, vparam2, vparamN)(
   if param1 > 0:
      #/ port1,
      pass
   if param2 > 0:
      #/ port2,
      pass
   if paramN > 0:
      #/ portN
      pass
   #/ );
   # vparams and ports are declared with verilog lines
   #/ start of module body
   #/ middle of module body
   #/ end of module body
   #/ endmodule

@convert_new
def Module_TOP(param_top1,param_top2):
    rst1 = 1
    rst2 = -2
    rstn = 3
    inst_ports_list = []
    #/ module TOP #(vparam_top1, vparam_top2, vparam_top3)(
    if param_top1 > 0:
       #/ port_top1
       inst_ports_list.append('A_IN')
       pass

    if param_top2 > 0:
       #/ port_top2
       inst_ports_list.append('B_IN')
       pass
    #/ );
    if param_top1 > 0:
        #/ INST:
        #/ PARAMS:
        #/ param1 : {rst1}
        #/ param2 : {rst2}
        #/ paramN : {rstn}
        #/ VPARAMS:
        #/ vparam1 : 3
        #/ vparam2 : 6
        #/ vparamN : 5
        #/ PORTS:
        #/ {inst_ports_list}
        #/ INST_NAME: MUL1
        #/ MODULE_NAME: MUL
        #/ ENDINST
        pass
    #/ ENDMODULE

Module_TOP(2,4)
# inst_code =   ['        #/ INST: \n\n', '        #/ PARAMS: \n\n', '        #/ param1 : 1\n\n', '        #/ param2 : 2', '#/ param3 : 3\n\n', '        #/ VPARAMS: \n\n', '        #/ vparam1 : 3\n\n', '        #/ vparam2 : 4\n\n','        #/ vparam3 : 5\n\n', '        #/ INST_NAME: MUL1\n\n', '        #/ MODULE_NAME: MUL\n\n']
# [X,Y,Z,W,P] = parseVerilog_inst_block(inst_code, ())locals