
.PHONY: help
help:
	@echo " == execute python test on some python .venv == "
	@echo "type 'make test-python' to execute python test with pytest"
	@echo ""
	@echo " == test-pypi upload == "
	@echo "type 'make clean wheel test-deploy' to upload test-pypi"
	@echo ""
	@echo " == pypi upload == "
	@echo "type 'make clean wheel deploy' to upload pypi"
	@echo ""
	@echo " == command references == "
	@echo "clean: clean build directory"
	@echo "wheel: build python project"
	@echo "deploy: upload to pypi"
	@echo "test-deploy: upload to pypi"
	@echo "test-python: test with pytest"
	@echo "ci: execute circleCI on local"



.PHONY: test-python
test-python:
	pytest ./test -vv --cov=./slack_api_decorator --cov-report=html

.PHONY: deploy
deploy:
	twine upload dist/*

.PHONY: test-deploy
test-deploy:
	twine upload -r testpypi dist/*

.PHONY: wheel
wheel:
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -f -r slack_api_decorator.egg-info/* dist/* -y

.PHONY: ci
ci:
	circleci local execute --job python_test_3_8