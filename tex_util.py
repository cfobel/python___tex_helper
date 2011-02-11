from path import path
from subprocess import check_call, Popen, PIPE

def script_path():
    try:
        script = path(__file__)
    except NameError:
        import sys

        script = path(sys.argv[0])

    if script.ext == '.pyc' or script.ext == '.pyo':
        script = path(script[:-1])
    return script


def set_headers(tex_src, left_header=None, right_header=None):
    import re

    if left_header:
        tex_src = re.sub(r'~!<<LEFTHEADER>>~!', r'\\lhead{%s}' % left_header, tex_src)
    else:
        tex_src = re.sub(r'~!<<LEFTHEADER>>~!', '', tex_src)
    if right_header:
        tex_src = re.sub(r'~!<<RIGHTHEADER>>~!', r'\\rhead{%s}' % right_header, tex_src)
    else:
        tex_src = re.sub(r'~!<<RIGHTHEADER>>~!', '', tex_src)
    return tex_src


def compile_pdf(tex_source, out_path, tex_output=False,
                include_paths=None):
    import os
    import tempfile

    include_paths = include_paths or []
    cwd = os.getcwd()
    out_path = path(out_path)

    temp_path = path(tempfile.mkdtemp(suffix='tex_helper'))
    print 'using temp directory: %s' % temp_path
    os.chdir(temp_path)

    for inc_path in include_paths:
        if inc_path.isdir():
            inc_path.copytree(temp_path / inc_path.name)
        else:
            inc_path.copy2(temp_path / inc_path.name)

    # copy styles into styles subdirectory
    styles_path = script_path().parent / path('styles')
    styles_path.copytree(temp_path / path('styles'))

    (handle, temp_tex) = tempfile.mkstemp(suffix='.tex', dir=temp_path)
    os.close(handle)

    tex_path = path(temp_tex)
    tex_path.write_bytes(tex_source)

    cmd = ['pdflatex', '-output-directory=%s' % temp_path, '%s' % tex_path]
    print ' '.join(cmd)
    check_call(cmd, stdout=PIPE, stderr=PIPE)

    os.chdir(cwd)

    pdf_path = temp_path / path('%s.pdf' % tex_path.namebase)
    pdf_path.move(out_path)
    if tex_output:
        tex_path.move(out_path.parent / '%s%s' % (out_path.namebase, tex_path.ext))
    temp_path.rmtree()


def compile_figure_set(out_path, figure_list,
                        tex_output=False, include_paths=None,
                        left_header=None, right_header=None):
    import re

    include_paths = include_paths or []
    figures = [path(f) for f in figure_list]
    include_paths += figures

    figs_per_page = 6
    set_idx = 0

    fig_src = []

    while set_idx < len(figures):
        subfigs = []
        for fig in figures[set_idx:set_idx + figs_per_page]:
            subfigs.append(r'''\subfigure{
            \includegraphics[width=0.5\\textwidth]{%s}
        }''' % fig.name)
        fig_src.append(r'''\\begin{figure}
%s
\\end{figure}''' % '\n'.join(subfigs))

        set_idx += figs_per_page

    tex_src = (script_path().parent / path('fig_template.tex')).bytes()
    tex_src = re.sub(r'~!~!~!~!', '\n'.join(fig_src), tex_src)
    if left_header:
        tex_src = re.sub(r'~!<<LEFTHEADER>>~!', r'\\lhead{%s}' % left_header, tex_src)
    else:
        tex_src = re.sub(r'~!<<LEFTHEADER>>~!', '', tex_src)
    if right_header:
        tex_src = re.sub(r'~!<<RIGHTHEADER>>~!', r'\\rhead{%s}' % right_header, tex_src)
    else:
        tex_src = re.sub(r'~!<<RIGHTHEADER>>~!', '', tex_src)

    compile_pdf(re.sub(r'~!~!~!~!', '\n'.join(fig_src), tex_src), 
                out_path,
                include_paths=include_paths,
                tex_output=True)



class PDFBuilder(object):
    def __init__(self, tex_path):
        self.tex_path = path(tex_path)
        self.scons_path = path('SConstruct')
        i = 0
        while self.scons_path.isfile():
            self.scons_path = path('%s%d' % (self.scons_path, i))
        print 'using SConstruct path: %s' % self.scons_path
        self.pdf_path = path('%s.pdf' % self.tex_path.namebase)
        sc_txt = '''PDF('%s', '%s')''' % (self.pdf_path, self.tex_path)
        self.scons_path.write_lines([sc_txt])


    def open(self):
        check_call(['gnome-open', self.pdf_path], stdout=PIPE, stderr=PIPE)


    def build(self, verbose=False):
        # build pdf
        cmd = ['scons', '-f', self.scons_path]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            print out
            print err
            self.cleanup()
        return (p.returncode == 0)


    def cleanup(self):
        check_call(['scons', '-f', self.scons_path, '-c'])
        if self.scons_path.isfile():
            self.scons_path.remove()
        if self.pdf_path.isfile():
            self.pdf_path.remove()
