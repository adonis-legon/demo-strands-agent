#!/usr/bin/env python3
"""
Banner display for the Demo Strands Agent
"""

from src.app.version import VERSION


def get_banner():
    """
    Generate a banner with the application name and version
    
    Returns:
        str: The banner text
    """
    banner = r"""
____  _____ __  _____      _____ _____ ____      _    _   _ ____  ____       _    ____ _____ _   _ _____ 
|  _ \| ____|  \/  / _ \    / ____|_   _|  _ \    / \  | \ | |  _ \/ ___|     / \  / ___| ____| \ | |_   _|
| | | |  _| | |\/| | | | |  \___ \  | | | |_) |  / _ \ |  \| | | | \___ \    / _ \| |  _|  _| |  \| | | |  
| |_| | |___| |  | | |_| |   ___) | | | |  _ <  / ___ \| |\  | |_| |___) |  / ___ \ |_| | |___| |\  | | |  
|____/|_____|_|  |_|\___/   |____/  |_| |_| \_\/_/   \_\_| \_|____/|____/  /_/   \_\____|_____|_| \_| |_|  
                                                                                                          
"""
    
    version_line = f"v{VERSION}"
    
    # Add the version line left-aligned under the banner
    banner += "\n" + version_line + "\n"
    
    return banner


def print_banner():
    """Print the banner to the console"""
    print(get_banner())


if __name__ == "__main__":
    # For testing
    print_banner()
