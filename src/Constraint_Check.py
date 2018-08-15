#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil

# ================================================================
# RISC-V feature list constraint checker

# ================================================================
# Imports of Python libraries

import sys
import pprint

# ================================================================
# Imports of project files

import RISCV_Feature_Types as RFT

# ================================================================
# Select feature type with given name from list of feature types

def select_ftype (ftypes, name):
    ftypes1 = [ftype for ftype in ftypes if RFT.ftype_name (ftype) == name]
    if len (ftypes1) == 0:
        return None
    elif len (ftypes1) == 1:
        return ftypes1 [0]
    else:
        print ("INTERNAL ERROR: more than one feature type with this name:", name)
        for ftype in ftypes1:
            print ("    ", ftype)

# ================================================================
# Split a feature list into standard and non-standard features
# i.e., membership (or not) in the list of feature types

def split_std_and_nonstd (ftypes, feature_dict):
    std = []
    nonstd = []
    for name in iter (feature_dict.keys()):
        val = feature_dict [name]
        fs = select_ftype (ftypes, name)
        if fs == None:
            nonstd.append ((name, val))
        else:
            std.append ((name, val))
    return (std, nonstd)

# ================================================================
# Check all constraints

# This iterates over all feature types (since the feature list may
# omit features, relying on defaults).
# Returns a boolean ('all constraints met') and a full feature list
# (original plus omitted defaults)

def check_all_constraints (verbosity, ftypes, features):
    n_constraints = 0
    n_pass        = 0
    features_out  = []
    for ftype in ftypes:
        n_constraints = n_constraints + 1
        (ok, feature_out) = check_ftype_constrint (verbosity, ftypes, features, ftype)
        if ok:
            n_pass = n_pass + 1
            if feature_out != None:
                features_out.append (feature_out)

    print ("Num constraints checked {0}; pass {1}; fail {2}".format (n_constraints, n_pass, n_constraints - n_pass))
    all_pass = (n_pass == n_constraints)
    return (all_pass, features_out)

# ================================================================
# Check the constraint on a particular feature type

def check_ftype_constrint (verbosity, ftypes, features, ftype):
    debug_print (verbosity, "================================\n")
    debug_print (verbosity, "Checking ftype {0}    {1}\n".format (RFT.ftype_name (ftype), RFT.ftype_descr (ftype)))

    prefix = ""

    default_val = eval (verbosity, ftypes, features, ftype, prefix, RFT.ftype_default (ftype))

    v = select_fval (features, RFT.ftype_name (ftype), default_val)
    debug_print (verbosity, "Feature value: {0}\n".format (v))

    false_preconds = []
    preconds = True
    for precond in RFT.ftype_preconds (ftype):
        debug_print (verbosity, "---- Checking precondition:\n")
        if (verbosity > 0): pprint.pprint (precond, indent = 4)

        precond_v = eval (verbosity, ftypes, features, ftype, prefix, precond)

        if precond_v:
            debug_print (verbosity, "Precondition is TRUE\n")
        else:
            debug_print (verbosity, "Precondition is FALSE\n")
            preconds = False
            false_preconds.append (precond)

    constraint  = RFT.ftype_constraint (ftype)
    feature_out = None
    debug_print (verbosity, "---- Checking constraint:")
    if (verbosity > 0): pprint.pprint (constraint, indent = 4)
    if preconds:
        x           = eval (verbosity, ftypes, features, ftype, prefix, constraint)
        feature_out = (RFT.ftype_name (ftype), v)
        if x:
            debug_print (verbosity, "Constraint evaluates TRUE\n")
        else:
            sys.stdout.write ("Constraint evaluates FALSE for ftype '{0}' ({1})\n".format (RFT.ftype_name (ftype),
                                                                                           RFT.ftype_descr (ftype)))
            sys.stdout.write ("  Feature value is {0}\n".format (v))
            sys.stdout.write ("  Constraint is: ")
            pprint.pprint (RFT.ftype_constraint (ftype), indent = 4)

    else:
        x = True
        debug_print (verbosity, "Constraint trivially TRUE\n")

        v1 = select_fval (features, RFT.ftype_name (ftype), None)
        if v1 != None:
            sys.stdout.write ("Feature '{0}':{1}    is not relevant\n".format (RFT.ftype_name (ftype), v1))
            sys.stdout.write ("  The following preconditions are false\n")
            for precond in false_preconds:
                pprint_at_indent (sys.stdout, precond, 4)

    return (x, feature_out)

# ================================================================
# Eval-Apply

def eval (verbosity, ftypes, features, ftype, prefix, e):
    debug_trace (verbosity, prefix + "==> Eval ", e)

    # Leaf term: Special variables 'v'
    if e == "v":
        v = select_fval (features, RFT.ftype_name (ftype), RFT.ftype_default (ftype))
        return debug_trace (verbosity, prefix + "<== Eval ", v)

    if e == "max_XLEN":
        v = select_fval (features, "XLEN", None)
        if (v == None):
            sys.stderr.write ("ERROR: XLEN not specified\n")
            sys.exit (1)
        if (v == 32):
            return debug_trace (verbosity, prefix + "<== Eval ", 0xFFFFFFFF)
        else:
            return debug_trace (verbosity, prefix + "<== Eval ", 0xFFFFFFFFFFFFFFFF)

    # Leaf term: Constants
    if e == None:        return debug_trace (verbosity, prefix + "<== Eval ", e)
    if type (e) == int:  return debug_trace (verbosity, prefix + "<== Eval ", e)
    if type (e) == str:  return debug_trace (verbosity, prefix + "<== Eval ", e)
    if type (e) == bool: return debug_trace (verbosity, prefix + "<== Eval ", e)
    if type (e) == list: return debug_trace (verbosity, prefix + "<== Eval ", e)

    # Assertion check that it's not a leaf term
    if type (e) != tuple:
        sys.stderr.write ("INTERNAL ERROR: unknown form of expression\n")
        pprint.pprint (e, indent = 4)
        sys.exit (1)

    op = e [0]
    e_args = e [1:]

    if op == "If":
        v_cond = eval (verbosity, ftypes, features, ftype, prefix + "    ", e_args [0])
        if v_cond == True:
            v1 = eval (verbosity, ftypes, features, ftype, prefix + "    ", e_args [1])
            return debug_trace (verbosity, prefix + "<=== Eval ", v1)
        else:
            v2 = eval (verbosity, ftypes, features, ftype, prefix + "    ", e_args [2])
            return debug_trace (verbosity, prefix + "<=== Eval ", v2)

    elif op in ["Or2", "Or3", "Or4", "Or5"]:
        result = False
        for e_arg in e_args:
            result = eval (verbosity, ftypes, features, ftype, prefix + "    ", e_arg)
            if result: break
        return debug_trace (verbosity, prefix + "<=== Eval ", result)

    elif op in ["And2", "And3", "And4", "And5"]:
        result = True
        for e_arg in e_args:
            result = eval (verbosity, ftypes, features, ftype, prefix + "    ", e_arg)
            if not result: break
        return debug_trace (verbosity, prefix + "<=== Eval ", result)

    elif op == "Lambda":
        return debug_trace (verbosity, prefix + "<=== Eval ", e)

    # Ordinary application: eval args, apply op to args
    v_args = [eval (verbosity, ftypes, features, ftype, prefix + "    ", e_arg) for e_arg in e_args]
    return apply (verbosity, ftypes, features, ftype, prefix, op, v_args)

def apply (verbosity, ftypes, features, ftype, prefix, op, v_args):
    debug_trace (verbosity, prefix + "    Apply: " + op + " ", v_args)

    if   op == "Is_bool":        result = (type (v_args [0]) == bool)
    elif op == "Is_int":         result = (type (v_args [0]) == int)
    elif op == "Is_string":      result = (type (v_args [0]) == str)
    elif op == "Is_address_map": result = is_address_map (v_args [0])
    elif op == "Are_hartids":    result = are_hartids (v_args [0])

    elif op == "Bit_Not":        result = (~ v_args [0])
    elif op == "Bit_And":        result = (v_args [0] &  v_args [1])
    elif op == "Bit_Or":         result = (v_args [0] |  v_args [1])
    elif op == "Bit_XOr":        result = (v_args [0] ^  v_args [1])

    elif op == "Ne":             result = (v_args [0] != v_args [1])
    elif op == "Eq":             result = (v_args [0] == v_args [1])

    elif op == "Lt":             result = (v_args [0] <  v_args [1])
    elif op == "Le":             result = (v_args [0] <= v_args [1])
    elif op == "Gt":             result = (v_args [0] >= v_args [1])
    elif op == "Ge":             result = (v_args [0] >  v_args [1])

    elif op == "Plus":           result = (v_args [0] +  v_args [1])
    elif op == "Minus":          result = (v_args [0] -  v_args [1])

    elif op == "Not":            result = (not v_args [0])

    elif op == "In":             result = (v_args [0] in  v_args [1])
    elif op == "Range":          result = range (v_args [0], v_args [1])
    elif op == "Is_power_of_2":  result = is_power_of_2 (v_args [0])

    elif op == "Fval":
        ftype = select_ftype (ftypes, v_args [0])
        default = RFT.ftype_default (ftype)
        result = select_fval (features, v_args [0], default)

    elif op == "XLEN_code":      result = XLEN_code (v_args [0])

    elif op == "Legal_WARL_fn":  result = legal_WARL_fn (verbosity, v_args [0], v_args [1])

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

def legal_WARL_fn (verbosity, x, y):
    if (verbosity > 0):
        sys.stdout.write ("TODO: check legality of WARL_fn for {0}\n".format (x))
        pprint_at_indent (y, 8)
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

def select_fval (features, fname, fdefault):
    # DEBUG: sys.stdout.write ("select_fval {0} from ".format (fname)); print (features)

    result = None
    for (name, val) in features:
        if (fname == name):
            result = val
            break

    if result == None:
        result = fdefault

    # sys.stdout.write ("select_fval <= ".format (fname)); print (result)
    return result

# ================================================================

def debug_print (verbosity, s):
    if verbosity > 0: sys.stdout.write (s)

def debug_trace (verbosity, prefix, e):
    if (verbosity > 1):
        sys.stdout.write (prefix); print (e)    
    return e

def pprint_at_indent (stream, x, indent):
    s = pprint.pformat (x, indent = 4)
    for line in s.splitlines ():
        stream.write ("        {0}\n".format (line))

# ================================================================
