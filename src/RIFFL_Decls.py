#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil

# ================================================================
# RISC-V feature declarations.
# Some of these features are ISA features.
# Some of these features are implementation options.

# Each feature declaration has the form:
#
#   mk_fdecl (<feature identifier>
#             <text brief description of feature>
#             <default value ('None', if this feature must be specified)>
#             <pre-conditions (for this feature to be relevant)>,
#             <constraint> )

# The constraint restricts the allowed values for a feature.
# It is a Boolean-valued expression that must evaluate True.
# It may involve the values of other features, because only certain
# combinations of features are meaningful (e.g., if the virtual memory
# feature is "Sv39", then the XLEN feature must be "RV64").

# ================================================================
# Imports of Python libraries

import sys
import pprint

# ================================================================
# Imports of project libraries

# --

# ================================================================
# RISC-V ISA feature decls
# This list is extended by the feature declarations that follow.

fdecls = []

# ================================================================
# Features: RISC-V Spec versions

fdecls.extend ([
    ("User_Spec_Version",
     "Version number of User Level ISA specification",
     "2.2",
     [],
     ["In", "$this", ["List", "2.2", "2.3" ]]),

    ("Privilege_Spec_Version",
     "Version number of Privileged Architecture specification",
     "1.10",
     [],
     ["In", "$this", ["List", "1.10", "1.11" ]]),

    ("XLEN",
     "Width of integer general-purpose registers",
     None,
     [],
     ["In", "$this", ["List", 32, 64 ]])
])

# ================================================================
# Features: MISA features

fdecls.extend ([
    ("MISA_MXL_WARL_fn",
     "WARL function to transform MISA.MXL field",
     ["WARL_fn", "$XLEN_code"],
     [],
     ["Is_WARL_fn", "MISA_MXL", "$this"]),

    ("MISA_A",
     "Optional ISA extension 'A' for Atomic Memory Operations",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_C",
     "Optional ISA extension 'C' (Compressed instructions)",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_D",
     "Optional ISA extension 'D' (Double precision floating point)",
     "False",
     [ ["==", "$MISA_F", "True"] ],    # "The D extension depends on the base single-precision subset F"
     ["Is_bool", "$this"]),

    ("MISA_F",
     "Optional ISA extension 'F' (Single precision floating point)",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_G",
     "Optional ISA extension 'G' (Additional standard extensions present)",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_I",
     "Required ISA extension 'I' ()",
     "True",
     [],
     ["==", "$this", "True"]),

    ("MISA_M",
     "Optional ISA extension 'M' for Integer Multiply/Divide Operations",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_N",
     "Optional ISA extension 'N' for User-level interrupts supported (requires U)",
     "False",
     [ ["==", "$MISA_U", "True"] ],
     ["Is_bool", "$this"]),

    ("MISA_Q",
     "Optional ISA extension 'Q' (Quad precision floating point, requires FD)",
     "False",
     [ ["==", "$XLEN", 64],
       ["==", "$MISA_D", "True"] ],
     ["Is_bool", "$this"]),

    ("MISA_S",
     "Optional ISA extension 'S' (Supervisor Privilege Mode)",
     "False",
     [ ["==", "$MISA_U", "True"] ],
     ["Is_bool", "$this"]),

    ("MISA_U",
     "Optional ISA extension 'U' (User Privilege Mode)",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MISA_X",
     "Optional ISA extension 'X' (Non-standard extensions present)",
     "False",
     [],
     ["Is_bool", "$this"])
])

# ================================================================
# Values of read-only Machine-level CSRs mvendorid, marchid, mimpid, hartids

# 'Hartids' for a single-thread implementation would be [0]
# For multi-thread implems, it is [0, ...], i.e., one hart has id '0',
#    and the remaining hartids are a set of ids different from 0
#    and need not be contigous. 'Are_hartids()' checks this.

fdecls.extend ([
    ("Vendorid",
     "Value of mvendorid CSR",
     0,
     [],
     ["Is_int", "$this"]),

    ("Archid",
     "Value of marchid CSR",
     0,
     [],
     ["Is_int", "$this"]),

    ("Impid",
     "Value of mimpid CSR",
     0,
     [],
     ["Is_int", "$this"]),

    ("Hartids",
     "Values of hartids (list of hartids [0, ...])",
     ["List", 0],
     [],
     ["Are_hartids", "$this"])
])

# ================================================================
# Features: MSTATUS fields

fdecls.extend ([
    ("MSTATUS_SXL",
     "WARL function to transform MSTATUS.SXL field in RV64 and RV128 when S-Mode is supported",
     ["WARL_fn", "$XLEN_code"],
     [ ["&&", ["!=", "$XLEN", 32],
              ["==", "$MISA_S", "True"]] ],
     ["Is_WARL_fn", "MSTATUS_SXL", "$this"]),

    ("MSTATUS_UXL",
     "WARL function to transform MSTATUS.UXL field in RV64 and RV128 when U-Mode is supported",
     ["WARL_fn", "$XLEN_code"],
     [ ["&&", ["!=", "$XLEN", 32],
              ["==", "$MISA_U", "True"]] ],
     ["Is_WARL_fn", "MSTATUS_UXL", "$this"]),

    ("MSTATUS_XS_wired_to_0",
     "MSTATUS.XL fiels id wired to 0 (no additional user-mode extensions",
     "True",
     [],
     ["Is_bool", "$this"]),

    ("MSTATUS_TW_timeout",
     "Timeout in nanoseconds when MSTATUS.TW=1 and WFI is executed in S-mode",
     0,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_int", "$this"])
])

# ================================================================
# Features: MIDELEG and MEDELEG WARL functions

fdecls.extend ([
    ("MIDELEG_WARL_fn",
     "WARL function to transform values written to MIDELEG (requires U)",
     ["WARL_fn", 0],
     [],
     ["Is_WARL_fn", "MIDELEG", "$this"]),

    ("MEDELEG_WARL_fn",
     "WARL function to transform values written to MEDELEG (requires U)",
     ["WARL_fn", 0],
     [],
     ["Is_WARL_fn", "MEDELEG", "$this"]),
])

# ================================================================
# Features: MIP and MIE WARL functions

fdecls.extend ([
    ("MIP_WARL_fn",
     "WARL function to transform values written to MIP",

     ["WARL_fn", ["&", "$writeval",
                       ["If", ["&&", ["==", "$MISA_S", "True"],
                                     ["==", "$MISA_U", "True"]],
                              0x333,
                              ["If", ["==", "$MISA_U", "True"],
                                     0x111,
                                     0]]]],
     [],
     ["Is_WARL_fn", "MIP", "$this"]),

    ("MIE_WARL_fn",
     "WARL function to transform values written to MIE",
     ["WARL_fn", ["&", "$writeval",
                       ["If", ["&&", ["==", "$MISA_S", "True"],
                                     ["==", "$MISA_U", "True"]],
                              0xbbb,
                              ["If", ["==", "$MISA_U", "True"],
                                     0x999,
                                     0x888]]]],
     [],
     ["Is_WARL_fn", "MIE", "$this"])
])

# ================================================================
# Features: addresses for memory-mapped MSIP, MTIME and MTIMECMP

fdecls.extend ([
    ("MSIP_address",
     "Address for memory-mapped MSIP register",
     None,
     [],
     ["Is_int", "$this"]),

    ("MTIME_address",
     "Address for memory-mapped MTIME register",
     None,
     [],
     ["Is_int", "$this"]),

    ("MTIMECMP_address",
     "Address for memory-mapped MTIMECMP register",
     None,
     [],
     ["Is_int", "$this"])
])

# ================================================================
# Features: MTVEC implementation choices

fdecls.extend ([
    ("MTVEC_is_read_only",
     "MTVEC is hardwired to a read-only value",
     None,
     [],
     ["Is_bool", "$this"]),

    ("MTVEC_reset_value",
     "MTVEC reset value (if MTVEC is not read-only)",
     0x100,
     [ ["==", "$MTVEC_is_read_only", "False"] ],
     ["&&", ["Is_int", "$this"],
            ["<=", "$this", ["-",  "$max_XLEN", 3]]]),

    ("MTVEC_read_only_value",
     "MTVEC value (if MTVEC is read-only)",
     None,
     [ ["==", "$MTVEC_is_read_only", "True"] ],
     ["&&", ["Is_int", "$this"],
            ["<=", "$this", ["-", "$max_XLEN", 3]]]),

    ("MTVEC_alignment_multiplier",
     "Additional alignment constraint on MTVEC when MODE is 'vectored' (multiplier x XLEN)",
     1,
     [ ["==", "$MTVEC_is_read_only", "False"] ],
     ["&&", ["Is_int", "$this"],
            ["In", "$this", ["List", 1, 2, 4]]]),

    ("MTVEC_BASE_WARL_fn",
     "WARL function to transform values written to MTVEC BASE field",
     None,
     [ ["==", "$MTVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "MTVEC_BASE", "$this"]),

    ("MTVEC_MODE_WARL_fn",
     "WARL function to transform values written to MTVEC MODE field",
     None,
     [ ["==", "$MTVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "MTVEC_BASE", "$this"]),

    ("STVEC_is_read_only",
     "STVEC is hardwired to a read-only value (requires S)",
     None,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_bool", "$this"]),

    ("STVEC_BASE_WARL_fn",
     "WARL function to transform values written to STVEC BASE field (requires S)",
     None,
     [ ["==", "$MISA_S", "True"],
       ["==", "$STVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "STVEC_MODE", "$this"]),

    ("STVEC_MODE_WARL_fn",
     "WARL function to transform values written to STVEC MODE field (requires S)",
     None,
     [ ["==", "$MISA_S", "True"],
       ["==", "$STVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "STVEC_MODE", "$this"]),

    ("UTVEC_is_read_only",
     "UTVEC is hardwired to a read-only value (requires N)",
     None,
     [ ["==", "$MISA_N", "True"] ],
     ["Is_bool", "$this"]),

    ("UTVEC_BASE_WARL_fn",
     "WARL function to transform values written to UTVEC BASE field (requires U, N)",
     None,
     [ ["==", "$MISA_N", "True"],
       ["==", "$UTVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "UTVEC_BASE", "$this"]),

    ("UTVEC_MODE_WARL_fn",
     "WARL function to transform values written to UTVEC MODE field (requires U, N)",
     None,
     [ ["==", "$MISA_N", "True"],
       ["==", "$UTVEC_is_read_only", "False"] ],
     ["Is_WARL_fn", "UTVEC_MODE", "$this"])
])

# ================================================================
# Features: Hardware Performance Monitor CSRs

fdecls.extend ([
    ("MHPM3_exists",
     "mhpmcounter3 exists and mhpmevent3 can be written",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MHPMEVENT3_WARL_fn",
     "WARL function to transform values written to MHPMEVENT3",
     None,
     [ ["==", "$MHPM3_exists", "True"] ],
     ["Is_WARL_fn", "MHPMEVENT3", "$this"]),

    ("MHPM4_exists",
     "mhpmcounter4 exists and mhpmevent4 can be written",
     "False",
     [],
     ["Is_bool", "$this"]),

    ("MHPMEVENT4_WARL_fn",
     "WARL function to transform values written to MHPMEVENT4",
     None,
     [ ["==", "$MHPM4_exists", "True"] ],
     ["Is_WARL_fn", "MHPMEVENT4", "$this"]),

    # ... TODO: and so on for HPMs 5..31

    ("MCOUNTEREN_WARL_fn",
     "WARL function to transform values written to MCOUNTEREN",
     ["WARL_fn", 0],
     [ ["==", "$MISA_U", "True"] ],
     ["Is_WARL_fn", "MCOUNTEREN", "$this"]),

    ("SCOUNTEREN_WARL_fn",
     "WARL function to transform values written to SCOUNTEREN",
     ["WARL_fn", 0],
     [ ["==", "$MISA_S", "True"] ],
     ["Is_WARL_fn", "SCOUNTEREN", "$this"])
])

# ================================================================
# Features: MEPC WARL function

fdecls.extend ([
    ("MEPC_WARL_fn",
     "WARL function to transform values written to MEPC",
     None,
     [],
     ["Is_WARL_fn", "MEPC", "$this"])
])

# ================================================================
# Features: MCAUSE value on reset and NMI

fdecls.extend ([
    ("MCAUSE_on_reset",
     "Value in mcause CSR on reset",
     None,
     [],
     ["Is_int", "$this"]),

    ("MCAUSE_on_NMI",
     "Value in mcause CSR on Non-maskable interrupt",
     0,
     [],
     ["Is_int", "$this"])
])

# ================================================================
# Features: SATP WARL functions

fdecls.extend ([
    ("SATP_MODE_WARL_fn",
     "WARL function to transform values written to SATP.MODE",
     None,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_WARL_fn", "SATP_MODE", "$this"])
])

fdecls.extend ([
    ("SATP_ASID_WARL_fn",
     "WARL function to transform values written to SATP.ASID",
     ["WARL_fn", 0],
     [ ["==", "$MISA_S", "True"] ],
     ["Is_WARL_fn", "SATP_ASID", "$this"])
])

fdecls.extend ([
    ("SATP_PPN_WARL_fn",
     "WARL function to transform values written to SATP.PPN",
     None,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_WARL_fn", "SATP_PPN", "$this"])
])

# ================================================================
# Features: Virtual memory schemes

fdecls.extend ([
    ("Sv32",
     "Virtual Memory (address-translation) scheme Sv32 (requires RV32, S)",
     "True",
     [ ["==", "$XLEN", 32],
       ["==", "$MISA_S", "True"] ],
     ["==", "$this", "True" ]),

    ("Sv39",
     "Virtual Memory (address-translation) scheme Sv39 (requires RV64, S)",
     "True",
     [ ["==", "$XLEN", 64],
       ["==", "$MISA_S", "True"] ],
     ["==", "$this", "True" ]),

    ("Sv48",
     "Virtual Memory (address-translation) scheme Sv48 (requires RV64, S, Sv39)",
     "False",
     [ ["==", "$XLEN", 64],
       ["==", "$Sv39", "True" ] ],
     ["Is_bool", "$this"]),

    ("PTE_A_trap",
     "Trap when PTE.A is zero",
     None,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_bool", "$this"]),

    ("PTE_D_trap",
     "Trap when PTE.D is zero on a store access",
     None,
     [ ["==", "$MISA_S", "True"] ],
     ["Is_bool", "$this"])
])

# ================================================================
# Features: misc. implementation choices

fdecls.extend ([
    ("Reset_PC",
     "Value of PC on reset",
     None,
     [],
     ["&&", ["Is_int", "$this"],
            ["<=", "$this", ["-",  "$max_XLEN", 3]]]),

    ("Traps_on_unaligned_mem_access",
     "Traps on unaligned memory accesses",
     None,
     [],
     ["Is_bool", "$this"]),

    ("WFI_is_nop",
     "WFI is a no-op, i.e., CPU does not actually pause waiting for interrupt",
     None,
     [],
     ["Is_bool", "$this"]),

    ("NMI_address",
     "Address of handler for non-maskable interrupts",
     None,
     [],
     ["Is_int", "$this"]),

    ("Num_PMP_registers",
     "Number of Physical Memory Protection Registers implemented",
     0,
     [],
     ["Is_int", "$this"]),

    ("CYCLE_defined",
     "CYCLE CSR is defined (else causes Machine-mode trap; can be emulated)",
     None,
     [],
     ["Is_bool", "$this"]),

    ("TIME_defined",
     "TIME CSR is defined (else causes Machine-mode trap; can be emulated)",
     None,
     [],
     ["Is_bool", "$this"]),

    ("INSTRET_defined",
     "INSTRET CSR is defined (else causes Machine-mode trap; can be emulated)",
     None,
     [],
     ["Is_bool", "$this"])
])

# ================================================================
# Features: Memory system implementation choices

fdecls.extend ([
    ("address_map",
     "List of (base, size, MEM/IO, RO/RW/WO, description)",
     None,
     [],
     ["Is_address_map", "$this"]),

    ("LR_SC_grain",
     "Aligned power-of-2 address granularity for LR/SC locks",
     4,
     [ ["==", "$MISA_A", "True"] ],
     ["&&", ["Is_int", "$this"],
            ["Is_power_of_2", "$this"]])
])

# ================================================================
