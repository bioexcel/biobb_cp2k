# Biobb CP2K changelog

## [Unreleased]

### Changes

* [FIX] `cp2k_prep`: with `input_rst_path` and a `cp2k_in` written in lower case (`force_eval`), the input file had two `&FORCE_EVAL` sections; the restart now goes into the existing one.
* [FIX] `cp2k_prep`: list values of `cp2k_in` (ie: the cell `abc`) now replace the ones of the template or of `input_inp_path`; they were ignored.
* [FIX] `cp2k_prep`: with `input_pdb_path`, the coordinates and the cell always reach the input file: the `FORCE_EVAL`, `SUBSYS` and `CELL` sections are created when the template or `cp2k_in` has none (the coordinates were dropped).
* [FIX] `cp2k_prep`: the `cp2k_in` property is no longer modified: the restart file and the PDB coordinates were written into it and reached the next call with the same properties.
* [UPDATE] `cp2k_prep`: its messages go to the log instead of the standard output.
* [FIX] `cp2k_run`: a relative `param_path` (relative to the current directory) works; CP2K runs in a temporary folder and did not find it.
* [REMOVE] `biobb_cp2k/utils/cp2k_cell.py` (`get_centroid()`), used by no block.

## What's new in version [5.3.0](https://github.com/bioexcel/biobb_amber/releases/tag/v5.3.0)?

### Changes

* [UPDATE] Update to biobb_common 5.3.1

## What's new in version [5.2.1](https://github.com/bioexcel/biobb_amber/releases/tag/v5.2.1)?

### Changes

* [UPDATE] Update to biobb_common 5.2.2

## What's new in version [5.2.0](https://github.com/bioexcel/biobb_amber/releases/tag/v5.2.0)?

### Changes

* [UPDATE] Update to biobb_common 5.2.0

## What's new in version [5.1.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v5.1.0)?

### Changes

* [UPDATE] Update to biobb_common 5.1.0

## What's new in version [5.0.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v5.0.0)?

### Changes

* [FEATURE](__init__): Importing submodules when a module is loaded
* [FEATURE] New sandbox_path property

## What's new in version [4.2.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v4.2.0)?
In version 4.2.0 the dependency biobb_common has been updated to 4.2.0 version.

### New features

* Update to biobb_common 4.2.0 (general)

## What's new in version [4.1.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v4.1.0)?
In version 4.1.0 the dependency biobb_common has been updated to 4.1.0 version.

### New features

* Update to biobb_common 4.1.0 (general)

## What's new in version [4.0.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v4.0.0)?
In version 4.0.0 the dependency biobb_common has been updated to 4.0.0 version.

### New features

* Update to biobb_common 4.0.0 (general)

## What's new in version [3.9.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v3.9.0)?
In version 3.9.0 the dependency biobb_common has been updated to 3.9.0 version.

### New features

* Update to biobb_common 3.9.0 (general)
* All inputs/outputs are checked for correct file format, extension and type (general)

## What's new in version [3.8.3](https://github.com/bioexcel/biobb_cp2k/releases/tag/v3.8.3)?
In the version 3.8.3 some bugs have been fixed.

### New features

* Bug fixes

## What's new in version [3.8.0](https://github.com/bioexcel/biobb_cp2k/releases/tag/v3.8.0)?
The version 3.8.0 is the first release of biobb_cp2k. There have been added the cp2k_prep and cp2k_run tools.

### New features

* First release
* CP2K module: cp2k_prep and cp2k_run tools