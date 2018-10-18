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
"    - features and values omitted in the input that have default values, and\n" \
"    - features and values from the input that were not recognized (passed through as-is).\n"

# ================================================================
# Imports of Python libraries

import sys
import os
import yaml
import pprint

# ================================================================
# Imports of project files

import RIFFL_Decls as RD

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
    output_feature_filename    = filename + "_checked"    + ext

    # Set verbosity if requested
    verbosity = 0
    if (len (argv) == 3):
        verbosity = int (argv [2])

    # List all feature decls if verbose
    if (verbosity > 1):
        sys.stdout.write ("All feature decls:\n")
        for fdecl in RD.fdecls:
            print_fdecl (fdecl)
        sys.stdout.write ("End of all feature specs\n")

    # Split input features into known and unknown features (and convert from dict to list)
    (known_features, unknown_features) = split_known_and_unknown (RD.fdecls, feature_dict)

    # Echo feature list, for info
    if (len (known_features) > 0):
        print ("Known features in input ----------------")
        for (fname, fval) in known_features:
            sys.stdout.write ("  {0}:".format (fname))
            pprint_at_indent (sys.stdout, fval, 4)
    if (len (unknown_features) > 0):
        print ("Unknown features in input ----------------")
        for (fname, fval) in unknown_features:
            sys.stdout.write ("  {0}:".format (fname))
            pprint_at_indent (sys.stdout, fval, 4)

    # Check ALL fdecls constraints on known features
    sys.stdout.write ("---------------- Checking all constraints\n")
    (all_pass, known_features_out) = check_all_constraints (verbosity, RD.fdecls, known_features)

    sys.exit (0)    # DELETE

    # If constraints met, write output file (input feature list + defaulted features)
    if all_pass:
        sys.stdout.write ("---------------- All constraints ok: writing output file '{0}'\n".
                          format (output_feature_filename))

        # Split known_features_out into the ones provided in known_features and the rest (i.e., defaults)
        (given_features_out, default_features_out) = split_given_and_defaults (known_features, known_features_out)

        with open (output_feature_filename, 'w') as stream:
            sys.stdout.write ("Writing {0} known features\n".format (len (given_features_out)))
            write_output_features (stream, given_features_out, "Known features")

            if (len (default_features_out) > 0):
                sys.stdout.write ("Writing {0} known default features\n".format (len (default_features_out)))
                write_output_features (stream, default_features_out, "Known default features")

            if (len (unknown_features) > 0):
                sys.stdout.write ("Writing {0} unknown features\n".format (len (unknown_features)))
                write_output_features (stream, unknown_features, "Unknown features")

        if verbosity > 0:
            write_output_features (sys.stdout,  known_features_out, "Known features")
            write_output_features (sys.stdout,  unknown_features, "Unknown features")

    return 0

def write_output_features (stream, features, title):
    stream.write ("\n\n# ---------------- {0} ----------------\n\n".format (title))
    for (name, val) in features:
        if (type (val) == str) or (type (val) == bool) or (type (val) == list):
            stream.write ("{0}: '{1}'\n".format (name, val))
        elif type (val) == int:
            stream.write ("{0}: {1}\n".format (name, val))
        else:
            stream.write ("'{0}':\n".format (name))
            pprint_at_indent (stream, val, 4)
    
# ================================================================
# Split a dict of features into two lists: known and unkown features
# based on membership (or not) in feature decls

def split_known_and_unknown (fdecls, feature_dict):
    known   = []
    unknown = []
    for name in iter (feature_dict.keys()):
        val = feature_dict [name]
        fs = select_fdecl (fdecls, name)
        if fs == None:
            unknown.append ((name, val))
        else:
            known.append ((name, val))
    return (known, unknown)

# ================================================================
# Split feature flist2 into those that are present in flist1
# and those that were not (and are therefore defaults)

def split_given_and_defaults (flist1, flist2):
    given    = []
    defaults = []
    for (name,val) in flist2:
        e = select_fval (flist1, name)
        if e != None:
            given.append ((name, val))
        else:
            defaults.append ((name, val))
    return (given, defaults)

# ****************************************************************
# ****************************************************************
# ****************************************************************
# RISC-V feature list constraint checker

# ================================================================
# These selectors encapsulate the representation of fdecls as 5-tuples.

def fdecl_name       (fdecl): return fdecl [0]
def fdecl_descr      (fdecl): return fdecl [1]
def fdecl_default    (fdecl): return fdecl [2]
def fdecl_preconds   (fdecl): return fdecl [3]
def fdecl_constraint (fdecl): return fdecl [4]

# ================================================================
# Check all constraints

#     'fdecls': feature decl list
#     'flist':  feature list

# Iterate over 'fdecls', checking each one's preconds and constraints.
# Returns a boolean ('all constraints met')
# and a full feature list (original feature plus omitted defaults)

def check_all_constraints (verbosity, fdecls, features):
    n_constraints = 0
    n_pass        = 0
    features_out  = []
    for fdecl in fdecls:
        n_constraints = n_constraints + 1
        (ok, feature_out) = check_fdecl_constraint (verbosity, fdecls, features, fdecl)
        if ok:
            n_pass = n_pass + 1
            if feature_out != None:
                features_out.append (feature_out)

    print ("Num constraints checked {0}; pass {1}; fail {2}".format (n_constraints, n_pass, n_constraints - n_pass))
    all_pass = (n_pass == n_constraints)
    return (all_pass, features_out)

# ================================================================
# Check the constraint on a particular feature decl

#     'fdecls': feature decl list
#     'flist':  feature list
#     'fdecl':  feature decl whose default/precond/constraint we are currently eval'ing

def check_fdecl_constraint (verbosity, fdecls, flist, fdecl):
    if (verbosity > 0):
        sys.stdout.write ("Checking fdecl\n")
        print_fdecl (fdecl)

    prefix = ""

    # Eval this feature's value from flist
    v = eval (verbosity, prefix, fdecls, flist, fdecl, "$this")
    debug_print (verbosity, "Feature value: {0}\n".format (v))

    # Check if all preconds of this fdecl are True (i.e., is it relevant?)
    # Collect all the False preconds, for informative message
    false_preconds = []
    preconds = True
    for precond in fdecl_preconds (fdecl):
        debug_print (verbosity, "---- Checking precondition:\n")
        if (verbosity > 0): pprint.pprint (precond, indent = 4)

        precond_v = eval (verbosity, prefix, fdecls, flist, fdecl, precond)

        if precond_v:
            debug_print (verbosity, "Precondition is TRUE\n")
        else:
            debug_print (verbosity, "Precondition is FALSE\n")
            preconds = False
            false_preconds.append (precond)

    # Check if constraint of this fdecl is True
    # If so, collect this feature-out
    constraint  = fdecl_constraint (fdecl)
    feature_out = None
    debug_print (verbosity, "---- Checking constraint:")
    if (verbosity > 0): pprint.pprint (constraint, indent = 4)
    if preconds:
        x           = eval (verbosity, prefix, fdecls, flist, fdecl, constraint)
        feature_out = (fdecl_name (fdecl), v)
        if x:
            debug_print (verbosity, "Constraint evaluates TRUE\n")
        else:
            sys.stdout.write ("Constraint evaluates FALSE for fdecl '{0}' ({1})\n".format (fdecl_name (fdecl),
                                                                                           fdecl_descr (fdecl)))
            sys.stdout.write ("  Feature value is {0}\n".format (v))
            sys.stdout.write ("  Constraint is: ")
            pprint.pprint (fdecl_constraint (fdecl), indent = 4)

    else:
        x = True
        debug_print (verbosity, "Constraint trivially TRUE\n")

        v1 = select_fval (flist, fdecl_name (fdecl))
        if v1 != None:
            sys.stdout.write ("Feature '{0}':{1}    is not relevant\n".format (fdecl_name (fdecl), v1))
            sys.stdout.write ("  The following preconditions are false\n")
            for precond in false_preconds:
                pprint_at_indent (sys.stdout, precond, 4)

    return (x, feature_out)

# ================================================================
# Eval-Apply

# Eval expression 'e' in context of 'fdecls', 'flist', 'fdecl'
#     'fdecls': feature decl list
#     'flist':  feature list
#     'fdecl':  feature decl whose default/precond/constraint we are currently eval'ing

def eval (verbosity, prefix, fdecls, flist, fdecl, e):
    debug_trace (verbosity, prefix + "==> Eval ", e)
    prefix_ret  = prefix + "<== Eval "
    prefix_next = prefix + "    "

    # Leaf term: Special variable '$this' (value of current feature)
    if e == "$this":
        fname  = fdecl_name (fdecl)
        v_expr = select_fval (flist, fname)
        if (v_expr == None):
            v_expr = fdecl_default (fdecl)
        v = eval (verbosity, prefix_next, fdecls, flist, fdecl, v_expr)
        return debug_trace (verbosity, prefix_ret, v)

    # Leaf term: Special variable '$max_XLEN' (max unsigned integer of width XLEN)
    if e == "$max_XLEN":
        v = select_fval (flist, "XLEN")
        if (v == None):
            sys.stderr.write ("ERROR: evaluating '$max_XLEN': XLEN has not been specified\n")
            sys.exit (1)
        if (v == 32):
            return debug_trace (verbosity, prefix_ret, 0xFFFFFFFF)
        elif (v == 64):
            return debug_trace (verbosity, prefix_ret, 0xFFFFFFFFFFFFFFFF)
        else:
            sys.stderr.write ("ERROR: evaluating '$max_XLEN': XLEN ({0}) is not 32 or 64\n".format (v))
            sys.exit (1)

    # Leaf term: Special variable '$<feature>'

    if (type (e) == str) and e.startswith ('$'):
        fname_x  = e [1:]
        v_expr_x = select_fval (flist, fname_x)
        if (v_expr_x == None):
            fdecl_x = select_fdecl (fdecls, fname_x)
            v_expr_x = fdecl_default (fdecl_x)
        result = eval (verbosity, prefix_next, fdecls, flist, fdecl, v_expr_x)
        return debug_trace (verbosity, prefix_ret, result)

    if e == "True":  return debug_trace (verbosity, prefix_ret, True)
    if e == "False":  return debug_trace (verbosity, prefix_ret, False)

    # Leaf term: Constants
    if e == None:        return debug_trace (verbosity, prefix_ret, e)
    if type (e) == int:  return debug_trace (verbosity, prefix_ret, e)
    if type (e) == str:  return debug_trace (verbosity, prefix_ret, e)
    if type (e) == bool: return debug_trace (verbosity, prefix_ret, e)

    # Assertion check that it's not a leaf term
    if type (e) != list:
        sys.stderr.write ("INTERNAL ERROR: unknown form of expression\n")
        pprint.pprint (e, indent = 4)
        sys.exit (1)

    op = e [0]
    e_args = e [1:]

    if op == "If":
        v_cond = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_args [0])
        if v_cond == True:
            v1 = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_args [1])
            return debug_trace (verbosity, prefix_ret, v1)
        else:
            v2 = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_args [2])
            return debug_trace (verbosity, prefix_ret, v2)

    if op in ["||"]:
        result = False
        for e_arg in e_args:
            result = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_arg)
            if result: break
        return debug_trace (verbosity, prefix_ret, result)

    if op in ["&&"]:
        result = True
        for e_arg in e_args:
            result = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_arg)
            if not result: break
        return debug_trace (verbosity, prefix_ret, result)

    if op.upper() == "LIST":
        result = []
        for e_arg in e_args:
            result_j = eval (verbosity, prefix_next, fdecls, flist, fdecl, e_arg)
            result.append (result_j)
        return debug_trace (verbosity, prefix_ret, result)

    if op == "Address_map":
        result = e
        return debug_trace (verbosity, prefix_ret, result)

    if op == "WARL_fn":
        return debug_trace (verbosity, prefix_ret, e)

    # Ordinary application: eval args, apply op to args
    v_args = [eval (verbosity, prefix_next, fdecls, flist, fdecl, e_arg) for e_arg in e_args]
    return apply (verbosity, prefix, fdecls, flist, fdecl, op, v_args)

# Apply 'op' to 'v_args' in context of 'fdecls', 'flist', 'fdecl'

def apply (verbosity, prefix, fdecls, flist, fdecl, op, v_args):
    debug_trace (verbosity, prefix + "    Apply: " + op + " ", v_args)
    prefix_next = prefix + "    "

    if   op == "Is_bool":        result = (type (v_args [0]) == bool)
    elif op == "Is_int":         result = (type (v_args [0]) == int)
    elif op == "Is_string":      result = (type (v_args [0]) == str)
    elif op == "Is_address_map": result = is_address_map (v_args [0])
    elif op == "Are_hartids":    result = are_hartids (v_args [0])

    elif op == "~":              result = (~ v_args [0])
    elif op == "&":              result = (v_args [0] &  v_args [1])
    elif op == "|":              result = (v_args [0] |  v_args [1])
    elif op == "^":              result = (v_args [0] ^  v_args [1])

    elif op == "!=":             result = (v_args [0] != v_args [1])
    elif op == "==":             result = (v_args [0] == v_args [1])

    elif op == "<":              result = (v_args [0] <  v_args [1])
    elif op == "<=":             result = (v_args [0] <= v_args [1])
    elif op == ">":              result = (v_args [0] >= v_args [1])
    elif op == ">=":             result = (v_args [0] >  v_args [1])

    elif op == "+":              result = (v_args [0] +  v_args [1])
    elif op == "-":              result = (v_args [0] -  v_args [1])
    elif op == "neg":            result = (0 - v_args [0])

    elif op == "not":            result = (not v_args [0])

    elif op == "In":             result = (v_args [0] in  v_args [1])
    elif op == "Range":          result = range (v_args [0], v_args [1])
    elif op == "Is_power_of_2":  result = is_power_of_2 (v_args [0])

    elif op == "XLEN_code":      result = XLEN_code (v_args [0])

    elif op == "Is_WARL_fn":  result = is_WARL_fn (verbosity, v_args [0], v_args [1])

    else:
        sys.stderr.write ("ERROR: unknown form of expression\n")
        pprint.pprint ([op] + v_args, indent = 4)
        sys.exit (1)

    return debug_trace (verbosity, prefix, result)

# ----------------------------------------------------------------
# is_address_map: xs must be
# - non-empty list of 5-lists (base:int, size:int, addr_type:str, addr_ops:str, description:str)
# - base and sizes are all positive
# - addr_type is string MEM or IO
# - addr_ops  is string RO, RW or WO
# - addr ranges are disjoint

def is_address_map (xs):
    if (xs == None):
        return False
    else:
        # TODO: see above checks
        return True

# ----------------------------------------------------------------
# xs must be a non-empty list of increasing (not necessarily contiguous) integers starting with 0

def are_hartids (xs):
    if xs == []: return False
    if xs [0] != 0: return False
    last_x = xs [0]
    for x in xs [1:]:
        if last_x >= x : return False
        last_x = x
    return True

# ----------------------------------------------------------------

def XLEN_code (xlen):
    if xlen == 32:
        return 1
    elif xlen == 64:
        return 2
    elif xlen == 128:
        return 3
    else:
        return 0

# ----------------------------------------------------------------
# Checks that y is a legal WARL_fn for field x
# TODO: this needs to be fleshed out for all the different WARL fields

def is_WARL_fn (verbosity, x, y):
    if (verbosity > 0):
        sys.stdout.write ("TODO: check legality of WARL_fn for {0}\n".format (x))
        pprint_at_indent (sys.stdout, y, 8)
    return True

# ----------------------------------------------------------------
# x must be a power of 2 (has exactly 1 bit set)

def is_power_of_2 (x):
    if x == 0: return False

    # Shift out zero lsbs
    while (x & 0x1 == 0):
        x = x >> 1

    # Shift out the non-zero lsb (which should be the only non-zero bit)
    x = x >> 1

    # The remaining bits should be 0
    return (x == 0)

# ================================================================
# Select feature decl with given name from list of feature decls

def select_fdecl (fdecls, name):
    fdecls1 = [fdecl for fdecl in fdecls if fdecl_name (fdecl) == name]
    if len (fdecls1) == 0:
        return None
    elif len (fdecls1) == 1:
        return fdecls1 [0]
    else:
        print ("INTERNAL ERROR: more than one feature decl with this name:", name)
        for fdecl in fdecls1:
            print ("    ", fdecl)

# ================================================================
# Select value of feature with 'fname' from feature list, if present;
# else return None

def select_fval (flist, fname):
    # DEBUG: sys.stdout.write ("select_fval {0} from ".format (fname)); print (flist)

    flist1 = [val for (n,val) in flist if (fname == n) ]

    if len (flist1) == 0:
        result = None
    elif len (flist1) == 1:
        result = flist1 [0]
    else:
        sys.stderr.write ("ERROR: feature list has duplicate entry for feature {0}\n".format (fname))
        pprint_at_indent (sys.stderr, flist, 4)
        sys.exit (1)

    # sys.stdout.write ("select_fval <= ".format (fname)); print (result)
    return result

# ================================================================

def debug_print (verbosity, s):
    if verbosity > 0: sys.stdout.write (s)

def debug_trace (verbosity, prefix, e):
    if (verbosity > 1):
        sys.stdout.write (prefix); print (e)    
    return e

def print_fdecl (fdecl):
    sys.stdout.write ("Feature Constraint\n")
    sys.stdout.write ("  Feature: {0}\n".format (fdecl_name (fdecl)))
    sys.stdout.write ("  Descr: {0}\n".format (fdecl_descr (fdecl)))
    sys.stdout.write ("  Default:\n")
    pprint_at_indent (sys.stdout, fdecl_default (fdecl), 4)
    sys.stdout.write ("  Preconds:\n")
    for precond in fdecl_preconds (fdecl):
        pprint_at_indent (sys.stdout, precond, 4)
    sys.stdout.write ("  Constraint:\n")
    pprint_at_indent (sys.stdout, fdecl_constraint (fdecl), 4)

def pprint_at_indent (stream, x, indent_n):
    s = pprint.pformat (x, indent = indent_n)
    for line in s.splitlines ():
        stream.write ("        {0}\n".format (line))

# ****************************************************************
# ****************************************************************
# ****************************************************************

# For non-interactive invocations, call main() and use its return value
# as the exit code.

if __name__ == '__main__':
  sys.exit (main (sys.argv))
