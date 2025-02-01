import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from cdp import Cdp

logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables with detailed logging"""
    env_path = Path('.env')
    if not env_path.exists():
        logger.error(".env file not found in current directory")
        env_path = Path('../.env')  # Try parent directory
        if not env_path.exists():
            logger.error(".env file not found in parent directory either")
            return False
    
    load_dotenv(env_path)
    logger.info(f"Loaded .env file from {env_path}")
    return True

def validate_credentials():
    """Validate CDP credentials with detailed logging"""
    api_key_name = os.getenv('CDP_API_KEY_NAME')
    private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')
    
    logger.info(f"API Key Name found: {'Yes' if api_key_name else 'No'}")
    logger.info(f"Private Key found: {'Yes' if private_key else 'No'}")
    
    if not api_key_name:
        logger.error("CDP_API_KEY_NAME not found in environment variables")
        return False
        
    if not private_key:
        logger.error("CDP_PRIVATE_KEY not found in environment variables")
        return False
    return True

def initialize_cdp():
    """Initialize CDP SDK with enhanced error handling"""
    try:
        # Load environment variables
        if not load_env_file():
            raise ValueError("Failed to load .env file")
        
        # Validate credentials
        if not validate_credentials():
            raise ValueError("CDP credentials validation failed")
        
        # Get credentials
        api_key_name = os.getenv('CDP_API_KEY_NAME')
        private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')
        # Configure CDP
        Cdp.configure(api_key_name, private_key)
        logger.info("CDP SDK initialized successfully")
        
        # Verify configuration worked
        try:
            # Simple test operation
            from cdp import Wallet
            test_wallet = Wallet.create()
            logger.info("CDP configuration verified - test wallet creation successful")
            return True
        except Exception as e:
            logger.error(f"CDP configuration verification failed: {e}")
            raise ValueError("CDP configuration verification failed")
            
    except Exception as e:
        logger.error(f"Failed to initialize CDP SDK: {str(e)}")
        raise
