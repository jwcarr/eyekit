import setuptools

with open('README.md', encoding='utf-8') as file:
	long_description = file.read()

setuptools.setup(
	name='eyekit',
	version='0.1.17',
	author='Jon Carr',
	author_email='jcarr@sissa.it',
	description='A lightweight Python package for doing open, transparent, reproducible science on reading behavior',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://jwcarr.github.io/eyekit/',
	license='MIT',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Science/Research'
	],
	python_requires='>=3.6',
	install_requires=['cairosvg>=2.4', 'numpy>=1.19', 'pillow>=7.2']
)