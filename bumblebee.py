import shutil
import os
import sys
from collections import OrderedDict
import c_templates
import c_utils
from xml.etree import ElementTree as ET
import re
#from _examples.bumblebee_spec import user_settings

THIS_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


BUILD_CONTEXT = {
    # auto detected
    "family_name" : "",       #stm32[fg]xxx
    "family_name_caps": "",   #STM32[FG]]xxx
    "cmsis_startup": "",      #startup_stm32fxxxxx.s
    "arch": "",               #arch_cortexm4, arch_cortexm3, arch_cortexm0
    "mcu_init_functions": [],
    # manually configured
    "BUILD_TOOL_TYPE_IS_MDK" : "",
    "BUILD_TOOL_TYPE" : "",
    "MX_GENERATED_CODE_PATH" : "",
    "MX_GENERATED_PRJ_NAME" : "",
    "COMPONENT_OUT_PATH" : "",
    "COMPONENT_SHORT_NAME" : ""
}

def h_file(fname, body=""):
    """ If the given name does not have an extension then add one.
    """
    fname_up = os.path.basename(fname).upper()
    fname_up, fext = os.path.splitext(fname_up)
    if not fext:
        fext = ".H"
    fname_up = (fname_up + fext).replace(".","_")
    h_file_cont = c_templates.H_FILE_TEMPLATE.format(file_name_uppercase=fname_up,
                                                     body = body)
    h_file_cont = h_file_cont.lstrip()
    return h_file_cont


def c_file(fname, body="", include=True):
    """ If the given name does not have an extension then add one.
    """
    fname_only = os.path.basename(fname).lower()
    fbase, fext = os.path.splitext(fname_only)
    h_file_name = fbase + ".h"

    body = body.lstrip()
    if not include:
        c_file_cont = c_templates.C_FILE_NO_INCLUDE_TEMPLATE.format(body = body)
    else:
        c_file_cont = c_templates.C_FILE_TEMPLATE.format(h_file_name = h_file_name, 
                                                        body = body)
    c_file_cont = c_file_cont.lstrip()
    return c_file_cont


def comp_structure(longname, shortname):
    sname = shortname.lower()
    lname = longname.lower()

    comp_tree =OrderedDict([ 
        ("app_source"         , "{}/apps/{}_app/source".format(lname, sname)          ),
        ("app_linkscript"     , "{}/apps/{}_app/link_script".format(lname, sname)     ),
        ("app_tool_ewarm"     , "{}/apps/{}_app/tools/ewarm".format(lname, sname)     ),
        ("app_tool_attolic"   , "{}/apps/{}_app/tools/attolic".format(lname, sname)   ),
        ("app_tool_mdk"       , "{}/apps/{}_app/tools/mdk".format(lname, sname)       ),
        ("app_tool_vscode"    , "{}/apps/{}_app/tools/vscode".format(lname, sname)    ),
        ("app_tool_codeblocks", "{}/apps/{}_app/tools/codeblocks".format(lname, sname)),
        ("source"             , "{}/source".format(lname)                             ),
        ("imported"           , "{}/imported".format(lname)                           ),
        ("docs"               , "{}/docs".format(lname)                               ),
        ("app_source_arch_cortex_mdk"    , "{}/apps/{}_app/source".format(lname, sname)          ),
    ])

    # Remove the whole top folder and subtree
    if os.path.isdir(lname):
        shutil.rmtree(lname)

    for n,d in comp_tree.items():
        if not os.path.isdir(d):
            os.makedirs(d)
    
    return comp_tree
    

def write_out_file(fpath, fname, fcont):
    f = os.path.join(fpath, fname)
    with open(f, 'w') as ofile:
        ofile.write(fcont)

#------------------------------------------------------------------------------
H_EXT = ".h"
C_EXT = ".c"

#------------------------------------------------------------------------------
def build_body__empty(path):
    return {H_EXT: "", C_EXT : ""}

#------------------------------------------------------------------------------
def build_body__mcu_init_gpio(mx_generated_code_path):
    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Inc\main.h")
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Inc\main.h")

    ifile_lines = []
    with open(f, 'r') as ifile:
        interesting_lines = []
        ifile_lines = ifile.readlines()
    for line in ifile_lines:
        if "GPIO" in line:
            interesting_lines.append(line)
    return {H_EXT: "".join(interesting_lines), C_EXT:""}

#------------------------------------------------------------------------------
def build_body__mcu_init(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Src\main.c")
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Src\main.c")

    ifile_lines = []
    with open(f, 'r') as ifile:
        ifile_lines = ifile.readlines()

    var_declarations = []
    init_funcs = {}
    mx_func = []
    mx_func_name = ""
    mx_func_state = 0
    for line in ifile_lines:
        if ("_HandleTypeDef " in line) and (";" in line):
            var_declarations.append(line)

        if mx_func_state == 0:
             mx_func_name = ""
             mx_func = []
             if ( (("static void MX_" in line) and (";" not in line)) or
                  (("void SystemClock_Config" in line) and (";" not in line))
                ):
                 mx_func.append(line)
                 mx_func_name = line
                 mx_func_state = 1
        elif mx_func_state == 1:
            mx_func.append(line)
            if line:
                if line[0] == "}":
                    init_funcs[mx_func_name] = "".join(mx_func)
                    mx_func_state = 0

    #Rewrite the file the proper way
    h_body  = []
    c_body = [
        '#include "mcu_init_gpio.h"\n',
        '#include "%s_hal.h"\n' % FN,
        '#include <stdint.h>\n'
    ]
    c_body.append("\n"*4)
    for v in var_declarations:
        c_body.append(v)
    c_body.append("\n"*4)

    for line in c_templates.FILE_MCU_INIT_ADDITIONS.split("\n"):
        c_body.append(line+"\n")
    h_body.append("void McuInit_systick(void);\n")
    h_body.append("void McuInit_HAL(void);\n")


    combined_inits = OrderedDict()
    for k,v in init_funcs.items():
        #example static void MX_CAN1_Init(void)
        v_clean = v.replace("static void MX_", "void McuInit_").replace("_Init(void)", "(void)")
        v_clean = v_clean.replace("void SystemClock_Config(void)", "void McuInit_clock(void)")
        v_clean = c_utils.clean_c_cc_comments(v_clean)
        c_body.append(v_clean+"\n\n")

        k_clean = k.replace("static void MX_", "void McuInit_").replace("_Init(void)", "(void)")
        k_clean = k_clean.replace("void SystemClock_Config(void)", "void McuInit_clock(void)")
        #BUILD_CONTEXT["mcu_init_functions"].append(k_clean.replace("(void)", "").replace("void", "").strip())
        k_clean = k_clean.strip() +";\n"
        # if the function name has numerical ending, wrap it in another generic non number
        k_clean_func_name = k_clean.replace("void ", "").replace("(void);", "").strip()
        if (k_clean_func_name[-1] not in "0123456789") and ("USART" not in k_clean_func_name):
            h_body.append(k_clean)
            BUILD_CONTEXT["mcu_init_functions"].append(k_clean_func_name)
        else:
            if "USART" in k_clean_func_name:
                k_clean_func_name_wrapper = "McuInit_UART"
            else:
                k_clean_func_name_wrapper = k_clean_func_name[:-1]
            if k_clean_func_name_wrapper  not in combined_inits:
                combined_inits[k_clean_func_name_wrapper] = [k_clean_func_name]
            else:
                combined_inits[k_clean_func_name_wrapper].append(k_clean_func_name)
            BUILD_CONTEXT["mcu_init_functions"].append(k_clean_func_name_wrapper)

    for f_combined_init, f_sub_inits in combined_inits.items():
        f_combined_body = "void {}()\n{{\n".format(f_combined_init)
        f_combined_body += "\n".join(["    {}();".format(f) for f in f_sub_inits])
        f_combined_body += "\n}\n\n"
        c_body.append(f_combined_body)
        h_body.append("void {}(void);\n".format(f_combined_init))


    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__hal_msp(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Src\%s_hal_msp.c" % FN)
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Src\%s_hal_msp.c" % FN)

    ifile_lines = []
    with open(f, 'r') as ifile:
        ifile_lines = ifile.readlines()

    #Rewrite the file the proper way
    c_body = [
        '#include "%s_hal.h"\n'%FN,
        '#include "mcu_init_gpio.h"\n',
        "\n",
        "extern void _Error_Handler(char *, int);"
    ]
    c_body.append("\n"*2)
    for line in ifile_lines:
        if "#include" in line:
            continue
        else:
            c_body.append(line)

    return {H_EXT: "", C_EXT : c_utils.clean_c_cc_comments("".join(c_body))}


#------------------------------------------------------------------------------
def build_body__hal_conf_h(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Inc\%s_hal_conf.h"%FN)
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Inc\%s_hal_conf.h"%FN)

    ifile_lines = []
    with open(f, 'r') as ifile:
        ifile_lines = ifile.readlines()

    #Take all of the body and add a few more lines related to the error handler
    h_body = []
    body_state = 0
    for line in ifile_lines:
        if body_state == 0:
            if('extern "C" {' in line):
                body_state = 1
        elif body_state == 1:
            if ("#endif" in line):
                body_state = 2
        else:
            if("ifdef __cplusplus" in line):
                break
            h_body.append(line)
    
    h_body.append("//---------------------------------------------------------------------------\n")
    h_body.append("void _Error_Handler(char *, int);\n")
    h_body.append("#define Error_Handler() _Error_Handler(__FILE__, __LINE__)\n\n")

    c_body = []

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}


#------------------------------------------------------------------------------
def build_body__hal_conf_c(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]


    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Inc\%s_hal_conf.h"%FN)
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Inc\%s_hal_conf.h"%FN)

    h_body = []
    c_body = []
    for line in c_templates.FILE_HAL_CONF_ADDITIONS.split("\n"):
        line = line.replace("device_hal", "%s_hal"%FN)
        c_body.append(line+"\n")
    
    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}


#------------------------------------------------------------------------------
def build_body__cmsis_system(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    if BUILD_CONTEXT["arch"] == "arch_cortexm3":
        f = os.path.join(mx_generated_code_path, r"Src\system_%s.c" % FN)
    else:
        f = os.path.join(mx_generated_code_path, r"Core\Src\system_%s.c" % FN)

    ifile_lines = []
    with open(f, 'r') as ifile:
        ifile_lines = ifile.readlines()

    #Take all of the body and add a few more lines related to the error handler
    h_body = []
    c_body = ifile_lines
    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}


#------------------------------------------------------------------------------
def build_body__board_hal_h(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    h_body = []
    c_body = []

    for line in c_templates.FILE_BOARD_HAL_H_ADDITIONS.split("\n"):
        line = line.replace("cmsis_device_include.h", "%s.h"%FN)
        h_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__board_app(mx_generated_code_path):
    h_body = []
    c_body = []

    for line in c_templates.FILE_BOARD_APP_H_ADDITIONS.split("\n"):
        h_body.append(line+"\n")

    for line in c_templates.FILE_BOARD_APP_C_ADDITIONS.split("\n"):
        c_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__board_state(mx_generated_code_path):
    h_body = []
    c_body = []

    for line in c_templates.FILE_BOARD_STATE_H_ADDITIONS.split("\n"):
        h_body.append(line+"\n")

    for line in c_templates.FILE_BOARD_STATE_C_ADDITIONS.split("\n"):
        c_body.append(line+"\n")
    
    #Make GPIO init the first call.
    mcu_init_calls = [c+"();\n" for c in BUILD_CONTEXT["mcu_init_functions"] if ("_GPIO" in c)]

    for c in BUILD_CONTEXT["mcu_init_functions"]:
        c = "    "+c+"();\n"
        if "_clock" in c:
            continue
        if c not in mcu_init_calls:
            mcu_init_calls.append(c)

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body).replace("//McuInit_*()","".join(mcu_init_calls))}

#------------------------------------------------------------------------------
def build_body__it(mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]

    h_body = []
    c_body = []

    for line in c_templates.FILE_IT_C_ADDITIONS.split("\n"):
        line = line.replace("device_hal.h", "%s_hal.h"%FN)
        c_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__main(mx_generated_code_path):
    h_body = []
    c_body = []

    for line in c_templates.FILE_MAIN_C_ADDITIONS.split("\n"):
        c_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__sys_time(mx_generated_code_path):
    h_body = []
    c_body = []

    for line in c_templates.FILE_SYS_TIME_H_ADDITIONS.split("\n"):
        h_body.append(line+"\n")

    for line in c_templates.FILE_SYS_TIME_C_ADDITIONS.split("\n"):
        c_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}

#------------------------------------------------------------------------------
def build_body__scheduler(mx_generated_code_path):
    h_body = []
    c_body = []

    for line in c_templates.FILE_SCHEDULER_H_ADDITIONS.split("\n"):
        h_body.append(line+"\n")

    for line in c_templates.FILE_SCHEDULER_C_ADDITIONS.split("\n"):
        c_body.append(line+"\n")

    return {H_EXT: "".join(h_body), C_EXT : "".join(c_body)}



#------------------------------------------------------------------------------
def build_body__startup(mx_generated_code_path, build_tool):
    if(build_tool == BUILD_CONTEXT["BUILD_TOOL_TYPE_IS_MDK"]):
        f = os.path.join(mx_generated_code_path, "MDK-ARM/%s"%BUILD_CONTEXT["cmsis_startup"])
    else:
        return ""

    ifile_lines = []
    with open(f, 'r') as ifile:
        ifile_lines = ifile.readlines()
    
    s_body = []
    body_state = 0
    for line in ifile_lines:
        if body_state == 0:
            line = line.lstrip()
            if line and (';' != line[0]):
                s_body.append(line)
                body_state = 1
        else:
            if("end of file" in line.lower()):
                continue
            s_body.append(line)

    return "".join(s_body)


#------------------------------------------------------------------------------
def build_body__toolproject(mx_generated_code_path, build_tool):
    result = {}
    prj_name = BUILD_CONTEXT["MX_GENERATED_PRJ_NAME"]
    if(build_tool == BUILD_CONTEXT["BUILD_TOOL_TYPE_IS_MDK"]):
        fname_prj = prj_name + ".uvprojx"
        fname_opt = prj_name + ".uvoptx"
        result = {fname_prj:"", fname_opt:""}
        #uvoptx file is direct copy - no processing
        f_opt = os.path.join(mx_generated_code_path, "MDK-ARM/"+fname_opt)
        ifile_lines = []
        with open(f_opt, 'r') as ifile:
            ifile_lines = ifile.readlines()
        result[fname_opt] = "".join(ifile_lines)
        #uvprojx needs modification
        f_prj = os.path.join(mx_generated_code_path, "MDK-ARM/"+fname_prj)
        ifile_lines = []
        with open(f_prj, 'r') as ifile:
            ifile_lines = ifile.readlines()
        
        FN = BUILD_CONTEXT["family_name"]
        FN_CAPS = BUILD_CONTEXT["family_name_caps"]
        ARCH = BUILD_CONTEXT["arch"]

        replacement_spec1 = [
            ("<OutputDirectory>", "<OutputDirectory>./build_out\\</OutputDirectory>"),
            ("<OutputName>", "<OutputName>{}</OutputName>".format(prj_name)),
            ("<ListingPath>",     "<ListingPath>./build_out\\</ListingPath>"),
        ]
        ifile_lines_processed_1 = []
        for line in ifile_lines:
            for rt, rw in replacement_spec1:
                if rt in line:
                    line = line.replace(line.lstrip(),"") + rw + "\n"
                    break
            ifile_lines_processed_1.append(line)
        
        if BUILD_CONTEXT["arch"] == "arch_cortexm3":
            inc_path = "../Inc"
            src_path = "../Src"
            user_group = "<GroupName>Application/User"
        else:
            inc_path = "../Core/Inc"
            src_path = "../Core/Src"
            user_group = "<GroupName>Application/User/Core"
        
        replacement_spec2 = [
            ("../Drivers/%s_HAL_Driver"%FN_CAPS, "../../../../imported/%s_HAL_Driver"%FN_CAPS),
            ("../Drivers/CMSIS", "../../../../imported/CMSIS"),
            (src_path, "../../source"),
            (inc_path, "../../source"),
            ("<GroupName>Drivers/%s_HAL_Driver"%FN_CAPS, "<GroupName>imported/%s_HAL_Driver"%FN_CAPS),
            ("<GroupName>Drivers/CMSIS", "<GroupName>application/CMSIS"),
            (user_group, "<GroupName>application"),
            ("<GroupName>Application/MDK-ARM", "<GroupName>application/%s/mdk"%ARCH),
            ("<FilePath>%s"%BUILD_CONTEXT["cmsis_startup"], "<FilePath>../../source/%s"%BUILD_CONTEXT["cmsis_startup"]),
            ("<GroupName>::CMSIS</GroupName>", "")
        ]
        ifile_lines_processed_2 = []
        for line in ifile_lines_processed_1:
            for rt, rw in replacement_spec2:
                if rt in line:
                    line = line.replace(rt, rw)
            ifile_lines_processed_2.append(line)

        result[fname_prj] = "".join(ifile_lines_processed_2)

        added_file_spec = [
            "%s_hal_conf.c" % FN,
            "board_app.c",
            "board_hal.h",
            "board_state.c",
            "mcu_init.c",
            "scheduler.c",
            "sys_cfg.c",
            "sys_time.c",
            "mcu_init_gpio.h"
        ]

        project_element = ET.fromstring(result[fname_prj])
        app_group_files = None
        groups = project_element.findall("Targets/Target/Groups/Group")
        for g in groups:
            g_n = g.find("GroupName")
            if (g_n != None) and (g_n.text == "application"):
                app_group_files = g.find("Files")
                break
        if app_group_files is None:
            print("Error: Cannot find Files in Targets/Target/Groups/Group")
            sys.exit(1)

        #<File>
        #    <FileName>main.c</FileName>
        #    <FileType>1</FileType>
        #    <FilePath>../../source/main.c</FilePath>
        #</File>

        for f in added_file_spec:
            f_el =  ET.SubElement(app_group_files, 'File')
            f_name_el = ET.SubElement(f_el, 'FileName')
            f_name_el.text = f
            f_type_el = ET.SubElement(f_el, 'FileType')
            if os.path.splitext(f)[1] == ".c":
                f_type_el.text = "1"
            else:
                f_type_el.text = "5"
            f_path_el = ET.SubElement(f_el, 'FilePath')
            f_path_el.text = "../../source/" + f

        project_element_str = ET.tostring(project_element, xml_declaration=True, encoding='UTF-8').decode()
        result[fname_prj] = project_element_str

    return result


def discover_device_spec(user_settings):

    BUILD_CONTEXT["BUILD_TOOL_TYPE_IS_MDK"] = user_settings.BUILD_TOOL_TYPE_IS_MDK
    BUILD_CONTEXT["BUILD_TOOL_TYPE"] = user_settings.BUILD_TOOL_TYPE
    BUILD_CONTEXT["MX_GENERATED_PRJ_NAME"] = user_settings.MX_GENERATED_PRJ_NAME
    BUILD_CONTEXT["MX_GENERATED_CODE_PATH"] = user_settings.MX_GENERATED_CODE_PATH
    BUILD_CONTEXT["COMPONENT_OUT_PATH"] = user_settings.COMPONENT_OUT_PATH
    BUILD_CONTEXT["COMPONENT_SHORT_NAME"] = user_settings.COMPONENT_SHORT_NAME

    prj_name = BUILD_CONTEXT["MX_GENERATED_PRJ_NAME"]
    if(BUILD_CONTEXT["BUILD_TOOL_TYPE"] == BUILD_CONTEXT["BUILD_TOOL_TYPE_IS_MDK"]):
        fname_prj = prj_name + ".uvprojx"
        f_prj = os.path.join(BUILD_CONTEXT["MX_GENERATED_CODE_PATH"], "MDK-ARM/"+fname_prj)
        ifile_lines = []
        with open(f_prj, 'r') as ifile:
            ifile_lines = ifile.readlines()
        ifile_cont = "".join(ifile_lines)

        #look for  <familly_name>_hal_msp.c file 
        family_name_pat = r"([a-zA-Z0-9_]*)_hal_msp\.c"
        m = re.search(family_name_pat, ifile_cont)
        if m:
            BUILD_CONTEXT["family_name"] = m.group(1)
        else:
            BUILD_CONTEXT["family_name"] = "unknown"

        #Some things use mixed lower and upper mix of the family name, for example "STM32F3xx_HAL_Driver"
        BUILD_CONTEXT["family_name_caps"] = BUILD_CONTEXT["family_name"].upper().replace("XX", "xx")

        startup_name_pat = r"(startup_[a-zA-Z0-9_]*\.s)"
        m = re.search(startup_name_pat, ifile_cont)
        if m:
            BUILD_CONTEXT["cmsis_startup"] = m[0]
        else:
            BUILD_CONTEXT["cmsis_startup"] = "startup_unknown.s"

        if "stm32f1" in  BUILD_CONTEXT["family_name"]:
            BUILD_CONTEXT["arch"] = "arch_cortexm3"
        elif "stm32f0" in BUILD_CONTEXT["family_name"]:
            BUILD_CONTEXT["arch"] = "arch_cortexm0"
        else:
            BUILD_CONTEXT["arch"] = "arch_cortexm4"

#------------------------------------------------------------------------------
def transform(comp_tree, mx_generated_code_path):
    FN = BUILD_CONTEXT["family_name"]
    FN_CAPS = BUILD_CONTEXT["family_name_caps"]

    COMPONENT_APP_BASIC_FILES = [
        ("main",  [C_EXT]),
        ("board_app", [C_EXT, H_EXT]),
        ("board_hal", [H_EXT]),
        ("mcu_init", [C_EXT, H_EXT]),
        ("mcu_init_gpio", [H_EXT]),
        ("board_state",  [C_EXT, H_EXT]),
        ("scheduler", [C_EXT, H_EXT]),
        ("%s_it"%FN, [C_EXT]),
        ("%s_hal_conf"%FN, [C_EXT]),
        ("%s_hal_conf"%FN, [H_EXT]),
        ("%s_hal_msp"%FN, [C_EXT]),
        ("system_%s"%FN, [C_EXT]),
        ("scheduler", [C_EXT, H_EXT]),
        ("sys_time", [C_EXT, H_EXT]),
        ("sys_cfg", [C_EXT, H_EXT]),
        ("version", [H_EXT])
    ]

    COMPONENT_APP_BASIC_FILES_BODY_GENERATORS = [
        ("mcu_init_gpio", [H_EXT],             build_body__mcu_init_gpio),
        ("mcu_init", [C_EXT, H_EXT],           build_body__mcu_init),
        ("%s_hal_msp"%FN, [C_EXT],             build_body__hal_msp),
        ("%s_hal_conf"%FN, [H_EXT],            build_body__hal_conf_h),
        ("%s_hal_conf"%FN, [C_EXT],            build_body__hal_conf_c),
        ("system_%s" % FN, [C_EXT],            build_body__cmsis_system),
        ("board_hal", [H_EXT],                 build_body__board_hal_h),
        ("board_app", [C_EXT, H_EXT],          build_body__board_app),
        ("board_state", [C_EXT, H_EXT],        build_body__board_state),
        ("%s_it"%FN, [C_EXT],                  build_body__it),
        ("main", [C_EXT],                      build_body__main),
        ("sys_time", [C_EXT, H_EXT],           build_body__sys_time),
        ("scheduler", [C_EXT, H_EXT],          build_body__scheduler)
    ]

    def get_body(f, ext, mx_generated_code_path):
        """ Pick a generator function(s), call and combine result 
        """
        body_generators = set()
        for e in ext:
            for g in COMPONENT_APP_BASIC_FILES_BODY_GENERATORS:
                if (f == g[0]) and (e in g[1]):
                    body_generators.add(g[2])
        
        if len(body_generators) == 0:
            body_generators.add(build_body__empty)

        f_body = {H_EXT: "", C_EXT: ""}
        for body_generator in body_generators:
            body = body_generator(mx_generated_code_path)
            if body[H_EXT]:
                f_body[H_EXT] = "\n".join([f_body[H_EXT], body[H_EXT]])
            if body[C_EXT]:
                f_body[C_EXT] = "\n".join([f_body[C_EXT], body[C_EXT]])

        return f_body
    

    #create folder structure
    for f, ext in COMPONENT_APP_BASIC_FILES:
        file_body = get_body(f, ext, mx_generated_code_path)
        for e in ext:
            file_cont = ""
            if e == H_EXT:
                file_cont = h_file(f, file_body[e])
            elif e == C_EXT:
                if len(ext) == 1:
                    file_cont = c_file(f, file_body[e], include=False)
                else:
                    file_cont = c_file(f, file_body[e])
            print("Proccessing {}{}".format(f, e))
            write_out_file(comp_tree["app_source"], f+e, file_cont)

    file_cont = build_body__startup(mx_generated_code_path, BUILD_CONTEXT["BUILD_TOOL_TYPE"])
    write_out_file(comp_tree["app_source_arch_cortex_mdk"], BUILD_CONTEXT["cmsis_startup"], file_cont)
    
    file_cont = build_body__toolproject(mx_generated_code_path, BUILD_CONTEXT["BUILD_TOOL_TYPE"])
    for fname,file_cont in file_cont.items():
        write_out_file(comp_tree["app_tool_mdk"], fname, file_cont)

    IMPORTED_COMPONENTS = [
        ("%s_HAL_Driver"%FN_CAPS, "Drivers/%s_HAL_Driver"%FN_CAPS),
        ("CMSIS/Include", "Drivers/CMSIS/Include"),
        ("CMSIS/Device/ST/%s/Include"%FN_CAPS, "Drivers/CMSIS/Device/ST/%s/Include"%FN_CAPS)
    ]
    for dst, src in IMPORTED_COMPONENTS:
        shutil.copytree(os.path.join(mx_generated_code_path, src), 
                        os.path.join(comp_tree["imported"], dst))

def main(args):
    if not os.path.isfile(args.spec):
        print("Cannot find {}".format(args.spec))
        sys.exit(1)
    bumblebee_spec = os.path.abspath(args.spec)

    from pydoc import importfile
    _temp = importfile(bumblebee_spec)

    c_templates.set_user_settings(_temp.user_settings)
    discover_device_spec(_temp.user_settings)
    comp_tree = comp_structure(BUILD_CONTEXT["COMPONENT_OUT_PATH"], BUILD_CONTEXT["COMPONENT_SHORT_NAME"])
    transform(comp_tree, BUILD_CONTEXT["MX_GENERATED_CODE_PATH"])


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Bumblbee stm32 cubemx transformer')
    parser.add_argument('--spec', type=str, required=True, help='Bumblee build specification py file')
    args = parser.parse_args()

    main(args)
