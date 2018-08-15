#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil

# ================================================================

usage_line = \
"Usage:    CMD    <feature_list.yaml>  <optional_verbosity>\n"

help_lines = \
"  Reads a YAML file containing a feature-list for a RISC-V implementation\n" \
"  and checks for consistency.\n" \
"  If consistent, writes an output feature-list to a YAML file consisting of\n" \
"    - features and values from the input for known features, and\n" \
"    - relevant features that were not in the input, with their default values.\n" \
"  Unknown features in the input are omitted.\n"

# ================================================================
# Imports of Python libraries

import sys
import os
import yaml
import pprint

# ================================================================
# Imports of project files

import RISCV_Feature_Types as RFT
import Constraint_Check    as CC

# ================================================================

def main (argv = None):
    sys.stdout.write ("Use --help or -h for help\n")

    if ((len (argv) == 1) or
        (argv [1] == "--help") or (argv [1] == "-h") or
        ((len (argv) != 2) and (len (argv) != 3))):

        sys.stdout.write (usage_line.replace ("CMD", argv [0]))
        sys.stdout.write ("\n")
        sys.stdout.write (help_lines.replace ("CMD", argv [0]))
        sys.stdout.write ("\n")
        return 0

    # Read input feature list from YAML file
    with open (argv [1], 'r') as stream:
        try:
            feature_dict = yaml.load (stream)

        except yaml.YAMLError as exc:
            sys.stdout.write ("ERROR: unable to open YAML input file: {0}\n".format (argv [1]))
            sys.stdout.write ("    Exception: "); print (exc)
            return 0
    (filename, ext) = os.path.splitext (argv [1])
    std_feature_filename    = filename + "_std"    + ext
    nonstd_feature_filename = filename + "_nonstd" + ext

    # Set verbosity if requested
    verbosity = 0
    if (len (argv) == 3):
        verbosity = int (argv [2])

    # Echo feature list, for info
    print ("---------------- Input features:")
    pprint.pprint (feature_dict, indent=4)

    # List all feature types if verbose
    if (verbosity > 1):
        sys.stdout.write ("All feature types:\n")
        for ftype in RFT.ftypes:
            print ("----------------")
            print (RFT.ftype_name (ftype), ": default ", RFT.ftype_default (ftype), "    # ", RFT.ftype_descr (ftype))
            pprint.pprint (RFT.ftype_constraint (ftype), indent=4)
        sys.stdout.write ("End of all feature specs\n")

    # Split input features into standard and non-standard features (and convert from dict to list)
    (std_features, nonstd_features) = CC.split_std_and_nonstd (RFT.ftypes, feature_dict)

    # Check ALL constraints
    sys.stdout.write ("---------------- Checking all constraints\n")
    (all_pass, std_features_out) = CC.check_all_constraints (verbosity, RFT.ftypes, std_features)

    # If constraints met, write out augmented feature list
    if all_pass:
        sys.stdout.write ("---------------- All constraints ok: writing output files\n")

        sys.stdout.write ("Writing {0} standard features to: {1}\n".format (len (std_features_out),
                                                                            std_feature_filename))
        with open (std_feature_filename, 'w') as stream:
            write_output_features (stream, std_features_out, "Standard features")

        sys.stdout.write ("Writing {0} non-standard features to: {1}\n".format (len (nonstd_features),
                                                                                nonstd_feature_filename))
        with open (nonstd_feature_filename, 'w') as stream:
            write_output_features (stream, nonstd_features, "Non-standard features")

        if verbosity > 0:
            write_output_features (sys.stdout,  std_features_out, "Standard features")
            write_output_features (sys.stdout,  nonstd_features, "Non-standard features")

    return 0

def write_output_features (stream, features, title):
    stream.write ("# ---------------- {0}\n".format (title))
    for (name, val) in features:
        if (type (val) == str) or (type (val) == bool) or (type (val) == list):
            stream.write ("{0}: '{1}'\n".format (name, val))
        elif type (val) == int:
            stream.write ("{0}: {1}\n".format (name, val))
        else:
            stream.write ("'{0}':\n".format (name))
            CC.pprint_at_indent (stream, val, 4)
    
# ================================================================
# For non-interactive invocations, call main() and use its return value
# as the exit code.
if __name__ == '__main__':
  sys.exit (main (sys.argv))
