#!/usr/bin/env python3

"""Module containing the Cp2kRun class and the command line interface."""
import argparse
import shutil, re, os
from pathlib import Path, PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
import biobb_cp2k.cp2k.cp2k_run as myself
from biobb_cp2k.cp2k.common import *

class Cp2kRun(BiobbObject):
    """
    | biobb_cp2k Cp2kRun
    | Wrapper of the `CP2K QM tool <https://www.cp2k.org/>`_ module.
    | Runs atomistic simulations of solid state, liquid, molecular, periodic, material, crystal, and biological systems using CP2K QM tool.

    Args:
        input_inp_path (str): Input configuration file (CP2K run options). File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp>`_. Accepted formats: inp (edam:format_2330), in (edam:format_2330), txt (edam:format_2330), wfn (edam:format_2333).
        output_log_path (str): Output log file. File type: output. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.log>`_. Accepted formats: log (edam:format_2330), out (edam:format_2330), txt (edam:format_2330), o (edam:format_2330).
        output_outzip_path (str): Output files. File type: output. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.zip>`_. Accepted formats: zip (edam:format_3987), gzip (edam:format_3987), gz (edam:format_3987).
        output_rst_path (str): Output restart file. File type: output. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.wfn>`_. Accepted formats: wfn (edam:format_2333).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **binary_path** (*str*) - ("cp2k.sopt") CP2K binary path to be used.
            * **param_path** (*str*) - (None) Path to the CP2K parameter data files (BASIS_SET, POTENTIALS, etc.). If not provided, the parameter data files included in the package will be used.
            * **mpi_bin** (*str*) - (None) Path to the MPI runner. Usually "mpirun" or "srun".
            * **mpi_np** (*int*) - (0) [0~1000|1] Number of MPI processes. Usually an integer bigger than 1.
            * **mpi_flags** (*str*) - (None) Path to the MPI hostlist file.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_cp2k.cp2k.cp2k_run import cp2k_run
            prop = {
                'binary_path': 'cp2k.sopt'
            }
            cp2k_run(input_inp_path='/path/to/cp2k_input.inp',
                         output_log_path='/path/to/cp2k_log.log',
                         output_outzip_path='/path/to/cp2k_out.zip',
                         output_rst_path='/path/to/cp2k_rst.wfn',
                         properties=prop)

    Info:
        * wrapped_software:
            * name: CP2K
            * version: >=7.1.0
            * license: GPL-2.0
            * multinode: mpi
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """
    def __init__(self, input_inp_path: str, output_log_path: str,
    output_outzip_path: str, output_rst_path: str,
    properties: dict = None, **kwargs) -> None:

        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            'in': { 'input_inp_path': input_inp_path },
            'out': {    'output_log_path': output_log_path,
                        'output_outzip_path': output_outzip_path,
                        'output_rst_path': output_rst_path }
        }

        # Properties specific for BB
        self.properties = properties
        self.binary_path = properties.get('binary_path', 'cp2k.sopt')
        self.param_path = properties.get('param_path', None)

        # Properties for MPI
        self.mpi_bin = properties.get('mpi_bin')
        self.mpi_np = properties.get('mpi_np')
        self.mpi_flags = properties.get('mpi_flags')

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, out_err):
        """ Checks input/output paths correctness """

        # Check input(s)
        self.io_dict["in"]["input_inp_path"] = check_input_path(self.io_dict["in"]["input_inp_path"], "input_inp_path", False, out_log, self.__class__.__name__)

        # Check output(s)
        self.io_dict["out"]["output_log_path"] = check_output_path(self.io_dict["out"]["output_log_path"],"output_log_path", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_outzip_path"] = check_output_path(self.io_dict["out"]["output_outzip_path"],"output_outzip_path", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_rst_path"] = check_output_path(self.io_dict["out"]["output_rst_path"],"output_rst_path", False, out_log, self.__class__.__name__)

    @launchlogger
    def launch(self):
        """Launches the execution of the Cp2kRun module."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # Creating temporary folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, self.out_log)

        shutil.copy2(self.io_dict["in"]["input_inp_path"], self.tmp_folder)

        # set path to the CP2K parameter data files 
        if not self.param_path: 
            #os.environ["CP2K_DATA_DIR"] = str(PurePath(myself.__file__).parent.joinpath('cp2k_data'))
            os.environ["CP2K_DATA_DIR"] =  str(Path(os.getenv("CONDA_PREFIX")).joinpath('cp2k_aux').joinpath('cp2k_data'))
        else:
            if not Path(PurePath(self.param_path)).exists():
                fu.log(self.__class__.__name__ + ': Unexisting  %s folder, exiting' % self.param_path, self.out_log)
                raise SystemExit(self.__class__.__name__ + ': Unexisting  %s folder' % self.param_path)
            os.environ["CP2K_DATA_DIR"] = self.param_path

        # Command line
        # cp2k.sopt -i benzene_dimer.inp -o mp2_test.out
        self.cmd = ['cd', self.tmp_folder, ';',
                self.binary_path,
               '-i', PurePath(self.io_dict["in"]["input_inp_path"]).name,
               '-o', PurePath(self.io_dict["out"]["output_log_path"]).name
               ]

        # general mpi properties
        if self.mpi_bin:
            mpi_cmd = [self.mpi_bin]
            if self.mpi_np:
                mpi_cmd.append('-n')
                mpi_cmd.append(str(self.mpi_np))
            if self.mpi_flags:
                mpi_cmd.extend(self.mpi_flags)
            self.cmd = mpi_cmd + self.cmd

        # Run Biobb block
        self.run_biobb()

        # Gather output files in a single zip file
        self.output = PurePath(self.tmp_folder).joinpath("cp2k_out.zip")
        out_files = []
        restart = ''
        for root, dirs, files in os.walk(self.tmp_folder):
            for file in files:
                #fu.log('FILE %s ' % file, self.out_log)
#                if file.endswith('.out'):
#                    out_files.append(file)
#                elif file.endswith('.wfn'):
#                    restart = file

                if file.endswith('.wfn'):
                    restart = self.tmp_folder + '/' + file
                else:
                    out_files.append(self.tmp_folder + '/' + file)

        fu.zip_list(self.output,out_files,self.out_log)

        # Copy outputs from temporary folder to output path
        shutil.copy2(self.output, PurePath(self.io_dict["out"]["output_outzip_path"]))
        shutil.copy2(PurePath(self.tmp_folder).joinpath(PurePath(self.io_dict["out"]["output_log_path"]).name), PurePath(self.io_dict["out"]["output_log_path"]))
        if restart:
            shutil.copy2(restart, PurePath(self.io_dict["out"]["output_rst_path"]))

        # Copy files to host
        self.copy_to_host()

        # remove temporary folder(s)
        self.tmp_files.extend([
            self.stage_io_dict.get("unique_dir"),
            self.tmp_folder
        ])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code

def cp2k_run(input_inp_path: str,
            output_log_path: str, output_outzip_path: str, output_rst_path: str,
            properties: dict = None, **kwargs) -> int:
    """Create :class:`Cp2kRun <cp2k.cp2k_run.Cp2kRun>`cp2k.cp2k_run.Cp2kRun class and
    execute :meth:`launch() <cp2k.cp2k_run.Cp2kRun.launch>` method"""

    return Cp2kRun( input_inp_path=input_inp_path,
                    output_log_path=output_log_path,
                    output_outzip_path=output_outzip_path,
                    output_rst_path=output_rst_path,
                    properties=properties).launch()

def main():
    parser = argparse.ArgumentParser(description='Running atomistic simulations of solid state, liquid, molecular, periodic, material, crystal, and biological systems using CP2K QM tool.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_inp_path', required=True, help='Input configuration file (QM run options). Accepted formats: inp, in, txt.')
    required_args.add_argument('--output_log_path', required=True, help='Output log file. Accepted formats: log, out, txt.')
    required_args.add_argument('--output_outzip_path', required=True, help='Output trajectory file. Accepted formats: zip, gz, gzip.')
    required_args.add_argument('--output_rst_path', required=True, help='Output restart file. Accepted formats: wfn.')

    args = parser.parse_args()
    #config = args.config if args.config else None
    args.config = args.config or "{}"
    #properties = settings.ConfReader(config=config).get_prop_dic()
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call
    cp2k_run(       input_inp_path=args.input_inp_path,
                    output_log_path=args.output_log_path,
                    output_outzip_path=args.output_outzip_path,
                    output_rst_path=args.output_rst_path,
                    properties=properties)

if __name__ == '__main__':
    main()
