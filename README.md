**FDP MANAGEMENT SYSTEM**
A web-based system to manage and track Faculty Development Programme (FDP) records efficiently.  
It supports role-based access, automated text extraction from uploaded certificates, and search functionality for academic data management.
**FEATURES**
- User registration, login, and password recovery via email  
- Role-based access (Admin/User)  
- Certificate upload with automatic text extraction and categorized storage  
- Search and filter FDP data by name, date, or programme type  
- Export query results to CSV  
- User profile view and edit  
- Admin access for upload and login history tracking  

**TECH STACK**
Frontend: HTML, CSS, JavaScript  
Backend: Python (Flask)  
Database: SQLite  
Libraries: Pandas, pytesseract, datetime  

**INSTALLATION**
1. **CLONE THE REPOSITORY**
   ```bash
   git clone https://github.com/ARADHYA-M/Fdp_Management_System.git
   cd Fdp_Management_System
   ```
2. **CREATE AND ACTIVATE A VIRTUAL ENVIRONMENT**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # For Windows
   source venv/bin/activate   # For macOS/Linux
   ```
3. **INSTALL REQUIRED DEPENDENCIES**
   ```bash
   pip install -r requirements.txt
   ```
4. **RUN THE APPLICATION**
   ```bash
   python app.py
   ```
5. **ACCESS THE SYSTEM**
   Open your browser and go to:  
   ```
   http://127.0.0.1:5000
   ```

**DATABASE TABLES**
- users – stores user details and roles  
- login_history – tracks login/logout times  
- fdp_attended,fdp_conducted,conference_attended,conference_conducted,lecture_conducted – store extracted FDP data  
- extracted_data – saves extracted certificate text  

**ADMIN ACCESS**
- View all uploaded certificates  
- Monitor user login/logout history  
- Manage all FDP records  
