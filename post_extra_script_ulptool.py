# Copyright (c) likeablob
# SPDX-License-Identifier: MIT
from pathlib import Path, PurePath
import subprocess
import sys
from SCons.Script import COMMAND_LINE_TARGETS, Import

Import("env", "projenv")
env = globals()["env"]
projenv = globals()["projenv"]

# Do not run extra script when IDE fetches C/C++ project metadata
if "idedata" in COMMAND_LINE_TARGETS:
    env.Exit(0)

project_dir = Path(env["PROJECT_DIR"])
ulptool_dir = Path(env["PROJECT_LIBDEPS_DIR"]) / env["PIOENV"] / "ulptool-pio"


def run_ulptool():
    platform = env.PioPlatform()

    framework_dir = platform.get_package_dir("framework-arduinoespressif32")
    toolchain_ulp_dir = platform.get_package_dir("toolchain-esp32ulp")
    toolchain_xtensa_dir = platform.get_package_dir("toolchain-xtensa32")

    cpp_defines = ""
    for raw in env["CPPDEFINES"]:
        k = None
        if type(raw) is tuple:
            k, v = raw
            v = v if type(v) is not str else v.replace(" ", r"\ ")
            flag = f"--D{k}={v};"
        else:
            k = raw
            flag = f"--D{k};"

        if k.startswith("ARDUINO"):
            cpp_defines += flag

    cpp_inc_flags = ""
    prefix = env["INCPREFIX"]
    suffix = env["INCSUFFIX"]

    for dir in env["CPPPATH"]:
        path = Path(dir)
        flag = prefix+str(path).replace("\\", "/")+suffix+";"
        cpp_inc_flags += flag

    cmd = str(env["PYTHONEXE"]).replace("\\", "/") + ";" + \
        str(ulptool_dir).replace("\\", "/")+"/src/esp32ulp_build_recipe.py;" + \
        cpp_inc_flags + \
        "-b"+str(project_dir).replace("\\", "/") + ";" + \
        "-p"+str(framework_dir).replace("\\", "/") + ";" + \
        "-u"+str(toolchain_ulp_dir).replace("\\", "/")+"/bin;" + \
        "-x"+str(toolchain_xtensa_dir).replace("\\", "/")+"/bin;" + \
        "-t"+str(ulptool_dir).replace("\\", "/")+"/src/;" + \
        str(cpp_defines)

    print()
    cmd = cmd.split(";")
    for part in cmd:
        print(part)
    print()
    #print("Run Process")
    console_string = ''
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err.decode('utf-8')
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    print("end of process")
    print(out)

    if proc:
        raise Exception("An error returned by ulptool.")


def cb(*args, **kwargs):
    print("Running ulptool")
    run_ulptool()


# Run ulptool just before linking .elf
env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", cb)
