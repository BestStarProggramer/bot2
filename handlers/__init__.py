from aiogram import Router
from handlers.start_handler import router as start_router
from handlers.group_handler import router as group_router
from handlers.subject_handler import router as subject_router
from handlers.lab_handler import router as lab_router
from handlers.queue_handler import router as queue_router
from handlers.swap_handler import router as swap_router
from handlers.verification_handler import router as verification_router

router = Router()
router.include_router(start_router)
router.include_router(group_router)
router.include_router(subject_router)
router.include_router(lab_router)
router.include_router(queue_router)
router.include_router(swap_router)
router.include_router(verification_router)