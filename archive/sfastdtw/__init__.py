try:
    from ._sfastdtw import sfastdtw, dtw
except ImportError:
    from .sfastdtw import sfastdtw, dtw
