import vModule
#/ INST:

#/ PARAM:
#/ PARAM1: 1
#/ PARAM2: 2
#/ PARAMN: 3

#/ VPARAM:
#/ VPARAM1: 1
#/ VPARAM2: 2
#/ VPARAMN: 3

#/ PORT:
#/ PORT1: A_IN
#/ PORT2: B_IN
#/ PORTN: C_OUT

#/ ENDINST
def Module_MUL(param1, param2, paramN):  # Params (called by the python script) are placed in the python function definition.
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

vM1 = vModule.vModule(Module_MUL)
param_dict = {'param1':-1, 'param2':-2, 'paramN':3}
ports_dict = {'portN':'A_IN'}
vparams_dict = {'vparam1': 'vp_inst1', 'vparam2': 'vp_inst2', 'vparam3' : 'vp_inst3'}
vM1.pre_instantiate(param_dict)
vM1.instantiate(ports_dict, vparams_dict)




