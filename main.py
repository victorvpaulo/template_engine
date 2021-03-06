import argparse
import sys
from pathlib import Path

from src.compiler import compile_template
from src.executor import execute_compiled_template
from src.utils import get_timestamp


def exit_on_arg_error(errormsg):
    print(errormsg)
    parser.print_usage()
    sys.exit(1)


parser = argparse.ArgumentParser(
    description="A simple Template Engine based on compilation."
                " Can receive a textual static template file and compile it,"
                " or execute a compiled template along with a data context to"
                " generate textual files with dynamic data.")
parser.add_argument("-c", "--compile", type=str,
                    metavar="<file path>",
                    help=" Creates a template from a static file.")
parser.add_argument("-co", "--compileoutput", type=str,
                    metavar="<file path>",
                    help=" Defines the output path for the compiled template."
                         " It must be a valid python module name, else"
                         " execution will fail."
                         " If not provided, the output will be sent to"
                         " the same directory of the provided static template"
                         " file, under the name 'tmplt<timestamp>.py'")

parser.add_argument("-e", "--execute", nargs="?", const="$compiled$",
                    metavar="<template file path>",
                    help=" Executes a compiled template, plugging dynamic data"
                         " from a context. Requires a context argument and a"
                         " template. By default executes the template"
                         " generated by the compile action, so no"
                         " argument must be passed."
                         " However, if the --compile argument is not passed"
                         " along with --execution"
                         " a path to a template file must be passed "
                         " as an argument.")

parser.add_argument("-d", "--context", type=str, metavar="<file path>",
                    help=" Context file path for the execution of a template."
                         " The context file provides the data to be pluged"
                         " into the  template. Must be a json file.")

parser.add_argument("-eo", "--executeoutput", type=str,
                    metavar="<directory path>",
                    help=" Directory path to store the output of the execution"
                         " operation. If not provided, the directory where the"
                         " context file is located will be used.")
args = parser.parse_args()

args_received = len(sys.argv)
if args_received < 2:
    exit_on_arg_error("ERROR - Invalid number of arguments.\n"
                      "\tThis program requires at least 1 argument.")

if args.compile is None and not args.execute:
    exit_on_arg_error(
        "ERROR - Either a compile or execute argument must be passed.\n")

static_template_path = None
compile_output_path = None
if args.compile is not None:
    static_template_path = Path(args.compile).resolve()
    if not static_template_path.is_file():
        exit_on_arg_error("ERROR - Invalid path for static template file"
                          " (--compile).")
    if args.compileoutput is not None:
        compile_output_path = Path(args.compileoutput).resolve()
        if not compile_output_path.parent.exists():
            exit_on_arg_error("ERROR - Invalid output path for compilation"
                              " - The output path directory does not exist."
                              " (--compileoutput).")
    else:
        compile_file_name = "tmplt" + get_timestamp() + ".py"
        compile_output_path = static_template_path.parent / compile_file_name

    compile_template(static_template_path, compile_output_path)

if args.execute:
    template_path = None
    template_path_parent_directory = None
    template_module = None
    if compile_output_path is None:
        if args.execute is "$compiled$":
            exit_on_arg_error("ERROR - A path must be passed to the execute"
                              " argument when execution does not occur along "
                              "with compilation (--execute <path>).")
        template_path = Path(args.execute).resolve()
        if not template_path.is_file():
            exit_on_arg_error("ERROR - Invalid path for the template to"
                              " be executed (--execute <path>).")
    else:
        template_path = compile_output_path
    template_path_parent_directory = template_path.parent
    template_module = template_path.parts[-1].replace(".py", "")
    if args.context is None:
        exit_on_arg_error("ERROR - Template execution requires a data context"
                          " (--context)")
    context_path = Path(args.context).resolve()
    if not context_path.is_file():
        exit_on_arg_error("ERROR - Invalid path for data context"
                          " (--context).")
    if args.executeoutput is not None:
        execute_output_path = Path(args.executeoutput).resolve()
        if not execute_output_path.is_dir():
            exit_on_arg_error("ERROR - Path for execution output is not"
                              " a directory path (--executeoutput).")
    else:
        execute_output_path = context_path.parent

    execute_compiled_template(template_path_parent_directory,
                              template_module,
                              context_path, execute_output_path)
