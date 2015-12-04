import contextlib
import os
import sys

import six


@contextlib.contextmanager
def push_env(**kwargs):
    """Temporarily modify os.environ within a given context.

    Args:
        **kwargs: An arbitrary list of names and values to set in
            the environment. Each name and value must be a string.

    """

    try:
        # NOTE(kgriffs): os.environ is actually of type os._Environ,
        #   which is a subclass of dict. os._Environ.copy() returns
        #   an instance of dict. We only use old_env to update (rather
        #   than reassign) os.environ, so we don't actually need an
        #   instance of os._Environ. If we were to try replacing
        #   os.environ with a regular dict, os.environ and os.getenv()
        #   would no longer stay in sync, we would lose the type
        #   check when assigning env values, etc.
        #
        #   If we wanted to reassign, we could probably get away with
        #   it by constructing old_env via os._Environ(), but that
        #   would make us more dependent on Python internals that may
        #   or may not change over time.
        old_env = os.environ.copy()

        for key, value in kwargs.items():
            os.environ[key] = value

        yield

    finally:
        # NOTE(kgriffs): Leave the existing instance of os.environ
        #   in place per the note above.
        os.environ.clear()
        os.environ.update(old_env)


@contextlib.contextmanager
def push_argv(*args):
    """Temporarily extend sys.argv with additional arguments.

    Args:
        *args: A list of strings to append to sys.argv

    """

    # NOTE(kgriffs): argparse is OK with args of type unicode,
    #   so push_argv isn't strict about it either.
    if not all(isinstance(arg, six.string_types) for arg in args):
        raise TypeError('All args must be strings')

    old_argv, sys.argv = sys.argv, sys.argv[:1]
    sys.argv.extend(args)

    try:
        yield
    finally:
        sys.argv = old_argv
