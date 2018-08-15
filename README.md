# Experimental Feature Model for RISC-V

This is an experimental exploration of a DSL to describe formally the
full feature set of a RISC-V implementation.  A typical use-case would
be to restrict a general RISC-V formal model or a "universal" RISC-V
simulator (such as Qemu or Imperas' simulator) to behave like some
particular implementation (e.g., to check the implementation's
compliance with the RISC-V specs).

This is not a formal proposal for a feature model (although it could
be developed into one if there is consensus); it is more intended to
provoke discussion and set a baseline for the expressive power of such
a DSL.  In particular, we're using Python here only for
quick-and-dirty experimentation.

"Features" include both general options and implementation-specific
options such as:

- RV32 vs RV64
- Optional ISA extensions such as M, A, C, F, D, ...
- Optional privilege levels such as U and S
- Implementation options such as support for misaligned memory accesses
- What actually gets written to a CSR WARL field on a CSR write

In this repo you will find:

- `RISCV_Feature_Types.py`: a specification of all possible features
    and their constraints (allowed values, preconditions, dependence
    on other features, etc.).  Please read the extensive comments in
    the file for how feature types are represented, and semantics, and
    peruse the feature types to see how preconditions, constraints and
    defaults are expressed.

    Note: currently contains many but not all features.

- `RV32IMU.yaml` and `RV64IMAUS.yaml`: two sample particular feature lists
    for two particular implementations.

See also some presentation slides in `Formal_Feature_Model.pdf`

If you are only reading, then the above files are enough.

----------------------------------------------------------------

The repo also contains Python files `Main.py` and
`Constraint_Check.py` using which you can execute.  Make sure your
installation has:

- Python 3.5 or 3.6
- The `python3-yaml` library.

Then, you can execute like this:

        ./Main.py  RV32IMU.yaml    <optional verbosity of 1, 2, ..>

This will:

 - read the YAML file,
 - separate the constraints into standard (present in `RISCV_Feature_Types`) and non-standard features,
 - check all constraints (on standard features)
 - write out two files:
     - `RV32IMU_std.yaml` which "completes" the given standard features with all defaults
     - `RV32IMU_nonstd.yam` which contains all the non-standard features (as-is from the input).

   These latter two files can be read by a formal ISA spec or universal
   simulator to contrain its behavior.

This has been tested on Python 3.5.3 and 3.6.5.
