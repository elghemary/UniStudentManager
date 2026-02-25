# UniStudentManager

## Overview
UniStudentManager is a Python-based application designed to manage university student records efficiently. The project provides a simple interface for adding, viewing, and exporting student data, making it suitable for academic and administrative use. It is structured to be easily extendable and maintainable, with a focus on clarity and usability.

The system supports:
- Adding multiple subjects
- Assigning different teachers to subjects
- Managing both student and teacher records for administrative purposes
- Generating certificates for students upon completion

## Features
- **Student Management:** Add, update, and view student records.
- **Subject Management:** Add multiple subjects for students, not limited to Python. Subjects can be customized as needed.
- **Teacher Management:** Assign different teachers to each subject, allowing for comprehensive administration of both students and teachers.
- **Administration Manager:** Use the application to manage both academic and administrative records, making it suitable for university administration tasks.
- **Certificate Generation:** Generate certificates for students upon successful completion of their courses or requirements.
- **Data Export:** Export student and subject data to CSV and JSON formats for reporting and analysis.
- **Modular Design:** Separation of concerns using models and main application logic.
- **Asset Management:** Organized structure for assets and exported files.

## Project Structure
```
UniStudentManager/
│
├── App.py           # Main application logic and entry point
├── models.py        # Data models and classes for student management
├── assets/          # Directory for static assets (e.g., images, templates)
├── exports/         # Directory for exported data files (CSV, JSON)
│   ├── hi.csv
│   └── hi.json
└── __pycache__/     # Python cache files (auto-generated)
```

## How to Run
1. Ensure you have Python 3.7 or higher installed.
2. Navigate to the project directory:
   ```bash
   cd /path/to/UniStudentManager
   ```
3. Run the application:
   ```bash
   python App.py
   ```

## Usage
- Follow the prompts in the terminal to add or view student records.
- Add multiple subjects for each student and assign teachers to those subjects.
- Manage both student and teacher information for administrative purposes.
- Generate certificates for students at the end of their courses or upon meeting requirements.
- Exported data will be saved in the `exports/` directory in both CSV and JSON formats.

## Customization
- You can extend the `models.py` file to add more features, such as additional subject fields, teacher information, or certificate templates.
- Modify `App.py` to change the application flow, add new commands, or customize certificate generation.

---
**Author:** EL GHEMARY Farah
**Date:** February 25, 2026
**Institution:** Faculty of Science and Technology of Tangier
