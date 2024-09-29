# New PyTv 
## Grammar
### Magic Comment Output
1. Every verilog line should follow a magic comment: `#/`.  
     - **Warning:** The verilog line must be consistent with python indent
     - **Warning:** No blank spaces are allowed between `#` and `/`. Some IDEs (such as pycharm) automatically adds a blank space after `#`
2. Inside a magic comment, the content enclosed by 2 apostrophes are intepreted as python variables. For instance: ```#/ LLR_RECV[`h_bit`:`l_bit`] <= 12'b`llr_1`;```
     - Idealy, PyTV supports all sorts of python expressions between 2 apostrophes. But for safety considerations, we do recommand doing operations outside the apostrophes and write only single python variable between the apostrophes. 

### Defining a Verilog Module with PyTV
1. Every definition of a verilog module is written in magic comments and embodied in the definition of a **python function**.
   - The name of the python function must start with `Module`. The function name is formulated as `Module_abstract_module_name`. In the current PyTV version, please **do not** define a normal function whose name start with `Module`. Also, the module function definition should be written in a **single** line. (We prepare to solve these 2 issues in future releases)
   - Every module function should be decorated with pytv using `@pytv`. Please write `@pytv` only in the line above each module function definition.
   - The parameters of the python function can be of any data type.
   - The function must **not** have any return value (We will support module functions with return values in future releases).
   - -Below is a very short definition of a verilog module using PyTV
     ``` python
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

## Instantiation with PyTV
1. Module Instantiation with PyTV is done by directly calling the defined module function with the original parameters and extra parameters for ports and inst name (This parameter can be left out with auto-naming).
2. Grammar for instantiation: `ModuleYOUR_MODULE_TO_INSTANTIATE (param1 = p1, param2 = p2, paramN = pN, PORTS = PORTS_DICT, INST_NAME = MY_INST_NAME)`.
3. An example for instantiation:
   ```python
      ModuleMUL(param1 = 1, param2 = 1, paramN = 1, PORTS = ["my_mul_port1", "my_mul_port2", "my_mul_port3"], INST_NAME = "mymul_inst")
      inst_ports_dict = {'PORT1':'name_port1', 'PORT2':'name_port2'}
      for i in range (1,5):
            ModuleBasic(p1=1, p2=1, PORTS=inst_ports_dict)
            ModuleBasic(p1=rst1, p2=-10, PORTS=["PORTA"])
            ModuleBasic(p1=1, p2=1, PORTS=inst_ports_dict)
   ```
4. Constraints:
   - The function param `PORTS` does not appear in the user's definition of the python function. It's a parameter added to the function by the decorator `pytv`. Unless you are instantiating a top module, you should assign value to this parameter (otherwise you will see warning message). Value assigned to this param can either be a  python `list` or  `dict`. It is **NOT** allowed to assign `PORTS` with a string.
   - The function param `INST_NAME` is not compulsory. Actually, we recommend the users to uuse automatic inst naming. (If this `INST_NAME` is not assigned a value, pytv will automatically name the instance the module)
   - The function param `MODULE_NAME` is supported but we strongly recommend the users to avoid using it because its usage may potentially corrupt the naming space in pytv.
   - Before generating instantiation code in the upper module, pytv will check whether the number of ports in the list/dict assigned to `PORTS` matches the ports in the module to be instantiated. If mismatch is found, pytv will throw an exception and terminate code generation. So make sure you have passed correct value to `PORTS`.
   - All parameters should be passed in the **keyword argument** format, but the order in which you pass the arguments can be switched.

### Auto Naming with PyTV
PyTV enables auto naming of modules, module files and instances. Auto-naming is done whenever a module function is called without the argument `MODULE_NAME` or `INST_NAME`. There are 3 naming modes to choose from (`HASH`, `MD5_SHORT`, `SEQUENTIAL`). `SEQUENTIAL` is the most recommended naming mode.
#### Setting naming mode
1. PyTV provides an api for specifying naming mode:
   ```python
       pytv.set_naming_mode("SEQUENTIAL")
   ```
3. You can also set naming mode by passing args in command line:
   ```shell
       --naming_mode "SEQUENTIAL"
   ```

#### Auto Naming Rules
1. Naming of modules or module files
   - Whether to generate new module: Every time a module function is called, pytv reads the python level params and inspects whether the params overlap with some earlier calls. If overlap is found, pytv will not generate a new module file.
   - Naming newly generated module: The module name in pytv is formulated as `abstract_module_name + module_identifier`. `abstract_module_name` is read from the name of the module function. `module_identifier` is auto-generated according to certain rules to distinguish between different modules. In `SEQUENTIAL` naming mode, `module_identifier` is a 10-digit hexadecimal number. In `HASH` mode, `module_identifier` is a hash value of the python layer params the module function received. In `MD5_SHORT` mode, `module_identifier` is a cut MD5 value of the python layer params.
2. Naming of instances
   - Instances are named according to the module they belong to. To avoid naming conflict across different instances, there is also an instance sequence number included in the instance names.
   - The instance name is formulated as: `u_sequence_number_module_name`.
3. An example for naming of module and instance.
   - pytv line: `ModuleBasic(p1=1, p2=1, PORTS=inst_ports_dict)`
   - generated module name: `Basic0000000001`
   - generated module file name: `Basic0000000001.v`
   - generated instance name: `Basic0000000001  u_0000000002_Basic0000000001` (This is 2nd time that the module function ModuleBasic is called with the same python layer params)

## Running pytv for generating RTL code
### Run with command line
You can run pytv with the following shell script:
```shell
cd "C:\your\path"
python your_pytv_file.py --naming_mode HASH --root_dir "C:\your\root_dir" --flag_save_param --disable_warning
```
### Configuration command line arguments
Meaning of each command line argument is presented below:
1. `--naming_mode`
   - **Meaning**: Sets the naming mode for the RTL files.
   - **Possible Values**:
     - `HASH`: Uses a hash value as part of the filename (default).
     - `MD5_SHORT`: Uses a shortened MD5 value as part of the filename.
     - `SEQUENTIAL`: Uses a sequential number as part of the filename.

2. `--root_dir`
   - **Meaning**: Specifies the path where RTL files will be saved.
   - **Possible Values**: Any valid folder path. The user must either pass this argument in command line or set moduleloader.root_dir with api functions. Otherwise, exceptions will be raised and RTL code generation will not start.

3. `--flag_save_param`
   - **Meaning**: Indicates whether to save the parameter file.
   - **Possible Values**:
     - `store_true`: If this parameter is present, the parameter file will be saved.
     - Default is `False` if this parameter is not provided.

4. `--disable_warning`
   - **Meaning**: Indicates whether to disable warnings (if true, pytv will display no warnings).
   - **Possible Values**:
     - `store_true`: If this parameter is present, the warnings will be dis-enabled.
     - Default is `False` if this parameter is not provided.

### Run with no command line args
If you want to run your pytv file without command line, you can configure root directory, naming, saving and warning settings with api functions of pytv. Examples of usage are presented below:
1. `moduleloader.set_naming_mode("SEQUENTIAL")`
2. `moduleloader.set_root_dir("C:\信道编码\SummerSchool\提交")`
3. `moduleloader.saveParams()`
4. `moduleloader.disEnableWarning()`
Note that these api functions must be called **before** you call a pytv module function.

## Output
1. You can find the generated module files in the folder `your_root_dir\\RTL_GEN`.
2. You can find the saved module parameters in the folder `your_root_dir\\PARAMS`.
3. You can view info and warning messages in the terminal.

