FUNCTION_APP_NAME = {your_function_app_name}


help:
	@echo ""
	@echo " # =========== # "
	@echo " # simple make # "
	@echo " # =========== # "
	@echo "type 'make publish' to publish to $(FUNCTION_APP_NAME)"
	@echo ""
	@echo " # ================================= # "
	@echo " # when azure raises functions error # "
	@echo " # ================================= # "
	@echo "type 'make clean' to publish to $(FUNCTION_APP_NAME) with nozip"
	@echo ""

.PHONY: help Makefile


clean:
	func azure functionapp publish $(FUNCTION_APP_NAME) --nozip

publish:
	func azure functionapp publish $(FUNCTION_APP_NAME)