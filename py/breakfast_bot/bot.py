import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery
import aiohttp
import qrcode
from io import BytesIO

# --- Конфигурация ---
BOT_TOKEN="8371817391:AAHRPLKuCLwPPQTR8RnTaBiOFiZXmb4pV5A"
SUPABASE_URL="https://wajpwzlkxplahlxhtgsx.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndhanB3emxreHBsYWhseGh0Z3N4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTU4NzMyMiwiZXhwIjoyMDc3MTYzMzIyfQ.d8o4I_Gbkg54Sk0vJE8IGcU2NTmY-N1tCPYiKh66z_A"


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Меню на неделю ---
WEEKLY_MENU = {
    0: {"name": "Традиционный", "price": 130, "desc": "Овсяная каша с маслом и сахаром + бутерброд с сыром + чай"},
    1: {"name": "Гречневый", "price": 130, "desc": "Гречка с подливой + хлеб + чай"},
    2: {"name": "Простой омлет", "price": 130, "desc": "Омлет из 2 яиц + бутерброд с колбасой + чай"},
    3: {"name": "Сырниковый", "price": 130, "desc": "Сырники (2 шт) со сметаной/вареньем + компот"},
    4: {"name": "Хот-дог классический", "price": 130, "desc": "Хот-дог + картофель фри + чай"},
    5: {"name": "Зерновая тарелка", "price": 130, "desc": "Смесь круп + овощной микс + яйцо + чай"},
    6: {"name": "Блинный", "price": 130, "desc": "Блины (2 шт) со сгущенкой + яблоко + чай"}
}

# --- Состояния FSM ---
class OrderStates(StatesGroup):
    waiting_for_room = State()
    waiting_for_customization = State()

# --- Вспомогательные функции ---
def get_tomorrow_menu():
    """Получить меню на завтра"""
    tomorrow_weekday = (datetime.now() + timedelta(days=1)).weekday()
    return WEEKLY_MENU.get(tomorrow_weekday, WEEKLY_MENU[0])

async def save_order_to_supabase(order_data):
    """Сохранить заказ в Supabase"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            async with session.post(
                f"{SUPABASE_URL}/rest/v1/orders",
                headers=headers,
                json=order_data
            ) as response:
                if response.status == 201:
                    logger.info(f"Order saved to Supabase: {order_data}")
                    return True
                else:
                    logger.error(f"Supabase error: {await response.text()}")
                    return False
    except Exception as e:
        logger.error(f"Error saving to Supabase: {e}")
        return False

def generate_qr_code(payload):
    """Генерация QR кода для оплаты"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payload)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

# --- Обработчики команд ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🍳 Добро пожаловать в ЕДА.DONSTU! 🍳

Мы доставляем вкусные завтраки прямо в вашу комнату в общежитии №10 ДГТУ.

📋 Как это работает:
1. Выбираете завтрак на завтра до 22:00
2. Указываете номер комнаты
3. Оплачиваете заказ
4. Утром получаете завтрак к указанному времени!

Нажмите кнопку ниже, чтобы посмотреть меню на завтра 👇
    """
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🍽️ Посмотреть меню на завтра", callback_data="show_tomorrow_menu")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)

# --- Обработчики callback-запросов ---
@dp.callback_query(F.data == "show_tomorrow_menu")
async def show_tomorrow_menu(callback: types.CallbackQuery):
    """Показать меню на завтра"""
    tomorrow_menu = get_tomorrow_menu()
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    
    menu_text = f"""
📅 Меню на {tomorrow_date}:

🍽️ <b>{tomorrow_menu['name']}</b>
📝 {tomorrow_menu['desc']}
💰 Цена: {tomorrow_menu['price']} руб.

Хотите заказать этот завтрак?
    """
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Заказать", callback_data="start_order")],
        [types.InlineKeyboardButton(text="⚙️ Настроить порцию", callback_data="customize_order")]
    ])
    
    await callback.message.edit_text(menu_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    """Начать процесс заказа"""
    await callback.message.answer("🏠 Пожалуйста, введите номер вашей комнаты (например: 1001):")
    await state.set_state(OrderStates.waiting_for_room)
    await callback.answer()

@dp.callback_query(F.data == "customize_order")
async def customize_order(callback: types.CallbackQuery, state: FSMContext):
    """Настройка заказа"""
    tomorrow_menu = get_tomorrow_menu()
    
    customization_text = f"""
⚙️ Настройка заказа: {tomorrow_menu['name']}

Вы можете:
• Увеличить порцию основного блюда (+20 руб за 50г)
• Добавить дополнительные бутерброды (+35 руб)
• Добавить булочку (+25 руб)
• Увеличить порцию напитка (+10 руб)

Введите ваши пожелания текстом или просто отправьте '0', если изменения не нужны:
    """
    
    await callback.message.answer(customization_text)
    await state.set_state(OrderStates.waiting_for_customization)
    await callback.answer()

# --- Обработчики состояний ---
@dp.message(OrderStates.waiting_for_room)
async def process_room_number(message: types.Message, state: FSMContext):
    """Обработка номера комнаты"""
    room_number = message.text.strip()
    
    # Простая валидация номера комнаты
    if not room_number.isdigit() or len(room_number) != 4:
        await message.answer("❌ Неверный формат номера комнаты. Введите 4 цифры (например: 1001):")
        return
    
    await state.update_data(room_number=room_number)
    
    # Предлагаем настроить заказ или сразу перейти к оплате
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚙️ Настроить заказ", callback_data="customize_order")],
        [types.InlineKeyboardButton(text="💰 Перейти к оплате", callback_data="proceed_to_payment")]
    ])
    
    await message.answer(f"✅ Номер комнаты {room_number} сохранён!", reply_markup=keyboard)

@dp.message(OrderStates.waiting_for_customization)
async def process_customization(message: types.Message, state: FSMContext):
    """Обработка настроек заказа"""
    customization = message.text.strip()
    
    if customization == '0':
        customization = "Без изменений"
    
    await state.update_data(customization=customization)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💰 Перейти к оплате", callback_data="proceed_to_payment")]
    ])
    
    await message.answer(f"✅ Настройки сохранены: {customization}", reply_markup=keyboard)

@dp.callback_query(F.data == "proceed_to_payment")
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Обработка оплаты"""
    user_data = await state.get_data()
    room_number = user_data.get('room_number')
    customization = user_data.get('customization', 'Без изменений')
    
    tomorrow_menu = get_tomorrow_menu()
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    
    # Подготовка данных для инвойса
    prices = [LabeledPrice(label=tomorrow_menu['name'], amount=tomorrow_menu['price'] * 100)]
    
    # Добавляем стоимость кастомизации если есть
    if customization != 'Без изменений':
        prices.append(LabeledPrice(label=f"Дополнения: {customization}", amount=5000))  # +50 руб за пример
    
    order_description = f"""
Завтрак на {tomorrow_date}
Комната: {room_number}
{'-' * 20}
{tomorrow_menu['name']}
{tomorrow_menu['desc']}
    """
    
    if customization != 'Без изменений':
        order_description += f"\nДополнения: {customization}"
    
    try:
        # Создаем инвойс
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"Завтрак: {tomorrow_menu['name']}",
            description=order_description,
            payload=f"order_{callback.from_user.id}_{datetime.now().timestamp()}",
            provider_token="YOUR_PROVIDER_TOKEN",  # Нужно получить у @BotFather
            currency="RUB",
            prices=prices,
            start_parameter="breakfast_order",
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False
        )
        
        # Сохраняем данные заказа в состоянии
        await state.update_data(
            menu_name=tomorrow_menu['name'],
            total_price=sum(price.amount for price in prices) / 100,
            order_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        await callback.message.answer("❌ Произошла ошибка при создании счёта. Попробуйте позже.")
    
    await callback.answer()

# --- Обработчик предварительной проверки оплаты ---
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Обработка предварительной проверки оплаты"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --- Обработчик успешной оплаты ---
@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message, state: FSMContext):
    """Обработка успешной оплаты"""
    user_data = await state.get_data()
    
    # Подготовка данных для сохранения
    order_data = {
        "user_id": str(message.from_user.id),
        "room_number": user_data.get('room_number'),
        "order_date": user_data.get('order_date'),
        "delivery_time": "08:30",  # Можно сделать выбор времени
        "breakfast_name": user_data.get('menu_name'),
        "total_price": user_data.get('total_price'),
        "customization": user_data.get('customization', 'Без изменений'),
        "created_at": datetime.now().isoformat(),
        "status": "paid"
    }
    
    # Сохраняем в Supabase
    success = await save_order_to_supabase(order_data)
    
    if success:
        confirmation_text = f"""
✅ <b>Заказ успешно оплачен и принят!</b>

📦 <b>Детали заказа:</b>
🍽️ {order_data['breakfast_name']}
🏠 Комната: {order_data['room_number']}
📅 Дата: {order_data['order_date']}
⏰ Время доставки: ~{order_data['delivery_time']}
💰 Сумма: {order_data['total_price']} руб.

Завтрак будет доставлен прямо в вашу комнату утром. Приятного аппетита! 🍴
        """
        
        # Генерация QR кода с номером заказа
        qr_payload = f"EDADONSTU:{message.from_user.id}:{order_data['order_date']}"
        qr_code = generate_qr_code(qr_payload)
        
        await message.answer_photo(
            photo=types.BufferedInputFile(qr_code.read(), filename="qrcode.png"),
            caption=confirmation_text,
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Произошла ошибка при сохранении заказа. Свяжитесь с поддержкой.")
    
    await state.clear()

# --- Запуск бота ---
async def main():
    logger.info("Бот ЕДА.DONSTU запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())