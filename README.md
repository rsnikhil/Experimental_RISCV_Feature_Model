# RIFFL: RISC-V Formal Feature List

RIFFL is an experimental DSL to formally describe the full feature set
of a RISC-V implementation.  Typical use-cases:

- In RISC-V Compliance Testing: when testing an implementation's
    compliance with the RISC-V specification, we compare the
    implementation's execution to the execution of a "Golden Reference
    Model" (an executable Formal ISA Spec, or a reference simulator).
    That Golden Reference Model is usually a "universal" simulator
    that can model any RISC-V system, and needs to be constrained to
    the specific set of features in the given implementation.

- In RISC-V system software configuration: system software needs to
    know the particular features of the platorm on which it is to run.

[ See also some presentation slides in `Formal_Feature_Model.pdf` ]

----------------------------------------------------------------
## Overview

### Flow

A RISC-V implementation is characterized by a Feature List, i.e., a
list of Feature Values that it supports.  This Feature List is
provided by the implementor in a [YAML](http://yaml.org) file, which
is a standard notation that can be used for lists of name-value pairs.
See the 'Examples' directory for examples.

`RIFFL_Check` is a Python program provided in this repo. Its input is
a Feature List (YAML file) provided by the implementor (say,
`foo.yaml`).  It checks the given feature list for consistency (about
which more below). If consistent, it outputs `foo_checked.yaml` which
contains the features in `foo.yaml` plus any features that were
omitted and took on default values.

`foo_checked.yaml` can then be provided as an input to various tools
such Golden Models, universal simulators and system/platform
configurators to configure them to support _exactly_ the specified
features.

Features in `foo.yaml` that are not recognized by `RIFFL_Check` are
passed through as-is and without checking (these are typically highly
implementation-specific).

Implementors may wish to extend `src/RIFFL_Decls.py` here to support
additional features specific to their implementation.

### Feature Values and Feature Lists

A Feature Value is a name:value pair.  Examples:

        XLEN: 32                               # For RV32
        Extn_C: False                          # no compressed instructions
        Extn_A: True                           # Atomic memory ops
        Extn_S: True                           # Supervisor privilege
        Sv39: True                             # Sv39 virtual memory scheme
        Traps_on_unaligned_mem_access: True
        LR_SC_grain: 64                        # Block byte size

As these examples demonstrate, features include both general RISC-V
options and highly implementation-specific options.


#### Feature Value Defaults

Some features _must_ be specified by the implementor, and some
features can be omitted, to take on default values.

In `RIFFL_Constraints.py`, each feature's declaration has a `default`
field.  This is either `None`, indicating that the feature must be
specified, or a specific value.

### Feature Constraints

The value of every feature must satisfy a *constraint*, which is a
predicate (Boolean-valued expression) on acceptable values.  The
constraint may not only constrain the data type (Boolean, string,
integer, address-map, WARL-function, ...), but may also express
dependencies on other features.  For example, `Sv39:True` is only
meaningful when `XLEN:64` is specified.

----------------------------------------------------------------
## This repository

In this repo you will find:

- `src/RIFFL_Decls.py` (Python source file): a 
    specification of all standard features, their defaults and their
    constraints (allowed values, preconditions, dependence on other
    features, etc.).

    The notation is very declarative.  Implementors may wish to add
    declarations for features specific to their
    implementation/environment.

- `Examples/` (directory): Several example input YAML files.

See also some presentation slides in `Formal_Feature_Model.pdf`

If you are only reading, then the above files are enough.

### Execution

The repo also contain executable Python file `src/RIFFL_Check.py`.  Make
sure your installation has:

- Python 3.5 or 3.6 (this code has been tested on Python 3.5.3 and 3.6.5).
- The `python3-yaml` library (used by `RIFFL_Check.py` to read/write yaml files)

Then, you can execute like this:

        $ src/RIFFL_Check.py    <feature_list_file (foo.yaml)>    <optional verbosity of 1, 2, ..>

        $ make demo    will do the above on Examples/eg1.yaml

This will:

 - read the YAML file (`foo.yaml`, say),
 - separate the constraints into known (declared in `RISCV_Feature_Types`) and unknown features,
 - check all constraints on known features and print diagnostics
 - if the constraints were consistent, write out `foo_checked.yaml` containing:
     - known features given in `foo.yaml`
     - known features omitted in `foo.yaml` that took on default values
     - unknown features in `foo.yaml`, passed through as is.

   These output file can be read by a formal ISA spec or universal
   simulator to contrain its behavior.
