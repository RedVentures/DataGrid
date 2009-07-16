test:
	@python -m doctest datagrid/*.py && echo "All tests passed"

testverbose:
	@python -m doctest datagrid/*.py -v && echo "All tests passed"

clean:
	@find . -name '*.pyc' | xargs rm -f

server:
	@python extras/demo/demo-server.py

phpdemo:
	@cd extras/bindings;php demo.php

