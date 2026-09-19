from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from core.i18n import get_text
from services.product_service import ProductService

router = Router()


def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("btn_buyer", lang), callback_data="role_buyer"),
                InlineKeyboardButton(text=get_text("btn_seller", lang), callback_data="role_seller"),
            ],
            [
                InlineKeyboardButton(text=get_text("btn_lang", lang), callback_data="change_language"),
            ]
        ]
    )


def get_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇦🇲 Հայերեն (hy)", callback_data="set_lang_hy"),
                InlineKeyboardButton(text="🇷🇺 Русский (ru)", callback_data="set_lang_ru"),
                InlineKeyboardButton(text="🇬🇧 English (en)", callback_data="set_lang_en"),
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, message.from_user.id)
    lang = user.language_preference
    welcome_msg = f"{get_text('welcome', lang)}\n\n{get_text('select_role', lang)}"
    await message.answer(welcome_msg, reply_markup=get_main_menu_keyboard(lang))


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    await callback.message.edit_text(
        f"{get_text('welcome', lang)}\n\n{get_text('select_role', lang)}",
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "change_language")
async def cb_change_language(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    await callback.message.edit_text(
        get_text("choose_lang", lang),
        reply_markup=get_lang_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def cb_set_language(callback: CallbackQuery, session: AsyncSession):
    new_lang = callback.data.split("_")[-1]
    await ProductService.update_user_language(session, callback.from_user.id, new_lang)
    await callback.message.edit_text(
        f"{get_text('lang_changed', new_lang)} {new_lang.upper()}",
        reply_markup=get_main_menu_keyboard(new_lang)
    )
    await callback.answer()
