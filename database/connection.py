from utils.logger_config import database_logger as logger

class DatabaseManager:
    def __init__(self):
        logger.info("Initializing database connections")
        self.results = []  # Store results in memory for now
    
    def store_results(self, result):
        """Store the processing results"""
        try:
            logger.info("Storing results")
            self.results.append(result)
            return True
        except Exception as e:
            logger.error(f"Error storing results: {str(e)}", exc_info=True)
            raise
    
    def query_data(self, params):
        """Query stored data"""
        try:
            logger.info(f"Querying data with params: {params}")
            return self.results
        except Exception as e:
            logger.error(f"Error querying data: {str(e)}", exc_info=True)
            raise
