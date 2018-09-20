# RIFFL: RISC-V Formal Feature List

RIFFL is an experimental DSL to formally describe the full feature set
of a RISC-V implementation.  A typical use-cases:

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
implementation-specific).  Implementors may wish to extend the code
here to support their additional features.

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

- `src/RIFFL_Decls.py` (Python source file): a specification of all
    possible features and their constraints (allowed values,
    preconditions, dependence on other features, etc.).  Please read
    the extensive comments in the file for how feature types are
    represented, and semantics, and peruse the feature types to see
    how preconditions, constraints and defaults are expressed.

    Note: currently contains many but not all features.

- `Examples/` (directory): Several example input YAML files.

See also some presentation slides in `Formal_Feature_Model.pdf`

If you are only reading, then the above files are enough.

### Execution

The repo also contains Python files `Main.py` and
`Constraint_Check.py` using which you can execute.  Make sure your
installation has:

- Python 3.5 or 3.6
- The `python3-yaml` library.

Then, you can execute like this:

        $ ./Main.py  <feature_list_file (foo.yaml)>    <optional verbosity of 1, 2, ..>

        $ make demo    will do the above on Examples/eg1.yaml

This will:

 - read the YAML file,
 - separate the constraints into standard (present in `RISCV_Feature_Types`) and non-standard features,
 - check all constraints (on standard features)
 - write out two files:
     - `foo_std.yaml` which "completes" the given standard features with all defaults
     - `foo_nonstd.yam` which contains all the non-standard features (as-is from the input).

   These latter two files can be read by a formal ISA spec or universal
   simulator to contrain its behavior.

This has been tested on Python 3.5.3 and 3.6.5.
