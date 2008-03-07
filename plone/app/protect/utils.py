from AccessControl.requestmethod import _buildFacade
import inspect

_default = []

# This is based on AccessControl.requestmethod.postonly
def protect(callable, *checkers):
    spec = inspect.getargspec(callable)
    args, defaults = spec[0], spec[3]
    try:
        r_index = args.index("REQUEST")
    except ValueError:
        raise ValueError("No REQUEST parameter in callable signature")

    arglen = len(args)
    if defaults is not None:
        defaults = zip(args[arglen - len(defaults):], defaults)
        arglen -= len(defaults)

    def _curried(*args, **kw):
        request = None

        if len(args) > r_index:
            request = args[r_index]

        for checker in checkers:
            checker(request)

        # Reconstruct keyword arguments
        if defaults is not None:
            args, kwparams = args[:arglen], args[arglen:]
            for positional, (key, default) in zip(kwparams, defaults):
                if positional is _default:
                    kw[key] = default
                else:
                    kw[key] = positional

        return callable(*args, **kw)

    # Build a facade, with a reference to our locally-scoped _curried
    facade_globs = dict(_curried=_curried, _default=_default)
    exec _buildFacade(spec, callable.__doc__) in facade_globs
    return facade_globs['_facade']

