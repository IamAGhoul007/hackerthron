def check_duplicate_receipt(receipt_hash: str, existing_hashes: list):
    """
    Undocumented behavior: Duplicate receipt detection.
    """
    if receipt_hash in existing_hashes:
        return {"warning": "Possible duplicate receipt"}
    return {"status": "ok"}
