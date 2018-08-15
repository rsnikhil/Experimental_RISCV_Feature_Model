.PHONY: help
help:
	@echo "    make clean                Removes Emacs ~ files"
	@echo "    make full_clean           Removes all generated files, __pycache__, etc."

.PHONY: clean
clean:
	rm -r -f  *~

.PHONY: full_clean
full_clean:
	rm -r -f  *~
	rm -r -f  *_std.yaml  *_nonstd.yaml  __pycache__
