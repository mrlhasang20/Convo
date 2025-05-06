
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import logging
from src.gui import ImageConverterGUI
from src.utils import setup_logging, load_config

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize and run the application
        app = ImageConverterGUI(config)
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()