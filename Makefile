test:
	@python -m doctest datagrid/*.py && echo "All tests passed"

testverbose:
	@python -m doctest datagrid/*.py -v && echo "All tests passed"

clean:
	@find . -name '*.pyc' | xargs rm -f

server:
	@python -c 'from datagrid.server.core import HTTPServer;server = HTTPServer();server.run()'

phpdemo:
	@cd extras/bindings;php demo.php

