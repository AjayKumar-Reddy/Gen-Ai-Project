import re
from typing import Optional, Tuple

# Mapping of raw course strings to distinct course codes and clean titles
COURSE_CODE_RULES = [
    # CS Specializations (check specific before general)
    (r"artificial\s*intelligence.*data\s*science", "AD", "Artificial Intelligence and Data Science"),
    (r"artificial\s*intelligence.*machine\s*learning|ai\s*&\s*ml", "AI", "Artificial Intelligence and Machine Learning"),
    (r"computer\s*science.*artificial\s*intelligence.*machine\s*learning", "CA", "Computer Science and Engineering (AI & ML)"),
    (r"computer\s*science.*artificial\s*intelligence", "CA", "Computer Science and Engineering (AI & ML)"),
    (r"computer\s*science.*data\s*science", "DS", "Computer Science and Engineering (Data Science)"),
    (r"computer\s*science.*cyber\s*security", "CY", "Computer Science and Engineering (Cyber Security)"),
    (r"computer\s*science.*business\s*systems", "CB", "Computer Science and Business Systems"),
    (r"computer\s*science.*design", "CD", "Computer Science and Design"),
    (r"computer\s*science.*internet\s*of\s*things|computer\s*science.*iot", "CI", "Computer Science and Engineering (IoT)"),
    (r"computer\s*science.*block\s*chain", "BC", "Computer Science and Engineering (Block Chain)"),
    (r"computer\s*science.*cloud", "CC", "Computer Science and Engineering (Cloud Computing)"),
    (r"data\s*science", "DS", "Data Science and Engineering"),
    (r"cyber\s*security", "CY", "Cyber Security Engineering"),
    (r"computer\s*science|computer\s*engineering", "CS", "Computer Science and Engineering"),
    (r"information\s*science|information\s*technology", "IS", "Information Science and Engineering"),

    # Electronics & Communication & Allied
    (r"electronics.*telecommunication", "ET", "Electronics and Telecommunication Engineering"),
    (r"electronics.*instrumentation", "EI", "Electronics and Instrumentation Engineering"),
    (r"electronics.*computer", "EM", "Electronics and Computer Engineering"),
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
    (r"civil.*infrastructure", "CI", "Civil and Infrastructure Engineering"),
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
    (r"planning|b\.plan", "PL", "Planning (B.Plan)"),
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
    cleaned_lower = cleaned.lower()
    
    for pattern, code, standard_name in COURSE_CODE_RULES:
        if re.search(pattern, cleaned_lower):
            return code, standard_name
            
    # Fallback: acronym of initials
    words = [w for w in cleaned.split() if w.lower() not in ["and", "&", "in", "of", "the", "b", "tech"]]
    fallback_code = "".join([w[0].upper() for w in words[:3]]) or "ENG"
    return fallback_code, cleaned


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
