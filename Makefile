
.PHONY: help
help: ## show commands ## make
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]" "[Example]"
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | perl -pe 's%^([/a-zA-Z_-]+):.*?(##)%$$1 $$2%' | awk -F " *?## *?" '{printf "\033[36m%-30s\033[0m %-50s %s\n", $$1, $$2, $$3}'

.PHONY: test-python
test-python: ## test with pytest ## make test-python
	pytest ./test -vv --cov=./slack_api_decorator --cov-report=html

.PHONY: deploy
deploy: ## upload to pypi ## make deploy
	twine upload dist/*

.PHONY: test-deploy
test-deploy: ## upload to pypi ## make test-deploy
	twine upload -r testpypi dist/*

.PHONY: wheel
wheel: ## build python project ## make wheel
	python setup.py sdist bdist_wheel

.PHONY: clean
clean: ## clean build directory ## make clean
	rm -f -r slack_api_decorator.egg-info/* dist/* -y
