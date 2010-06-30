from path import path

def script_path():
    try:
        script = path(__file__)
    except NameError:
        import sys

        script = path(sys.argv[0])

    if script.ext == '.pyc' or script.ext == '.pyo':
        script = path(script[:-1])
    return script


def compile_pdf(tex_source, out_path, tex_output=False):
    import os
    import tempfile
    from subprocess import check_call, PIPE

    cwd = os.getcwd()
    out_path = path(out_path)

    temp_path = path(tempfile.mkdtemp(suffix='tex_helper'))
    print 'using temp directory: %s' % temp_path
    os.chdir(temp_path)

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
