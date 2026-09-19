from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from core.i18n import get_text
from services.product_service import ProductService
from services.wb_api import WildberriesAPIClient

router = Router()


class SellerForm(StatesGroup):
    waiting_for_api_key = State()


def get_seller_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_seller_dashboard", lang), callback_data="seller_dashboard")],
            [InlineKeyboardButton(text=get_text("btn_sync_now", lang), callback_data="seller_sync")],
            [InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")]
        ]
    )


@router.callback_query(F.data == "role_seller")
async def cb_role_seller(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    seller = await ProductService.get_seller_by_user_id(session, callback.from_user.id)

    if not seller:
        await state.set_state(SellerForm.waiting_for_api_key)
        await callback.message.edit_text(
            f"{get_text('seller_not_reg', lang)}\n\n{get_text('enter_api_key', lang)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")]
            ])
        )
    else:
        await callback.message.edit_text(
            f"{get_text('seller_welcome', lang)}\n\nShop: **{seller.shop_name or 'Wildberries Supplier'}**",
            reply_markup=get_seller_menu_keyboard(lang),
            parse_mode="Markdown"
        )
    await callback.answer()


@router.message(SellerForm.waiting_for_api_key)
async def process_api_key(message: Message, session: AsyncSession, state: FSMContext):
    user = await ProductService.get_or_create_user(session, message.from_user.id)
    lang = user.language_preference
    api_key = message.text.strip()

    validating_msg = await message.answer(get_text("api_key_validating", lang))

    client = WildberriesAPIClient(api_key=api_key)
    is_valid = await client.validate_api_key()

    if not is_valid:
        await validating_msg.edit_text(
            get_text("api_key_invalid", lang),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")]
            ])
        )
        return

    seller = await ProductService.register_seller(session, message.from_user.id, raw_api_key=api_key)
    synced_count = await ProductService.sync_seller_products(session, seller)

    await state.clear()
    await validating_msg.edit_text(
        f"{get_text('seller_registered', lang)}\n{get_text('sync_complete', lang, count=synced_count)}",
        reply_markup=get_seller_menu_keyboard(lang)
    )


@router.callback_query(F.data == "seller_sync")
async def cb_seller_sync(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    seller = await ProductService.get_seller_by_user_id(session, callback.from_user.id)

    if not seller:
        await callback.answer(get_text("seller_not_reg", lang), show_alert=True)
        return

    await callback.message.edit_text(get_text("sync_started", lang))
    synced_count = await ProductService.sync_seller_products(session, seller)

    await callback.message.edit_text(
        get_text("sync_complete", lang, count=synced_count),
        reply_markup=get_seller_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "seller_dashboard")
async def cb_seller_dashboard(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    seller = await ProductService.get_seller_by_user_id(session, callback.from_user.id)

    if not seller:
        await callback.answer(get_text("seller_not_reg", lang), show_alert=True)
        return

    products = await ProductService.get_seller_products(session, seller.id)

    if not products:
        await callback.message.edit_text(
            "No products found. Please run sync.",
            reply_markup=get_seller_menu_keyboard(lang)
        )
        await callback.answer()
        return

    msg = "📊 **Your WB Products (Armenian Local Stock Toggle)**:\n\n"
    keyboard_buttons = []

    for prod in products:
        status_str = get_text("status_local", lang) if prod.is_local_stock else get_text("status_non_local", lang)
        msg += f"• **{prod.title}**\n   SKU: `{prod.wb_sku_id}` | Price: {prod.discount_price:,.0f} AMD | Status: {status_str}\n\n"
        toggle_label = f"Toggle Local: {prod.title[:20]}..."
        keyboard_buttons.append([InlineKeyboardButton(text=toggle_label, callback_data=f"toggle_prod_{prod.id}")])

    keyboard_buttons.append([InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")])

    await callback.message.edit_text(
        msg,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_prod_"))
async def cb_toggle_product_stock(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[-1])
    await ProductService.toggle_product_local_stock(session, product_id)
    await cb_seller_dashboard(callback, session)
