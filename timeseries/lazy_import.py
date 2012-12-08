class LazyImport(object): # pragma: no cover
    '''Lazily import modules that aren't required for most functionality
    in the library.'''

    numpy_module = None
    rpy2_module = None
    pylab_module = None

    @staticmethod
    def numpy():
        '''Lazily import the numpy module'''
        if LazyImport.numpy_module is None:
            try:
                LazyImport.numpy_module = __import__('numpypy')
            except ImportError:
                try:
                    LazyImport.numpy_module = __import__('numpy')
                except ImportError:
                    raise ImportError('The numpy module is required')
        return LazyImport.numpy_module

    @staticmethod
    def rpy2():
        '''Lazily import the rpy2 module'''
        if LazyImport.rpy2_module is None:
            try:
                rpy2 = __import__('rpy2.robjects')
            except ImportError:
                raise ImportError('The rpy2 module is required')
            LazyImport.rpy2_module = rpy2
            try:
                rpy2.forecast = rpy2.robjects.packages.importr('forecast')
            except:
                raise ImportError('R and the "forecast" package are required')
            rpy2.ts = rpy2.robjects.r['ts']
            __import__('rpy2.robjects.numpy2ri')
            rpy2.robjects.numpy2ri.activate()
        return LazyImport.rpy2_module

    @staticmethod
    def pylab():
        if LazyImport.pylab_module is None:
            try:
                LazyImport.pylab_module = __import__('pylab')
            except ImportError:
                raise ImportError('The matplotlib library is required')
        return LazyImport.pylab_module

