test:
	@python -m doctest datagrid/*.py && echo "All tests passed"

testverbose:
	@python -m doctest datagrid/*.py -v && echo "All tests passed"
