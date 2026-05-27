import asyncio
import logging
import json
from typing import Optional, List, Dict, Union
from datetime import datetime, date, timedelta

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, ContentType, 
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import aiosqlite

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "8712539909:AAFZFeVV_BwaJY14CfeW65Nd7rz5D1JFr6M"
# Список ID преподавателей (3 админа)
TEACHER_IDS = [8007732168, 8191523909, 1094295756]
DATABASE = "homework.db"

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def is_teacher(user_id: int) -> bool:
    """Проверка, является ли пользователь преподавателем"""
    return user_id in TEACHER_IDS

async def notify_all_teachers(bot: Bot, text: str, reply_markup=None):
    """Отправить уведомление всем преподавателям"""
    for teacher_id in TEACHER_IDS:
        try:
            await bot.send_message(teacher_id, text, reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Failed to notify teacher {teacher_id}: {e}")

async def send_to_first_available_teacher(bot: Bot, text: str, files: List[str] = None, reply_markup=None):
    """Отправить сообщение первому доступному преподавателю"""
    for teacher_id in TEACHER_IDS:
        try:
            await bot.send_message(teacher_id, text, reply_markup=reply_markup)
            if files:
                for fid in files:
                    try:
                        await bot.send_document(teacher_id, fid)
                    except:
                        try:
                            await bot.send_photo(teacher_id, fid)
                        except:
                            pass
            return teacher_id
        except Exception as e:
            logging.error(f"Failed to send to teacher {teacher_id}: {e}")
    return None

def get_weekdays_dates() -> List[str]:
    """Получить даты текущей и следующей недели (без субботы и воскресенья)"""
    dates = []
    today = date.today()
    
    # Находим начало текущей недели (понедельник)
    days_since_monday = today.weekday()  # 0 = Monday, 6 = Sunday
    current_week_start = today - timedelta(days=days_since_monday)
    
    # Текущая неделя
    for i in range(5):  # Пн-Пт
        d = current_week_start + timedelta(days=i)
        if d >= today:  # Только сегодня и будущие дни
            dates.append(d.strftime("%d.%m.%Y"))
    
    # Следующая неделя
    next_week_start = current_week_start + timedelta(days=7)
    for i in range(5):  # Пн-Пт
        d = next_week_start + timedelta(days=i)
        dates.append(d.strftime("%d.%m.%Y"))
    
    return dates

# ===== СОСТОЯНИЯ =====
class HomeworkSubmission(StatesGroup):
    subject = State()
    task_description = State()
    files = State()
    comment = State()
    confirm = State()

class AttendanceHistoryState(StatesGroup):
    selecting_student = State()

class TeacherTaskState(StatesGroup):
    selecting_student = State()
    entering_date = State()
    entering_subject = State()
    entering_task = State()
    confirming = State()

# ===== БАЗА ДАННЫХ =====
async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        # Создаем таблицу homeworks если не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS homeworks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                student_username TEXT,
                student_name TEXT,
                subject TEXT NOT NULL,
                task_description TEXT,
                file_ids TEXT,
                comment TEXT,
                status TEXT DEFAULT 'pending',
                teacher_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                assigned_by_teacher BOOLEAN DEFAULT 0,
                due_date TEXT,
                assigned_by_teacher_id INTEGER
            )
        """)
        
        # Проверяем и добавляем колонки если их нет
        try:
            await db.execute("SELECT assigned_by_teacher_id FROM homeworks LIMIT 1")
        except aiosqlite.OperationalError:
            await db.execute("ALTER TABLE homeworks ADD COLUMN assigned_by_teacher_id INTEGER")
            logging.info("Added column assigned_by_teacher_id to homeworks")
        
        try:
            await db.execute("SELECT assigned_by_teacher FROM homeworks LIMIT 1")
        except aiosqlite.OperationalError:
            await db.execute("ALTER TABLE homeworks ADD COLUMN assigned_by_teacher BOOLEAN DEFAULT 0")
            logging.info("Added column assigned_by_teacher to homeworks")
        
        try:
            await db.execute("SELECT due_date FROM homeworks LIMIT 1")
        except aiosqlite.OperationalError:
            await db.execute("ALTER TABLE homeworks ADD COLUMN due_date TEXT")
            logging.info("Added column due_date to homeworks")
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                student_name TEXT,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                notified_at TIMESTAMP,
                confirmed_by_teacher BOOLEAN DEFAULT 0,
                confirmed_by_teacher_id INTEGER,
                UNIQUE(student_id, date)
            )
        """)
        
        # Проверяем и добавляем колонки для attendance
        try:
            await db.execute("SELECT confirmed_by_teacher FROM attendance LIMIT 1")
        except aiosqlite.OperationalError:
            await db.execute("ALTER TABLE attendance ADD COLUMN confirmed_by_teacher BOOLEAN DEFAULT 0")
            logging.info("Added column confirmed_by_teacher to attendance")
        
        try:
            await db.execute("SELECT confirmed_by_teacher_id FROM attendance LIMIT 1")
        except aiosqlite.OperationalError:
            await db.execute("ALTER TABLE attendance ADD COLUMN confirmed_by_teacher_id INTEGER")
            logging.info("Added column confirmed_by_teacher_id to attendance")
        
        await db.commit()

async def add_student(user_id: int, username: Optional[str], full_name: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            INSERT OR REPLACE INTO students (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        await db.commit()

async def save_homework(student_id: int, student_username: Optional[str], 
                       student_name: str, subject: str, task_description: str,
                       file_ids: List[str], comment: Optional[str] = None,
                       assigned_by_teacher: bool = False, due_date: Optional[str] = None,
                       assigned_by_teacher_id: Optional[int] = None) -> int:
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("""
            INSERT INTO homeworks 
            (student_id, student_username, student_name, subject, 
             task_description, file_ids, comment, assigned_by_teacher, due_date, assigned_by_teacher_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, student_username, student_name, subject,
              task_description, json.dumps(file_ids), comment,
              assigned_by_teacher, due_date, assigned_by_teacher_id))
        await db.commit()
        return cursor.lastrowid

async def get_homework(homework_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM homeworks WHERE id = ?", (homework_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                data['file_ids'] = json.loads(data['file_ids']) if data['file_ids'] else []
                return data
            return None

async def get_student_homeworks(student_id: int) -> List[Dict]:
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM homeworks WHERE student_id = ? ORDER BY created_at DESC", (student_id,)) as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                data = dict(row)
                data['file_ids'] = json.loads(data['file_ids']) if data['file_ids'] else []
                result.append(data)
            return result

async def update_homework_status(homework_id: int, status: str, teacher_comment: Optional[str] = None, teacher_id: Optional[int] = None):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            UPDATE homeworks 
            SET status = ?, teacher_comment = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, teacher_comment, homework_id))
        await db.commit()

# ===== ФУНКЦИИ ПОСЕЩАЕМОСТИ =====
async def save_attendance_notification(student_id: int, student_name: str, will_attend: bool):
    today = date.today().isoformat()
    status = "notified_yes" if will_attend else "notified_no"
    
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            INSERT OR REPLACE INTO attendance (student_id, student_name, date, status, notified_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, student_name, today, status))
        await db.commit()

async def get_today_attendance() -> List[Dict]:
    today = date.today().isoformat()
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM attendance WHERE date = ? ORDER BY notified_at DESC
        """, (today,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_student_attendance_last_30_days(student_id: int) -> List[Dict]:
    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
    today = date.today().isoformat()
    
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM attendance 
            WHERE student_id = ? AND date >= ? AND date <= ?
            ORDER BY date DESC
        """, (student_id, thirty_days_ago, today)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_student_attendance_stats(student_id: int) -> Dict:
    records = await get_student_attendance_last_30_days(student_id)
    
    total = len(records)
    present = sum(1 for r in records if r['status'] in ('present', 'notified_yes'))
    absent = sum(1 for r in records if r['status'] in ('absent', 'notified_no'))
    confirmed = sum(1 for r in records if r['confirmed_by_teacher'])
    
    return {
        'total_days_marked': total,
        'present': present,
        'absent': absent,
        'confirmed_by_teacher': confirmed,
        'attendance_rate': round((present / total * 100), 1) if total > 0 else 0
    }

async def confirm_attendance_by_teacher(student_id: int, att_date: str, present: bool, teacher_id: Optional[int] = None):
    status = "present" if present else "absent"
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            UPDATE attendance 
            SET status = ?, confirmed_by_teacher = 1, confirmed_by_teacher_id = ?
            WHERE student_id = ? AND date = ?
        """, (status, teacher_id, student_id, att_date))
        await db.commit()

async def get_all_students() -> List[Dict]:
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM students ORDER BY full_name") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ===== КЛАВИАТУРЫ =====
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Сдать домашнее задание")],
            [KeyboardButton(text="📋 Мои задания"), KeyboardButton(text="📅 Посещаемость")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def teacher_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Задание ученику")],
            [KeyboardButton(text="📊 Посещаемость учеников")],
            [KeyboardButton(text="📈 Статистика")]
        ],
        resize_keyboard=True
    )

def subjects_keyboard():
    subjects = [
        "Основы алгоритмизации и программирования",
        "Теория вероятностей и математическая статистика",
        "Элементы высшей математики"
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s)] for s in subjects] + [[KeyboardButton(text="◀️ Назад")]],
        resize_keyboard=True
    )

def attendance_student_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Буду сегодня"), KeyboardButton(text="❌ Не буду сегодня")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )

def attendance_teacher_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Сегодняшняя посещаемость")],
            [KeyboardButton(text="📅 История за месяц")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )

def students_list_keyboard(students: List[Dict], prefix: str = "👤"):
    """Клавиатура со списком учеников"""
    buttons = []
    for student in students:
        name = student['full_name'][:25]
        buttons.append([KeyboardButton(text=f"{prefix} {name}")])
    buttons.append([KeyboardButton(text="◀️ Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def dates_keyboard():
    """Клавиатура с датами (только будни текущей и следующей недели)"""
    dates = get_weekdays_dates()
    buttons = [[KeyboardButton(text=d)] for d in dates]
    buttons.append([KeyboardButton(text="◀️ Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def task_confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Отправить задание"), KeyboardButton(text="❌ Отменить")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Отправить"), KeyboardButton(text="❌ Отменить")],
                  [KeyboardButton(text="◀️ Назад")]],
        resize_keyboard=True
    )

def teacher_actions_keyboard(homework_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{homework_id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{homework_id}")],
        [InlineKeyboardButton(text="💬 Комментарий", callback_data=f"comment_{homework_id}"),
         InlineKeyboardButton(text="📎 Файлы", callback_data=f"files_{homework_id}")]
    ])

def attendance_confirm_keyboard(student_id: int, att_date: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Присутствовал", callback_data=f"att_present_{student_id}_{att_date}"),
         InlineKeyboardButton(text="❌ Отсутствовал", callback_data=f"att_absent_{student_id}_{att_date}")]
    ])

def cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отменить")]], resize_keyboard=True)

def skip_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏭ Пропустить")], [KeyboardButton(text="❌ Отменить")]], resize_keyboard=True)

def done_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="❌ Отменить")]], resize_keyboard=True)

# ===== РОУТЕР =====
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await init_db()
    await add_student(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    if is_teacher(message.from_user.id):
        await message.answer(
            "👨‍🏫 Добро пожаловать, преподаватель!\n\n"
            "📝 Задание ученику — отправить ДЗ\n"
            "📊 Посещаемость — проверить кто придёт\n"
            "📈 Статистика — посмотреть статистику",
            reply_markup=teacher_menu_keyboard()
        )
    else:
        await message.answer(
            "👋 Привет! Я бот для учёбы.\n\n"
            "📚 Сдавай домашки\n"
            "📅 Отмечай посещаемость",
            reply_markup=main_menu_keyboard()
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 Помощь:\n\n"
        "<b>Для студентов:</b>\n"
        "• 📚 Сдать ДЗ — отправить домашку\n"
        "• 📅 Посещаемость — отметить буду/не буду\n"
        "• 📋 Мои задания — статус проверки\n\n"
        "<b>Для преподавателя:</b>\n"
        "• 📝 Задание ученику — отправить ДЗ ученику\n"
        "• 📊 Посещаемость учеников — кто придёт сегодня\n"
        "• 📈 Статистика — статистика посещаемости",
        parse_mode="HTML"
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    kb = teacher_menu_keyboard() if is_teacher(message.from_user.id) else main_menu_keyboard()
    await message.answer("Отменено.", reply_markup=kb)

# ===== ОТПРАВКА ЗАДАНИЯ УЧЕНИКУ =====

@router.message(F.text == "📝 Задание ученику")
async def teacher_assign_task_start(message: Message, state: FSMContext):
    """Начало отправки задания ученику"""
    if not is_teacher(message.from_user.id):
        return
    
    students = await get_all_students()
    
    if not students:
        await message.answer("📭 Нет зарегистрированных учеников")
        return
    
    await state.set_state(TeacherTaskState.selecting_student)
    await message.answer(
        "📝 Выберите ученика для отправки задания:",
        reply_markup=students_list_keyboard(students, prefix="👤")
    )

@router.message(TeacherTaskState.selecting_student, F.text.startswith("👤 "))
async def teacher_select_student_for_task(message: Message, state: FSMContext):
    """Выбран ученик — запрашиваем дату"""
    if not is_teacher(message.from_user.id):
        return
    
    student_name = message.text.replace("👤 ", "").strip()
    
    students = await get_all_students()
    selected_student = None
    for s in students:
        if s['full_name'] == student_name:
            selected_student = s
            break
    
    if not selected_student:
        await message.answer("❌ Ученик не найден. Попробуйте снова.")
        return
    
    await state.update_data(
        selected_student_id=selected_student['user_id'],
        selected_student_name=selected_student['full_name']
    )
    await state.set_state(TeacherTaskState.entering_date)
    
    # Получаем будни текущей и следующей недели
    dates = get_weekdays_dates()
    
    await message.answer(
        f"👤 Ученик: {selected_student['full_name']}\n\n"
        f"📅 Выберите дату сдачи задания (только будни):",
        reply_markup=dates_keyboard()
    )

@router.message(TeacherTaskState.entering_date)
async def teacher_enter_date(message: Message, state: FSMContext):
    """Введена дата — запрашиваем предмет"""
    if message.text == "◀️ Назад":
        await state.clear()
        return await message.answer("Отменено.", reply_markup=teacher_menu_keyboard())
    
    date_str = message.text.strip()
    
    # Проверяем, что дата из списка доступных
    valid_dates = get_weekdays_dates()
    if date_str not in valid_dates:
        await message.answer("❌ Пожалуйста, выберите дату из списка")
        return
    
    await state.update_data(due_date=date_str)
    await state.set_state(TeacherTaskState.entering_subject)
    
    await message.answer(
        f"📅 Дата сдачи: {date_str}\n\n"
        f"📚 Выберите предмет:",
        reply_markup=subjects_keyboard()
    )

@router.message(TeacherTaskState.entering_subject)
async def teacher_enter_subject(message: Message, state: FSMContext):
    """Выбран предмет — запрашиваем текст задания"""
    if message.text == "◀️ Назад":
        await state.clear()
        return await message.answer("Отменено.", reply_markup=teacher_menu_keyboard())
    
    valid_subjects = [
        "Основы алгоритмизации и программирования",
        "Теория вероятностей и математическая статистика",
        "Элементы высшей математики"
    ]
    
    if message.text not in valid_subjects:
        await message.answer("❌ Выберите предмет из списка")
        return
    
    await state.update_data(subject=message.text)
    await state.set_state(TeacherTaskState.entering_task)
    
    await message.answer(
        f"📚 Предмет: {message.text}\n\n"
        f"📝 Введите текст задания:",
        reply_markup=cancel_keyboard()
    )

@router.message(TeacherTaskState.entering_task)
async def teacher_enter_task_text(message: Message, state: FSMContext):
    """Введено задание — показываем предпросмотр"""
    if message.text == "❌ Отменить":
        await state.clear()
        return await message.answer("Отменено.", reply_markup=teacher_menu_keyboard())
    
    await state.update_data(task_description=message.text)
    data = await state.get_data()
    
    preview = (
        f"📋 <b>Предпросмотр задания:</b>\n\n"
        f"👤 Ученик: {data['selected_student_name']}\n"
        f"📅 Сдать до: {data['due_date']}\n"
        f"📚 Предмет: {data['subject']}\n"
        f"📝 Задание:\n{data['task_description'][:500]}\n\n"
        f"Отправить задание ученику?"
    )
    
    await state.set_state(TeacherTaskState.confirming)
    await message.answer(preview, parse_mode="HTML", reply_markup=task_confirm_keyboard())

@router.message(TeacherTaskState.confirming, F.text == "✅ Отправить задание")
async def teacher_send_task_to_student(message: Message, state: FSMContext, bot: Bot):
    """Отправка задания ученику"""
    data = await state.get_data()
    
    student_id = data['selected_student_id']
    student_name = data['selected_student_name']
    due_date = data['due_date']
    subject = data['subject']
    task_description = data['task_description']
    teacher_id = message.from_user.id
    
    # Сохраняем в БД
    homework_id = await save_homework(
        student_id=student_id,
        student_username=None,
        student_name=student_name,
        subject=subject,
        task_description=task_description,
        file_ids=[],
        comment=f"Сдать до: {due_date}",
        assigned_by_teacher=True,
        due_date=due_date,
        assigned_by_teacher_id=teacher_id
    )
    
    # Отправляем ученику
    student_text = (
        f"🆕 <b>Новое задание от преподавателя!</b>\n\n"
        f"🆔 Номер: #{homework_id}\n"
        f"📚 Предмет: {subject}\n"
        f"📅 Сдать до: {due_date}\n\n"
        f"📝 Задание:\n{task_description}\n\n"
        f"Отправьте решение через кнопку «📚 Сдать домашнее задание»"
    )
    
    try:
        await bot.send_message(student_id, student_text, parse_mode="HTML")
        
        await message.answer(
            f"✅ Задание #{homework_id} отправлено!\n\n"
            f"👤 Ученик: {student_name}\n"
            f"📅 Дата сдачи: {due_date}\n"
            f"📚 Предмет: {subject}",
            reply_markup=teacher_menu_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить задание: {e}\n"
            f"Возможно, ученик не начал диалог с ботом.",
            reply_markup=teacher_menu_keyboard()
        )
    
    await state.clear()

@router.message(TeacherTaskState.confirming, F.text == "❌ Отменить")
async def teacher_cancel_task(message: Message, state: FSMContext):
    """Отмена отправки задания"""
    await state.clear()
    await message.answer("Отправка отменена.", reply_markup=teacher_menu_keyboard())

# ===== ПОСЕЩАЕМОСТЬ СТУДЕНТ =====

@router.message(F.text == "📅 Посещаемость")
async def student_attendance_menu(message: Message):
    today = date.today().isoformat()
    history = await get_student_attendance_last_30_days(message.from_user.id)
    
    today_record = None
    for record in history:
        if record['date'] == today:
            today_record = record
            break
    
    if today_record:
        status_text = {
            "notified_yes": "✅ Вы отметили: БУДУ",
            "notified_no": "❌ Вы отметили: НЕ БУДУ",
            "present": "✅ Подтверждено: БЫЛ",
            "absent": "❌ Подтверждено: ОТСУТСТВОВАЛ"
        }.get(today_record['status'], "⏳ Неизвестно")
        
        await message.answer(
            f"📅 Сегодня ({date.today().strftime('%d.%m.%Y')}):\n{status_text}\n\n"
            f"Хотите изменить?",
            reply_markup=attendance_student_keyboard()
        )
    else:
        await message.answer(
            f"📅 Сегодня {date.today().strftime('%d.%m.%Y')}\n\n"
            f"Вы сегодня будете на занятии?",
            reply_markup=attendance_student_keyboard()
        )

@router.message(F.text == "✅ Буду сегодня")
async def student_attendance_yes(message: Message, bot: Bot):
    await save_attendance_notification(
        message.from_user.id,
        message.from_user.full_name,
        will_attend=True
    )
    
    await notify_teachers_about_attendance(bot, message.from_user, will_attend=True)
    
    await message.answer(
        "✅ Отлично! Ждём вас на занятии.\n\n"
        "Учитель получил уведомление.",
        reply_markup=main_menu_keyboard()
    )

@router.message(F.text == "❌ Не буду сегодня")
async def student_attendance_no(message: Message, bot: Bot):
    await save_attendance_notification(
        message.from_user.id,
        message.from_user.full_name,
        will_attend=False
    )
    
    await notify_teachers_about_attendance(bot, message.from_user, will_attend=False)
    
    await message.answer(
        "❌ Поняли. Желаем скорее выздороветь/разобраться с делами.\n\n"
        "Учитель получил уведомление.",
        reply_markup=main_menu_keyboard()
    )

async def notify_teachers_about_attendance(bot: Bot, student, will_attend: bool):
    """Уведомить всех преподавателей о посещаемости"""
    status = "✅ БУДЕТ" if will_attend else "❌ НЕ БУДЕТ"
    
    text = (
        f"📅 Новая отметка посещаемости!\n\n"
        f"👤 {student.full_name} (@{student.username or 'нет'})\n"
        f"📆 {date.today().strftime('%d.%m.%Y')}\n"
        f"Статус: {status}"
    )
    
    await notify_all_teachers(bot, text)

# ===== ПОСЕЩАЕМОСТЬ ПРЕПОДАВАТЕЛЬ =====

@router.message(F.text == "📊 Посещаемость учеников")
async def teacher_attendance_menu(message: Message):
    if not is_teacher(message.from_user.id):
        return
    
    await message.answer(
        "📊 Управление посещаемостью\n\n"
        "Выберите действие:",
        reply_markup=attendance_teacher_keyboard()
    )

@router.message(F.text == "📋 Сегодняшняя посещаемость")
async def teacher_today_attendance(message: Message):
    if not is_teacher(message.from_user.id):
        return
    
    today = date.today()
    attendance = await get_today_attendance()
    
    if not attendance:
        await message.answer(
            f"📅 {today.strftime('%d.%m.%Y')}\n\n"
            f"📭 Пока никто не отметился\n\n"
            f"Студенты могут отметиться через кнопку «📅 Посещаемость»"
        )
        return
    
    will_come = []
    wont_come = []
    not_marked = []
    
    all_students = await get_all_students()
    marked_ids = {a['student_id'] for a in attendance}
    
    for student in all_students:
        if student['user_id'] not in marked_ids:
            not_marked.append(student)
    
    for record in attendance:
        if record['status'] in ('notified_yes', 'present'):
            will_come.append(record)
        else:
            wont_come.append(record)
    
    text = f"📅 Посещаемость на {today.strftime('%d.%m.%Y')}\n\n"
    
    text += f"✅ Будут ({len(will_come)}):\n"
    for s in will_come:
        confirmed = "✓" if s['status'] == 'present' else "⏳"
        text += f"  {confirmed} {s['student_name']}\n"
    
    text += f"\n❌ Не будут ({len(wont_come)}):\n"
    for s in wont_come:
        confirmed = "✓" if s['status'] == 'absent' else "⏳"
        text += f"  {confirmed} {s['student_name']}\n"
    
    if not_marked:
        text += f"\n⏳ Не отметились ({len(not_marked)}):\n"
        for s in not_marked:
            text += f"  • {s['full_name']}\n"
    
    text += f"\n📊 Итого: {len(will_come)}/{len(all_students)} ожидается"
    
    await message.answer(text)
    
    if will_come or wont_come:
        await message.answer(
            "Для подтверждения фактического присутствия нажмите на студента:",
            reply_markup=attendance_check_keyboard(attendance)
        )

def attendance_check_keyboard(attendance_list: List[Dict]):
    buttons = []
    for record in attendance_list:
        student_id = record['student_id']
        att_date = record['date']
        name = record['student_name'][:20]
        status = "✓" if record['confirmed_by_teacher'] else "?"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {name}", 
                callback_data=f"check_att_{student_id}_{att_date}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data.startswith("check_att_"))
async def show_attendance_details(callback: CallbackQuery):
    parts = callback.data.split("_")
    student_id = int(parts[2])
    att_date = parts[3]
    
    history = await get_student_attendance_last_30_days(student_id)
    record = None
    for h in history:
        if h['date'] == att_date:
            record = h
            break
    
    if not record:
        await callback.answer("Запись не найдена")
        return
    
    text = (
        f"👤 {record['student_name']}\n"
        f"📆 {record['date']}\n"
        f"📝 Отметил: {'✅ Буду' if record['status'] in ('notified_yes', 'present') else '❌ Не буду'}\n"
        f"⏰ Время: {record['notified_at'][:16] if record['notified_at'] else 'неизвестно'}\n\n"
        f"Подтвердите фактическое присутствие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=attendance_confirm_keyboard(student_id, att_date)
    )

@router.callback_query(F.data.startswith("att_present_"))
async def confirm_present(callback: CallbackQuery):
    parts = callback.data.split("_")
    student_id = int(parts[2])
    att_date = parts[3]
    
    teacher_id = callback.from_user.id
    
    await confirm_attendance_by_teacher(student_id, att_date, present=True, teacher_id=teacher_id)
    await callback.answer("✅ Присутствие подтверждено")
    await callback.message.edit_text(callback.message.text + "\n\n✅ ПОДТВЕРЖДЕНО: БЫЛ")

@router.callback_query(F.data.startswith("att_absent_"))
async def confirm_absent(callback: CallbackQuery):
    parts = callback.data.split("_")
    student_id = int(parts[2])
    att_date = parts[3]
    
    teacher_id = callback.from_user.id
    
    await confirm_attendance_by_teacher(student_id, att_date, present=False, teacher_id=teacher_id)
    await callback.answer("❌ Отсутствие подтверждено")
    await callback.message.edit_text(callback.message.text + "\n\n❌ ПОДТВЕРЖДЕНО: ОТСУТСТВОВАЛ")

# ===== ИСТОРИЯ ЗА МЕСЯЦ =====

@router.message(F.text == "📅 История за месяц")
async def teacher_attendance_history_start(message: Message, state: FSMContext):
    if not is_teacher(message.from_user.id):
        return
    
    students = await get_all_students()
    
    if not students:
        await message.answer("📭 Нет зарегистрированных учеников")
        return
    
    await state.set_state(AttendanceHistoryState.selecting_student)
    await message.answer(
        "📅 Выберите ученика для просмотра посещаемости за последние 30 дней:",
        reply_markup=students_list_keyboard(students)
    )

@router.message(AttendanceHistoryState.selecting_student, F.text.startswith("👤 "))
async def show_student_history(message: Message, state: FSMContext):
    if not is_teacher(message.from_user.id):
        return
    
    if message.text == "◀️ Назад":
        await state.clear()
        return await message.answer("Главное меню:", reply_markup=teacher_menu_keyboard())
    
    student_name = message.text.replace("👤 ", "").strip()
    
    students = await get_all_students()
    selected_student = None
    for s in students:
        if s['full_name'] == student_name:
            selected_student = s
            break
    
    if not selected_student:
        await message.answer("❌ Ученик не найден. Попробуйте снова.")
        return
    
    student_id = selected_student['user_id']
    
    history = await get_student_attendance_last_30_days(student_id)
    stats = await get_student_attendance_stats(student_id)
    
    text = f"📊 Посещаемость: {selected_student['full_name']}\n"
    text += f"📅 За последние 30 дней\n\n"
    
    text += f"📈 Статистика:\n"
    text += f"• Всего отметок: {stats['total_days_marked']}\n"
    text += f"✅ Был/Будет: {stats['present']} ({stats['attendance_rate']}%)\n"
    text += f"❌ Отсутствовал: {stats['absent']}\n"
    text += f"✓ Подтверждено учителем: {stats['confirmed_by_teacher']}\n\n"
    
    if history:
        text += f"📋 Детальный список ({len(history)} записей):\n\n"
        
        current_month = None
        for record in history:
            record_date = datetime.fromisoformat(record['date'])
            month_name = record_date.strftime("%B %Y")
            
            if month_name != current_month:
                current_month = month_name
                text += f"\n📆 {month_name}:\n"
            
            day = record_date.strftime("%d.%m")
            status_emoji = {
                'present': '✅',
                'absent': '❌',
                'notified_yes': '🟢',
                'notified_no': '🔴'
            }.get(record['status'], '❓')
            
            confirmed = "✓" if record['confirmed_by_teacher'] else "⏳"
            text += f"  {status_emoji} {day} — {confirmed}\n"
    else:
        text += "📭 Нет записей за последние 30 дней"
    
    await message.answer(text, reply_markup=attendance_teacher_keyboard())
    await state.clear()

# ===== СДАЧА ДЗ СТУДЕНТОМ =====

@router.message(F.text == "📚 Сдать домашнее задание")
async def start_homework(message: Message, state: FSMContext):
    homeworks = await get_student_homeworks(message.from_user.id)
    pending_teacher_tasks = [h for h in homeworks if h['assigned_by_teacher'] and h['status'] == 'pending']
    
    if pending_teacher_tasks:
        text = "📝 <b>У вас есть задания от преподавателя:</b>\n\n"
        for h in pending_teacher_tasks[:5]:
            text += f"🆔 #{h['id']} — {h['subject']}\n"
            text += f"📅 Сдать до: {h['due_date'] or 'не указана'}\n"
            text += f"📝 {h['task_description'][:100]}...\n\n"
        text += "Выберите предмет для сдачи:"
    else:
        text = "Выберите предмет:"
    
    await state.set_state(HomeworkSubmission.subject)
    await message.answer(text, parse_mode="HTML", reply_markup=subjects_keyboard())

@router.message(HomeworkSubmission.subject)
async def process_subject(message: Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await state.clear()
        return await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
    
    await state.update_data(subject=message.text)
    await state.set_state(HomeworkSubmission.task_description)
    await message.answer("📝 Опишите выполненное задание:", reply_markup=cancel_keyboard())

@router.message(HomeworkSubmission.task_description)
async def process_description(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        return await cmd_cancel(message, state)
    
    await state.update_data(task_description=message.text)
    await state.set_state(HomeworkSubmission.files)
    await message.answer("📎 Отправьте файлы с решением. Когда закончите — «✅ Готово»:", reply_markup=done_keyboard())

@router.message(HomeworkSubmission.files, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.AUDIO, ContentType.VOICE}))
async def process_file(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get('files', [])
    
    file_id = (message.photo[-1].file_id if message.photo else 
               message.document.file_id if message.document else
               message.video.file_id if message.video else
               message.audio.file_id if message.audio else
               message.voice.file_id)
    
    files.append(file_id)
    await state.update_data(files=files)
    await message.answer(f"✅ Файл добавлен (всего: {len(files)})")

@router.message(HomeworkSubmission.files, F.text == "✅ Готово")
async def finish_files(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('files'):
        return await message.answer("❌ Нужен хотя бы один файл!")
    
    await state.set_state(HomeworkSubmission.comment)
    await message.answer("💬 Комментарий (или «⏭ Пропустить»):", reply_markup=skip_keyboard())

@router.message(HomeworkSubmission.comment)
async def process_comment(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        return await cmd_cancel(message, state)
    
    comment = None if message.text == "⏭ Пропустить" else message.text
    await state.update_data(comment=comment)
    data = await state.get_data()
    
    preview = (f"📋 Предпросмотр:\n\n📚 {data['subject']}\n📝 {data['task_description'][:100]}...\n"
               f"📎 Файлов: {len(data['files'])}\n💬 Комментарий: {comment or 'Нет'}\n\nВсё верно?")
    
    await state.set_state(HomeworkSubmission.confirm)
    await message.answer(preview, reply_markup=confirm_keyboard())

@router.message(HomeworkSubmission.confirm, F.text == "✅ Отправить")
async def confirm_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    homework_id = await save_homework(
        message.from_user.id, message.from_user.username, message.from_user.full_name,
        data['subject'], data['task_description'], data['files'], data.get('comment')
    )
    
    text = (f"🆕 Новое задание #{homework_id}!\n👤 {message.from_user.full_name}\n"
            f"📚 {data['subject']}\n📝 {data['task_description'][:200]}...")
    
    await send_to_first_available_teacher(
        bot, 
        text, 
        files=data['files'], 
        reply_markup=teacher_actions_keyboard(homework_id)
    )
    
    await state.clear()
    await message.answer(f"✅ Задание #{homework_id} отправлено!", reply_markup=main_menu_keyboard())

@router.message(HomeworkSubmission.confirm, F.text == "❌ Отменить")
async def cancel_send(message: Message, state: FSMContext):
    await cmd_cancel(message, state)

# ===== ПРОСМОТР ЗАДАНИЙ =====

@router.message(F.text == "📋 Мои задания")
async def my_homeworks(message: Message):
    homeworks = await get_student_homeworks(message.from_user.id)
    if not homeworks:
        return await message.answer("📭 Нет заданий")
    
    text = "📋 Ваши задания:\n\n"
    for hw in homeworks[:10]:
        emoji = {'pending': '⏳', 'accepted': '✅', 'rejected': '❌'}.get(hw['status'], '❓')
        assigned = "👨‍🏫 " if hw.get('assigned_by_teacher') else ""
        text += f"{emoji} {assigned}#{hw['id']} - {hw['subject'][:25]}... ({hw['status']})\n"
        if hw.get('due_date'):
            text += f"📅 Сдать до: {hw['due_date']}\n"
        if hw['teacher_comment']:
            text += f"💬 {hw['teacher_comment']}\n"
        text += "\n"
    await message.answer(text)

# ===== ПРЕПОДАВАТЕЛЬ ДЗ =====

@router.message(F.text == "📈 Статистика")
async def teacher_stats(message: Message):
    if not is_teacher(message.from_user.id):
        return
    
    students = await get_all_students()
    if not students:
        return await message.answer("📭 Нет данных")
    
    text = "📈 Общая статистика посещаемости (30 дней):\n\n"
    
    for student in students:
        stats = await get_student_attendance_stats(student['user_id'])
        emoji = "🟢" if stats['attendance_rate'] >= 80 else "🟡" if stats['attendance_rate'] >= 50 else "🔴"
        text += f"{emoji} {student['full_name'][:20]}: {stats['present']}/{stats['total_days_marked']} ({stats['attendance_rate']}%)\n"
    
    await message.answer(text)

@router.callback_query(F.data.startswith("accept_"))
async def accept_homework(callback: CallbackQuery, bot: Bot):
    hw_id = int(callback.data.split("_")[1])
    teacher_id = callback.from_user.id
    await update_homework_status(hw_id, "accepted", "Принято", teacher_id)
    hw = await get_homework(hw_id)
    if hw:
        await bot.send_message(hw['student_id'], f"✅ Задание #{hw_id} принято!")
    await callback.answer("Принято!")

@router.callback_query(F.data.startswith("reject_"))
async def reject_homework(callback: CallbackQuery, bot: Bot):
    hw_id = int(callback.data.split("_")[1])
    teacher_id = callback.from_user.id
    await update_homework_status(hw_id, "rejected", "Отклонено", teacher_id)
    hw = await get_homework(hw_id)
    if hw:
        await bot.send_message(hw['student_id'], f"❌ Задание #{hw_id} отклонено")
    await callback.answer("Отклонено!")

# ===== НАЗАД =====

@router.message(F.text == "◀️ Назад")
async def go_back(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()
    
    if current_state and "TeacherTaskState" in str(current_state):
        kb = teacher_menu_keyboard()
    elif is_teacher(message.from_user.id):
        kb = teacher_menu_keyboard()
    else:
        kb = main_menu_keyboard()
    
    await message.answer("Главное меню:", reply_markup=kb)

@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    await cmd_help(message)

# ===== ЗАПУСК =====
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Бот запущен!")
    print(f"👨‍🏫 Преподавателей: {len(TEACHER_IDS)}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())