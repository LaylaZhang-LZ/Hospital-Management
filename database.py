#!/usr/bin/env python3
import psycopg2

#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''
def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    userid = "xxx"
    passwd = "xxx"
    myHost = "xxx"

    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=userid,
                               user=userid,
                               password=passwd,
                               host=myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)

    # return the connection to use
    return conn

'''
Validate staff based on username and password
'''
def checkLogin(login, password):
    conn = openConnection()
    cur = conn.cursor()
    try:
        # Convert both UserName and login to lowercase
        cur.execute("SELECT * FROM Administrator WHERE LOWER(UserName) = LOWER(%s) AND Password = %s", (login, password))
        admin = cur.fetchone()
        if admin:
            # If a matching administrator is found, their details are returned
            userName = admin[0]
            firstName = admin[2]
            lastName = admin[3]
            email = admin[4]
            return [userName, firstName, lastName, email]
        else:
            # If no matching administrator is found, return None
            return None
    except psycopg2.Error as e:
        print("Database error:", e)
        return None
    finally:
        cur.close()
        conn.close()

'''
List all the associated admissions records in the database by staff
'''
def findAdmissionsByAdmin(login):
    conn = openConnection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                AdmissionID,
                AdmissionTypeName,
                DeptName,
                DischargeDate,
                Fee,
                PatientFullName,
                Condition
            FROM get_admissions_by_admin(%s)
        """, (login,))
        admissions = cur.fetchall()

        admission_list = []
        for admission in admissions:
            admission_dict = {
                'admission_id': admission[0] or '',
                'admission_type': admission[1] or '',
                'admission_department': admission[2] or '',
                'discharge_date': admission[3].strftime('%d-%m-%Y') if admission[3] else '',
                'fee': f"{admission[4]:.2f}" if admission[4] is not None else '',
                'patient': admission[5] or '',
                'condition': admission[6] or ''
            }
            admission_list.append(admission_dict)

        return admission_list
    except psycopg2.Error as e:
        print("Database error:", e)
        return []
    finally:
        cur.close()
        conn.close()

'''
Find a list of admissions based on the searchString provided as parameter
See assignment description for search specification
'''
def findAdmissionsByCriteria(searchString):
    conn = openConnection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                AdmissionID,
                AdmissionTypeName,
                DeptName,
                DischargeDate,
                Fee,
                PatientFullName,
                Condition
            FROM get_admissions_by_criteria(%s)
        """, (searchString,))
        admissions = cur.fetchall()

        admission_list = []
        for admission in admissions:
            admission_dict = {
                'admission_id': admission[0] or '',
                'admission_type': admission[1] or '',
                'admission_department': admission[2] or '',
                'discharge_date': admission[3].strftime('%d-%m-%Y') if admission[3] else '',
                'fee': f"{admission[4]:.2f}" if admission[4] is not None else '',
                'patient': admission[5] or '',
                'condition': admission[6] or ''
            }
            admission_list.append(admission_dict)

        return admission_list
    except psycopg2.Error as e:
        print("Database error:", e)
        return []
    finally:
        cur.close()
        conn.close()

'''
Add a new addmission 
'''
def addAdmission(type, department, patient, condition, admin):
    conn = openConnection()
    cur = conn.cursor()
    try:
        # Rename 'type' and 'department' parameters to avoid conflicts with reserved keywords
        type_name = type
        department_name = department
        patient_id = patient

        # Convert input AdmissionTypeName to corresponding AdmissionTypeID, case-insensitive matching
        cur.execute("SELECT AdmissionTypeID FROM AdmissionType WHERE LOWER(AdmissionTypeName) = LOWER(%s)", (type_name,))
        type_result = cur.fetchone()
        if type_result is None:
            print("No matching AdmissionType found for:", type_name)
            return False
        admission_type_id = type_result[0]

        # Convert input DepartmentName to corresponding DeptId, case-insensitive matching
        cur.execute("SELECT DeptId FROM Department WHERE LOWER(DeptName) = LOWER(%s)", (department_name,))
        dept_result = cur.fetchone()
        if dept_result is None:
            print("No matching Department found for:", department_name)
            return False
        department_id = dept_result[0]

        # Check if input PatientID exists, case-insensitive matching
        cur.execute("SELECT PatientID FROM Patient WHERE LOWER(PatientID) = LOWER(%s)", (patient_id,))
        patient_result = cur.fetchone()
        if patient_result is None:
            print("No matching PatientID found for:", patient_id)
            return False
        patient_id_db = patient_result[0]

        # Insert new Admission record
        # Fee and DischargeDate will be NULL as they are not assigned
        cur.execute("""
            INSERT INTO Admission (AdmissionType, Department, Patient, Administrator, Condition)
            VALUES (%s, %s, %s, %s, %s)
        """, (admission_type_id, department_id, patient_id_db, admin, condition))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print("Database error:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

'''
Update an existing admission
'''
def updateAdmission(id, type, department, dischargeDate, fee, patient, condition):
    conn = openConnection()
    cur = conn.cursor()
    try:
        # Rename 'type' and 'department' parameters to avoid conflicts with reserved keywords
        type_name = type
        department_name = department
        patient_id = patient

        # Convert input AdmissionTypeName to corresponding ID, case-insensitive
        cur.execute("SELECT AdmissionTypeID FROM AdmissionType WHERE LOWER(AdmissionTypeName) = LOWER(%s)", (type_name,))
        type_result = cur.fetchone()
        if type_result is None:
            print("No matching AdmissionType found for:", type_name)
            return False
        admission_type_id = type_result[0]

        # Convert input DepartmentName to corresponding ID, case-insensitive
        cur.execute("SELECT DeptId FROM Department WHERE LOWER(DeptName) = LOWER(%s)", (department_name,))
        dept_result = cur.fetchone()
        if dept_result is None:
            print("No matching Department found for:", department_name)
            return False
        department_id = dept_result[0]

        # Check if input PatientID exists, case-insensitive
        cur.execute("SELECT PatientID FROM Patient WHERE LOWER(PatientID) = LOWER(%s)", (patient_id,))
        patient_result = cur.fetchone()
        if patient_result is None:
            print("No matching PatientID found for:", patient_id)
            return False
        patient_id_db = patient_result[0]

        # Set fee to None if empty string, otherwise convert to float
        if fee == '':
            fee = None
        else:
            try:
                fee = float(fee)
            except ValueError:
                print("Invalid fee format:", fee)
                return False

        # Update Admission record
        cur.execute("""
            UPDATE Admission
            SET AdmissionType = %s,
                Department = %s,
                DischargeDate = %s,
                Fee = %s,
                Patient = %s,
                condition = %s
            WHERE AdmissionID = %s
        """, (admission_type_id, department_id, dischargeDate, fee, patient_id_db, condition, id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print("Database error:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()