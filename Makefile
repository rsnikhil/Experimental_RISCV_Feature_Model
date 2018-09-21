.PHONY: help
help:
	@echo "    make clean                Removes Emacs ~ files"
	@echo "    make full_clean           Removes all generated files, __pycache__, etc."

# ================================================================

EG ?= eg1

.PHONY: demo
demo:
	src/RIFFL_Check.py  Examples/$(EG).yaml

.PHONY: demo_RV64
demo_RV64:
	src/RIFFL_Check.py  Examples/RV64IMAUS.yaml

.PHONY: demo_RV64_v1
demo_RV64_v1:
	src/RIFFL_Check.py  Examples/RV64IMAUS.yaml  1

.PHONY: demo_RV64_v2
demo_RV64_v2:
	src/RIFFL_Check.py  Examples/RV64IMAUS.yaml  2

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
