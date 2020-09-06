import setuptools

with open('README.md', 'r') as file:
	long_description = file.read()

setuptools.setup(
	name='eyekit',
	version='0.1.1',
	author='Jon Carr',
	author_email='jcarr@sissa.it',
	description='A lite Python package for handling and visualizing eyetracking data',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/jwcarr/eyekit',
	license='MIT',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6',
	install_requires=['numpy>=1.13', 'cairosvg>=2.4']
)