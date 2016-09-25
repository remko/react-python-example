import sys
sys.path.append("vendor/")

# Work around GAE problem of missing __main__
# See https://code.google.com/p/googleappengine/issues/detail?id=12981
import sys
if '__main__' not in sys.modules:
	sys.modules['__main__'] = sys.modules[__name__]
