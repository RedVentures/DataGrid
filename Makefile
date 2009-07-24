test:
	@python -m doctest datagrid/*.py && echo "All doc-tests passed"
	@echo '----------------------------------------------------------------------'
	@python tests/runner.py

testverbose:
	python -m doctest datagrid/*.py -v && echo "All doc-tests passed"
	@echo '----------------------------------------------------------------------'
	python tests/runner.py

clean:
	@find . -name '*.pyc' | xargs rm -f
	@rm -rf build

server:
	@python extras/demo/server.py

install:
	./setup.py install

