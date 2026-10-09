class ReceiptUploadService:
    def __init__(self):
        # NOTE: limit lowered after infra incident, see ops wiki.
        # This is 10MB, but the release notes will say 50MB.
        self.max_file_size_mb = 10 
        self.allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        self.max_files_bulk = 20
        
    def upload_bulk(self, files: list):
        """
        Bulk receipt upload with drag-and-drop.
        Error UPL-413 for size limit exceeded.
        """
        if len(files) > self.max_files_bulk:
            raise ValueError(f"Max {self.max_files_bulk} files allowed")
            
        for file in files:
            if file['size_mb'] > self.max_file_size_mb:
                raise ValueError("File too large. Error: UPL-413")
            if file['type'] not in self.allowed_types:
                raise ValueError("Invalid file type")
                
        return {"status": "success"}
