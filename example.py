import logging
import warnings
import time
import random
from cdnsim.core.simulator import CDNSimulator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress NumExpr threading info
warnings.filterwarnings('ignore', message='.*NumExpr.*')

def main():
    # Initialize simulator
    simulator = CDNSimulator(num_nodes=5)
    
    # Simulate some traffic
    content_types = ['video', 'image', 'text']
    num_requests = 100
    
    logger.info("Starting traffic simulation...")
    
    # Process requests
    for i in range(num_requests):
        content_type = random.choice(content_types)
        success = simulator.handle_request(content_type)
        
        if i % 10 == 0:  # Log every 10 requests
            logger.info(f"Processed {i} requests")
        
        # Add some delay between requests
        time.sleep(0.1)
    
    # Get and display current metrics
    metrics = simulator.get_current_metrics()
    logger.info(f"Current Metrics: {metrics}")
    
    # Keep the program running to allow metrics collection
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")

if __name__ == "__main__":
    main()
