from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.models.department import Department

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
        
        if not department:
            return None  # Return an appropriate response or error if department doesn't exist
        
        # Update department details (you can add additional fields if necessary)
        if not department_new_name or not faultyadmin_id:
            department.faultyadmin_id = faultyadmin_id
        
        # Save the updated department to the database
            await department.update(session, department)
        
            return department
