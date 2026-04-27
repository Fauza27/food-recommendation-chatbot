from datetime import datetime, timedelta
import pytz
import re
from typing import Tuple, Optional

def get_samarinda_time() -> datetime:
    """Get current time in Samarinda, Indonesia (WITA - UTC+8)"""
    samarinda_tz = pytz.timezone('Asia/Makassar')  # WITA timezone
    return datetime.now(samarinda_tz)

def get_time_context() -> str:
    """Determine meal time context based on current time"""
    current_time = get_samarinda_time()
    hour = current_time.hour
    
    if 5 <= hour < 10:
        return "sarapan"
    elif 10 <= hour < 15:
        return "makan siang"
    elif 15 <= hour < 18:
        return "cemilan sore"
    elif 18 <= hour < 22:
        return "makan malam"
    else:
        return "makan malam"

def parse_time(time_str: str) -> Tuple[int, int]:
    """Parse time string (HH:MM) to hour and minute"""
    if time_str == 'Unknown' or not time_str:
        return None, None
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour, minute
    except:
        return None, None

def check_operational_status(jam_buka: str, jam_tutup: str, hari_operasional: str) -> str:
    """Check if restaurant is currently open"""
    current_time = get_samarinda_time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_day = current_time.strftime('%A')
    
    # Check if open today
    if hari_operasional != 'Unknown' and 'Setiap Hari' not in hari_operasional:
        if current_day not in hari_operasional:
            return "Tutup (Tidak beroperasi hari ini)"
    
    # Parse operating hours
    open_hour, open_minute = parse_time(jam_buka)
    close_hour, close_minute = parse_time(jam_tutup)
    
    if open_hour is None or close_hour is None:
        return "Jam operasional tidak tersedia"
    
    # Convert to minutes for easier comparison
    current_minutes = current_hour * 60 + current_minute
    open_minutes = open_hour * 60 + open_minute
    close_minutes = close_hour * 60 + close_minute
    
    # Handle overnight operations
    if close_minutes < open_minutes:
        close_minutes += 24 * 60
        if current_minutes < open_minutes:
            current_minutes += 24 * 60
    
    if open_minutes <= current_minutes < close_minutes:
        return "Buka Sekarang"
    elif current_minutes < open_minutes:
        hours_until_open = (open_minutes - current_minutes) // 60
        if hours_until_open == 0:
            minutes_until_open = open_minutes - current_minutes
            return f"Buka dalam {minutes_until_open} menit"
        return f"Buka dalam {hours_until_open} jam"
    else:
        return "Tutup"

def get_day_name_indonesian() -> str:
    """Get current day name in Indonesian"""
    current_time = get_samarinda_time()
    day_map = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    return day_map.get(current_time.strftime('%A'), current_time.strftime('%A'))

def extract_number_from_text(text: str) -> Optional[int]:
    """
    Extract number from text with typo tolerance
    Handles: angka (1-20), kata (satu-dua puluh), typo (lma->lima, tjuh->tujuh)
    """
    text_lower = text.lower()
    
    # Try to find digits first (most reliable)
    digit_match = re.search(r'\b(\d+)\b', text)
    if digit_match:
        num = int(digit_match.group(1))
        if 1 <= num <= 20:  # Reasonable limit
            return num
    
    # Number word mapping with typo variations (order matters - check longer patterns first)
    number_patterns = [
        # Standard with spaces (check first)
        (r'\bdua\s+puluh\b', 20), (r'\bsembilan\s+belas\b', 19), (r'\bdelapan\s+belas\b', 18),
        (r'\btujuh\s+belas\b', 17), (r'\benam\s+belas\b', 16), (r'\blima\s+belas\b', 15),
        (r'\bempat\s+belas\b', 14), (r'\btiga\s+belas\b', 13), (r'\bdua\s+belas\b', 12),
        
        # Standard single words
        (r'\bsebelas\b', 11), (r'\bsepuluh\b', 10),
        (r'\bsembilan\b', 9), (r'\bdelapan\b', 8), (r'\btujuh\b', 7),
        (r'\benam\b', 6), (r'\blima\b', 5), (r'\bempat\b', 4),
        (r'\btiga\b', 3), (r'\bdua\b', 2), (r'\bsatu\b', 1),
        
        # Typo variations
        (r'\bdlapan\b', 8), (r'\bdlpan\b', 8), (r'\bdlapn\b', 8),
        (r'\btjuh\b', 7), (r'\btuju\b', 7), (r'\btujh\b', 7),
        (r'\bsmbilan\b', 9), (r'\bsmblan\b', 9), (r'\bsemblan\b', 9),
        (r'\benm\b', 6), (r'\bnam\b', 6),
        (r'\blma\b', 5), (r'\blim\b', 5), (r'\blimma\b', 5),
        (r'\bempet\b', 4), (r'\bmpat\b', 4), (r'\bempaat\b', 4),
        (r'\btga\b', 3), (r'\btigga\b', 3),
        (r'\bdu\b', 2), (r'\bduwa\b', 2), (r'\bduaa\b', 2),
        (r'\bstu\b', 1), (r'\bsat\b', 1),
        (r'\bspuluh\b', 10), (r'\bspluh\b', 10), (r'\bsepulu\b', 10),
    ]
    
    # Try to find number words with word boundaries
    for pattern, num in number_patterns:
        if re.search(pattern, text_lower):
            return num
    
    return None

def parse_future_time(text: str) -> Optional[Tuple[datetime, str]]:
    """
    Parse future time from text
    Examples: "besok pagi", "besok siang", "malam ini", "nanti malam", "besok jam 7"
    Returns: (target_datetime, time_context_description)
    """
    text_lower = text.lower()
    current_time = get_samarinda_time()
    
    # Check for "besok" (tomorrow)
    if 'besok' in text_lower:
        target_date = current_time + timedelta(days=1)
        
        # Check for specific time
        if 'pagi' in text_lower or 'sarapan' in text_lower:
            target_time = target_date.replace(hour=8, minute=0, second=0, microsecond=0)
            return target_time, "sarapan besok"
        elif 'siang' in text_lower or 'lunch' in text_lower:
            target_time = target_date.replace(hour=12, minute=0, second=0, microsecond=0)
            return target_time, "makan siang besok"
        elif 'sore' in text_lower:
            target_time = target_date.replace(hour=16, minute=0, second=0, microsecond=0)
            return target_time, "cemilan sore besok"
        elif 'malam' in text_lower or 'dinner' in text_lower:
            target_time = target_date.replace(hour=19, minute=0, second=0, microsecond=0)
            return target_time, "makan malam besok"
        else:
            # Default to lunch time
            target_time = target_date.replace(hour=12, minute=0, second=0, microsecond=0)
            return target_time, "besok"
    
    # Check for "nanti malam" or "malam ini"
    if ('nanti' in text_lower and 'malam' in text_lower) or 'malam ini' in text_lower:
        target_time = current_time.replace(hour=19, minute=0, second=0, microsecond=0)
        if target_time <= current_time:
            target_time += timedelta(days=1)
        return target_time, "malam ini"
    
    # Check for "nanti siang"
    if 'nanti' in text_lower and 'siang' in text_lower:
        target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
        if target_time <= current_time:
            target_time += timedelta(days=1)
        return target_time, "nanti siang"
    
    # Check for specific hour (e.g., "jam 7", "pukul 19")
    hour_match = re.search(r'(?:jam|pukul)\s*(\d{1,2})', text_lower)
    if hour_match:
        hour = int(hour_match.group(1))
        if 0 <= hour <= 23:
            target_time = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            if target_time <= current_time:
                target_time += timedelta(days=1)
            
            # Determine context
            if 5 <= hour < 10:
                context = f"jam {hour} (sarapan)"
            elif 10 <= hour < 15:
                context = f"jam {hour} (makan siang)"
            elif 15 <= hour < 18:
                context = f"jam {hour} (cemilan sore)"
            else:
                context = f"jam {hour} (makan malam)"
            
            return target_time, context
    
    return None

def check_operational_status_at_time(jam_buka: str, jam_tutup: str, hari_operasional: str, target_time: datetime) -> str:
    """Check if restaurant will be open at specific future time"""
    target_hour = target_time.hour
    target_minute = target_time.minute
    target_day = target_time.strftime('%A')
    
    # Check if open on that day
    if hari_operasional != 'Unknown' and 'Setiap Hari' not in hari_operasional:
        if target_day not in hari_operasional:
            return "Tutup (Tidak beroperasi hari ini)"
    
    # Parse operating hours
    open_hour, open_minute = parse_time(jam_buka)
    close_hour, close_minute = parse_time(jam_tutup)
    
    if open_hour is None or close_hour is None:
        return "Jam operasional tidak tersedia"
    
    # Convert to minutes
    target_minutes = target_hour * 60 + target_minute
    open_minutes = open_hour * 60 + open_minute
    close_minutes = close_hour * 60 + close_minute
    
    # Handle overnight operations
    if close_minutes < open_minutes:
        close_minutes += 24 * 60
        if target_minutes < open_minutes:
            target_minutes += 24 * 60
    
    if open_minutes <= target_minutes < close_minutes:
        return "Akan Buka"
    else:
        return "Akan Tutup"
