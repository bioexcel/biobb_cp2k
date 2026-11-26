#!/usr/bin/env python3

"""Module containing the Cp2kRun class and the command line interface."""
from typing import Optional
import shutil
import os
from pathlib import Path, PurePath
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu


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
            * **mpi_np** (*int*) - (None) [0~1000|1] Number of MPI processes. Usually an integer bigger than 1.
            * **mpi_flags** (*str*) - (None) Path to the MPI hostlist file.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

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
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def run(self):
        """Launches the execution of the Cp2kRun module."""

        # Temporary folder in the sandbox where CP2K runs: it only holds the input and the files CP2K writes
        tmp_folder = self.create_tmp_dir(log=True)

        shutil.copy2(self.sandbox_file("input_inp_path"), tmp_folder)

        # Path to the CP2K parameter data files, in the environment of the command (also in a container)
        if self.param_path:
            if not Path(PurePath(self.param_path)).exists():
                fu.log(self.__class__.__name__ + ': Unexisting  %s folder, exiting' % self.param_path, self.out_log)
                raise SystemExit(self.__class__.__name__ + ': Unexisting  %s folder' % self.param_path)
            self.env_vars_dict["CP2K_DATA_DIR"] = self.param_path
        elif self.container_path:
            # The biobb_cp2k image has its conda environment in /usr/local
            self.env_vars_dict["CP2K_DATA_DIR"] = "/usr/local/cp2k_aux/cp2k_data"
        else:
            self.env_vars_dict["CP2K_DATA_DIR"] = str(Path(os.getenv("CONDA_PREFIX", "")).joinpath('cp2k_aux').joinpath('cp2k_data'))

        # Command line, run in the temporary folder
        # cp2k.sopt -i benzene_dimer.inp -o mp2_test.out
        self.cmd = [self.binary_path,
                    '-i', self.stage_io_dict["in"]["input_inp_path"],
                    '-o', self.stage_io_dict["out"]["output_log_path"]]

        # general mpi properties
        if self.mpi_bin:
            mpi_cmd = [self.mpi_bin]
            if self.mpi_np:
                mpi_cmd.append('-n')
                mpi_cmd.append(str(self.mpi_np))
            if self.mpi_flags:
                mpi_cmd.append(self.mpi_flags)
            self.cmd = mpi_cmd + self.cmd

        # Run Biobb block
        self.run_biobb(cwd=tmp_folder)

        # Gather the files written by CP2K in the temporary folder (on the host) in the output zip file
        out_files = []
        restart = ''
        for root, dirs, files in os.walk(tmp_folder):
            for file in files:
                if file.endswith('.wfn'):
                    restart = tmp_folder + '/' + file
                else:
                    out_files.append(tmp_folder + '/' + file)

        fu.zip_list(self.sandbox_file("output_outzip_path"), out_files, self.out_log)

        # Outputs in the sandbox, copied to the host by BiobbObject.launch()
        shutil.copy2(PurePath(tmp_folder).joinpath(self.stage_io_dict["out"]["output_log_path"]), self.sandbox_file("output_log_path"))
        if restart:
            shutil.copy2(restart, self.sandbox_file("output_rst_path"))


cp2k_run = launcher(Cp2kRun)

if __name__ == '__main__':
    Cp2kRun.main()
