from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.i18n import get_text
from services.product_service import ProductService
from models.product import Product

router = Router()


def get_buyer_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_categories", lang), callback_data="buyer_categories")],
            [InlineKeyboardButton(text=get_text("btn_bargains", lang), callback_data="buyer_bargains")],
            [InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")]
        ]
    )


def format_product_caption(product: Product, lang: str) -> str:
    deeplink = settings.wb_deeplink_base_url.format(sku=product.wb_sku_id)
    caption = (
        f"📌 **{product.title}**\n\n"
        f"🏷 {get_text('original_price', lang)}: ~{product.price:,.0f} AMD~\n"
        f"💥 **{get_text('discount_price', lang)}: {product.discount_price:,.0f} AMD**\n\n"
        f"{get_text('delivery_time', lang)}\n"
        f"📦 SKU: `{product.wb_sku_id}`"
    )
    return caption


def get_product_card_keyboard(product: Product, lang: str, cat_name: str = "", index: int = 0, total: int = 1, is_bargain: bool = False) -> InlineKeyboardMarkup:
    deeplink = settings.wb_deeplink_base_url.format(sku=product.wb_sku_id)
    buttons = [
        [InlineKeyboardButton(text=get_text("btn_buy_wb", lang), url=deeplink)]
    ]

    nav_row = []
    prefix = "bargain" if is_bargain else f"cat_{cat_name}"
    if index > 0:
        nav_row.append(InlineKeyboardButton(text=get_text("btn_prev", lang), callback_data=f"show_{prefix}_{index - 1}"))
    if index < total - 1:
        nav_row.append(InlineKeyboardButton(text=get_text("btn_next", lang), callback_data=f"show_{prefix}_{index + 1}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "role_buyer")
async def cb_role_buyer(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    await callback.message.edit_text(
        get_text("buyer_menu", lang),
        reply_markup=get_buyer_menu_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "buyer_categories")
async def cb_buyer_categories(callback: CallbackQuery, session: AsyncSession):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    categories = await ProductService.get_categories(session)

    if not categories:
        await callback.message.edit_text(
            get_text("no_categories", lang),
            reply_markup=get_buyer_menu_keyboard(lang)
        )
        await callback.answer()
        return

    keyboard_buttons = [
        [InlineKeyboardButton(text=f"📁 {cat}", callback_data=f"show_cat_{cat}_0")]
        for cat in categories
    ]
    keyboard_buttons.append([InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")])

    await callback.message.edit_text(
        get_text("select_category", lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    )
    await callback.answer()


@router.callback_query(F.data == "buyer_bargains")
async def cb_buyer_bargains(callback: CallbackQuery, session: AsyncSession):
    await show_bargain_product(callback, session, index=0)


@router.callback_query(F.data.startswith("show_bargain_"))
async def cb_show_bargain(callback: CallbackQuery, session: AsyncSession):
    index = int(callback.data.split("_")[-1])
    await show_bargain_product(callback, session, index=index)


async def show_bargain_product(callback: CallbackQuery, session: AsyncSession, index: int):
    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    products = await ProductService.get_bargain_deals(session, limit=20)

    if not products:
        await callback.message.edit_text(
            get_text("no_products_in_cat", lang),
            reply_markup=get_buyer_menu_keyboard(lang)
        )
        await callback.answer()
        return

    product = products[index]
    caption = format_product_caption(product, lang)
    reply_markup = get_product_card_keyboard(product, lang, index=index, total=len(products), is_bargain=True)

    default_img = "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"
    img_url = product.image_url if product.image_url else default_img

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=img_url, caption=caption, parse_mode="Markdown"),
            reply_markup=reply_markup
        )
    except Exception:
        await callback.message.answer_photo(
            photo=img_url,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("show_cat_"))
async def cb_show_category_product(callback: CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    index = int(parts[-1])
    cat_name = "_".join(parts[2:-1])

    user = await ProductService.get_or_create_user(session, callback.from_user.id)
    lang = user.language_preference
    products = await ProductService.get_products_by_category(session, category=cat_name, limit=20)

    if not products:
        await callback.message.edit_text(
            get_text("no_products_in_cat", lang),
            reply_markup=get_buyer_menu_keyboard(lang)
        )
        await callback.answer()
        return

    product = products[index]
    caption = format_product_caption(product, lang)
    reply_markup = get_product_card_keyboard(product, lang, cat_name=cat_name, index=index, total=len(products), is_bargain=False)

    default_img = "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"
    img_url = product.image_url if product.image_url else default_img

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=img_url, caption=caption, parse_mode="Markdown"),
            reply_markup=reply_markup
        )
    except Exception:
        await callback.message.answer_photo(
            photo=img_url,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    await callback.answer()
