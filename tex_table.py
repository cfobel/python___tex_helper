def escape_tex(data):
    import re

    return data

table_template = r'''
\documentclass[12pt,letter]{article}
\PassOptionsToPackage{pdftex}{graphics}
\usepackage{styles/subfigure}
\usepackage{styles/ctable}

\oddsidemargin -0.25in
\evensidemargin 0.0in
\textwidth 7in
\topmargin -0.5in
\textheight 9.0in

\begin{document}

\footnotesize
{
\ctable[
  label = {%s},
  caption = {%s},
  sideways
]
{%s}{
}{
%%(data)s
}
}

\end{document}
'''



class Table(object):
    def __init__(self, caption, label, layout):
        self.caption = caption
        self.label = label
        self.layout = layout
        self.template = table_template % (label, caption, layout)
        self.data = []

    
    def add_data(self, data):
        self.data.append(data)


    def __str__(self):
        output = []
        i = 0
        while i < len(self.data):
            item = self.data[i]
            i += 1
            output.append(item)
            if type(item) is Line:
                if i == len(self.data) or\
                        type(self.data[i]) is not Separator:
                    # We have a line and either the next item is
                    # not a separator, or there are no more items.
                    # We must add a separator.
                    output.append(Separator())

        return self.template % {'data': '\n'.join([str(line) for line in output])}


class Cell(object):
    def __init__(self, contents, alignment, forced=False,
                    left_line=False,
                    right_line=False, span=1, bold=False,
                    italic=False):
        self.contents = contents
        self.alignment = alignment
        self.forced = forced
        self.left_line = left_line
        self.right_line = right_line
        self.span = span
        self.bold = bold
        self.italic = italic


    def __str__(self):
        import re

        data = self.contents

        data = re.sub(r'_', r'\_', data)

        if self.italic:
            data = r'\emph{%s}' % data
        if self.bold:
            data = r'\textbf{%s}' % data

        if self.span > 1 or self.left_line\
                or self.right_line or self.forced:
            alignment = self.alignment
            if self.left_line:
                alignment = '|%s' % alignment
            if self.right_line:
                alignment = '%s|' % alignment
            data = r'\multicolumn{%s}{%s}{%s}' % (self.span, 
                        alignment, data)
        return data


class Line(object):
    def __init__(self, cells):
        self.cells = cells

    def __str__(self):
        cells = [str(cell) for cell in self.cells]
        max_len = max([len(cell) for cell in cells])
        format_str = r'%%%ds' % (max_len + 1)
        return ' & '.join([format_str % cell for cell in cells])


class Separator(object):
    def __init__(self, style=r'\\'):
        self.style = style


    def __str__(self):
        return self.style
