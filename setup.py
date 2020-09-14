import setuptools

project_page = 'https://jwcarr.github.io/eyekit/'

with open('README.md', 'r') as file:
	long_description = file.read()
long_description = long_description.replace('./docs/', project_page)

setuptools.setup(
	name='eyekit',
	version='0.1.11',
	author='Jon Carr',
	author_email='jcarr@sissa.it',
	description='A Python package for handling, analyzing, and visualizing eyetracking data',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url=project_page,
	license='MIT',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6',
	install_requires=['numpy>=1.19', 'matplotlib>=3.3', 'fonttools>=4.14', 'cairosvg>=2.4']
)