from guidata import disthelpers as dh
dist = dh.Distribution()
dist.setup('example', '1.0', 'guiqwt app example', './src/run.py')
dist.add_modules('guidata', 'guiqwt')
dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead
