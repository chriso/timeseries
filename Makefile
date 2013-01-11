check:
	@python test.py

clean:
	@rm -rf timeseries/*.pyc test/*.pyc *.pyc build dist \
			timeseries.egg-info .coverage htmlcov

coverage:
	@coverage run test.py && \
		coverage report -m && coverage html

install:
	@python setup.py install

dist:
	@python setup.py sdist \
		&& mv dist/timeseries*.tar.gz .

publish:
	@python setup.py sdist upload

test: check

.PHONY: check clean coverage install publish dist
