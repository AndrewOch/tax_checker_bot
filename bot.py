from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

import keyboard as kb
import search_domain
import search_inn
import validation
from config import TOKEN
from data import START, ENTER_INN, ENTER_DOMAIN, MENU_INN, MENU_DOMAIN, BACK_TO_MENU, MENU_MESSAGE, LICENSES, \
    ARBITRATION, ENFORCEMENT, REVISIONS

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    keyboard = kb.create_keyboard_start()
    await message.reply(START, reply_markup=keyboard)
    await state.finish()
    await state.update_data(current_page='menu')


@dp.message_handler()
async def message_catcher(message: types.Message, state: FSMContext):
    if message.text == MENU_INN:
        await to_inn(message, state)
        return
    if message.text == MENU_DOMAIN:
        await to_domain(message, state)
        return
    if message.text == BACK_TO_MENU:
        await to_menu(message, state)
        return
    if message.text == LICENSES:
        await to_licenses(message, state)
        return
    if message.text == ARBITRATION:
        await to_arbitrary(message, state)
        return
    if message.text == ENFORCEMENT:
        await to_enforcement(message, state)
        return
    if message.text == REVISIONS:
        await to_revisions(message, state)
        return
    data = await state.get_data()
    current_page = data.get('current_page')
    if current_page == "menu":
        return
    if current_page == "inn":
        await process_inn(message, state)
        return
    if current_page == "domain":
        await process_domain(message)
        return


async def to_menu(message: types.Message, state: FSMContext):
    keyboard = kb.create_keyboard_start()
    await message.reply(MENU_MESSAGE, reply_markup=keyboard)
    await state.finish()
    await state.update_data(current_page='menu')


async def to_inn(message: types.Message, state: FSMContext):
    keyboard = kb.create_keyboard_domain()
    await message.reply(ENTER_INN, reply_markup=keyboard)
    await state.finish()
    await state.update_data(current_page='inn')


async def to_domain(message: types.Message, state: FSMContext):
    keyboard = kb.create_keyboard_domain()
    await message.reply(ENTER_DOMAIN, reply_markup=keyboard)
    await state.finish()
    await state.update_data(current_page='domain')


async def process_inn(message: types.Message, state: FSMContext):
    search_text = message.text
    if validation.validate_inn(search_text):
        output, contragent_id = search_inn.search(search_text)
        if output == "":
            reply = "Ничего не найдено"
            keyboard = kb.create_keyboard_domain()
        else:
            reply = output
            keyboard = kb.create_keyboard_inn()
            await state.update_data(current_contragent=contragent_id)
    else:
        reply = "Некорректный ИНН"
        keyboard = kb.create_keyboard_domain()
    await message.reply(reply, reply_markup=keyboard)


async def process_domain(message: types.Message):
    keyboard = kb.create_keyboard_domain()
    search_text = message.text
    output = search_domain.search(search_text)
    if output == "":
        reply = "Ничего не найдено"
    else:
        reply = output
    await message.reply(reply, reply_markup=keyboard)


async def to_licenses(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_contragent = data.get('current_contragent')

    output, count = search_inn.search_licenses(current_contragent, 1)
    await state.update_data(total_licenses_count=count, current_license_index=1,
                            current_licenses=output, current_licenses_page=1)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="licenses_prev"),
                 InlineKeyboardButton(f"1 / {count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="licenses_next"))
    await message.reply(output[0], reply_markup=keyboard)


async def to_arbitrary(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_contragent = data.get('current_contragent')

    output, count = search_inn.search_arbitrary(current_contragent, 1)
    await state.update_data(total_arbitrary_count=count, current_arbitrary_index=1,
                            current_arbitrary=output, current_arbitrary_page=1)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="arbitrary_prev"),
                 InlineKeyboardButton(f"1 / {count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="arbitrary_next"))
    await message.reply(output[0], reply_markup=keyboard)


async def to_enforcement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_contragent = data.get('current_contragent')

    output, count = search_inn.search_enforcement(current_contragent, 1)
    await state.update_data(total_enforcement_count=count, current_enforcement_index=1,
                            current_enforcement=output, current_enforcement_page=1)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="enforcement_prev"),
                 InlineKeyboardButton(f"1 / {count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="enforcement_next"))
    await message.reply(output[0], reply_markup=keyboard)


async def to_revisions(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_contragent = data.get('current_contragent')

    output, count = search_inn.search_revisions(current_contragent, 1)
    await state.update_data(total_revisions_count=count, current_revision_index=1,
                            current_revisions=output, current_revisions_page=1)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="revisions_prev"),
                 InlineKeyboardButton(f"1 / {count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="revisions_next"))
    await message.reply(output[0], reply_markup=keyboard)


async def show_license_page(call: types.CallbackQuery, state: FSMContext, page):
    data = await state.get_data()
    current_licenses = data.get('current_licenses')
    current_licenses_page = data.get('current_licenses_page')
    total_licenses_count = data.get('total_licenses_count')
    start = (current_licenses_page - 1) * 20
    end = start + 21
    if start < page & page < end:
        i = page - start
        output = current_licenses[i - 1]
        await state.update_data(total_licenses_count=total_licenses_count, current_license_index=page,
                                current_licenses=current_licenses, current_licenses_page=current_licenses_page)
    else:
        data = await state.get_data()
        current_contragent = data.get('current_contragent')
        current_licenses_page = page // 20 + 1
        page_index = page - ((current_licenses_page - 1) * 20)
        res, count = search_inn.search_licenses(current_contragent, current_licenses_page)
        total_licenses_count = count
        current_licenses = res
        output = current_licenses[page_index - 1]
        await state.update_data(total_licenses_count=total_licenses_count, current_license_index=page,
                                current_licenses=current_licenses, current_licenses_page=current_licenses_page)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="licenses_prev"),
                 InlineKeyboardButton(f"{page} / {total_licenses_count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="licenses_next"))
    await call.message.edit_text(text=output, reply_markup=keyboard)


async def show_arbitrary_page(call: types.CallbackQuery, state: FSMContext, page):
    data = await state.get_data()
    current_arbitrary = data.get('current_arbitrary')
    current_arbitrary_page = data.get('current_arbitrary_page')
    total_arbitrary_count = data.get('total_arbitrary_count')
    start = (current_arbitrary_page - 1) * 20
    end = start + 21
    if start < page & page < end:
        i = page - start
        output = current_arbitrary[i - 1]
        await state.update_data(total_arbitrary_count=total_arbitrary_count, current_arbitrary_index=page,
                                current_arbitrary=current_arbitrary, current_arbitrary_page=current_arbitrary_page)
    else:
        data = await state.get_data()
        current_contragent = data.get('current_contragent')
        current_arbitrary_page = page // 20 + 1
        page_index = page - ((current_arbitrary_page - 1) * 20)
        res, count = search_inn.search_arbitrary(current_contragent, current_arbitrary_page)
        total_arbitrary_count = count
        current_arbitrary = res
        output = current_arbitrary[page_index - 1]
        await state.update_data(total_arbitrary_count=total_arbitrary_count, current_arbitrary_index=page,
                                current_arbitrary=current_arbitrary, current_arbitrary_page=current_arbitrary_page)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="arbitrary_prev"),
                 InlineKeyboardButton(f"{page} / {total_arbitrary_count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="arbitrary_next"))
    await call.message.edit_text(text=output, reply_markup=keyboard)


async def show_enforcement_page(call: types.CallbackQuery, state: FSMContext, page):
    data = await state.get_data()
    current_enforcement = data.get('current_enforcement')
    current_enforcement_page = data.get('current_enforcement_page')
    total_enforcement_count = data.get('total_enforcement_count')
    start = (current_enforcement_page - 1) * 20
    end = start + 21
    if start < page & page < end:
        i = page - start
        output = current_enforcement[i - 1]
        await state.update_data(total_enforcement_count=total_enforcement_count, current_enforcement_index=page,
                                current_enforcement=current_enforcement, current_enforcement_page=current_enforcement_page)
    else:
        data = await state.get_data()
        current_contragent = data.get('current_contragent')
        current_enforcement_page = page // 20 + 1
        page_index = page - ((current_enforcement_page - 1) * 20)
        res, count = search_inn.search_enforcement(current_contragent, current_enforcement_page)
        total_enforcement_count = count
        current_enforcement = res
        output = current_enforcement[page_index - 1]
        await state.update_data(total_enforcement_count=total_enforcement_count, current_enforcement_index=page,
                                current_enforcement=current_enforcement, current_enforcement_page=current_enforcement_page)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="enforcement_prev"),
                 InlineKeyboardButton(f"{page} / {total_enforcement_count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="enforcement_next"))
    await call.message.edit_text(text=output, reply_markup=keyboard)


async def show_revision_page(call: types.CallbackQuery, state: FSMContext, page):
    data = await state.get_data()
    current_revision = data.get('current_revisions')
    current_revision_page = data.get('current_revisions_page')
    total_revisions_count = data.get('total_revisions_count')
    start = (current_revision_page - 1) * 20
    end = start + 21
    if start < page & page < end:
        i = page - start
        output = current_revision[i - 1]
        await state.update_data(total_revisions_count=total_revisions_count, current_revision_index=page,
                                current_revisions=current_revision, current_revisions_page=current_revision_page)
    else:
        data = await state.get_data()
        current_contragent = data.get('current_contragent')
        current_revision_page = page // 20 + 1
        page_index = page - ((current_revision_page - 1) * 20)
        res, count = search_inn.search_revisions(current_contragent, current_revision_page)
        total_revisions_count = count
        current_revision = res
        output = current_revision[page_index - 1]
        await state.update_data(total_revisions_count=total_revisions_count, current_revision_index=page,
                                current_revisions=current_revision, current_revisions_page=current_revision_page)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="revisions_prev"),
                 InlineKeyboardButton(f"{page} / {total_revisions_count}", callback_data="."),
                 InlineKeyboardButton("Далее", callback_data="revisions_next"))
    await call.message.edit_text(text=output, reply_markup=keyboard)


@dp.callback_query_handler()
async def call_data_process(call: types.CallbackQuery, state: FSMContext):
    if call.data == "licenses_prev" or call.data == "licenses_next":
        await call_data_process_licenses(call, state)
        return
    if call.data == "arbitrary_prev" or call.data == "arbitrary_next":
        await call_data_process_arbitrary(call, state)
        return
    if call.data == "enforcement_prev" or call.data == "enforcement_next":
        await call_data_process_enforcement(call, state)
        return
    if call.data == "revisions_prev" or call.data == "revisions_next":
        await call_data_process_revisions(call, state)
        return


async def call_data_process_licenses(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get('current_license_index')
    total_licenses_count = data.get('total_licenses_count')
    if call.data == "licenses_next":
        index += 1
        if index == total_licenses_count + 1:
            index = 1
    elif call.data == "licenses_prev":
        index -= 1
        if index == 0:
            index = total_licenses_count
    else:
        return
    index = max(1, min(index, total_licenses_count + 1))
    await show_license_page(call, state, index)


async def call_data_process_arbitrary(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get('current_arbitrary_index')
    total_arbitrary_count = data.get('total_arbitrary_count')
    if call.data == "arbitrary_next":
        index += 1
        if index == total_arbitrary_count + 1:
            index = 1
    elif call.data == "arbitrary_prev":
        index -= 1
        if index == 0:
            index = total_arbitrary_count
    else:
        return
    index = max(1, min(index, total_arbitrary_count + 1))
    await show_arbitrary_page(call, state, index)


async def call_data_process_enforcement(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get('current_enforcement_index')
    total_count = data.get('total_enforcement_count')
    if call.data == "enforcement_next":
        index += 1
        if index == total_count + 1:
            index = 1
    elif call.data == "enforcement_prev":
        index -= 1
        if index == 0:
            index = total_count
    else:
        return
    index = max(1, min(index, total_count + 1))
    await show_enforcement_page(call, state, index)


async def call_data_process_revisions(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get('current_revision_index')
    total_count = data.get('total_revisions_count')
    if call.data == "revisions_next":
        index += 1
        if index == total_count + 1:
            index = 1
    elif call.data == "revisions_prev":
        index -= 1
        if index == 0:
            index = total_count
    else:
        return
    index = max(1, min(index, total_count + 1))
    await show_revision_page(call, state, index)


if __name__ == '__main__':
    executor.start_polling(dp)
