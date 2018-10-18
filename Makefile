.PHONY: help
help:
	@echo "  Help:"
	@echo "    make demo1/../demo6       to run demo on examples in Examples/ dir"
	@echo "    make V=1/2 demoJ          to run demo at higher verbosity"
	@echo "    make clean                Removes Emacs ~ files"
	@echo "    make full_clean           Removes all generated files, __pycache__, etc."

# ================================================================

V ?=

.PHONY: demo1
demo1:
	src/RIFFL_Check.py  Examples/eg1.yaml  $(V)

.PHONY: demo2
demo2:
	src/RIFFL_Check.py  Examples/eg2.yaml  $(V)

.PHONY: demo3
demo3:
	src/RIFFL_Check.py  Examples/eg3.yaml  $(V)

.PHONY: demo4
demo4:
	src/RIFFL_Check.py  Examples/eg4.yaml  $(V)

.PHONY: demo5
demo5:
	src/RIFFL_Check.py  Examples/RV32IMU.yaml  $(V)

.PHONY: demo6
demo6:
	src/RIFFL_Check.py  Examples/RV64AIMSU.yaml  $(V)

# ================================================================

.PHONY: README
README:
	markdown  README.md  > README.html

# ================================================================

.PHONY: clean
clean:
	rm -r -f  *~

.PHONY: full_clean
full_clean:
	rm -r -f  *~
	rm -r -f  Examples/*_std.yaml  Examples/*_nonstd.yaml  src/__pycache__
