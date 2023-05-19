from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import data

inn = KeyboardButton(data.MENU_INN)
domain = KeyboardButton(data.MENU_DOMAIN)

menu = KeyboardButton(data.BACK_TO_MENU)
arbitration = KeyboardButton(data.ARBITRATION)
enforcement = KeyboardButton(data.ENFORCEMENT)
revisions = KeyboardButton(data.REVISIONS)
licenses = KeyboardButton(data.LICENSES)


def create_keyboard_start():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(inn, domain)
    return keyboard


def create_keyboard_inn():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(arbitration, enforcement)
    keyboard.add(revisions, licenses)
    keyboard.row(menu)
    return keyboard


def create_keyboard_domain():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(menu)
    return keyboard
