import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

# Mapping of raw course strings to distinct course codes and clean titles
# NOTE: rules are matched against a "compact" key with all whitespace removed
# (see map_course_to_code), because the KEA PDF often splits words across
# lines, e.g. "DA TA SCIENCE", "CY BER SECURITY", "AR TIFICIAL".
COURSE_CODE_RULES = [
    # CS Specializations (check specific before general)
    (r"computer\s*science.*artifici?al\s*intelligence.*data\s*science", "CM", "Computer Science and Engineering (AI & Data Science)"),
    (r"computer\s*science.*(artifici?al\s*intelligence|aiml|ai&ml)", "CA", "Computer Science and Engineering (AI & ML)"),
    (r"artifici?al\s*intelligence.*data\s*science", "AD", "Artificial Intelligence and Data Science"),
    (r"artifici?al\s*intelligence.*machine\s*learning|ai\s*&\s*ml", "AI", "Artificial Intelligence and Machine Learning"),
    (r"computer\s*science.*data\s*science", "DS", "Computer Science and Engineering (Data Science)"),
    (r"computer\s*science.*cyber\s*security", "CY", "Computer Science and Engineering (Cyber Security)"),
    (r"computer\s*science.*business\s*systems", "CB", "Computer Science and Business Systems"),
    (r"computer\s*science.*design", "CD", "Computer Science and Design"),
    (r"computer\s*science.*internet\s*of\s*things|computer\s*science.*iot", "CI", "Computer Science and Engineering (IoT)"),
    (r"computer\s*science.*block\s*chain", "BC", "Computer Science and Engineering (Block Chain)"),
    (r"computer\s*science.*cloud", "CC", "Computer Science and Engineering (Cloud Computing)"),
    (r"data\s*science", "DS", "Data Science and Engineering"),
    (r"cyber\s*security", "CY", "Cyber Security Engineering"),
    # Hybrid electronics/electrical + computer programmes must be checked before plain CS
    (r"electronics\s*&?\s*(and)?\s*computer", "EM", "Electronics and Computer Engineering"),
    (r"electrical.*computer", "EK", "Electrical and Computer Engineering"),
    (r"computer\s*science|computer\s*engineering", "CS", "Computer Science and Engineering"),
    (r"information\s*science|information\s*technology", "IS", "Information Science and Engineering"),

    # Electronics & Communication & Allied
    (r"electronics.*telecommunication", "ET", "Electronics and Telecommunication Engineering"),
    (r"electronics.*instrumentation", "EI", "Electronics and Instrumentation Engineering"),
    (r"vlsi", "VL", "Electronics Engineering (VLSI Design and Technology)"),
    (r"medical\s*electronics", "MD", "Medical Electronics Engineering"),
    (r"bio[- ]*medical", "BM", "Biomedical Engineering"),
    (r"electronics.*communication", "EC", "Electronics and Communication Engineering"),
    (r"electrical.*electronics", "EE", "Electrical and Electronics Engineering"),
    (r"electrical", "EE", "Electrical and Electronics Engineering"),

    # Mechanical & Aero
    (r"mechatronics", "MC", "Mechatronics Engineering"),
    (r"robotics.*automation", "RO", "Robotics and Automation"),
    (r"robotics", "RA", "Robotics and Artificial Intelligence"),
    (r"aero\s*space|aerospace", "AS", "Aerospace Engineering"),
    (r"aeronautical", "AE", "Aeronautical Engineering"),
    (r"automobile|automotive", "AU", "Automobile Engineering"),
    (r"industrial\s*iot", "IT", "Industrial IoT"),
    (r"industrial.*management", "IM", "Industrial Engineering and Management"),
    (r"industrial.*production", "IP", "Industrial and Production Engineering"),
    (r"mechanical", "ME", "Mechanical Engineering"),

    # Civil, Chemical, Bio & Others
    (r"civil.*infrastructure", "CN", "Civil and Infrastructure Engineering"),
    (r"civil.*environmental", "CE", "Civil and Environmental Engineering"),
    (r"civil", "CV", "Civil Engineering"),
    (r"chemical", "CH", "Chemical Engineering"),
    (r"bio[- ]*technology", "BT", "Biotechnology Engineering"),
    (r"silk\s*technology", "SK", "Silk Technology"),
    (r"textile", "TX", "Textile Technology"),
    (r"mining", "MN", "Mining Engineering"),
    (r"agriculture|agricultural", "AG", "Agricultural Engineering"),
    (r"fashion\s*design", "FD", "Fashion Design"),
    (r"interior\s*design", "ID", "Interior Design"),
    (r"design", "DE", "Design"),
    (r"planning|b\.?plan", "PL", "Planning (B.Plan)"),
    (r"architecture", "AR", "Architecture"),
]


def normalize_whitespace(text: str) -> str:
    """Normalize inconsistent whitespace and newlines."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_location(college_name: str) -> Tuple[str, str]:
    """
    Extract the clean college name and location from the raw college string.
    Returns (cleaned_name, location).
    """
    cleaned = normalize_whitespace(college_name)
    
    cities = [
        "Bangalore", "Bengaluru", "Mysore", "Mysuru", "Mangalore", "Mangaluru",
        "Belgaum", "Belagavi", "Dharwad", "Hubballi", "Hubli", "Tumkur", "Tumakuru",
        "Davangere", "Davanagere", "Bellary", "Ballari", "Gulbarga", "Kalaburagi",
        "Shimoga", "Shivamogga", "Hassan", "Bidar", "Raichur", "Kolar",
        "Bagalkot", "Bagalkote", "Mandya", "Udupi", "Chikkaballapur",
        "Chamarajanagar", "Koppal", "Gadag", "Yadgir", "Ramanagara",
        "Chitradurga", "Haveri", "Vijayanagara", "Chikkamagaluru", "Karwar"
    ]
    
    location = "Karnataka"
    for city in cities:
        pattern = r"\b" + re.escape(city) + r"\b"
        if re.search(pattern, cleaned, re.IGNORECASE):
            location = city
            break
            
    name_only = cleaned
    name_only = re.sub(r"-\s*\d{5,6}\b", "", name_only)
    name_only = re.sub(r"\b\d{5,6}\b", "", name_only)
    name_only = normalize_whitespace(name_only)
    
    return name_only, location


def map_course_to_code(raw_course_name: str) -> Tuple[str, str]:
    """
    Maps raw course name from PDF to standard course code and standardized name.
    """
    cleaned = normalize_whitespace(raw_course_name)
    # Compact key: lower-case with all whitespace removed, so that words split
    # by the PDF renderer ("DA TA SCIENCE") still match the rules.
    compact = re.sub(r"\s+", "", cleaned.lower())

    for pattern, code, standard_name in COURSE_CODE_RULES:
        if re.search(pattern, compact):
            return code, standard_name
            
    # Fallback: acronym of initials
    words = [w for w in cleaned.split() if w.lower() not in ["and", "&", "in", "of", "the", "b", "tech"]]
    fallback_code = "".join([w[0].upper() for w in words[:3]]) or "ENG"
    return fallback_code, cleaned


_DEGREE_PREFIX = re.compile(r"^\s*b\.?\s*tech\.?\s*(\(hons\))?\s*(in)?\s+", re.IGNORECASE)


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def disambiguate_course_names(raw_names: List[str]) -> Dict[str, Tuple[str, str]]:
    """
    Map each raw course name of ONE college to a (course_code, course_name)
    pair such that distinct raw programmes never share a course_name.

    Several distinct programmes of a college can fall under the same branch
    family (e.g. "COMPUTER ENGINEERING" and "COMPUTER SCIENCE AND ENGINEERING").
    The programme closest to the standard name keeps the standard name; the
    others get the standard name plus their own programme title, so that no
    record overwrites another during database upsert.
    """
    groups: Dict[Tuple[str, str], List[str]] = {}
    for raw in raw_names:
        code, std = map_course_to_code(raw)
        groups.setdefault((code, std), [])
        if raw not in groups[(code, std)]:
            groups[(code, std)].append(raw)

    result: Dict[str, Tuple[str, str]] = {}
    for (code, std), raws in groups.items():
        if len(raws) == 1:
            result[raws[0]] = (code, std)
            continue
        std_key = _compact(std)
        canonical = max(
            raws,
            key=lambda r: (
                SequenceMatcher(None, _compact(_DEGREE_PREFIX.sub("", normalize_whitespace(r))), std_key).ratio(),
                -len(r),
            ),
        )
        for raw in raws:
            if raw == canonical:
                result[raw] = (code, std)
            else:
                title = _DEGREE_PREFIX.sub("", normalize_whitespace(raw)).strip().title()
                result[raw] = (code, f"{std} - {title}")
    return result


def clean_rank_value(val: str) -> Optional[int]:
    """
    Converts raw cutoff string into integer rank.
    Preserves missing values ('--') as None.
    NEVER converts missing value to zero.
    """
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str in ["--", "-", "", "None", "null", "NULL"]:
        return None
    try:
        f_val = float(val_str)
        if f_val <= 0:
            return None
        return int(round(f_val))
    except (ValueError, TypeError):
        return None
