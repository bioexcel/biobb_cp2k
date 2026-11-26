#!/usr/bin/env python3

"""Module containing the Cp2kPrep class and the command line interface."""
from typing import Optional
from typing import Any
import os
import copy
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu

SIMULATION_TYPES = ('energy', 'geom_opt', 'md', 'mp2')


def _find_key(d: dict, name: str) -> str:
    """Goes from a section or keyword name to its key in d, in any case (the name itself if d has none)."""
    return next((key for key in d if key.upper() == name.upper()), name)


class Cp2kPrep(BiobbObject):
    """
    | biobb_cp2k Cp2kPrep
    | Helper bb to prepare inputs for the `CP2K QM tool <https://www.cp2k.org/>`_ module.
    | Prepares input files for the CP2K QM tool.

    Args:
        input_inp_path (str) (Optional): Input configuration file (CP2K run options). File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp>`_. Accepted formats: inp (edam:format_2330), in (edam:format_2330), txt (edam:format_2330), wfn (edam:format_2333).
        input_pdb_path (str) (Optional): Input PDB file. File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/H2O_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        input_rst_path (str) (Optional): Input restart file (WFN). File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k.wfn>`_. Accepted formats: wfn (edam:format_2333).
        output_inp_path (str): Output CP2K input configuration file. File type: output. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_prep_out.inp>`_. Accepted formats: inp (edam:format_2330), in (edam:format_2330), txt (edam:format_2330).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **simulation_type** (*str*) - ("energy") Default options for the cp2k_in file. Each creates a different inp file. Values: `energy <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_energy.inp>`_ (Computes Energy and Forces), `geom_opt <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_geom_opt.inp>`_ (Runs a geometry optimization), `md <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_md.inp>`_ (Runs an MD calculation), `mp2 <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_mp2.inp>`_ (Runs an MP2 calculation).
            * **cp2k_in** (*dict*) - ({}) CP2K run options specification.
            * **cell_cutoff** (*float*) - (5.0) CP2K cell cutoff, to build the cell around the system (only used if input_pdb_path is defined).
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_cp2k.cp2k.cp2k_prep import cp2k_prep
            prop = {
                'simulation_type': 'geom_opt'
            }
            cp2k_prep(input_pdb_path='/path/to/input.pdb',
                         input_inp_path='/path/to/cp2k_in.inp',
                         output_inp_path='/path/to/cp2k_out.inp',
                         properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, output_inp_path: str,
                 input_pdb_path: Optional[str] = None, input_inp_path: Optional[str] = None, input_rst_path: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def iterdict(self, d, depth, fileout_h):
        for k, v in d.items():
            if k.upper() == "FORCE_EVAL" or k.upper() == "MOTION":
                depth = 0
            elif "-" in k:
                k = k.split("-")[0]
            if isinstance(v, dict):
                depth = depth+1
                if 'name' in v.keys():
                    print(' ' * depth + "&" + k.upper(), v['name'], file=fileout_h)
                else:
                    print(' ' * depth + "&" + k.upper(), file=fileout_h)
                self.iterdict(v, depth, fileout_h)
                print(' ' * depth + "&END", k.upper(), file=fileout_h)
                depth = depth-1
            else:
                if k.isnumeric():
                    print(' ' * depth, v, file=fileout_h)
                elif isinstance(v, list):
                    if not isinstance(v[0], dict):
                        print(' ' * depth, k, ' '.join(v), file=fileout_h)
                    elif isinstance(v[0], dict):
                        depth = depth+1
                        if k.upper() == 'KIND':
                            for atom in v:
                                print(' ' * depth + "&" + k.upper(), atom['name'], file=fileout_h)
                                self.iterdict(atom, depth, fileout_h)
                                print(' ' * depth + "&END", k.upper(), file=fileout_h)

                        elif k.upper() == 'COORD':
                            print(' ' * depth + "&" + k.upper(), file=fileout_h)
                            for atom in v:
                                self.iterdict(atom, depth, fileout_h)
                        else:
                            print(' ' * depth + "&" + k.upper(), file=fileout_h)

                        if k.upper() != 'KIND':
                            print(' ' * depth + "&END", k.upper(), file=fileout_h)
                            depth = depth-1

                elif k != 'name':
                    print(' ' * depth, k.upper(), v, file=fileout_h)

    def parse_rec_def(self, cp2k_in_array: list[Any], index: int, stop: str) -> dict[Any, Any]:
        dict_var: dict[Any, Any] = {}
        dict_var2: dict[Any, Any] = {}
        depth = 0
        rec = False
        for line in cp2k_in_array[index:]:
            index = index+1
            if line.startswith('#') or not line.strip():
                continue

            if 'END' in line:
                depth = depth - 1
                vals = line.lstrip().split()

                if depth < 0:
                    return dict_var
            elif '&' in line:
                depth = depth + 1
                if depth == 1:
                    vals = line.lstrip().split()
                    key = vals[0].replace('&', '')
                    if (key == 'KIND'):
                        key_name = key + "-" + vals[1]
                        if dict_var.get(key):
                            dict_var[key].append(self.parse_rec_def(cp2k_in_array, index, key_name))
                        else:
                            dict_var[key] = []
                            dict_var[key].append(self.parse_rec_def(cp2k_in_array, index, key_name))
                    else:
                        rec = True
                        dict_var[key] = self.parse_rec_def(cp2k_in_array, index, key)
                        if len(vals) > 1 and key != 'KIND':
                            dict_var[key]['name'] = vals[1].strip()

            elif not rec:
                vals = line.lstrip().split()
                if (stop == 'COORD'):
                    if dict_var2.get('coords_list'):
                        dict_var2['coords_list'].append({vals[0]: vals[1:]})
                    else:
                        dict_var2['coords_list'] = []
                        dict_var2['coords_list'].append({vals[0]: vals[1:]})

                    dict_var = dict_var2['coords_list']  # type: ignore
                elif (len(vals) == 2):
                    if (stop.startswith('KIND-')):
                        key2, name = stop.split('-')
                        dict_var['name'] = name
                    dict_var[vals[0]] = vals[1].strip()
                else:
                    dict_var[vals[0]] = vals[1:]

        return dict_var

    def parse_pdb(self, pdb_file: str) -> dict[str, Any]:
        """Goes from a PDB file to its CP2K coordinates and a cell around them with cell_cutoff of margin."""
        coord = []
        xyz = []
        with open(pdb_file) as pdb_fh:
            for line in pdb_fh:
                if line.startswith(('ATOM', 'HETATM')):
                    x, y, z = line[30:38], line[38:46], line[46:54]
                    coord.append({line[76:78].strip(): [x, y, z]})
                    xyz.append((float(x), float(y), float(z)))
        abc = [str(float(f'{max(axis) - min(axis):.3f}') + self.cell_cutoff) for axis in zip(*xyz)]
        return {'coord': coord, 'cell': {'ABC': abc}}

    def merge(self, a: dict, b: dict) -> dict:
        """Goes from two CP2K input dicts to a with b merged in: names in any case, KIND sections matched by name."""
        for key_b, value_b in b.items():
            key_a = _find_key(a, key_b)
            value_a = a.get(key_a)
            if isinstance(value_a, dict) and isinstance(value_b, dict):
                self.merge(value_a, value_b)
            elif key_a.upper() == 'KIND' and isinstance(value_a, list) and isinstance(value_b, list):
                for kind_b in value_b:
                    kind_a = next((kind for kind in value_a if kind['name'] == kind_b['name']), None)
                    if kind_a is None:
                        value_a.append(kind_b)
                    else:
                        self.merge(kind_a, kind_b)
            else:
                a[key_a] = value_b
        return a

    def replace_coords(self, inp: dict, pdb: dict) -> dict:
        """Goes from a CP2K input dict to the same with the coordinates and the cell of the PDB (parse_pdb)."""
        fu.log('Replacing the coordinates and the cell with the ones of the PDB', self.out_log, self.global_log)
        force_eval = inp.setdefault(_find_key(inp, 'FORCE_EVAL'), {})
        subsys = force_eval.setdefault(_find_key(force_eval, 'SUBSYS'), {})
        subsys[_find_key(subsys, 'COORD')] = pdb['coord']
        cell = subsys.setdefault(_find_key(subsys, 'CELL'), {})
        cell[_find_key(cell, 'ABC')] = pdb['cell']['ABC']
        return inp

    def stage_files(self) -> None:
        """The block does not use the sandbox: there are no files to stage."""

    def run(self):
        """Launches the execution of the Cp2kPrep module."""
        # CP2K input: input_inp_path, else the template of simulation_type
        inp_path = self.io_dict["in"]["input_inp_path"]
        if inp_path:
            if self.properties.get('simulation_type'):
                fu.log(f"Both simulation_type [{self.simulation_type}] and input_inp_path [{inp_path}] given: using input_inp_path", self.out_log, self.global_log)
        elif self.simulation_type:
            if self.simulation_type not in SIMULATION_TYPES:
                msg = f"{type(self).__name__}: ERROR: Simulation type {self.simulation_type} not defined"
                fu.log(msg, self.out_log)
                raise SystemExit(msg)
            inp_path = str(Path(os.getenv("CONDA_PREFIX", "")).joinpath('cp2k_aux', 'cp2k_in', f'cp2k_{self.simulation_type}.inp'))
        if not inp_path and not self.cp2k_in:
            msg = f"{type(self).__name__}: ERROR: Neither simulation_type, input_inp_path nor cp2k_in were defined"
            fu.log(msg, self.out_log)
            raise SystemExit(msg)

        final_dict: dict = {}
        if inp_path:
            with open(inp_path) as inp_fh:
                final_dict = self.parse_rec_def(inp_fh.readlines(), 0, 'Stop')
        if self.cp2k_in:
            # Merged as a copy: the restart and the coordinates do not reach the properties of the caller
            self.merge(final_dict, copy.deepcopy(self.cp2k_in))

        if self.io_dict["in"]["input_rst_path"]:
            rst_path = str(Path(self.io_dict["in"]["input_rst_path"]).resolve())
            self.merge(final_dict, {'FORCE_EVAL': {'DFT': {'WFN_RESTART_FILE_NAME': rst_path, 'SCF': {'SCF_GUESS': 'RESTART'}}}})

        if self.io_dict["in"]["input_pdb_path"]:
            self.replace_coords(final_dict, self.parse_pdb(self.io_dict["in"]["input_pdb_path"]))

        with open(self.io_dict["out"]["output_inp_path"], 'w') as cp2k_out_fh:
            self.iterdict(final_dict, 0, cp2k_out_fh)


cp2k_prep = launcher(Cp2kPrep)

if __name__ == '__main__':
    Cp2kPrep.main()
