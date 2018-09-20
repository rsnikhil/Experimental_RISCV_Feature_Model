#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil

# ================================================================
# RISC-V feature types.
# Some of these features are ISA features.
# Some of these features are implementation options.

# Terminolgy:
#  Feature types: The contents of this file.
#                 Each feature type describes the set of allowed
#                 values for that feature.  This is expressed as a
#                 predicate (contraint)-- a Boolean-valued
#                 expression-- that identifies acceptable values.  The
#                 contraint may involve the values of other features,
#                 because only certain combinations of features are
#                 meaningful (e.g., if the virtual memory feature is
#                 "Sv39", then the XLEN feature must be "RV64").
#
#  Feature list:  A separate YAML file of name-value pairs giving
#                 specific choices of values for features.

# ================================================================
# Imports of Python libraries

import sys
import pprint

# ================================================================
# Each 'feature type'

# 'Expressions' are used for the prerequisite, constraint and default
# in a feature type.

# These expressions are similar to, but less expressive than
# expressions in a full-blown programming language.


# An 'Expression' is:
#   - a FIRST-ORDER TERM described below
#   - an arity-2 lambda whose body is a FIRST-ORDER TERM (no recursion)

# Note: for quick experimentation and prototyping we've here exploited
# Python syntax and data structres, but this is conceptually a
# standalone DSL.
# A non-leaf expression is represented by a Python tuple
#     (op, arg1, arg, ..., argN)
# where 'op' is represented by a string, and args are nested expressions.
# This is just a quick-and-dirty representational choice for an AST
# (abstract syntax tree).

# ---- Leaf terms: literal constants
# Literal Python term: None    (used only to signal absence of a default)
# Literal Python boolean terms: True, False
# Literal Python strings: "foo" or 'foo'
# Literal Python integers: 23
# Literal flat (not nested) Python lists of constants (e.g., for address maps)

# ---- Leaf terms: variables (just a few standard variables): 
v        = "v"          # Evaluates to the value of this ftype's feature (see below)
max_XLEN = "max_XLEN"   # Evaluates to 0xFFFF_FFFF or 0xFFFF_FFFF_FFFF_FFFF depending on XLEN

# ---- Non-leaf terms (arity > 0 constructors; arguments are, recursively nested terms)
def Is_bool (x):         return ("Is_bool", x)
def Is_int (x):          return ("Is_int", x)
def Is_string (x):       return ("Is_string", x)
def Is_address_map (x):  return ("Is_address_map", x)
def Are_hartids (x):     return ("Are_hartids", x)

def Not  (x):            return ("Not", x)

def Or2  (a,b):          return ("Or2", a, b)
def Or3  (a,b,c):        return ("Or3", a, b, c)
def Or4  (a,b,c,d):      return ("Or4", a, b, c, d)
def Or5  (a,b,c,d,e):    return ("Or5", a, b, c, d, e)

def And2 (a,b):          return ("And2", a, b)
def And3 (a,b,c):        return ("And3", a, b, c)
def And4 (a,b,c,d):      return ("And4", a, b, c, d)
def And5 (a,b,c,d,e):    return ("And4", a, b, c, d, e)

def If (b,t,e):          return ("If", b, t, e)

def Bit_Not (x):         return ("Bit_Not", x)
def Bit_And (x,y):       return ("Bit_And", x, y)
def Bit_Or (x,y):        return ("Bit_Or", x, y)

def Eq  (x,y):           return ("Eq", x, y)
def Ne  (x,y):           return ("Ne", x, y)

def Lt  (x,y):           return ("Lt", x, y)
def Le  (x,y):           return ("Le", x, y)
def Gt  (x,y):           return ("Gt", x, y)
def Ge  (x,y):           return ("Ge", x, y)

def Plus (x,y):          return ("Plus", x, y)
def Minus (x,y):         return ("Minus", x, y)

def In (x, ys):          return ("In", x, ys)                  # x is a member of list ys
def Range (x, y):        return ("Range", x, y)                # List of ints [x,x+1,...,y-1]
def Is_power_of_2 (x):   return ("Is_power_of_2", x)

def Fval (x):            return ("Fval", x)                    # Value of feature x
def XLEN_code (x):       return ("XLEN_code", x)               # 32->1, 64->2, 128->3
def Legal_WARL_fn (x,f): return ("Legal_WARL_fn", x, f)        # Check that f is a legal WARL function for feature x

def Lambda (args,e):     return ("Lambda", args, e)

# ================================================================
# Feature Type abstract data type and its access functions.
# Representation: 5-tuple.

# Note: logically, 'preconds' can be incorporated into 'constraint':
#         (preconds AND contraint) OR (NOT preconds)
# i.e., a constraint is trivially true if its preconds are false.
# Keeping preconds separate is a usability choice, allowing sharper
# and more meaningful error messages.

def mk_ftype (name, default, descr, preconds, constraint):
    return (name,        # String: name of feature (identifier)
            descr,       # String: text description of feature
            default,     # Expression ('None', if this feature has no default)
            preconds,    # List of boolean-valued expressions (these are logically ANDed)
            constraint)  # Boolean-valued expression

def ftype_name (f):       return f [0]
def ftype_descr (f):      return f [2]
def ftype_default (f):    return f [1]
def ftype_preconds (f):   return f [3]
def ftype_constraint (f): return f [4]

# 'preconds' is a list of expressions (logically ANDed).
# 'constraint' is an expression.

# 'preconds' and 'constraint' expressions can involve the special variable:
#    'v'    representing the value of the feature in a given feature list
# (Thus, these expressions can be viewed as 'lambda (v).E'

# Expressions can involve 'Fval ("foo")' representing the value of feature "foo"
# in a given feature list.

# A WARL-function feature value is an arity-2 lambda whose body is a
# first-oder expression.  A WARL-function ("Write Any, Read Legal") is
# used during a write to a WARL field in a CSR.  The two arguments
# represent the new value attempted to be written (which may be
# illegal) and the current (old) value in the field.  The output of
# the function is the new, legal value actually written (to be
# returned on subsequent reads).

# ================================================================
# RISC-V ISA feature types

ftypes = []

# ================================================================
# Features: RISC-V Spec versions

ftypes.extend ([
    mk_ftype ("User_Spec_Version",
              "Version number of User Level ISA specification",
              "2.2",
              [],
              In (v, [ "2.2", "2.3" ])),
    
    mk_ftype ("Privilege_Spec_Version",
              "Version number of Privileged Architecture specification",
              "1.10",
              [],
              In (v, [ "1.10", "1.11" ])),

    mk_ftype ("XLEN",
              "Width of integer registers",
              None,
              [],
              In (v, [32, 64])),    # RV32 and RV64 only (can extend to RV128)
])

# ================================================================
# Features: MISA features

ftypes.extend ([
    mk_ftype ("MISA_MXL_WARL_fn",
              "WARL function to transform MISA.MXL field",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              [],
              Legal_WARL_fn ("MISA_MXL", v)),

    mk_ftype ("Extn_A",
              "Optional ISA extension 'A' for Atomic Memory Operations",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_C",
              "Optional ISA extension 'C' (Compressed instructions)",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_D",
              "Optional ISA extension 'D' (Double precision floating point)",
              False,
              [ Eq (Fval ("Extn_F"), True) ],    # "The D extension depends on the base single-precision subset F"
              Is_bool (v)),

    mk_ftype ("Extn_F",
              "Optional ISA extension 'F' (Single precision floating point)",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_G",
              "Optional ISA extension 'G' (Additional standard extensions present)",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_I",
              "Required ISA extension 'I' ()",
              True,
              [],
              Eq (v, True)),

    mk_ftype ("Extn_M",
              "Optional ISA extension 'M' for Integer Multiply/Divide Operations",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_N",
              "Optional ISA extension 'N' for User-level interrupts supported (requires U)",
              False,
              [ Eq (Fval ("Extn_U"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_Q",
              "Optional ISA extension 'Q' (Quad precision floating point, requires FD)",
              False,
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("Extn_D"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_S",
              "Optional ISA extension 'S' (Supervisor Privilege Mode)",
              False,
              [ Eq (Fval ("Extn_U"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_U",
              "Optional ISA extension 'U' (User Privilege Mode)",
              False,
              [],
              Is_bool (v)),

    mk_ftype ("Extn_X",
              "Optional ISA extension 'X' (Non-standard extensions present)",
              False,
              [],
              Is_bool (v))
])

# ================================================================
# Values of read-only Machine-level CSRs mvendorid, marchid, mimpid, hartids

# 'Hartids' for a single-thread implementation would be [0]
# For multi-thread implems, it is [0, ...], i.e., one hart has id '0',
#    and the remaining hartids are a set of ids different from 0
#    and need not be contigous. 'Are_hartids()' checks this.

ftypes.extend ([
    mk_ftype ("Vendorid",
              "Value of mvendorid CSR",
              0,
              [],
              Is_int (v)),

    mk_ftype ("Archid",
              "Value of marchid CSR",
              0,
              [],
              Is_int (v)),

    mk_ftype ("Impid",
              "Value of mimpid CSR",
              0,
              [],
              Is_int (v)),

    mk_ftype ("Hartids",
              "Values of hartids (list of hartids [0, ...])",
              [0],
              [],
              Are_hartids (v))
])

# ================================================================
# Features: MSTATUS fields

ftypes.extend ([
    mk_ftype ("MSTATUS_SXL",
              "WARL function to transform MSTATUS.SXL field in RV64 and RV128 when S-Mode is supported",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              [ And2 (Ne (Fval ("XLEN"), 32),
                      Eq (Fval ("Extn_S"), True)) ],
              Legal_WARL_fn ("MSTATUS_SXL", v)),

    mk_ftype ("MSTATUS_UXL",
              "WARL function to transform MSTATUS.UXL field in RV64 and RV128 when U-Mode is supported",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              [ And2 (Ne (Fval ("XLEN"), 32),
                      Eq (Fval ("Extn_U"), True)) ],
              Legal_WARL_fn ("MSTATUS_UXL", v)),

    mk_ftype ("MSTATUS_XS_wired_to_0",
              "MSTATUS.XL fiels id wired to 0 (no additional user-mode extensions",
              True,
              [],
              Is_bool (v)),

    mk_ftype ("MSTATUS_TW_timeout",
              "Timeout in nanoseconds when MSTATUS.TW=1 and WFI is executed in S-mode",
              0,
              [ Eq (Fval ("Extn_S"), True) ],
              Is_int (v))
])

# ================================================================
# Features: MIDELEG and MEDELEG WARL functions

ftypes.extend ([
    mk_ftype ("MIDELEG_WARL_fn",
              "WARL function to transform values written to MIDELEG (requires U)",
              Lambda (["old_val", "write_val"],
                      If (Eq (Fval ("Extn_U"), False),
                          0,
                          "old_val")),
              [],
              Legal_WARL_fn ("MIDELEG", v)),

    mk_ftype ("MEDELEG_WARL_fn",
              "WARL function to transform values written to MEDELEG (requires U)",
              Lambda (["old_val", "write_val"],
                      If (Eq (Fval ("Extn_U"), False),
                          0,
                          "old_val")),
              [],
              Legal_WARL_fn ("MEDELEG", v)),
])

# ================================================================
# Features: MIP and MIE WARL functions

ftypes.extend ([
    mk_ftype ("MIP_WARL_fn",
              "WARL function to transform values written to MIP",
              Lambda (["old_val", "write_val"],
                      Bit_And ("write_val",
                               If (And2 (Eq (Fval ("Extn_S"), True),
                                         Eq (Fval ("Extn_U"), True)),
                                   0x333,
                                   If (Eq (Fval ("Extn_U"), True),
                                       0x111,
                                       0)))),
              [],
              Legal_WARL_fn ("MIP", v)),

    mk_ftype ("MIE_WARL_fn",
              "WARL function to transform values written to MIE",
              Lambda (["old_val", "write_val"],
                      Bit_And ("write_val",
                               If (And2 (Eq (Fval ("Extn_S"), True),
                                         Eq (Fval ("Extn_U"), True)),
                                   0xbbb,
                                   If (Eq (Fval ("Extn_U"), True),
                                       0x999,
                                       0x888)))),
              [],
              Legal_WARL_fn ("MIE", v))
])

# ================================================================
# Features: addresses for memory-mapped MSIP, MTIME and MTIMECMP

ftypes.extend ([
    mk_ftype ("MSIP_address",
              "Address for memory-mapped MSIP register",
              None,
              [],
              Is_int (v)),

    mk_ftype ("MTIME_address",
              "Address for memory-mapped MTIME register",
              None,
              [],
              Is_int (v)),

    mk_ftype ("MTIMECMP_address",
              "Address for memory-mapped MTIMECMP register",
              None,
              [],
              Is_int (v))
])

# ================================================================
# Features: MTVEC implementation choices

ftypes.extend ([
    mk_ftype ("MTVEC_is_read_only",
              "MTVEC is hardwired to a read-only value",
              None,
              [],
              Is_bool (v)),

    mk_ftype ("MTVEC_reset_value",
              "MTVEC reset value (if MTVEC is not read-only)",
              0x100,
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              And2 (Is_int (v),
                    Le (v, Minus  (max_XLEN, 3)))),

    mk_ftype ("MTVEC_read_only_value",
              "MTVEC value (if MTVEC is read-only)",
              None,
              [ Eq (Fval ("MTVEC_is_read_only"), True) ],
              And2 (Is_int (v),
                    Le (v, Minus (max_XLEN, 3)))),

    mk_ftype ("MTVEC_alignment_multiplier",
              "Additional alignment constraint on MTVEC when MODE is 'vectored' (multiplier x XLEN)",
              1,
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              And2 (Is_int (v),
                    In (v, [1,2,4]))),

    mk_ftype ("MTVEC_BASE_WARL_fn",
              "WARL function to transform values written to MTVEC BASE field",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("MTVEC_BASE", v)),

    mk_ftype ("MTVEC_MODE_WARL_fn",
              "WARL function to transform values written to MTVEC MODE field",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("MTVEC_BASE", v)),

    mk_ftype ("STVEC_is_read_only",
              "STVEC is hardwired to a read-only value (requires S)",
              None,
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v)),

    mk_ftype ("STVEC_BASE_WARL_fn",
              "WARL function to transform values written to STVEC BASE field (requires S)",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_S"), True),
                Eq (Fval ("STVEC_is_read_only"), False) ],
              Legal_WARL_fn ("STVEC_MODE", v)),

    mk_ftype ("STVEC_MODE_WARL_fn",
              "WARL function to transform values written to STVEC MODE field (requires S)",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_S"), True),
                Eq (Fval ("STVEC_is_read_only"), False) ],
              Legal_WARL_fn ("STVEC_MODE", v)),

    mk_ftype ("UTVEC_is_read_only",
              "UTVEC is hardwired to a read-only value (requires N)",
              None,
              [ Eq (Fval ("Extn_N"), True) ],
              Is_bool (v)),

    mk_ftype ("UTVEC_BASE_WARL_fn",
              "WARL function to transform values written to UTVEC BASE field (requires U, N)",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_N"), True),
                Eq (Fval ("UTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("UTVEC_BASE", v)),

    mk_ftype ("UTVEC_MODE_WARL_fn",
              "WARL function to transform values written to UTVEC MODE field (requires U, N)",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_N"), True),
                Eq (Fval ("UTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("UTVEC_MODE", v)),

])

# ================================================================
# Features: Hardware Performance Monitor CSRs

ftypes.extend ([
    mk_ftype ("MHPM3_exists",
              "mhpmcounter3 exists and mhpmevent3 can be written",
              False,
              [],
              Is_bool (v)),
    mk_ftype ("MHPMEVENT3_WARL_fn",
              "WARL function to transform values written to MHPMEVENT3",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("MHPM3_exists"), True) ],
              Legal_WARL_fn ("MHPMEVENT3", v)),

    mk_ftype ("MHPM4_exists",
              "mhpmcounter4 exists and mhpmevent4 can be written",
              False,
              [],
              Is_bool (v)),
    mk_ftype ("MHPMEVENT4_WARL_fn",
              "WARL function to transform values written to MHPMEVENT4",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("MHPM4_exists"), True) ],
              Legal_WARL_fn ("MHPMEVENT4", v)),

    # ... TODO: and so on for HPMs 5..31

    mk_ftype ("MCOUNTEREN_WARL_fn",
              "WARL function to transform values written to MCOUNTEREN",
              Lambda (["old_val", "write_val"], 0),
              [ Eq (Fval ("Extn_U"), True) ],
              Legal_WARL_fn ("MCOUNTEREN", v)),

    mk_ftype ("SCOUNTEREN_WARL_fn",
              "WARL function to transform values written to SCOUNTEREN",
              Lambda (["old_val", "write_val"], 0),
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SCOUNTEREN", v))
])

# ================================================================
# Features: MEPC WARL function

ftypes.extend ([
    mk_ftype ("MEPC_WARL_fn",
              "WARL function to transform values written to MEPC",
              Lambda (["old_val", "write_val"], "old_val"),
              [],
              Legal_WARL_fn ("MEPC", v))
])

# ================================================================
# Features: MCAUSE value on reset and NMI

ftypes.extend ([
    mk_ftype ("MCAUSE_on_reset",
              "Value in mcause CSR on reset",
              None,
              [],
              Is_int (v)),

    mk_ftype ("MCAUSE_on_NMI",
              "Value in mcause CSR on Non-maskable interrupt",
              0,
              [],
              Is_int (v))
])

# ================================================================
# Features: SATP WARL functions

ftypes.extend ([
    mk_ftype ("SATP_MODE_WARL_fn",
              "WARL function to transform values written to SATP.MODE",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_MODE", v))
])

ftypes.extend ([
    mk_ftype ("SATP_ASID_WARL_fn",
              "WARL function to transform values written to SATP.ASID",
              Lambda (["old_val", "write_val"], 0),
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_ASID", v))
])

ftypes.extend ([
    mk_ftype ("SATP_PPN_WARL_fn",
              "WARL function to transform values written to SATP.PPN",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_PPN", v))
])

# ================================================================
# Features: Virtual memory schemes

ftypes.extend ([
    mk_ftype ("SATP_WARL_fn",
              "WARL function to transform values written to SATP",
              Lambda (["old_val", "write_val"], "old_val"),
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP", v)),

    mk_ftype ("VM_Sv32",
              "Virtual Memory (address-translation) scheme Sv32 (requires RV32, S)",
              True,
              [ Eq (Fval ("XLEN"), 32),
                Eq (Fval ("Extn_S"), True) ],
              Eq (v, True)),

    mk_ftype ("VM_Sv39",
              "Virtual Memory (address-translation) scheme Sv39 (requires RV64, S)",
              True,
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("Extn_S"), True) ],
              Eq (v, True)),

    mk_ftype ("VM_Sv48",
              "Virtual Memory (address-translation) scheme Sv48 (requires RV64, S, Sv39)",
              False,
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("VM_Sv39"), True) ],
              Is_bool (v)),

    mk_ftype ("PTE_A_trap",
              "Trap when PTE.A is zero",
              None,
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v)),

    mk_ftype ("PTE_D_trap",
              "Trap when PTE.D is zero on a store access",
              None,
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v))
])

# ================================================================
# Features: misc. implementation choices

ftypes.extend ([
    mk_ftype ("Reset_PC",
              "Value of PC on reset",
              None,
              [],
              And2 (Is_int (v),
                    Le (v, max_XLEN))),

    mk_ftype ("Traps_on_unaligned_mem_access",
              "Traps on unaligned memory accesses",
              None,
              [],
              Is_bool (v)),

    mk_ftype ("WFI_is_nop",
              "WFI is a no-op, i.e., CPU does not actually pause waiting for interrupt",
              None,
              [],
              Is_bool (v)),

    mk_ftype ("NMI_address",
              "Address of handler for non-maskable interrupts",
              None,
              [],
              Is_int (v)),

    mk_ftype ("Num_PMP_registers",
              "Number of Physical Memory Protection Registers implemented",
              0,
              [],
              Is_int (v)),

    mk_ftype ("CYCLE_defined",
              "CYCLE CSR is defined (else causes Machine-mode trap; can be emulated)",
              None,
              [],
              Is_bool (v)),

    mk_ftype ("TIME_defined",
              "TIME CSR is defined (else causes Machine-mode trap; can be emulated)",
              None,
              [],
              Is_bool (v)),

    mk_ftype ("INSTRET_defined",
              "INSTRET CSR is defined (else causes Machine-mode trap; can be emulated)",
              None,
              [],
              Is_bool (v))
])

# ================================================================
# Features: Memory system implementation choices

ftypes.extend ([
    mk_ftype ("address_map",
              "List of (base, size, MEM/IO, RO/RW/WO, description)",
              None,
              [],
              Is_address_map (v)),

    mk_ftype ("LR_SC_grain",
              "Aligned power-of-2 address granularity for LR/SC locks",
              4,
              [ Eq (Fval ("Extn_A"), True) ],
              And2 (Is_int (v),
                    Is_power_of_2 (v)))
])

# ================================================================
