#!/usr/bin/env python3

"""Module containing the Cp2kPrep class and the command line interface."""
import argparse
#import json
#import shutil, re, os
import os
import collections.abc
from pathlib import Path, PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_cp2k.cp2k.common import *
import biobb_cp2k.cp2k.cp2k_run as myself

class Cp2kPrep(BiobbObject):
    """
    | biobb_cp2k Cp2kPrep
    | Helper bb to prepare inputs for the `CP2K QM tool <https://www.cp2k.org/>`_ module.
    | Prepares input files for the CP2K QM tool.

    Args:
        input_inp_path (str) (Optional): Input configuration file (CP2K run options). File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp>`_. Accepted formats: pdb (edam:format_1476).
        input_pdb_path (str) (Optional): Input PDB file. File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/H2O_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        input_rst_path (str) (Optional): Input restart file (WFN). File type: input. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k.wfn>`_. Accepted formats: wfn (edam:format_2333).
        output_inp_path (str): Output CP2K input configuration file. File type: output. `Sample file <https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_prep_out.inp>`_. Accepted formats: inp (edam:format_2330), in (edam:format_2330), txt (edam:format_2330).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **simulation_type** (*str*) - ("energy") Default options for the cp2k_in file. Each creates a different inp file. Values: `energy <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_energy.inp>`_ (Computes Energy and Forces), `geom_opt <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_geom_opt.inp>`_ (Runs a geometry optimization), `md <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_md.inp>`_ (Runs an MD calculation), `mp2 <https://biobb-cp2k.readthedocs.io/en/latest/_static/cp2k_in/cp2k_mp2.inp>`_ (Runs an MP2 calculation).
            * **cp2k_in** (*dict*) - ({}) CP2K run options specification.
            * **cell_cutoff** (*float*) - (5.0) CP2K cell cutoff, to build the cell around the system (only used if input_pdb_path is defined).
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

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
    input_pdb_path: str = None, input_inp_path: str = None, input_rst_path: str = None,
    properties: dict = None, **kwargs) -> None:

        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            'in': { 'input_pdb_path': input_pdb_path,
                    'input_inp_path': input_inp_path,
                    'input_rst_path': input_rst_path },
            'out': { 'output_inp_path': output_inp_path }
        }

        # Properties specific for BB
        self.properties = properties
        self.simulation_type = properties.get('simulation_type', "energy")
        self.cell_cutoff = properties.get('cell_cutoff', 5.0)
        self.cp2k_in = properties.get('cp2k_in', dict())
        #self.cp2k_in = {k: str(v) for k, v in properties.get('cp2k_in', dict()).items()}

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def iterdict(self, d, depth, fileout_h):
      for k,v in d.items():
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
             print(' ' * depth + "&END",k.upper(), file=fileout_h)
             depth = depth-1
         else:
             if k.isnumeric():
                 print (' ' * depth,v, file=fileout_h)
             elif isinstance(v, list):
                if not isinstance(v[0], dict):
                    print (' ' * depth,k,' '.join(v),file=fileout_h)
                elif isinstance(v[0], dict):
                    depth = depth+1
                    if k.upper()=='KIND':
                        for atom in v:
                            print(' ' * depth + "&" + k.upper(), atom['name'], file=fileout_h)
                            self.iterdict(atom, depth, fileout_h)
                            print(' ' * depth + "&END",k.upper(), file=fileout_h)

                    elif k.upper()=='COORD':
                        print(' ' * depth + "&" + k.upper(), file=fileout_h)
                        for atom in v:
                            self.iterdict(atom, depth, fileout_h)
                    else:
                        print(' ' * depth + "&" + k.upper(), file=fileout_h)

                    if k.upper()!='KIND':
                        print(' ' * depth + "&END",k.upper(), file=fileout_h)
                        depth = depth-1

             elif k != 'name':
                 print (' ' * depth,k.upper(),v,file=fileout_h)

    #global dict3 = {}
    def parse_rec_def(self,cp2k_in_array,index,stop):
        dict = {}
        dict2 = {}
        depth = 0
        rec = False
        for line in cp2k_in_array[index:]:
            index=index+1
            if line.startswith('#') or not line.strip():
                continue

            if 'END' in line:
                depth = depth - 1
                vals = line.lstrip().split()

                if depth < 0:
                    return dict
            elif '&' in line:
                depth = depth + 1
                if depth == 1:
                    vals = line.lstrip().split()
                    key = vals[0].replace('&','')
                    if (key == 'KIND'):
                        key_name = key + "-" + vals[1]
                        if dict.get(key):
                            dict[key].append(self.parse_rec_def(cp2k_in_array,index,key_name))
                        else:
                            dict[key] = []
                            dict[key].append(self.parse_rec_def(cp2k_in_array,index,key_name))
                    else:
                        rec = True
                        dict[key] = self.parse_rec_def(cp2k_in_array,index,key)
                        if len(vals)>1 and key != 'KIND':
                            #print(stop + " Add dict[key]['name'] = " + str(vals[1].strip()))
                            dict[key]['name'] = vals[1].strip()

            elif not rec:
                vals = line.lstrip().split()
                #print(stop + " Add dict[" + str(vals[0]) + "] = " + str(vals[1].strip()))
                if (stop == 'COORD'):
                    if dict2.get('coords_list'):
                        dict2['coords_list'].append({vals[0]:vals[1:]})
                    else:
                        dict2['coords_list'] = []
                        dict2['coords_list'].append({vals[0]:vals[1:]})

                    dict = dict2['coords_list']
                elif (len(vals) == 2):
                    if (stop.startswith('KIND-')):
                        key2,name = stop.split('-')
                        dict['name'] = name
                    dict[vals[0]] = vals[1].strip()
                else:
                    dict[vals[0]] = vals[1:]

        return dict

    def parse_pdb(self,pdb_file):
        dict = {}
        #coord = {}
        coord = []
        cell = {}
        max_x = -999.999
        max_y = -999.999
        max_z = -999.999
        min_x = 999.999
        min_y = 999.999
        min_z = 999.999
        for line in open(pdb_file):
            # ATOM      2  C7  JZ4     1      21.520 -27.270  -4.230  1.00  0.00
            if line[0:4] == 'ATOM' or line[0:6] == 'HETATM':
                #atom = line[12:16]
                elem = line[77]
                x = line[30:38]
                y = line[38:46]
                z = line[46:54]
                if (float(x) > float(max_x)):
                    max_x = x
                if (float(y) > float(max_y)):
                    max_y = y
                if (float(z) > float(max_z)):
                    max_z = z
                if (float(x) < float(min_x)):
                    min_x = x
                if (float(y) < float(min_y)):
                    min_y = y
                if (float(z) < float(min_z)):
                    min_z = z
                #coord[elem] = [x,y,z]
                lcoord = []              
                coord.append({elem: [x,y,z]})
                #coord[elem] = lcoord

        box_x = float(max_x) - float(min_x)
        box_y = float(max_y) - float(min_y)
        box_z = float(max_z) - float(min_z)

        box_x = float(f'{box_x:.3f}')
        box_y = float(f'{box_y:.3f}')
        box_z = float(f'{box_z:.3f}')

        box_x = box_x + self.cell_cutoff
        box_y = box_y + self.cell_cutoff
        box_z = box_z + self.cell_cutoff

        #cell['A'] = [str(box_x),'0.000','0.000']
        #cell['B'] = ['0.000',str(box_y),'0.000']
        #cell['C'] = ['0.000','0.000',str(box_z)]

        cell['ABC'] = [str(box_x),str(box_y),str(box_z)]

        dict['coord'] = coord
        #dict['coords'] = coords
        dict['cell'] = cell

        return dict

    def merge(self, a, b):
        for key_b in b:
            key_bu =  key_b.upper()
            if key_bu in (key_a.upper() for key_a in a):
                for key_a in a:
                    key_au = key_a.upper()
                    if "-" in key_au:
                        key_au = key_au.split("-")[0]
                    if key_au == key_bu:
                        if isinstance(a[key_a], dict) and isinstance(b[key_b], dict):
                            self.merge(a[key_a], b[key_b])
                        elif isinstance(a[key_a], list) and isinstance(b[key_b], list):
                            if (key_au == 'KIND'):
                                for idxB,elemB in enumerate(b[key_b]):
                                    done = False
                                    for idxA,elemA in enumerate(a[key_a]):
                                        if elemB['name'] == elemA['name']:
                                                done = True
                                                self.merge(a[key_a][idxA], b[key_b][idxB])
                                    if not done:
                                        a[key_a].append(b[key_b][idxB])
                        elif a[key_a] == b[key_b]:
                            pass # same leaf value
                        else:
                            a[key_a] = b[key_b]
            else:
                 a[key_b] = b[key_b]
        return a

    def replace_coords(self,a,b):
        #dict['force_eval'] = {'subsys' : {'coord' : coord } }
        print("BioBB_CP2K, replacing coordinates...")
        for key in a:
            if key.upper() == 'FORCE_EVAL':
                for key_2 in a[key]:
                    if key_2.upper() == 'SUBSYS':
                        if 'coord' in a[key][key_2]:
                            a[key][key_2]['coord'] = b['coord']
                        elif 'Coord' in a[key][key_2]:
                            a[key][key_2]['Coord'] = b['coord']
                        elif 'COORD' in a[key][key_2]:
                            a[key][key_2]['COORD'] = b['coord']
                        else:
                            a[key][key_2]['coord'] = b['coord']

                        if 'cell' in a[key][key_2]:
                            if 'ABC' in a[key][key_2]['cell']:
                                a[key][key_2]['cell']['ABC'] = b['cell']['ABC']
                            elif 'abc' in a[key][key_2]['cell']:
                                a[key][key_2]['cell']['abc'] = b['cell']['ABC']
                            elif 'Abc' in a[key][key_2]['cell']:
                                a[key][key_2]['cell']['Abc'] = b['cell']['ABC']
                            else:
                                a[key][key_2]['cell']['abc'] = b['cell']['ABC']
                        elif 'Cell' in a[key][key_2]:
                            if 'ABC' in a[key][key_2]['Cell']:
                                a[key][key_2]['Cell']['ABC'] = b['cell']['ABC']
                            elif 'abc' in a[key][key_2]['Cell']:
                                a[key][key_2]['Cell']['abc'] = b['cell']['ABC']
                            elif 'Abc' in a[key][key_2]['Cell']:
                                a[key][key_2]['Cell']['Abc'] = b['cell']['ABC']
                            else:
                                a[key][key_2]['Cell']['abc'] = b['cell']['ABC']
                        elif 'CELL' in a[key][key_2]:
                            if 'ABC' in a[key][key_2]['CELL']:
                                a[key][key_2]['CELL']['ABC'] = b['cell']['ABC']
                            elif 'abc' in a[key][key_2]['CELL']:
                                a[key][key_2]['CELL']['abc'] = b['cell']['ABC']
                            elif 'Abc' in a[key][key_2]['CELL']:
                                a[key][key_2]['CELL']['Abc'] = b['cell']['ABC']
                            else:
                                a[key][key_2]['CELL']['abc'] = b['cell']['ABC']
                        else:
                            a[key][key_2]['cell'] = b['cell']
        return a

    def check_data_params(self, out_log, out_err):
        """ Checks input/output paths correctness """

        # Check input(s)
        self.io_dict["in"]["input_inp_path"] = check_input_path(self.io_dict["in"]["input_inp_path"], "input_inp_path", True, out_log, self.__class__.__name__)
        self.io_dict["in"]["input_pdb_path"] = check_input_path(self.io_dict["in"]["input_pdb_path"], "input_pdb_path", True, out_log, self.__class__.__name__)
        self.io_dict["in"]["input_rst_path"] = check_input_path(self.io_dict["in"]["input_rst_path"], "input_rst_path", True, out_log, self.__class__.__name__)

        # Check output(s)
        self.io_dict["out"]["output_inp_path"] = check_output_path(self.io_dict["out"]["output_inp_path"],"output_inp_path", False, out_log, self.__class__.__name__)

    def update(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @launchlogger
    def launch(self):
        """Launches the execution of the Cp2kPrep module."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # Generating inp file

        # Parsing the input PDB file (if any)
        if self.io_dict["in"]["input_pdb_path"]:
            coord = self.parse_pdb(self.io_dict["in"]["input_pdb_path"])
            #print(coord)
            #print(json.dumps(coord,indent=4))

        # Parsing the input CP2K file (if any)
        if self.io_dict["in"]["input_inp_path"] and self.simulation_type:
            print("Incompatible inputs found: simulation_type [{0}] and input_inp_path [{1}].".format(self.simulation_type,self.io_dict['in']['input_inp_path']))
            print("Will take just the input_inp_path.")
        elif(self.simulation_type):
            #path_cp2k_in = PurePath(myself.__file__).parent
            path_cp2k_in = Path(os.getenv("CONDA_PREFIX")).joinpath('cp2k_aux')
            if (self.simulation_type == 'energy'):
                self.io_dict["in"]["input_inp_path"] = str(
                Path(path_cp2k_in).joinpath("cp2k_in/cp2k_energy.inp"))
            elif (self.simulation_type == 'geom_opt'):
                self.io_dict["in"]["input_inp_path"] = str(
                Path(path_cp2k_in).joinpath("cp2k_in/cp2k_geom_opt.inp"))
            elif (self.simulation_type == 'md'):
                self.io_dict["in"]["input_inp_path"] = str(
                Path(path_cp2k_in).joinpath("cp2k_in/cp2k_md.inp"))
            elif (self.simulation_type == 'mp2'):
                self.io_dict["in"]["input_inp_path"] = str(
                Path(path_cp2k_in).joinpath("cp2k_in/cp2k_mp2.inp"))
            else:
                fu.log(self.__class__.__name__ + ': ERROR: Simulation type %s not defined' % self.simulation_type, self.out_log)
                raise SystemExit(self.__class__.__name__ + ': ERROR: Simulation type %s not defined' % self.simulation_type)
        else:
            print("ERROR: Neither simulation type nor input_inp_path were defined.")

        if self.io_dict["in"]["input_inp_path"]:
            cp2k_in_array = []
            with open(self.io_dict["in"]["input_inp_path"], 'r') as cp2k_in_fh:
                #inp_in = self.parse(cp2k_in_fh)
                for line in cp2k_in_fh:
                    cp2k_in_array.append(line)
            self.inp_in = self.parse_rec_def(cp2k_in_array,0,'Stop')
            #print(json.dumps(self.inp_in,indent=4))

        if self.io_dict["in"]["input_inp_path"] and self.cp2k_in:
            final_dict = self.merge(self.inp_in,self.cp2k_in)
            #final_dict = self.merge(self.cp2k_in,self.inp_in)
            #print(json.dumps(final_dict,indent=4))
        elif self.io_dict["in"]["input_inp_path"] and not self.cp2k_in:
            final_dict = self.inp_in
            #print(json.dumps(final_dict,indent=4))
        elif self.cp2k_in and not self.io_dict["in"]["input_inp_path"]:
            final_dict = self.cp2k_in
            #print(json.dumps(final_dict,indent=4))
        else:
            print ("HOUSTON....")

        if self.io_dict["in"]["input_rst_path"]:
            #new_dict={'FORCE_EVAL':{'DFT':{'WFN_RESTART_FILE_NAME': os.path.abspath(self.io_dict["in"]["input_rst_path"]), 'SCF' : {'SCF_GUESS':'RESTART'}}}}
            new_dict={'FORCE_EVAL':{'DFT':{'WFN_RESTART_FILE_NAME': Path(self.io_dict["in"]["input_rst_path"]).resolve(), 'SCF' : {'SCF_GUESS':'RESTART'}}}}
            self.update(final_dict, new_dict)
            #print(json.dumps(final_dict,indent=4))

        final_dict2 = final_dict
        if self.io_dict["in"]["input_pdb_path"]:
            final_dict2 = self.replace_coords(final_dict,coord)

        #print(json.dumps(final_dict,indent=4))

        with open(self.io_dict["out"]["output_inp_path"], 'w') as cp2k_out_fh:
            self.iterdict(final_dict2,0,cp2k_out_fh)

        self.tmp_files.extend([
            self.stage_io_dict.get("unique_dir")
        ])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)

        return 0

def cp2k_prep(output_inp_path: str,
            input_inp_path: str = None, input_pdb_path: str = None, input_rst_path: str = None,
            properties: dict = None, **kwargs) -> int:
    """Create :class:`Cp2kPrep <cp2k.cp2k_prep.Cp2kPrep>`cp2k.cp2k_prep.Cp2kPrep class and
    execute :meth:`launch() <cp2k.cp2k_prep.Cp2kPrep.launch>` method"""

    return Cp2kPrep( input_inp_path=input_inp_path,
                    input_pdb_path=input_pdb_path,
                    input_rst_path=input_rst_path,
                    output_inp_path=output_inp_path,
                    properties=properties).launch()

def main():
    parser = argparse.ArgumentParser(description='Prepares input files for the CP2K QM tool.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--output_inp_path', required=True, help='Output CP2K input inp file. Accepted formats: inp, in, txt.')
    parser.add_argument('--input_inp_path', required=False, help='Input configuration file (QM options) (CP2K inp). Accepted formats: inp, in, txt.')
    parser.add_argument('--input_pdb_path', required=False, help='Input PDB file. Accepted formats: pdb.')
    parser.add_argument('--input_rst_path', required=False, help='Input Restart file (WFN). Accepted formats: wfn.')

    args = parser.parse_args()
    #config = args.config if args.config else None
    args.config = args.config or "{}"
    #properties = settings.ConfReader(config=config).get_prop_dic()
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call
    cp2k_prep(      input_inp_path=args.input_inp_path,
                    input_pdb_path=args.input_pdb_path,
                    input_rst_path=args.input_rst_path,
                    output_inp_path=args.output_inp_path,
                    properties=properties)

if __name__ == '__main__':
    main()
