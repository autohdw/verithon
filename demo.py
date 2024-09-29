from pytv_new import *

@pytv
def ModuleBasic(p1, p2):
    #/ module BASIC(
    if p1 > 0:
       #/ portBA1,
       pass
    if p2 > 0:
       #/ portBA2,
       pass
    #/ );
    #/ start of BASIC
    #/ middle of BASIC
    #/ end of BASIC
    #/ endmodule


@pytv
def ModuleMUL(param1, param2, paramN, **kwargs):  # Params (called by the python script) are placed in the python function definition.
    #/ module MUL(
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

    myport1 = "myport1"
    myport2 = "myport2"
    inst_port_list = [myport1, myport2]
    vparams_dict = {'vparamB1':19, 'vparamB2':6, 'vparamBN':5}
    ModuleBasic(p1 = 1, p2 = 1, PORTS = inst_port_list)
    ModuleBasic(p1= 5, p2 = 6, PORTS=inst_port_list)
    # vparams and ports are declared with verilog lines
    #/ start of MUL
    #/ middle of MUL
    #/ end of MUL
    #/ endmodule

@pytv
def ModuleTOP(param_top1,param_top2):
    rst1 = 1
    rst2 = 2
    rstn = 3
    inst_ports_list = []
    #/ module TOP(
    if param_top1 > 0:
       #/ port_top1,
       inst_ports_list.append('A_IN')
       pass

    if param_top2 > 0:
       #/ port_top2,
       inst_ports_list.append('B_IN')
       pass
    #/ );
    if param_top1 > 0:
        inst_ports_dict = {'PORT1':'name_port1', 'PORT2':'name_port2'}
        inst_vparams_dict = {'vparam1':3, 'vparam2':8, 'vparam3':80}
        # Instantiation:
        # all arguments must be passed as keyword argument
        # Ports are passed in a list/dictionary to the "PORTS" argument. Can not pass a single string.
        # INST_NAME should be a string
        # We do not encourage manually setting INST_NAME and MODULE_NAME
        ModuleMUL(param1 = 1, param2 = 1, paramN = 1, PORTS = ["my_mul_port1", "my_mul_port2", "my_mul_port3"], INST_NAME = "mymul_inst")
        for i in range (1,5):
            ModuleBasic(p1=1, p2=1, PORTS=inst_ports_dict)
            ModuleBasic(p1=rst1, p2=-10, PORTS=["PORTA"])
            ModuleBasic(p1=1, p2=1, PORTS=inst_ports_dict)
    dwt = 3
    codeLength = 32
    llr_width = 8
    llr_0 = "0000_0001"
    llr_1 = "1111_1110"
    info_pos = [8,10,11,13,18,19,21,32] #all 1 (len=32)
    # info_pos = [1,2,5,8,10,11,15,16,19,20,22,23,25,28,29,30]
    for i in range(1,33):
        h_bit = 8 * i - 1
        l_bit = 8 * (i - 1)
        if i in info_pos:
            #/ LLR_RECV[`h_bit`:`l_bit`] <= 12'b`llr_1`;
            pass
        else:
            #/ LLR_RECV[`h_bit`:`l_bit`] <= 12'b`llr_0`;
            pass
    #/ reg [`dwt`:0] K_reg
    #/ start of module TOP
    #/ middle of module TOP
    #/ end of module TOP
    #/ endmodule

# you can manually call api to set naming mode, save dir, and disable warnings or enable params saving,
# if you do not like command line
moduleloader.set_naming_mode("SEQUENTIAL")
moduleloader.set_root_dir("C:\信道编码\SummerSchool\提交")
moduleloader.saveParams()
moduleloader.disEnableWarning()

# Call module functions to generate RTL code
ModuleTOP(param_top1 = 20,param_top2 = 4)
#print(v_declaration)

#print(v_declaration)
import re


