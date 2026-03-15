import pytest
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import User, Group, Subject, Lab, Priority, Registration, Weight, Queue, QueueEntry, AcademicStudent
from services.user_service import get_or_create_user
from services.group_service import create_group, join_group
from services.subject_service import add_subject
from services.lab_service import create_lab, get_lab_details, close_lab, get_lab_priorities
from services.queue_service import generate_queue_for_lab, register_for_lab, get_queue_details
from services.verification_service import add_student_to_group, get_group_students, claim_student, verify_student
from services.swap_service import create_swap_request, accept_swap_request
from sqlalchemy import select

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    await init_db()
    yield

class MockUser:
    def __init__(self, tg_id, username):
        self.id = tg_id
        self.username = username
        self.first_name = username
        self.last_name = ""

@pytest.mark.asyncio
class TestFullIntegration:
    
    async def test_full_queue_workflow(self):
        user1 = await get_or_create_user(MockUser(777001, "headman"))
        user2 = await get_or_create_user(MockUser(777002, "student1"))
        user3 = await get_or_create_user(MockUser(777003, "student2"))
        
        group = await create_group(user1.id, "Интеграционный Тест")
        await join_group(group.id, user2.id)
        await join_group(group.id, user3.id)
        
        subject = await add_subject(group.id, "Тестовый Предмет")
        
        await add_student_to_group(group.id, "Староста")
        await add_student_to_group(group.id, "Студент Один")
        await add_student_to_group(group.id, "Студент Два")
        
        students = await get_group_students(group.id)
        if len(students) >= 3:
            await claim_student(students[0].id, user1.id)
            await claim_student(students[1].id, user2.id)
            await claim_student(students[2].id, user3.id)
            await verify_student(user1.id, students[0].id, True)
            await verify_student(user2.id, students[1].id, True)
            await verify_student(user3.id, students[2].id, True)
            
            lab = await create_lab(group.id, subject.id, datetime.now() + timedelta(days=7))
            
            priorities = await get_lab_priorities(lab.id)
            assert len(priorities) >= 1
            
            if priorities:
                await register_for_lab(lab.id, user1.id, priorities[0].id)
                await register_for_lab(lab.id, user2.id, priorities[0].id)
                await register_for_lab(lab.id, user3.id, priorities[0].id)
                
                queue = await generate_queue_for_lab(lab.id, user1.id)
                assert queue is not None
                
                queue_details = await get_queue_details(lab.id)
                assert queue_details is not None
            
            await close_lab(lab.id)
            lab_details = await get_lab_details(lab.id)
            assert lab_details["is_closed"] == True
    
    async def test_weight_calculation_across_queues(self):
        user1 = await get_or_create_user(MockUser(777011, "headman2"))
        group = await create_group(user1.id, "Тест Весов")
        subject = await add_subject(group.id, "Предмет Для Весов")
        
        lab1 = await create_lab(group.id, subject.id, datetime.now() + timedelta(days=7))
        lab2 = await create_lab(group.id, subject.id, datetime.now() + timedelta(days=14))
        
        await add_student_to_group(group.id, "Тест Студент")
        students = await get_group_students(group.id)
        if students:
            await claim_student(students[0].id, user1.id)
            await verify_student(user1.id, students[0].id, True)
            
            priorities1 = await get_lab_priorities(lab1.id)
            priorities2 = await get_lab_priorities(lab2.id)
            
            if priorities1 and priorities2:
                await register_for_lab(lab1.id, user1.id, priorities1[0].id)
                await register_for_lab(lab2.id, user1.id, priorities2[0].id)
                
                queue1 = await generate_queue_for_lab(lab1.id, user1.id)
                assert queue1 is not None
                
                async with SessionLocal() as session:
                    result = await session.execute(
                        select(Weight).where(Weight.user_id == user1.id, Weight.subject_id == subject.id)
                    )
                    weight = result.scalar_one_or_none()
                    assert weight is not None
                    assert weight.value > 0