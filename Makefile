PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
CASE ?= invalid_pin

.PHONY: install validate-data test security-review run-baseline investigate evaluate-baseline evaluate-final evaluate-all audit phase-checks reproduce-all

install:
	python3 -m venv --without-pip .venv
	.venv/bin/python scripts/install_local.py
	.venv/bin/python -c "import tracepay, sys; print('TracePay', tracepay.__version__, 'installed on Python', sys.version.split()[0])"

validate-data:
	$(PYTHON) -m tracepay validate-data

test:
	$(PYTHON) scripts/run_tests.py

security-review:
	$(PYTHON) scripts/run_security_review.py

run-baseline:
	$(PYTHON) -m tracepay baseline $(CASE)

investigate:
	$(PYTHON) -m tracepay investigate $(CASE)

evaluate-baseline:
	$(PYTHON) evaluation/run_evaluation.py --mode baseline

evaluate-final:
	$(PYTHON) evaluation/run_evaluation.py --mode final

evaluate-all:
	$(PYTHON) evaluation/run_evaluation.py --mode baseline
	$(PYTHON) evaluation/run_evaluation.py --mode stage1
	$(PYTHON) evaluation/run_evaluation.py --mode stage2
	$(PYTHON) evaluation/run_evaluation.py --mode stage3
	$(PYTHON) evaluation/run_evaluation.py --mode stage4_removed
	$(PYTHON) evaluation/run_evaluation.py --mode final

audit:
	$(PYTHON) evaluation/run_audit.py

phase-checks:
	$(PYTHON) scripts/run_phase_checks.py

reproduce-all:
	$(PYTHON) scripts/reproduce_all.py
