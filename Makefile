
help:
	@echo " == execute python test on some python .venv == "
	@echo "type 'make test-python' to execute python test with pytest"
	@echo ""
	@echo " == test-pypi upload == "
	@echo "type 'make clean build test-deploy' to upload test-pypi"
	@echo ""
	@echo " == pypi upload == "
	@echo "type 'make clean build deploy' to upload pypi"
	@echo ""
	@echo " == command references == "
	@echo "clean: clean build directory"
	@echo "build: build python project"
	@echo "deploy: upload to pypi"
	@echo "test-deploy: upload to pypi"


.PHONY: help

test-python:
	pytest ./test -vv --cov=./azfs --cov-report=html

deploy:
	twine upload dist/*

test-deploy:
	twine upload -r testpypi dist/*

build:
	python setup.py sdist bdist_wheel

clean:
	rm -f -r azfs.egg-info/* dist/* -y
