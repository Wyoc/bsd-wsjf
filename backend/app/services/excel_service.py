import os
from datetime import datetime
from io import BytesIO

import pandas as pd
import xlsxwriter

from app.core.config import settings
from app.models import WSJFItemResponse


class ExcelService:
    def __init__(self):
        self.export_path = settings.EXCEL_EXPORT_PATH
        os.makedirs(self.export_path, exist_ok=True)

    def generate_excel(
        self, items: list[WSJFItemResponse], program_increment: str
    ) -> BytesIO:
        """Generate Excel file from WSJF items.

        Args:
            items (list[WSJFItemResponse]): List of WSJF items to export.
            program_increment (str): Program Increment identifier for the worksheet.

        Returns:
            BytesIO: In-memory Excel file buffer.
        """
        # Create BytesIO buffer for in-memory Excel file
        output = BytesIO()

        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet(f"WSJF {program_increment}")

        # Define formats
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#4472C4",
                "font_color": "white",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )

        high_priority_format = workbook.add_format({"bg_color": "#FFE699", "border": 1})

        normal_format = workbook.add_format({"border": 1})

        number_format = workbook.add_format({"border": 1, "num_format": "0.00"})

        # Define headers
        headers = [
            "ID",
            "Priority",
            "Subject",
            "Description",
            "Business Value",
            "Time Criticality",
            "Risk Reduction",
            "Job Size",
            "WSJF Score",
            "Status",
            "Owner",
            "Team",
            "Program Increment",
            "Created Date",
        ]

        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write data
        for row, item in enumerate(items, start=1):
            # Determine if this is a high priority item (top 25%)
            is_high_priority = item.priority and item.priority <= max(
                1, len(items) // 4
            )
            cell_format = high_priority_format if is_high_priority else normal_format

            # Write each column
            worksheet.write(row, 0, str(item.id), cell_format)
            worksheet.write(row, 1, item.priority or "", cell_format)
            worksheet.write(row, 2, item.subject, cell_format)
            worksheet.write(row, 3, item.description, cell_format)
            worksheet.write(row, 4, item.business_value, cell_format)
            worksheet.write(row, 5, item.time_criticality, cell_format)
            worksheet.write(row, 6, item.risk_reduction, cell_format)
            worksheet.write(row, 7, item.job_size, cell_format)
            worksheet.write(
                row,
                8,
                item.wsjf_score,
                number_format
                if not is_high_priority
                else workbook.add_format(
                    {"bg_color": "#FFE699", "border": 1, "num_format": "0.00"}
                ),
            )
            worksheet.write(row, 9, item.status.value, cell_format)
            worksheet.write(row, 10, item.owner or "", cell_format)
            worksheet.write(row, 11, item.team or "", cell_format)
            worksheet.write(row, 12, item.program_increment, cell_format)
            worksheet.write(
                row, 13, item.created_date.strftime("%Y-%m-%d %H:%M:%S"), cell_format
            )

        # Auto-adjust column widths
        column_widths = [38, 8, 25, 40, 12, 15, 12, 8, 10, 12, 15, 15, 15, 18]
        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)

        # Freeze header row
        worksheet.freeze_panes(1, 0)

        # Add auto-filter
        worksheet.autofilter(0, 0, len(items), len(headers) - 1)

        # Add data validation for scores (if editing is enabled)
        if len(items) > 0:
            # Business Value validation
            worksheet.data_validation(
                1,
                4,
                len(items),
                4,
                {
                    "validate": "integer",
                    "criteria": "between",
                    "minimum": 1,
                    "maximum": 10,
                    "error_message": "Business Value must be between 1 and 10",
                },
            )

            # Time Criticality validation
            worksheet.data_validation(
                1,
                5,
                len(items),
                5,
                {
                    "validate": "integer",
                    "criteria": "between",
                    "minimum": 1,
                    "maximum": 10,
                    "error_message": "Time Criticality must be between 1 and 10",
                },
            )

            # Risk Reduction validation
            worksheet.data_validation(
                1,
                6,
                len(items),
                6,
                {
                    "validate": "integer",
                    "criteria": "between",
                    "minimum": 1,
                    "maximum": 10,
                    "error_message": "Risk Reduction must be between 1 and 10",
                },
            )

            # Job Size validation
            worksheet.data_validation(
                1,
                7,
                len(items),
                7,
                {
                    "validate": "integer",
                    "criteria": "between",
                    "minimum": 1,
                    "maximum": 10,
                    "error_message": "Job Size must be between 1 and 10",
                },
            )

            # Status validation
            worksheet.data_validation(
                1,
                9,
                len(items),
                9,
                {
                    "validate": "list",
                    "source": [
                        "New",
                        "In Progress",
                        "Blocked",
                        "Completed",
                        "Cancelled",
                    ],
                    "error_message": "Please select a valid status",
                },
            )

        # Set print settings
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)  # Fit to 1 page wide

        # Close workbook and get Excel data
        workbook.close()
        output.seek(0)

        return output

    def save_excel_file(
        self, items: list[WSJFItemResponse], program_increment: str
    ) -> str:
        """Save Excel file to disk and return file path.

        Args:
            items (list[WSJFItemResponse]): List of WSJF items to export.
            program_increment (str): Program Increment identifier for the filename.

        Returns:
            str: Absolute path to the saved Excel file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WSJF_{program_increment}_{timestamp}.xlsx"
        filepath = os.path.join(self.export_path, filename)

        # Generate Excel content
        excel_data = self.generate_excel(items, program_increment)

        # Save to file
        with open(filepath, "wb") as f:
            f.write(excel_data.getvalue())

        return filepath

    def create_dataframe(self, items: list[WSJFItemResponse]) -> pd.DataFrame:
        """Convert WSJF items to pandas DataFrame for analysis.

        Args:
            items (list[WSJFItemResponse]): List of WSJF items to convert.

        Returns:
            pd.DataFrame: DataFrame containing WSJF item data.
        """
        data = []
        for item in items:
            data.append(
                {
                    "ID": str(item.id),
                    "Priority": item.priority,
                    "Subject": item.subject,
                    "Description": item.description,
                    "Business Value": item.business_value,
                    "Time Criticality": item.time_criticality,
                    "Risk Reduction": item.risk_reduction,
                    "Job Size": item.job_size,
                    "WSJF Score": item.wsjf_score,
                    "Status": item.status.value,
                    "Owner": item.owner,
                    "Team": item.team,
                    "Program Increment": item.program_increment,
                    "Created Date": item.created_date,
                }
            )

        return pd.DataFrame(data)


# Global service instance
excel_service = ExcelService()
