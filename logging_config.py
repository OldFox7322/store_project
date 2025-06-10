import logging
from logging.handlers import RotatingFileHandler
import os



def setup_logging():
	log_dir = 'logs'
	os.makedirs(log_dir, exist_ok=True)
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter(
		"%(asctime)s - %(levelname)s - %(name)s - %(message)s"
		)




	history_handler = RotatingFileHandler(
		filename=os.path.join(log_dir, 'app.log'),
		maxBytes=5 * 1024 * 1024,
		backupCount=5
		)
	history_handler.setLevel(logging.INFO)
	history_handler.setFormatter(formatter)


	error_handler = RotatingFileHandler(
		filename=os.path.join(log_dir, 'error.log'),
		maxBytes=2 * 1024 * 1024,
		backupCount=3
		)
	error_handler.setLevel(logging.ERROR)
	error_handler.setFormatter(formatter)



	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)	
	console_handler.setFormatter(formatter)


	logger.addHandler(history_handler)
	logger.addHandler(error_handler)
	logger.addHandler(console_handler)

	

















