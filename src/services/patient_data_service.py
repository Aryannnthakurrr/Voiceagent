class PatientDataService:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def get_patient_data(self, patient_id):
        # Logic to retrieve patient data from the database
        query = "SELECT * FROM patients WHERE id = %s"
        cursor = self.database_connection.cursor()
        cursor.execute(query, (patient_id,))
        patient_data = cursor.fetchone()
        cursor.close()
        return patient_data

    def update_patient_data(self, patient_id, data):
        # Logic to update patient data in the database
        query = "UPDATE patients SET name = %s, age = %s, condition = %s WHERE id = %s"
        cursor = self.database_connection.cursor()
        cursor.execute(query, (data['name'], data['age'], data['condition'], patient_id))
        self.database_connection.commit()
        cursor.close()

    def delete_patient_data(self, patient_id):
        # Logic to delete patient data from the database
        query = "DELETE FROM patients WHERE id = %s"
        cursor = self.database_connection.cursor()
        cursor.execute(query, (patient_id,))
        self.database_connection.commit()
        cursor.close()