thespread
=========

This is the repository for posts on [thespread.us](http://thespread.us). In order to reproduce the posts on the spread, you will need to purchase play-by-play data from [Armchair Analysis](http://armchairanalysis.com) for $25. 

## Dependencies

To use the files in this repo, you should be on a UNIX-based system (Mac OS X should work, though these files have only been tested in Linux Mint 15 and Ubuntu 13.10). You will also need the following dependencies installed:

- [Python 2.7](http://python.org)
- [IPython Notebook](http://ipython.org)
- [PostgreSQL](http://www.postgresql.org/)
- [csvkit](http://csvkit.readthedocs.org/en/latest/index.html)

You can clone this repo where you would like to install these files and use `setup.sh` to get all of the databases created. The syntax is:

`setup.sh [name of Armchair Analysis zip file] [desired name of database]`

## Python library dependencies

I use a number of Python libraries. If you have done any kind of data science or statistical work in Python before, you probably have them installed. You should be able to install them with [`pip`](https://pypi.python.org/pypi/pip) or [`setuptools`](https://pypi.python.org/pypi/pip). Some of these libraries include:

- `pandas`
- `scikit-learn`
- `numpy`
- `matplotlib`
- `seaborn`

If you have any questions, please [let me know](mailto:trey@thespread.us). Unfortunately I cannot offer tech support, but I'm glad to help where I can.

Trey