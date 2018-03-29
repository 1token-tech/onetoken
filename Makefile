default:
	python3 setup.py sdist bdist_wheel && cd dist && pip3 install onetoken*whl --upgrade
