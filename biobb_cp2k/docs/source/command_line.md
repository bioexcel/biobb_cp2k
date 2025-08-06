# BioBB CP2K Command Line Help
Generic usage:
```python
biobb_command [-h] --config CONFIG --input_file(s) <input_file(s)> --output_file <output_file>
```
-----------------


## Cp2k_prep
Helper bb to prepare inputs for the CP2K QM tool module.
### Get help
Command:
```python
cp2k_prep -h
```
    usage: cp2k_prep [-h] [--config CONFIG] --output_inp_path OUTPUT_INP_PATH [--input_inp_path INPUT_INP_PATH] [--input_pdb_path INPUT_PDB_PATH] [--input_rst_path INPUT_RST_PATH]
    
    Prepares input files for the CP2K QM tool.
    
    options:
      -h, --help            show this help message and exit
      --config CONFIG       Configuration file
      --input_inp_path INPUT_INP_PATH
                            Input configuration file (QM options) (CP2K inp). Accepted formats: inp, in, txt.
      --input_pdb_path INPUT_PDB_PATH
                            Input PDB file. Accepted formats: pdb.
      --input_rst_path INPUT_RST_PATH
                            Input Restart file (WFN). Accepted formats: wfn.
    
    required arguments:
      --output_inp_path OUTPUT_INP_PATH
                            Output CP2K input inp file. Accepted formats: inp, in, txt.
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_inp_path** (*string*): Input configuration file (CP2K run options). File type: input. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp). Accepted formats: PDB
* **input_pdb_path** (*string*): Input PDB file. File type: input. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/H2O_box.pdb). Accepted formats: PDB
* **input_rst_path** (*string*): Input restart file (WFN). File type: input. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k.wfn). Accepted formats: WFN
* **output_inp_path** (*string*): Output CP2K input configuration file. File type: output. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_prep_out.inp). Accepted formats: INP, IN, TXT
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **simulation_type** (*string*): (energy) Default options for the cp2k_in file. Each creates a different inp file. .
* **cp2k_in** (*object*): ({}) CP2K run options specification..
* **cell_cutoff** (*number*): (5.0) CP2K cell cutoff, to build the cell around the system (only used if input_pdb_path is defined)..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
* **sandbox_path** (*string*): (./) Parent path to the sandbox directory..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_cp2k/blob/master/biobb_cp2k/test/data/config/config_cp2k_prep.yml)
```python
properties:
  simulation_type: energy

```
#### Command line
```python
cp2k_prep --config config_cp2k_prep.yml --input_inp_path cp2k_energy.inp --input_pdb_path H2O_box.pdb --input_rst_path cp2k.wfn --output_inp_path cp2k_prep_out.inp
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_cp2k/blob/master/biobb_cp2k/test/data/config/config_cp2k_prep.json)
```python
{
  "properties": {
    "simulation_type": "energy"
  }
}
```
#### Command line
```python
cp2k_prep --config config_cp2k_prep.json --input_inp_path cp2k_energy.inp --input_pdb_path H2O_box.pdb --input_rst_path cp2k.wfn --output_inp_path cp2k_prep_out.inp
```

## Cp2k_run
Wrapper of the CP2K QM tool module.
### Get help
Command:
```python
cp2k_run -h
```
    usage: cp2k_run [-h] [--config CONFIG] --input_inp_path INPUT_INP_PATH --output_log_path OUTPUT_LOG_PATH --output_outzip_path OUTPUT_OUTZIP_PATH --output_rst_path OUTPUT_RST_PATH
    
    Running atomistic simulations of solid state, liquid, molecular, periodic, material, crystal, and biological systems using CP2K QM tool.
    
    options:
      -h, --help            show this help message and exit
      --config CONFIG       Configuration file
    
    required arguments:
      --input_inp_path INPUT_INP_PATH
                            Input configuration file (QM run options). Accepted formats: inp, in, txt.
      --output_log_path OUTPUT_LOG_PATH
                            Output log file. Accepted formats: log, out, txt.
      --output_outzip_path OUTPUT_OUTZIP_PATH
                            Output trajectory file. Accepted formats: zip, gz, gzip.
      --output_rst_path OUTPUT_RST_PATH
                            Output restart file. Accepted formats: wfn.
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_inp_path** (*string*): Input configuration file (CP2K run options). File type: input. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp). Accepted formats: INP, IN, TXT, WFN
* **output_log_path** (*string*): Output log file. File type: output. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.log). Accepted formats: LOG, OUT, TXT, O
* **output_outzip_path** (*string*): Output files. File type: output. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.zip). Accepted formats: ZIP, GZIP, GZ
* **output_rst_path** (*string*): Output restart file. File type: output. [Sample file](https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.wfn). Accepted formats: WFN
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **binary_path** (*string*): (cp2k.sopt) CP2K binary path to be used..
* **param_path** (*string*): (None) Path to the CP2K parameter data files (BASIS_SET, POTENTIALS, etc.). If not provided, the parameter data files included in the package will be used..
* **mpi_bin** (*string*): (None) Path to the MPI runner. Usually "mpirun" or "srun"..
* **mpi_np** (*integer*): (0) Number of MPI processes. Usually an integer bigger than 1..
* **mpi_flags** (*string*): (None) Path to the MPI hostlist file..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
* **sandbox_path** (*string*): (./) Parent path to the sandbox directory..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_cp2k/blob/master/biobb_cp2k/test/data/config/config_cp2k_run.yml)
```python
properties:
  remove_tmp: true

```
#### Command line
```python
cp2k_run --config config_cp2k_run.yml --input_inp_path cp2k_energy.inp --output_log_path cp2k_run_out.log --output_outzip_path cp2k_run_out.zip --output_rst_path cp2k_run_out.wfn
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_cp2k/blob/master/biobb_cp2k/test/data/config/config_cp2k_run.json)
```python
{
  "properties": {
    "remove_tmp": true
  }
}
```
#### Command line
```python
cp2k_run --config config_cp2k_run.json --input_inp_path cp2k_energy.inp --output_log_path cp2k_run_out.log --output_outzip_path cp2k_run_out.zip --output_rst_path cp2k_run_out.wfn
```
