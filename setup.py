#!/usr/bin/env python

from distutils.core import setup

setup(name = "tex-helper",
    version = "0.01",
    description = "A helper package for LaTex tables, and figures.",
    keywords = "latex tex table figure",
    author = "Christian Fobel",
    url = "https://github.com/cfobel/python___tex_helper",
    license = "LGPL",
    long_description = """""",
    packages = ['tex_helper'],
    package_data = {'tex_helper': ['fig_template.tex',
            'styles/ctable.sty',
            'styles/multirow.sty',
            'styles/subfigure.sty',]}
)
