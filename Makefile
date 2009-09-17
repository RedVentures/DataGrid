test: testpyunit
	@python -m doctest datagrid/*.py && echo "All doc-tests passed"

testverbose: testpyunit
	python -m doctest datagrid/*.py -v && echo "All doc-tests passed"

testpyunit:
	python tests/runner.py
	@echo '----------------------------------------------------------------------'

clean:
	@find . -name '*.pyc' | xargs rm -f
	@rm -rf MANIFEST dist build

server:
	@python extras/demo/server.py

install:
	./setup.py install

