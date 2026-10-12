Database Migration
_____________________
.\env\Scripts\activate 
cd .\crm\
pip install pyodbc mssql-django  
python .\manage.py migrate  
python manage.py makemigrations  
