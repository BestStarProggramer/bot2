import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from services.user_service import get_or_create_user
from services.group_service import create_group
from services.subject_service import add_subject
from services.lab_service import create_lab, get_lab_priorities
from services.queue_service import register_for_lab
from services.verification_service import add_student_to_group, claim_student, verify_student, get_group_students
from services.swap_service import create_swap_request, accept_swap_request, reject_swap_request, get_lab_students_for_swap

class MockUser:
    def __init__(self, tg_id, username):
        self.id = tg_id
        self.username = username
        self.first_name = username
        self.last_name = ""

@pytest_asyncio.fixture
async def setup_lab_with_students():
    user1 = await get_or_create_user(MockUser(888881, "student1"))
    user2 = await get_or_create_user(MockUser(888882, "student2"))
    
    group = await create_group(user1.id, "Swap Test Group")
    subject = await add_subject(group.id, "Swap Test Subject")
    lab = await create_lab(group.id, subject.id, datetime.now() + timedelta(days=7))
    
    await add_student_to_group(group.id, "Студент Один")
    await add_student_to_group(group.id, "Студент Два")
    students = await get_group_students(group.id)
    
    if len(students) >= 2:
        await claim_student(students[0].id, user1.id)
        await claim_student(students[1].id, user2.id)
        await verify_student(user1.id, students[0].id, True)
        await verify_student(user2.id, students[1].id, True)
        
        priorities = await get_lab_priorities(lab.id)
        if priorities:
            await register_for_lab(lab.id, user1.id, priorities[0].id)
            await register_for_lab(lab.id, user2.id, priorities[0].id)
    
    return {"user1": user1, "user2": user2, "group": group, "lab": lab}

@pytest.mark.asyncio
class TestSwapService:
    
    async def test_create_swap_request(self, setup_lab_with_students):
        data = setup_lab_with_students
        swap = await create_swap_request(data["lab"].id, data["user1"].id, data["user2"].id)
        assert swap is not None
        assert swap.status == "pending"
    
    async def test_accept_swap_request(self, setup_lab_with_students):
        data = setup_lab_with_students
        swap = await create_swap_request(data["lab"].id, data["user1"].id, data["user2"].id)
        accepted = await accept_swap_request(swap.id, data["user2"].id)
        assert accepted.status == "accepted"
    
    async def test_reject_swap_request(self, setup_lab_with_students):
        data = setup_lab_with_students
        swap = await create_swap_request(data["lab"].id, data["user1"].id, data["user2"].id)
        rejected = await reject_swap_request(swap.id, data["user2"].id)
        assert rejected.status == "rejected"