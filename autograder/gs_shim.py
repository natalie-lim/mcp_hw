"""Weight decorator that works with or without gradescope-utils installed.

On Gradescope, `gradescope_utils` provides @weight and JSONTestRunner. Locally
we fall back to a no-op decorator + plain text runner so you can run the exact
same tests before uploading.
"""
try:
    from gradescope_utils.autograder_utils.decorators import weight, number  # noqa: F401
    HAVE_GS = True
except Exception:  # pragma: no cover
    HAVE_GS = False

    def weight(w):
        def deco(fn):
            fn.__weight__ = w
            return fn
        return deco

    def number(n):
        def deco(fn):
            return fn
        return deco
