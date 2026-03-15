# utils.py
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime
from functools import wraps
import time
import glob

import sqlite3  
import json
from typing import List, Dict, Any

# Create logs directory if it doesn't exist
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO, rotation_type='size', 
                max_bytes=10*1024*1024, backup_count=5):
    """
    Function to setup a custom logger with rotation options
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        rotation_type: 'size' or 'time'
        max_bytes: Max file size before rotation (for size-based)
        backup_count: Number of backup files to keep
    """
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(module)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Choose rotation handler based on type
    if rotation_type == 'time':
        # Rotates daily at midnight
        handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
    else:  # size-based rotation (default)
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes,  # Default 10MB
            backupCount=backup_count,  # Keep 5 backup files
            encoding='utf-8'
        )
    
    handler.setFormatter(formatter)
    
    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    logger.addHandler(handler)
    logger.addHandler(stream_handler)
    
    return logger

def cleanup_old_logs(days_to_keep=7, file_pattern="*.log*"):
    """
    Remove log files older than specified days
    
    Args:
        days_to_keep: Number of days to keep logs
        file_pattern: Pattern to match log files
    """
    try:
        current_time = time.time()
        cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
        
        log_files = glob.glob(os.path.join(LOGS_DIR, file_pattern))
        deleted_count = 0
        
        for file_path in log_files:
            try:
                file_age = os.path.getctime(file_path)
                if file_age < cutoff_time:
                    os.remove(file_path)
                    filename = os.path.basename(file_path)
                    print(f"Deleted old log file: {filename}")
                    deleted_count += 1
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old log files")
        
    except Exception as e:
        print(f"Error during log cleanup: {e}")

def get_log_directory_size():
    """Get total size of logs directory in MB"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(LOGS_DIR):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
    except Exception as e:
        print(f"Error calculating log directory size: {e}")
        return 0

def get_log_stats():
    """Get statistics about log files"""
    try:
        log_files = glob.glob(os.path.join(LOGS_DIR, "*.log*"))
        total_size_mb = get_log_directory_size()
        
        return {
            "total_files": len(log_files),
            "total_size_mb": total_size_mb,
            "files": [os.path.basename(f) for f in log_files],
            "oldest_file": min(log_files, key=os.path.getctime) if log_files else None,
            "newest_file": max(log_files, key=os.path.getctime) if log_files else None
        }
    except Exception as e:
        print(f"Error getting log stats: {e}")
        return {}

# Create main logger with rotation
log_file = os.path.join(LOGS_DIR, f'arbitrage_bot_{datetime.now().strftime("%Y%m%d")}.log')

# You can choose rotation type: 'size' or 'time'
logger = setup_logger(
    'performance_automation', 
    log_file, 
    rotation_type='size',  # or 'time' for daily rotation
    max_bytes=100*1024*1024,  # 100MB per file
    backup_count=10  # Keep 10 backup files
)

def log_error(e: Exception, context: str = ''):
    """Log an exception with optional context"""
    error_msg = f'{context} - {str(e)}' if context else str(e)
    logger.error(f'Error: {error_msg}', exc_info=True)

def log_info(message: str):
    """Log an info message"""
    logger.info(message)

def log_warning(message: str):
    """Log a warning message"""
    logger.warning(message)

def log_debug(message: str):
    """Log a debug message"""
    logger.debug(message)

# Utility function to run cleanup on startup
def initialize_logging(cleanup_on_start=True, days_to_keep=7):
    """
    Initialize logging system with optional cleanup
    
    Args:
        cleanup_on_start: Whether to clean old logs on startup
        days_to_keep: Number of days of logs to keep
    """
    if cleanup_on_start:
        log_info("Starting log cleanup...")
        cleanup_old_logs(days_to_keep)
        
    log_stats = get_log_stats()
    log_info(f"Logging initialized. Current stats: {log_stats}")

# Auto-cleanup function that can be called periodically
def periodic_log_maintenance(max_size_mb=100, days_to_keep=7):
    """
    Perform periodic log maintenance
    
    Args:
        max_size_mb: Maximum total log directory size in MB
        days_to_keep: Number of days to keep logs
    """
    try:
        current_size = get_log_directory_size()
        
        if current_size > max_size_mb:
            log_warning(f"Log directory size ({current_size}MB) exceeds limit ({max_size_mb}MB). Cleaning up...")
            cleanup_old_logs(days_to_keep)
            
        # Also clean by age
        cleanup_old_logs(days_to_keep)
        
    except Exception as e:
        log_error(e, "Error during periodic log maintenance")

def timing_decorator(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f'{func.__name__} took {end_time - start_time:.2f} seconds to execute')
        return result
    return wrapper

# utils.py

# ... (your logging functions) ...

def calculate_average_price(order_book_side: list, amount_to_trade: float, is_buy: bool) -> tuple:
    """
    Calculates the average price for a given trade size by walking the order book.

    Args:
        order_book_side: A list of [price, volume] pairs (bids for selling, asks for buying).
        amount_to_trade: The amount of QUOTE currency for buys, or BASE currency for sells.
        is_buy: A boolean, True if buying, False if selling.

    Returns:
        A tuple of (average_price, total_amount_base, total_cost_quote).
    """
    total_cost_quote = 0
    total_amount_base = 0
    
    if is_buy: # Trading a fixed amount of QUOTE currency
        remaining_quote = amount_to_trade
        for price, volume in order_book_side:
            cost_of_level = price * volume
            if cost_of_level >= remaining_quote:
                amount_to_buy_base = remaining_quote / price
                total_amount_base += amount_to_buy_base
                total_cost_quote += remaining_quote
                remaining_quote = 0
                break
            else:
                total_amount_base += volume
                total_cost_quote += cost_of_level
                remaining_quote -= cost_of_level
        if remaining_quote > 0: return None # Not enough liquidity
    
    else: # Selling a fixed amount of BASE currency
        remaining_base = amount_to_trade
        for price, volume in order_book_side:
            if volume >= remaining_base:
                total_amount_base += remaining_base
                total_cost_quote += remaining_base * price
                remaining_base = 0
                break
            else:
                total_amount_base += volume
                total_cost_quote += volume * price
                remaining_base -= volume
        if remaining_base > 0: return None # Not enough liquidity

    if total_amount_base == 0: return None
    
    average_price = total_cost_quote / total_amount_base
    return average_price, total_amount_base, total_cost_quote , price


def format_price(num):
    """ 
    Formats a number to a string with 6 decimal places for numbers >= 0.001
    For very small numbers, uses 0,0{n}XXX format
    examples:
    0.0003 -> 0,0{3}300
    0.0000004344343 -> 0,0{6}43
    0.001 -> 0,0010
    """
    if num is None or not isinstance(num, (int, float)) or not (-float('inf') < num < float('inf')):
        return '0'
    
    if num == 0:
        return '0'
    
    sign = '-' if num < 0 else ''
    abs_num = abs(num)
    
    if abs_num >= 0.001:
        # Round to 6 decimals and strip trailing zeros
        rounded = round(abs_num, 6)
        return sign + f'{rounded:g}'  # :g automatically strips trailing zeros
    
    # Very small numbers -> 0,0{n}XXX format
    # Convert to string with high precision to avoid scientific notation
    num_str = f'{abs_num:.18f}'
    frac_part = num_str.split('.')[1]
    
    # Count leading zeros in fractional part
    zeros = 0
    while zeros < len(frac_part) and frac_part[zeros] == '0':
        zeros += 1
    
    # Get first 3 significant digits
    sig_digits = frac_part[zeros:zeros + 3] or '0'
    
    return sign + f'0,0{{{zeros}}}{sig_digits}'

# def round_price(num):
#     """ 
#     Rounds a number to 2 decimal places for numbers >= 0.01
#     For very small numbers, keeps first 2 significant digits
#     examples:
#     0.123412 -> 0.12
#     0.0000004344343 -> 0.00000043
#     1.999 -> 2
#     0.001 -> 0.001 (edge case)
#     0.0001234 -> 0.00012
#     12.3456 -> 12.35
#     0 -> 0
#     None -> 0
#     """
#     if num is None or not isinstance(num, (int, float)) or not (-float('inf') < num < float('inf')):
#         return '0'
    
#     if num == 0:
#         return '0'
    
#     sign = '-' if num < 0 else ''
#     abs_num = abs(num)
    
#     if abs_num >= 0.01:
#         # Round to 2 decimals for numbers >= 0.01
#         return sign + f'{abs_num:.2f}'.rstrip('0').rstrip('.')
    
#     # For very small numbers, keep first 2 significant digits
#     num_str = f'{abs_num:.18f}'
#     frac_part = num_str.split('.')[1]
    
#     # Find first non-zero digit
#     first_nonzero = 0
#     while first_nonzero < len(frac_part) and frac_part[first_nonzero] == '0':
#         first_nonzero += 1
    
#     if first_nonzero >= len(frac_part):
#         return '0'
    
#     # Take 2 significant digits
#     sig_digits = frac_part[first_nonzero:first_nonzero + 2].ljust(2, '0')
    
#     # Build result with leading zeros + 2 sig digits
#     result = '0.' + '0' * first_nonzero + sig_digits
    
#     return sign + result.rstrip('0').rstrip('.')


def round_price(num, sig_digits=2):
    """
    Rounds a number to sig_digits decimal places for numbers >= 0.01
    For very small numbers, keeps first sig_digits significant digits
    
    Args:
        num: Number to format
        sig_digits: Number of significant digits to keep (default: 2)
    
    Examples:
        round_price(0.123412) -> "0.12"
        round_price(0.123412, 3) -> "0.123"
        round_price(0.0000004344343) -> "0.00000043"
        round_price(0.0000004344343, 4) -> "0.0000004344"
    """
    if num is None or not isinstance(num, (int, float)) or not (-float('inf') < num < float('inf')):
        return '0'
    
    if num == 0:
        return '0'
    
    sign = '-' if num < 0 else ''
    abs_num = abs(num)
    
    if abs_num >= 0.01:
        # Round to sig_digits decimals for numbers >= 0.01
        return sign + f'{abs_num:.{sig_digits}f}'.rstrip('0').rstrip('.')
    
    # For very small numbers, keep first sig_digits significant digits
    num_str = f'{abs_num:.18f}'
    frac_part = num_str.split('.')[1]
    
    # Find first non-zero digit
    first_nonzero = 0
    while first_nonzero < len(frac_part) and frac_part[first_nonzero] == '0':
        first_nonzero += 1
    
    if first_nonzero >= len(frac_part):
        return '0'
    
    # Take sig_digits significant digits
    sig_part = frac_part[first_nonzero:first_nonzero + sig_digits].ljust(sig_digits, '0')
    
    # Build result with leading zeros + sig_digits
    result = '0.' + '0' * first_nonzero + sig_part
    
    return sign + result.rstrip('0').rstrip('.')



class PathFilter:

    def __init__(self, config_file: str = 'data/data.json'):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load filtering configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Support both old and new structure
            self.symbols_to_ignore = data.get('symbol_to_ignore', {})
            self.paths_to_ignore = data.get('paths_to_ignore', [])
            
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Creating default...")
            self.symbols_to_ignore = {}
            self.paths_to_ignore = []
            self.save_config()
    
    def save_config(self):
        """Save current configuration to JSON file"""
        config = {
            'symbol_to_ignore': self.symbols_to_ignore,
            'paths_to_ignore': self.paths_to_ignore
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def add_symbol_to_ignore(self, symbol: str, reason: str = "Not profitable"):
        """Add a symbol to ignore globally"""
        self.symbols_to_ignore[symbol] = reason
        self.save_config()
    
    def add_path_to_ignore(self, symbol: str, buy_exchange: str, sell_exchange: str, reason: str = "Not withdrawable"):
        """Add a specific path to ignore"""
        path = {
            'symbol': symbol,
            'buy_on': buy_exchange,
            'sell_on': sell_exchange,
            'reason': reason
        }
        self.paths_to_ignore.append(path)
        self.save_config()
    
    def should_ignore_path(self, path: Dict[str, Any]) -> bool:
        """Check if a path should be ignored"""
        symbol = path['symbol']
        buy_on = path['buy_on']
        sell_on = path['sell_on']
        
        # Check if symbol is globally ignored
        if symbol in self.symbols_to_ignore:
            return True
        
        # Check if specific path is ignored
        for ignored_path in self.paths_to_ignore:
            if (ignored_path['symbol'] == symbol and 
                ignored_path['buy_on'] == buy_on and 
                ignored_path['sell_on'] == sell_on):
                return True
        
        return False
    
    def filter_paths_by_ignore(self, paths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
       
        """Filter out ignored paths"""
        filtered_paths = []
        ignored_count = 0
        
        for path in paths:
            if self.should_ignore_path(path):
                ignored_count += 1
                continue
            filtered_paths.append(path)
        
        print(f"Filtered out {ignored_count} paths")
        print(f"Remaining paths: {len(filtered_paths)}")
        
        return filtered_paths

    def filter_paths_by_fully_validated(self , paths: List[Dict[str, Any]]):
        """Filter out paths that are not fully validated"""
        filtered_paths = []
        ignored_count = 0
        
        for path in paths:
            if path['validation_status'] != 'FULLY_VALIDATED':
                ignored_count += 1
                continue
            filtered_paths.append(path)
        
        print(f"Filtered out {ignored_count} paths")
        print(f"Remaining paths: {len(filtered_paths)}")
        
        return filtered_paths

def get_filtered_paths():
    """Main function to get filtered arbitrage paths"""
    # Initialize filter
    filter_manager = PathFilter('data/data.json')
    
    # Connect to database
    conn = sqlite3.connect('data/arbitrage.db')
    conn.row_factory = sqlite3.Row
    
    # Get all paths
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arbitrage_paths")
    all_paths = [dict(row) for row in cursor.fetchall()]
    
    print(f"Total paths before filtering: {len(all_paths)}")
    
    # Filter paths
    filtered_paths = filter_manager.filter_paths_by_ignore(all_paths)
    
    conn.close()
    return filtered_paths

# # Usage examples:
# if __name__ == "__main__":
#     # Initialize filter manager
#     filter_manager = PathFilter()
    
#     # Add symbols to ignore globally (they're worthless on all exchanges)
#     filter_manager.add_symbol_to_ignore("PRAI/USDT", "Worthless token")
    
#     # Add specific paths to ignore (symbol might be good on some exchanges but not others)
#     filter_manager.add_path_to_ignore("DEFI/USDT", "mexc", "bybit", "Not withdrawable from MEXC")
#     filter_manager.add_path_to_ignore("DEFI/USDT", "kucoin", "bybit", "Not withdrawable from KuCoin")
#     filter_manager.add_path_to_ignore("DEFI/USDT", "mexc", "gate", "Not withdrawable from MEXC")
#     filter_manager.add_path_to_ignore("DEFI/USDT", "kucoin", "gate", "Not withdrawable from KuCoin")
    
#     # Get filtered paths
#     filtered_paths = get_filtered_paths()
    
#     # Display results
#     for path in filtered_paths[:5]:  # Show first 5 for demo
#         print(f"✅ {path['symbol']} | {path['buy_on']} -> {path['sell_on']}")    

if __name__ == "__main__":
    #initialize_logging(cleanup_on_start=True, days_to_keep=7)
    for i in range(100000):
        log_info(f"Test log {i}")
        #time.sleep(1)
        