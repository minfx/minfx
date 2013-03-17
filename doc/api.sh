#! /bin/sh

# Shell script for building the API documentation.
epydoc --html -o doc/api --docformat epytext --css white --name minfx --url https://gna.org/projects/minfx --show-frames --show-private --show-imports -v --graph all --show-sourcecode --exclude=devel_scripts --exclude=extern --exclude=graphics --exclude=minfx.scipy_subset minfx
