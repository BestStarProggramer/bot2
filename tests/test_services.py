import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import User, Group, GroupMember, Subject, Lab, Priority, Registration, Weight, AcademicStudent
from services.user_service import get_or_create_user, update_user_gender
from services.group_service import create_group, get_group_by_code, join_group, get_user_groups
from services.subject_service import add_subject, get_group_subjects
from services.lab_service import create_lab, get_group_labs, get_lab_details, close_lab, get_lab_priorities
from services.queue_service import generate_queue_for_lab, calculate_new_weight, register_for_lab
from services.verification_service import add_student_to_group, get_group_students, claim_student, verify_student

class MockUser:
    def __init__(self, tg_id, username):
        self.id = tg_id
        self.username = username
        self.first_name = username
        self.last_name = ""

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    await init_db()
    yield

@pytest.mark.asyncio
class TestUserService:
    
    async def test_get_or_create_user(self):
        user = await get_or_create_user(MockUser(123456, "test_user"))
        assert user is not None
        assert user.telegram_id == 123456
        assert user.username == "test_user"

@pytest.mark.asyncio
class TestGroupService:
    
    async def test_create_group(self):
        user = await get_or_create_user(MockUser(222222, "owner"))
        group = await create_group(user.id, "Test Group")
        assert group is not None
        assert group.name == "Test Group"
        assert group.invite_code is not None
    
    async def test_get_group_by_code(self):
        user = await get_or_create_user(MockUser(222223, "owner2"))
        group = await create_group(user.id, "Test Group 2")
        found_group = await get_group_by_code(group.invite_code)
        assert found_group is not None
    
    async def test_join_group(self):
        user1 = await get_or_create_user(MockUser(222224, "owner3"))
        user2 = await get_or_create_user(MockUser(222225, "member"))
        group = await create_group(user1.id, "Test Group 3")
        member = await join_group(group.id, user2.id)
        assert member is not None
        assert member.role == "student"

@pytest.mark.asyncio
class TestSubjectService:
    
    async def test_add_subject(self):
        user = await get_or_create_user(MockUser(333333, "owner4"))
        group = await create_group(user.id, "Test Group 4")
        subject = await add_subject(group.id, "Программирование")
        assert subject is not None
        assert subject.name == "Программирование"
    
    async def test_get_group_subjects(self):
        user = await get_or_create_user(MockUser(333334, "owner5"))
        group = await create_group(user.id, "Test Group 5")
        await add_subject(group.id, "Предмет 1")
        await add_subject(group.id, "Предмет 2")
        subjects = await get_group_subjects(group.id)
        assert len(subjects) == 2

@pytest.mark.asyncio
class TestLabService:
    
    async def test_create_lab(self):
        user = await get_or_create_user(MockUser(444444, "owner6"))
        group = await create_group(user.id, "Test Group 6")
        subject = await add_subject(group.id, "Предмет для лабы")
        lab_date = datetime.now() + timedelta(days=7)
        lab = await create_lab(group.id, subject.id, lab_date)
        assert lab is not None
        assert lab.is_closed == False
    
    async def test_get_group_labs(self):
        user = await get_or_create_user(MockUser(444445, "owner7"))
        group = await create_group(user.id, "Test Group 7")
        subject = await add_subject(group.id, "Предмет")
        await create_lab(group.id, subject.id, datetime.now() + timedelta(days=7))
        await create_lab(group.id, subject.id, datetime.now() + timedelta(days=14))
        labs = await get_group_labs(group.id)
        assert len(labs) == 2
    
    async def test_close_lab(self):
        user = await get_or_create_user(MockUser(444446, "owner8"))
        group = await create_group(user.id, "Test Group 8")
        subject = await add_subject(group.id, "Предмет")
        lab = await create_lab(group.id, subject.id, datetime.now() + timedelta(days=7))
        closed_lab = await close_lab(lab.id)
        assert closed_lab.is_closed == True

@pytest.mark.asyncio
class TestVerificationService:
    
    async def test_add_student_to_group(self):
        user = await get_or_create_user(MockUser(666666, "owner11"))
        group = await create_group(user.id, "Test Group 11")
        student = await add_student_to_group(group.id, "Иванов Иван")
        assert student is not None
        assert student.full_name == "Иванов Иван"