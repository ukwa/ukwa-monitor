'''
script arguments handling
Only expected argument identifies script environ, to allow different settings
for the different development environmens
'''

import sys
import logging

logger = logging.getLogger(__name__)


def passed():
	environ = ''
	if len(sys.argv) == 2:
		environ = sys.argv[1]
		logger.debug(f"Script argument [{environ}]")

		# test environ value
		if environ == 'dev' or environ == 'beta' or environ == 'prod':
			pass
		else:
			logger.error(f"Script environ argument not recognised [{environ}]")
			sys.exit()

	else:
		logger.error("Script environ argument not identified")
		logger.error(f"sys.argv [{sys.argv}]")
		sys.exit()

	return environ
