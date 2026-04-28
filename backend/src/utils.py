import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pytz

_WITA_TZ = pytz.timezone("Asia/Makassar")

_DAY_ID = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Minggu",
}


def get_samarinda_time() -> datetime:
    """Waktu saat ini di zona WITA (UTC+8)."""
    return datetime.now(_WITA_TZ)


def get_time_context() -> str:
    """Konteks makan berdasarkan jam sekarang."""
    hour = get_samarinda_time().hour
    if 5 <= hour < 10:
        return "sarapan"
    if 10 <= hour < 15:
        return "makan siang"
    if 15 <= hour < 18:
        return "cemilan sore"
    return "makan malam"


def get_day_name_indonesian() -> str:
    """Nama hari saat ini dalam Bahasa Indonesia."""
    eng = get_samarinda_time().strftime("%A")
    return _DAY_ID.get(eng, eng)


def _parse_time(time_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse 'HH:MM' → (hour, minute).
    Mengembalikan None jika format tidak valid atau nilai 'Unknown'.
    """
    if not time_str or time_str.strip().lower() in ("unknown", ""):
        return None
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return None


def _to_minutes(hour: int, minute: int) -> int:
    return hour * 60 + minute


def _compute_status(
    open_hm: Tuple[int, int],
    close_hm: Tuple[int, int],
    current_hm: Tuple[int, int],
    open_label: str = "Buka Sekarang",
    closed_label: str = "Tutup",
) -> str:
    """
    Hitung status berdasarkan pasangan (hour, minute).
    """
    open_m = _to_minutes(*open_hm)
    close_m = _to_minutes(*close_hm)
    raw_cur_m = _to_minutes(*current_hm)   
    cur_m = raw_cur_m

    overnight = close_m < open_m

    if overnight:
        close_m += 1440
        if cur_m < open_m:
            cur_m += 1440

    if open_m <= cur_m < close_m:
        return open_label

    if raw_cur_m < open_m:
        mins_until = open_m - raw_cur_m
    elif overnight and raw_cur_m < _to_minutes(*close_hm):
        mins_until = 0
    elif overnight:
        mins_until = open_m - raw_cur_m
    else:
        return closed_label

    if mins_until > 0:
        hours, mins = divmod(mins_until, 60)
        if hours == 0:
            return f"Buka dalam {mins} menit"
        return f"Buka dalam {hours} jam"

    return closed_label


def _is_open_today(hari_operasional: str, day_name_en: str) -> bool:
    """True jika restoran beroperasi pada hari yang diberikan."""
    if not hari_operasional or hari_operasional.strip().lower() in ("unknown", ""):
        return True  
    if "Setiap Hari" in hari_operasional:
        return True
    return day_name_en in hari_operasional


def check_operational_status(
    jam_buka: str, jam_tutup: str, hari_operasional: str
) -> str:
    """Status operasional berdasarkan waktu *sekarang*."""
    now = get_samarinda_time()

    if not _is_open_today(hari_operasional, now.strftime("%A")):
        return "Tutup (Tidak beroperasi hari ini)"

    open_hm = _parse_time(jam_buka)
    close_hm = _parse_time(jam_tutup)

    if open_hm is None or close_hm is None:
        return "Jam operasional tidak tersedia"

    return _compute_status(
        open_hm, close_hm, (now.hour, now.minute)
    )


def check_operational_status_at_time(
    jam_buka: str,
    jam_tutup: str,
    hari_operasional: str,
    target_time: datetime,
) -> str:
    """Status operasional pada *waktu mendatang* tertentu."""
    if not _is_open_today(hari_operasional, target_time.strftime("%A")):
        return "Akan Tutup (Tidak beroperasi hari itu)"

    open_hm = _parse_time(jam_buka)
    close_hm = _parse_time(jam_tutup)

    if open_hm is None or close_hm is None:
        return "Jam operasional tidak tersedia"

    return _compute_status(
        open_hm,
        close_hm,
        (target_time.hour, target_time.minute),
        open_label="Akan Buka",
        closed_label="Akan Tutup",
    )



_NUMBER_PATTERNS: list[Tuple[str, int]] = [ 
    (r"\bbelas\b", 11),
    (r"\bdua\s+bela\b", 12),
    (r"\btiga\s+bela\b", 13),
    (r"\bempat\s+bela\b", 14),
    (r"\blima\s+bela\b", 15),
    (r"\benam\s+bela\b", 16),
    (r"\btujuh\s+bela\b", 17),
    (r"\bdelapan\s+bela\b", 18),
    (r"\bsem\s+bela\b", 19),
    (r"\bdua\s+puluh\s+sat[uu]\b", 21),
    (r"\bdua\s+puluh\b", 20),
    (r"\bsembilan\s+belas\b", 19),
    (r"\bdelapan\s+belas\b", 18),
    (r"\btujuh\s+belas\b", 17),
    (r"\benam\s+belas\b", 16),
    (r"\blima\s+belas\b", 15),
    (r"\bempat\s+belas\b", 14),
    (r"\btiga\s+belas\b", 13),
    (r"\bdua\s+belas\b", 12),
    (r"\bsebelas\b", 11),
    (r"\bsepuluh\b", 10),

    (r"\bsembilan\b", 9),
    (r"\bdelapan\b", 8),
    (r"\btujuh\b", 7),
    (r"\benam\b", 6),
    (r"\blima\b", 5),
    (r"\bempat\b", 4),
    (r"\btiga\b", 3),
    (r"\bdua\b", 2),
    (r"\bsatu\b", 1),

    (r"\bsmbilan\b", 9), (r"\bsemblan\b", 9),
    (r"\bdlapan\b", 8), (r"\bdlpan\b", 8),
    (r"\btjuh\b", 7), (r"\btuju\b", 7),

    (r"\benam\b", 6),
    (r"\blma\b", 5), (r"\blim\b", 5),
    (r"\bempet\b", 4), (r"\bmpat\b", 4),
    (r"\btga\b", 3),
    (r"\bspuluh\b", 10), (r"\bspluh\b", 10),
]


def extract_number_from_text(text: str) -> Optional[int]:
    """
    Ekstrak angka rekomendasi dari teks.

    Prioritas:
    1. Angka digit (paling andal).
    2. Kata angka (dengan toleransi typo ringan).

    Kembalikan None jika tidak ditemukan angka yang valid (1–20).
    """
    match = re.search(r"\b(\d+)\b", text)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 20:
            return num

    text_lower = text.lower()
    for pattern, num in _NUMBER_PATTERNS:
        if re.search(pattern, text_lower):
            return num

    return None


def parse_future_time(text: str) -> Optional[Tuple[datetime, str]]:
    """
    Deteksi ekspresi waktu mendatang dalam teks Bahasa Indonesia.

    Contoh yang didukung:
    - "besok pagi / siang / sore / malam"
    - "nanti malam / siang"
    - "jam 19" / "pukul 12"
    """
    text_lower = text.lower()
    now = get_samarinda_time()

    def _make_target(base: datetime, hour: int) -> datetime:
        """Buat datetime pada jam tertentu; geser +1 hari jika sudah lewat."""
        t = base.replace(hour=hour, minute=0, second=0, microsecond=0)
        if t <= now:
            t += timedelta(days=1)
        return t

    if "besok" in text_lower:
        tomorrow = now + timedelta(days=1)

        if any(k in text_lower for k in ("pagi", "sarapan")):
            return tomorrow.replace(hour=8, minute=0, second=0, microsecond=0), "sarapan besok"
        if any(k in text_lower for k in ("siang", "lunch")):
            return tomorrow.replace(hour=12, minute=0, second=0, microsecond=0), "makan siang besok"
        if "sore" in text_lower:
            return tomorrow.replace(hour=16, minute=0, second=0, microsecond=0), "cemilan sore besok"
        if any(k in text_lower for k in ("malam", "dinner")):
            return tomorrow.replace(hour=19, minute=0, second=0, microsecond=0), "makan malam besok"

        return tomorrow.replace(hour=12, minute=0, second=0, microsecond=0), "besok"

    if ("nanti" in text_lower and "malam" in text_lower) or "malam ini" in text_lower:
        return _make_target(now, 19), "malam ini"

    if "nanti" in text_lower and "siang" in text_lower:
        return _make_target(now, 12), "nanti siang"

    match = re.search(r"(?:jam|pukul)\s*(\d{1,2})", text_lower)
    if match:
        hour = int(match.group(1))
        if 0 <= hour <= 23:
            target = _make_target(now, hour)
            ctx_map = {
                range(5, 10): f"jam {hour} (sarapan)",
                range(10, 15): f"jam {hour} (makan siang)",
                range(15, 18): f"jam {hour} (cemilan sore)",
            }
            context = next(
                (label for r, label in ctx_map.items() if hour in r),
                f"jam {hour} (makan malam)",
            )
            return target, context

    return None