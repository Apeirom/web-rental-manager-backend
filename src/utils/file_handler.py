def verify_file_path(file_path: str) -> bool:
    if not file_path:
        return False
        
    clean_path = file_path.strip().lower()
    
    if "http" not in clean_path and clean_path.endswith(".pdf"):
        return True
        
    return False
