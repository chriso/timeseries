check:
	@python test.py

clean:
	@rm -rf timeseries/*.pyc test/*.pyc *.pyc build dist \
			timeseries.egg-info .coverage htmlcov

coverage:
	@coverage run test.py && \
		coverage report -m && coverage html

dependencies:
	@python setup.py install

dist:
	@python setup.py sdist \
		&& mv dist/timeseries*.tar.gz .

docs: documentation

deps: dependencies

test: check

.PHONY: check clean coverage dependencies dist
