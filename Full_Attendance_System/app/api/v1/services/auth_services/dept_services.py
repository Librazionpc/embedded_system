from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.department import Department

class DepartmentAuthServices:
    
    @staticmethod
    async def register_department(data: dict, session: AsyncSession):
        """
        Register a new department with the department name and faulty admin ID.
        It ensures that the department does not already exist.
        """
        departmentname = data.get("departmentname")
        faultyadmin_id = data.get("faultyadmin_id")
        
        if not departmentname or not faultyadmin_id:
            return None  # Return an appropriate response or error if the input is invalid
        
        # Check if the department already exists
        existing_department = await Department.filter_by(session, departmentname=departmentname)
        if existing_department:
            return None  # Return an appropriate response or error if department exists
        
        # Create a new department entry
        new_dept = Department(departmentname=departmentname, faultyadmin_id=faultyadmin_id)
        
        # Save the department to the database
        await new_dept.new(session, new_dept)
        
        return new_dept
    
    @staticmethod
    async def update_department(data: dict, session: AsyncSession):
        """
        Update the department details by department name.
        """
        departmentname = data.get("departmentname")
        faultyadmin_id = data.get("faultyadmin_id")
        department_new_name = data.get("new_name")
        
        if not departmentname or not faultyadmin_id:
            return None  # Return an appropriate response or error if the input is invalid
        
        # Find the department by department name
        department = await Department.filter_by(session, departmentname=departmentname)
        
        if department:
            if faultyadmin_id:
                department.faultyadmin_id = faultyadmin_id
            elif department_new_name:
                department.departmentname = department_new_name
            # Save the updated department to the database
            await department.update(session, department)
        
            return department
        
        else:
            return None
    @staticmethod   
    async def get_department_details(data: dict, session: AsyncSession):
        """
        Retrieve department details including lecturers and students.
        """
        departmentname = data.get("departmentname")
        
        if not departmentname:
            return {"Error": "field is requred"}
        
        department = await Department.filter_by(session, departmentname=departmentname)
        
        if not department:
            return {"Error": "Department not found"}

        return {
           department.to_dict()
        }

    @staticmethod
    async def delete(data: dict, session):
        departmentemail = data.get("departmentemail")
        if not departmentemail:
            return {"Error : email not provided"}

        department = await Department.filter_by(session=session, email=departmentemail)
        if not department:
            return {"Error: Not Found"}
        return await Department.delete(session, department)
    
