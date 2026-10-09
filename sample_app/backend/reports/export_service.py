class ExportService:
    def export_reports(self, format_type: str, date_range_selected: bool, rows: int, excel_flag: bool):
        """
        Export reports to CSV/Excel.
        Export button is disabled until date range selected.
        Exports capped at 10,000 rows.
        Excel requires reports_excel flag.
        Error RPT-429 for too many rows.
        """
        if not date_range_selected:
            raise ValueError("Date range must be selected")
            
        if rows > 10000:
            raise ValueError("Max 10,000 rows allowed. Error: RPT-429")
            
        if format_type == "Excel" and not excel_flag:
            raise ValueError("Excel export not enabled for this tenant")
            
        return {"status": "exported", "format": format_type}
