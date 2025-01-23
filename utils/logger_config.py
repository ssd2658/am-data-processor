import logging
import sys

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create loggers for different components
fund_extractor = logging.getLogger('fund_extractor')
processor_logger = logging.getLogger('processor')
database_logger = logging.getLogger('database')

# Set levels
fund_extractor.setLevel(logging.INFO)
processor_logger.setLevel(logging.INFO)
database_logger.setLevel(logging.INFO)
