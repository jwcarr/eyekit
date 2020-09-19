import setuptools

project_page = 'https://jwcarr.github.io/eyekit/'

with open('README.md', encoding='utf-8') as file:
	long_description = file.read()
long_description = long_description.replace('./docs/', project_page)

setuptools.setup(
	name='eyekit',
	version='0.1.14',
	author='Jon Carr',
	author_email='jcarr@sissa.it',
	description='A lightweight Python package for doing open, transparent, reproducible science on reading behavior',
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
	install_requires=['cairosvg>=2.4', 'numpy>=1.19', 'pillow>=7.2']
)