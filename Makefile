.PHONY: package

package:
		pip install --user setuptools wheel twine

		# create a source distribution and create a wheel
		python setup.py sdist bdist_wheel
