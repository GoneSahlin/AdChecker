VENV = .venv
MODULE = ad_checker
PROJECT = $(shell basename $(CURDIR))

$(VENV): setup.cfg pyproject.toml
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e .[dev]
	touch $(VENV)
	$(VENV)/bin/python3 -m ipykernel install --user --name $(PROJECT)	

.PHONY: capture_images
capture_images: $(VENV)
	$(VENV)/bin/python3 $(MODULE)/capture_images.py

.PHONY: label_images
label_images: $(VENV)
	$(VENV)/bin/python3 $(MODULE)/label_images.py

.PHONY: database
database: $(VENV)
	$(VENV)/bin/python3 $(MODULE)/database.py

.PHONY: test
test: $(VENV)
	$(VENV)/bin/pytest
	# $(VENV)/bin/pytest $(MODULE)
	# $(VENV)/bin/python3 -m unittest discover test

.PHONY: lint
lint: $(VENV)
	-$(VENV)/bin/flake8 --exclude $(VENV)

.PHONY: clean
clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf *.eggs
	rm -rf *.egg
	rm -rf *.egg-info
	
