#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil

# ================================================================
# RISC-V feature types.
# Some of these features are ISA features.
# Some of these features are implementation options.

# Terminolgy:
#  Feature types: The contents of this file.
#                 Each feature type describes the set of values for that feature,
#                 and a constraint on those values that may involve other features.
#
#  Feature list:  A separate YAML file of name-value pairs giving
#                 specific choices of values for features.

# ================================================================
# Imports of Python libraries

import sys
import pprint

# ================================================================
# An 'Expression' is:
#   - a FIRST-ORDER TERM described below
#   - an arity-2 lambda whose body is a FIRST-ORDER TERM

# Expressions are used for the prerequisite, constraint and default in a feature type.

# Note: for quick experimentation and prototyping we've here exploited
# Python syntax and data structres, but this is conceptually a
# standalone DSL.
# A non-leaf expression is represented by a Python tuple
#     (op, arg1, arg, ..., argN)
# where 'op' is represented by a string, and args are nested expressions.
# This is just a quick-and-dirty representational choice for an AST
# (abstract syntax tree).

# ---- Leaf terms: literal constants
# Literal Python term: None    (used to signal absence of a default)
# Literal Python boolean terms: True, False
# Literal Python strings: "foo" or 'foo'
# Literal Python integers: 23
# Literal flat (not nested) Python lists of constants

# ---- Leaf terms: variables (just a few standard variables): 
v        = "v"          # Evaluates to the value of this ftype's feature (see below)
max_XLEN = "max_XLEN"   # Evaluates to 0xFFFF_FFFF or 0xFFFF_FFFF_FFFF_FFFF depending on XLEN

# ---- Non-leaf terms (arity > 0 constructors; arguments are, recursively nested terms)
def Is_bool (x):         return ("Is_bool", x)
def Is_int (x):          return ("Is_int", x)
def Is_string (x):       return ("Is_string", x)
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
    return (name,        # String: name of feature
            default,     # expression ('None', if this feature has no default)
            descr,       # String: text description of feature
            preconds,    # List of boolean-valued expressions (these are logically ANDed)
            constraint)  # Boolean-valued expression

def ftype_name (f):       return f [0]
def ftype_default (f):    return f [1]
def ftype_descr (f):      return f [2]
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
              None,
              "Version number of User Level ISA specification",
              [],
              In (v, [ "2.2", "2.3" ])),
    
    mk_ftype ("Privilege_Spec_Version",
              None,
              "Version number of Privileged Architecture specification",
              [],
              In (v, [ "1.10", "1.11" ])),

    mk_ftype ("XLEN",
              None,
              "Width of integer registers",
              [],
              In (v, [32, 64])),    # RV32 and RV64 only
])

# ================================================================
# Features: MISA features

ftypes.extend ([
    mk_ftype ("MISA_MXL_WARL_fn",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              "WARL function to transform MISA.MXL field",
              [],
              Legal_WARL_fn ("MISA_MXL", v)),

    mk_ftype ("Extn_A",
              False,
              "Optional ISA extension 'A' for Atomic Memory Operations",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_C",
              False,
              "Optional ISA extension 'C' (Compressed instructions)",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_D",
              False,
              "Optional ISA extension 'D' (Double precision floating point)",
              [ Eq (Fval ("Extn_F"), True) ],    # "The D extension depends on the base single-precision subset F"
              Is_bool (v)),

    mk_ftype ("Extn_F",
              False,
              "Optional ISA extension 'F' (Single precision floating point)",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_G",
              False,
              "Optional ISA extension 'G' (Additional standard extensions present)",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_I",
              True,
              "Required ISA extension 'I' ()",
              [],
              Eq (v, True)),

    mk_ftype ("Extn_M",
              False,
              "Optional ISA extension 'M' for Integer Multiply/Divide Operations",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_N",
              False,
              "Optional ISA extension 'N' for User-level interrupts supported (requires U)",
              [ Eq (Fval ("Extn_U"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_Q",
              False,
              "Optional ISA extension 'Q' (Quad precision floating point, requires FD)",
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("Extn_D"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_S",
              False,
              "Optional ISA extension 'S' (Supervisor Privilege Mode)",
              [ Eq (Fval ("Extn_U"), True) ],
              Is_bool (v)),

    mk_ftype ("Extn_U",
              False,
              "Optional ISA extension 'U' (User Privilege Mode)",
              [],
              Is_bool (v)),

    mk_ftype ("Extn_X",
              False,
              "Optional ISA extension 'X' (Non-standard extensions present)",
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
              0,
              "Value of mvendorid CSR",
              [],
              Is_int (v)),

    mk_ftype ("Archid",
              0,
              "Value of marchid CSR",
              [],
              Is_int (v)),

    mk_ftype ("Impid",
              0,
              "Value of mimpid CSR",
              [],
              Is_int (v)),

    mk_ftype ("Hartids",
              [0],
              "Values of hartids (list of hartids [0, ...])",
              [],
              Are_hartids (v))
])

# ================================================================
# Features: MSTATUS fields

ftypes.extend ([
    mk_ftype ("MSTATUS_SXL",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              "WARL function to transform MSTATUS.SXL field in RV64 and RV128 when S-Mode is supported",
              [ And2 (Ne (Fval ("XLEN"), 32),
                      Eq (Fval ("Extn_S"), True)) ],
              Legal_WARL_fn ("MSTATUS_SXL", v)),

    mk_ftype ("MSTATUS_UXL",
              Lambda (["old_val", "write_val"],
                      XLEN_code (Fval ("XLEN"))),
              "WARL function to transform MSTATUS.UXL field in RV64 and RV128 when U-Mode is supported",
              [ And2 (Ne (Fval ("XLEN"), 32),
                      Eq (Fval ("Extn_U"), True)) ],
              Legal_WARL_fn ("MSTATUS_UXL", v)),

    mk_ftype ("MSTATUS_XS_wired_to_0",
              True,
              "MSTATUS.XL fiels id wired to 0 (no additional user-mode extensions",
              [],
              Is_bool (v)),

    mk_ftype ("MSTATUS_TW_timeout",
              0,
              "Timeout in nanoseconds when MSTATUS.TW=1 and WFI is executed in S-mode",
              [ Eq (Fval ("Extn_S"), True) ],
              Is_int (v))
])

# ================================================================
# Features: MIDELEG and MEDELEG WARL functions

ftypes.extend ([
    mk_ftype ("MIDELEG_WARL_fn",
              Lambda (["old_val", "write_val"],
                      If (Eq (Fval ("Extn_U"), False),
                          0,
                          "write_val")),
              "WARL function to transform values written to MIDELEG (requires U)",
              [],
              Legal_WARL_fn ("MIDELEG", v)),

    mk_ftype ("MEDELEG_WARL_fn",
              Lambda (["old_val", "write_val"],
                      If (Eq (Fval ("Extn_U"), False),
                          0,
                          "write_val")),
              "WARL function to transform values written to MEDELEG (requires U)",
              [],
              Legal_WARL_fn ("MEDELEG", v)),
])

# ================================================================
# Features: MIP and MIE WARL functions

ftypes.extend ([
    mk_ftype ("MIP_WARL_fn",
              Lambda (["old_val", "write_val"],
                      Bit_And ("write_val",
                               If (And2 (Eq (Fval ("Extn_S"), True),
                                         Eq (Fval ("Extn_U"), True)),
                                   0x333,
                                   If (Eq (Fval ("Extn_U"), True),
                                       0x111,
                                       0)))),
              "WARL function to transform values written to MIP",
              [],
              Legal_WARL_fn ("MIP", v)),

    mk_ftype ("MIE_WARL_fn",
              Lambda (["old_val", "write_val"],
                      Bit_And ("write_val",
                               If (And2 (Eq (Fval ("Extn_S"), True),
                                         Eq (Fval ("Extn_U"), True)),
                                   0xbbb,
                                   If (Eq (Fval ("Extn_U"), True),
                                       0x999,
                                       0x888)))),
              "WARL function to transform values written to MIE",
              [],
              Legal_WARL_fn ("MIE", v))
])

# ================================================================
# Features: addresses for memory-mapped MSIP, MTIME and MTIMECMP

ftypes.extend ([
    mk_ftype ("MSIP_address",
              None,
              "Address for memory-mapped MSIP register",
              [],
              Is_int (v)),

    mk_ftype ("MTIME_address",
              None,
              "Address for memory-mapped MTIME register",
              [],
              Is_int (v)),

    mk_ftype ("MTIMECMP_address",
              None,
              "Address for memory-mapped MTIMECMP register",
              [],
              Is_int (v))
])

# ================================================================
# Features: MTVEC implementation choices

ftypes.extend ([
    mk_ftype ("MTVEC_is_read_only",
              None,
              "MTVEC is hardwired to a read-only value",
              [],
              Is_bool (v)),

    mk_ftype ("MTVEC_reset_value",
              0x100,
              "MTVEC reset value (if MTVEC is not read-only)",
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              And2 (Is_int (v),
                    Le (v, Minus  (max_XLEN, 3)))),

    mk_ftype ("MTVEC_read_only_value",
              None,
              "MTVEC value (if MTVEC is read-only)",
              [ Eq (Fval ("MTVEC_is_read_only"), True) ],
              And2 (Is_int (v),
                    Le (v, Minus (max_XLEN, 3)))),

    mk_ftype ("MTVEC_alignment_multiplier",
              1,
              "Additional alignment constraint on MTVEC when MODE is 'vectored' (multiplier x XLEN)",
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              And2 (Is_int (v),
                    In (v, [1,2,4]))),

    mk_ftype ("MTVEC_BASE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to MTVEC BASE field",
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("MTVEC_BASE", v)),

    mk_ftype ("MTVEC_MODE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to MTVEC MODE field",
              [ Eq (Fval ("MTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("MTVEC_BASE", v)),

    mk_ftype ("STVEC_is_read_only",
              None,
              "STVEC is hardwired to a read-only value (requires S)",
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v)),

    mk_ftype ("STVEC_BASE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to STVEC BASE field (requires S)",
              [ Eq (Fval ("Extn_S"), True),
                Eq (Fval ("STVEC_is_read_only"), False) ],
              Legal_WARL_fn ("STVEC_MODE", v)),

    mk_ftype ("STVEC_MODE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to STVEC MODE field (requires S)",
              [ Eq (Fval ("Extn_S"), True),
                Eq (Fval ("STVEC_is_read_only"), False) ],
              Legal_WARL_fn ("STVEC_MODE", v)),

    mk_ftype ("UTVEC_is_read_only",
              None,
              "UTVEC is hardwired to a read-only value (requires N)",
              [ Eq (Fval ("Extn_N"), True) ],
              Is_bool (v)),

    mk_ftype ("UTVEC_BASE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to UTVEC BASE field (requires U, N)",
              [ Eq (Fval ("Extn_N"), True),
                Eq (Fval ("UTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("UTVEC_BASE", v)),

    mk_ftype ("UTVEC_MODE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to UTVEC MODE field (requires U, N)",
              [ Eq (Fval ("Extn_N"), True),
                Eq (Fval ("UTVEC_is_read_only"), False) ],
              Legal_WARL_fn ("UTVEC_MODE", v)),

])

# ================================================================
# Features: Hardware Performance Monitor CSRs

ftypes.extend ([
    mk_ftype ("MHPM3_exists",
              False,
              "mhpmcounter3 exists and mhpmevent3 can be written",
              [],
              Is_bool (v)),
    mk_ftype ("MHPMEVENT3_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to MHPMEVENT3",
              [ Eq (Fval ("MHPM3_exists"), True) ],
              Legal_WARL_fn ("MHPMEVENT3", v)),

    mk_ftype ("MHPM4_exists",
              False,
              "mhpmcounter4 exists and mhpmevent4 can be written",
              [],
              Is_bool (v)),
    mk_ftype ("MHPMEVENT4_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to MHPMEVENT4",
              [ Eq (Fval ("MHPM4_exists"), True) ],
              Legal_WARL_fn ("MHPMEVENT4", v)),

    # ... TODO: and so on for HPMs 5..31

    mk_ftype ("MCOUNTEREN_WARL_fn",
              Lambda (["old_val", "write_val"], 0),
              "WARL function to transform values written to MCOUNTEREN",
              [ Eq (Fval ("Extn_U"), True) ],
              Legal_WARL_fn ("MCOUNTEREN", v)),

    mk_ftype ("SCOUNTEREN_WARL_fn",
              Lambda (["old_val", "write_val"], 0),
              "WARL function to transform values written to SCOUNTEREN",
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SCOUNTEREN", v))
])

# ================================================================
# Features: MEPC WARL function

ftypes.extend ([
    mk_ftype ("MEPC_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to MEPC",
              [],
              Legal_WARL_fn ("MEPC", v))
])

# ================================================================
# Features: MCAUSE value on reset and NMI

ftypes.extend ([
    mk_ftype ("MCAUSE_on_reset",
              None,
              "Value in mcause CSR on reset",
              [],
              Is_int (v)),

    mk_ftype ("MCAUSE_on_NMI",
              0,
              "Value in mcause CSR on Non-maskable interrupt",
              [],
              Is_int (v))
])

# ================================================================
# Features: SATP WARL functions

ftypes.extend ([
    mk_ftype ("SATP_MODE_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to SATP.MODE",
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_MODE", v))
])

ftypes.extend ([
    mk_ftype ("SATP_ASID_WARL_fn",
              Lambda (["old_val", "write_val"], 0),
              "WARL function to transform values written to SATP.ASID",
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_ASID", v))
])

ftypes.extend ([
    mk_ftype ("SATP_PPN_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to SATP.PPN",
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP_PPN", v))
])

# ================================================================
# Features: Virtual memory schemes

ftypes.extend ([
    mk_ftype ("SATP_WARL_fn",
              Lambda (["old_val", "write_val"], "write_val"),
              "WARL function to transform values written to SATP",
              [ Eq (Fval ("Extn_S"), True) ],
              Legal_WARL_fn ("SATP", v)),

    mk_ftype ("VM_Sv32",
              True,
              "Virtual Memory (address-translation) scheme Sv32 (requires RV32, S)",
              [ Eq (Fval ("XLEN"), 32),
                Eq (Fval ("Extn_S"), True) ],
              Eq (v, True)),

    mk_ftype ("VM_Sv39",
              True,
              "Virtual Memory (address-translation) scheme Sv39 (requires RV64, S)",
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("Extn_S"), True) ],
              Eq (v, True)),

    mk_ftype ("VM_Sv48",
              False,
              "Virtual Memory (address-translation) scheme Sv48 (requires RV64, S, Sv39)",
              [ Eq (Fval ("XLEN"), 64),
                Eq (Fval ("VM_Sv39"), True) ],
              Eq (v, True)),

    mk_ftype ("PTE_A_trap",
              None,
              "Trap when PTE.A is zero",
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v)),

    mk_ftype ("PTE_D_trap",
              None,
              "Trap when PTE.D is zero on a store access",
              [ Eq (Fval ("Extn_S"), True) ],
              Is_bool (v))
])

# ================================================================
# Features: misc. implementation choices

ftypes.extend ([
    mk_ftype ("Reset_PC",
              None,
              "Value of PC on reset",
              [],
              And2 (Is_int (v),
                    Le (v, max_XLEN))),

    mk_ftype ("Traps_on_unaligned_mem_access",
              None,
              "Traps on unaligned memory accesses",
              [],
              Is_bool (v)),

    mk_ftype ("WFI_is_nop",
              None,
              "WFI is a no-op, i.e., CPU does not actually pause waiting for interrupt",
              [],
              Is_bool (v)),

    mk_ftype ("NMI_address",
              None,
              "Address of handler for non-maskable interrupts",
              [],
              Is_int (v)),

    mk_ftype ("Num_PMP_registers",
              0,
              "Number of Physical Memory Protection Registers implemented",
              [],
              Is_int (v)),

    mk_ftype ("CYCLE_defined",
              None,
              "CYCLE CSR is defined (else causes Machine-mode trap; can be emulated)",
              [],
              Is_bool (v)),

    mk_ftype ("TIME_defined",
              None,
              "TIME CSR is defined (else causes Machine-mode trap; can be emulated)",
              [],
              Is_bool (v)),

    mk_ftype ("INSTRET_defined",
              None,
              "INSTRET CSR is defined (else causes Machine-mode trap; can be emulated)",
              [],
              Is_bool (v))
])

# ================================================================
# Features: Memory system implementation choices

ftypes.extend ([
    mk_ftype ("LR_SC_grain",
              4,
              "Aligned power-of-2 address granularity for LR/SC locks",
              [ Eq (Fval ("Extn_A"), True) ],
              And2 (Is_int (v),
                    Is_power_of_2 (v)))
])

# ================================================================
