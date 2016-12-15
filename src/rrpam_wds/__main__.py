"""
Entrypoint module, in case you use `python -mrrpam_wds`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""
# from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

from rrpam_wds.cli import Main

if __name__ == "__main__":   # pragma: no cover
    logger=logging.getLogger();  logger.info("Tweet")
    Main().show_application()
