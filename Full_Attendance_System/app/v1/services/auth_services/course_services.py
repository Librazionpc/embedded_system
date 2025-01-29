from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.models.course import Course

class CourseAuthServices:
    
    @staticmethod
    async def register_course(data: dict, session: AsyncSession):
        """
        Register a new course with the course name and faulty admin ID.
        It ensures that the course does not already exist.
        """
        cousrename = data.get("cousrename")
        coursecode = data.get("coursecode")
        department_id = data.get("department_id")
        
        if not coursecode or not department_id:
            return None  # Return an appropriate response or error if the input is invalid
        
        # Check if the course already exists
        existing_course = await Course.filter_by(session, cousrecode=coursecode)
        if existing_course:
            return None  # Return an appropriate response or error if course exists
        
        # Create a new course entry
        new_course = Course(cousrename=cousrename, 
                          coursecode=coursecode,
                          department_id=department_id)
        
        # Save the course to the database
        await new_course.new(session, new_course)
        
        return new_course
    
    @staticmethod
    async def update_course(data: dict, session: AsyncSession):
        """
        Update the course details by course name.
        """
        cousrecode = data.get("cousrecode")
        faultyadmin_id = data.get("faultyadmin_id")
        course_new_course_code = data.get("new_course_code")
        course_new_name = data.get("new_name")
        
        if not cousrecode or not faultyadmin_id:
            return None  # Return an appropriate response or error if the input is invalid
        
        # Find the course by course name
        course = await course.filter_by(session, cousrecode=cousrecode)
        
        if course:
            if faultyadmin_id:
                course.faultyadmin_id = faultyadmin_id
            elif course_new_name:
                course.cousrecode = course_new_name
            elif course_new_course_code:
                course.coursecode = course_new_course_code
            # Save the updated course to the database
            await course.update(session, course)
            return course
        else:
            return None
        
    @staticmethod
    async def delete(data: dict, session):
        cousrecode = data.get("cousrecode")
        if not cousrecode:
            return {"Error : email not provided"}

        course = await Course.filter_by(session=session, cousrecode=cousrecode)
        if not course:
            return {"Error: Not Found"}
        return await Course.delete(session, course)
