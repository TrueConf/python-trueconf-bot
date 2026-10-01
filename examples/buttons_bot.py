"""
Buttons Bot — a single TrueConf bot showcasing inline keyboards, combined into one
project with five routers:

    /buttons — a gallery of every inline-button type (command, url, message, draft,
               copy-to-clipboard, button styles, up to the 64-button limit)
    /menu    — a multi-level store menu, re-rendered in place via edit_message
    /ttt     — tic-tac-toe against the bot (win > block > center > corner),
               score badge, winning line highlighted
    /chess   — full chess on an 8x8 board (64 buttons = API limit): all pieces,
               captures, castling, en passant, automatic queen promotion,
               check, checkmate, stalemate
    /calendar — a date picker (table booking): 8x7 month grid, selected day
               highlighted, today/weekends styled, prev/next month

Run:
    python examples/buttons_bot/bot.py

Then open the bot in the TrueConf client and send one of the commands above.
Game state (tic-tac-toe, chess) is kept in memory per chat, so it resets on restart.
"""

import asyncio
import calendar
import datetime
import logging

from trueconf import (
    Bot,
    ButtonStyle,
    CallbackQuery,
    Dispatcher,
    F,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Router,
)
from trueconf.filters import Command

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) -> %(funcName)s(): %(message)s",
    encoding="utf-8",
)

dp = Dispatcher()

# Five routers, one dispatcher. Note: root routers are independent — every
# callback event reaches all of them, so each router's handlers must be
# filtered by its own command prefix ("btn:", "menu:", "ttt:", "calendar:",
# "chess:").
buttons_r = Router(name="buttons")
menu_r = Router(name="menu")
ttt_r = Router(name="ttt")
calendar_r = Router(name="calendar")
chess_r = Router(name="chess")
dp.include_router(buttons_r)
dp.include_router(menu_r)
dp.include_router(ttt_r)
dp.include_router(calendar_r)
dp.include_router(chess_r)

bot = Bot.from_credentials(
    server="10.140.1.255",
    username="button_bot",
    password="123tr",
    verify_ssl=False,
    dispatcher=dp,
    receive_system_messages=True,
)

# ===================================================================== /buttons


def build_all_button_sets() -> list[tuple[str, InlineKeyboardMarkup]]:
    sets = []

    sets.append(
        (
            "1. command: simple button",
            InlineKeyboardMarkup(
                buttons=[
                    [InlineKeyboardButton(text="Press me", command="btn:simple")],
                ]
            ),
        )
    )

    sets.append(
        (
            "2. command + custom_data",
            InlineKeyboardMarkup(
                buttons=[
                    [
                        InlineKeyboardButton(
                            text="With data",
                            command="btn:with_data",
                            custom_data="eyJpZCI6IDQyfQ==",
                        )
                    ],
                ]
            ),
        )
    )

    sets.append(
        (
            "3. command + custom_data + id",
            InlineKeyboardMarkup(
                buttons=[
                    [
                        InlineKeyboardButton(
                            text="Full set",
                            command="btn:full",
                            custom_data="data-1",
                            button_id="btn-full-1",
                        )
                    ],
                ]
            ),
        )
    )

    sets.append(
        (
            "4. all button styles: <i>default, primary, danger, success</i>:",
            InlineKeyboardMarkup(
                buttons=[
                    [
                        InlineKeyboardButton(text="default", command="btn:style:default"),
                        InlineKeyboardButton(text="primary", command="btn:style:primary", style=ButtonStyle.PRIMARY),
                        InlineKeyboardButton(text="danger", command="btn:style:danger", style=ButtonStyle.DANGER),
                        InlineKeyboardButton(text="success", command="btn:style:success", style=ButtonStyle.SUCCESS),
                    ],
                ]
            ),
        )
    )

    sets.append(
        (
            "5. command + to (forward to bot 'bot1')",
            InlineKeyboardMarkup(
                buttons=[
                    [InlineKeyboardButton(text="Forward", command="btn:forward", to="bot1")],
                ]
            ),
        )
    )

    url_row = [
        InlineKeyboardButton(text="https", url="https://trueconf.com"),
        InlineKeyboardButton(text="http", url="http://example.com"),
        InlineKeyboardButton(text="mailto", url="mailto:test@trueconf.com"),
        InlineKeyboardButton(text="trueconf:", url="trueconf:test@server.trueconf.name"),
    ]
    sets.append(("6. url: all schemes (https/http/mailto/trueconf)", InlineKeyboardMarkup(buttons=[url_row])))

    message_row = [
        InlineKeyboardButton(text="Send text", message="Hi! Sent via button"),
        InlineKeyboardButton(text="Draft", message="This goes to the draft field", draft=True),
    ]
    sets.append(("7. message: send and draft", InlineKeyboardMarkup(buttons=[message_row])))

    copy_row = [
        InlineKeyboardButton(text="Copy promo code", copy_data="PROMO-12345"),
        InlineKeyboardButton(text="Copy (danger)", copy_data="SECRET-777", style=ButtonStyle.DANGER),
    ]
    sets.append(("8. copy: clipboard", InlineKeyboardMarkup(buttons=[copy_row])))

    all_types_row = [
        InlineKeyboardButton(text="Cmd", command="btn:all:cmd"),
        InlineKeyboardButton(text="URL", url="https://trueconf.com"),
        InlineKeyboardButton(text="Msg", message="Text from button"),
        InlineKeyboardButton(text="Copy", copy_data="copied"),
    ]
    sets.append(("9. all 4 types in one row", InlineKeyboardMarkup(buttons=[all_types_row])))

    grid = [[InlineKeyboardButton(text=f"R{i}C{j}", command=f"btn:grid:{i}{j}") for j in range(2)] for i in range(3)]
    sets.append(("10. 3x2 grid", InlineKeyboardMarkup(buttons=grid)))

    wide_row = [InlineKeyboardButton(text=f"{i}", command=f"btn:wide:{i}") for i in range(8)]
    sets.append(("11. row of 8 buttons (max width)", InlineKeyboardMarkup(buttons=[wide_row])))

    dup_row = [
        InlineKeyboardButton(text="Same cmd (1)", command="btn:dup", custom_data="1"),
        InlineKeyboardButton(text="Same cmd (2)", command="btn:dup", custom_data="2"),
    ]
    sets.append(("12. same command, different custom_data", InlineKeyboardMarkup(buttons=[dup_row])))

    sets.append(
        (
            "13. label=32 and command=255 chars",
            InlineKeyboardMarkup(
                buttons=[
                    [InlineKeyboardButton(text="A" * 32, command="c" * 255)],
                ]
            ),
        )
    )

    max_grid = [
        [InlineKeyboardButton(text=f"{r * 8 + c:02d}", command=f"btn:max:{r * 8 + c}") for c in range(8)]
        for r in range(8)
    ]
    sets.append(("14. maximum: 8x8 = 64 buttons", InlineKeyboardMarkup(buttons=max_grid)))

    return sets


@buttons_r.message(Command("buttons"))
async def on_buttons(event: Message):
    for description, markup in build_all_button_sets():
        await event.answer(description, buttons=markup, parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.5)


@buttons_r.callback_query(F.command.startswith("btn:"))
async def on_button(callback: CallbackQuery):
    print(
        f"Button pressed: {callback.command}"
        f" | custom_data={callback.custom_data}"
        f" | button_id={callback.command_source.button_id}"
    )


# ====================================================================== /menu


MENU: dict[str, dict] = {
    "menu:root": {
        "header": "🏠 Main Menu",
        "buttons": [
            ("🛍 Catalog", "menu:catalog"),
            ("❓ Support", "menu:support"),
            ("ℹ️ About the bot", "menu:about"),  # noqa: RUF001
        ],
    },
    "menu:catalog": {
        "header": "🛍 Catalog",
        "buttons": [
            ("📱 Electronics", "menu:electronics"),
            ("👕 Clothes", "menu:clothes"),
            ("◀️ Back", "menu:root"),
        ],
    },
    "menu:electronics": {
        "header": "📱 Electronics",
        "buttons": [
            ("Smartphones", "menu:electronics:phones"),
            ("Laptops", "menu:electronics:laptops"),
            ("◀️ Back", "menu:catalog"),
        ],
    },
    "menu:electronics:phones": {
        "header": "📱 Smartphones",
        "content": "iPhone 17 — from $999\nSamsung S26 — from $899",
        "buttons": [("◀️ Back", "menu:electronics")],
    },
    "menu:electronics:laptops": {
        "header": "💻 Laptops",
        "content": "MacBook Pro — from $1,999\nThinkPad X1 — from $1,499",
        "buttons": [("◀️ Back", "menu:electronics")],
    },
    "menu:clothes": {
        "header": "👕 Clothes",
        "buttons": [
            ("T-shirts", "menu:clothes:tshirts"),
            ("◀️ Back", "menu:catalog"),
        ],
    },
    "menu:clothes:tshirts": {
        "header": "👕 T-shirts",
        "content": "Basic — $19\nOversize — $25",
        "buttons": [("◀️ Back", "menu:clothes")],
    },
    "menu:support": {
        "header": "❓ Support",
        "buttons": [
            ("FAQ", "menu:support:faq"),
            ("◀️ Back", "menu:root"),
        ],
    },
    "menu:support:faq": {
        "header": "FAQ",
        "buttons": [
            ("💳 How to pay?", "menu:support:faq:pay"),
            ("↩️ Refund policy", "menu:support:faq:refund"),
            ("◀️ Back", "menu:support"),
        ],
    },
    "menu:support:faq:pay": {
        "header": "💳 Payment",
        "content": "By card, bank transfer, or 0% installments up to 12 months",
        "buttons": [("◀️ Back", "menu:support:faq")],
    },
    "menu:support:faq:refund": {
        "header": "↩️ Refund policy",
        "content": "Within 14 days of delivery",
        "buttons": [("◀️ Back", "menu:support:faq")],
    },
    "menu:about": {
        "header": "ℹ️ About the bot",  # noqa: RUF001
        "buttons": [
            ("Version", "menu:about:version"),
            ("◀️ Back", "menu:root"),
        ],
    },
    "menu:about:version": {
        "header": "ℹ️ Version: 1.5.0",  # noqa: RUF001
        "content": "Built with python-trueconf-bot",
        "buttons": [("◀️ Back", "menu:about")],
    },
}


def text_for(node: dict) -> str:
    """Full menu text: header + (optional) content."""
    if content := node.get("content"):
        return f"{node['header']}\n{content}"
    return node["header"]


def markup_for(node: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        buttons=[[InlineKeyboardButton(text=label, command=command)] for label, command in node["buttons"]]
    )


@menu_r.message(Command("menu"))
async def open_menu(event: Message):
    node = MENU["menu:root"]
    await bot.send_message(
        chat_id=event.chat.chat_id,
        text=text_for(node),
        buttons=markup_for(node),
    )
    print("Main menu opened")


async def _render(callback: CallbackQuery, key: str):
    node = MENU[key]
    await callback.edit_message(
        text=text_for(node),
        buttons=markup_for(node),
    )
    print("Menu shown:", key, "|", node["header"])


@menu_r.callback_query(F.command == "menu:catalog")
async def on_catalog(callback: CallbackQuery):
    print("CLICK: menu:catalog")
    await _render(callback, "menu:catalog")


@menu_r.callback_query(F.command == "menu:electronics")
async def on_electronics(callback: CallbackQuery):
    print("CLICK: menu:electronics")
    await _render(callback, "menu:electronics")


@menu_r.callback_query(F.command == "menu:electronics:phones")
async def on_electronics_phones(callback: CallbackQuery):
    print("CLICK: menu:electronics:phones")
    await _render(callback, "menu:electronics:phones")


@menu_r.callback_query(F.command == "menu:electronics:laptops")
async def on_electronics_laptops(callback: CallbackQuery):
    print("CLICK: menu:electronics:laptops")
    await _render(callback, "menu:electronics:laptops")


@menu_r.callback_query(F.command == "menu:clothes")
async def on_clothes(callback: CallbackQuery):
    print("CLICK: menu:clothes")
    await _render(callback, "menu:clothes")


@menu_r.callback_query(F.command == "menu:clothes:tshirts")
async def on_clothes_tshirts(callback: CallbackQuery):
    print("CLICK: menu:clothes:tshirts")
    await _render(callback, "menu:clothes:tshirts")


@menu_r.callback_query(F.command == "menu:support")
async def on_support(callback: CallbackQuery):
    print("CLICK: menu:support")
    await _render(callback, "menu:support")


@menu_r.callback_query(F.command == "menu:support:faq")
async def on_support_faq(callback: CallbackQuery):
    print("CLICK: menu:support:faq")
    await _render(callback, "menu:support:faq")


@menu_r.callback_query(F.command == "menu:support:faq:pay")
async def on_support_faq_pay(callback: CallbackQuery):
    print("CLICK: menu:support:faq:pay")
    await _render(callback, "menu:support:faq:pay")


@menu_r.callback_query(F.command == "menu:support:faq:refund")
async def on_support_faq_refund(callback: CallbackQuery):
    print("CLICK: menu:support:faq:refund")
    await _render(callback, "menu:support:faq:refund")


@menu_r.callback_query(F.command == "menu:about")
async def on_about(callback: CallbackQuery):
    print("CLICK: menu:about")
    await _render(callback, "menu:about")


@menu_r.callback_query(F.command == "menu:about:version")
async def on_about_version(callback: CallbackQuery):
    print("CLICK: menu:about:version")
    await _render(callback, "menu:about:version")


@menu_r.callback_query(F.command == "menu:root")
async def on_root(callback: CallbackQuery):
    print("CLICK: menu:root")
    await _render(callback, "menu:root")


# ======================================================================== /ttt


LINES = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]

# Per-chat state — see fresh_state().
ttt_state: dict[str, dict] = {}


def fresh_ttt_state() -> dict:
    return {
        "board": [[None] * 3 for _ in range(3)],  # None | 'X' (player) | 'O' (bot)
        "turn": "X",
        "winner": None,  # 'X' | 'O' | 'draw' | None
        "line": [],  # winning cells [(r, c), ...]
        "score": {"wins": 0, "losses": 0, "draws": 0},
    }


# ---------------------------------------------------------------- logic


def check_winner(board: list[list[str | None]]) -> tuple[str | None, list[tuple[int, int]]]:
    for line in LINES:
        cells = [board[r][c] for r, c in line]
        if cells[0] is not None and cells[0] == cells[1] == cells[2]:
            return cells[0], line
    if all(cell is not None for row in board for cell in row):
        return "draw", []
    return None, []


def choose_bot_move(board: list[list[str | None]]) -> tuple[int, int] | None:
    """Bot move: win > block > center > corner > first empty cell."""
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]
    if not empty:
        return None
    for mark in ("O", "X"):  # win first, then block
        for r, c in empty:
            board[r][c] = mark
            if check_winner(board)[0] == mark:
                board[r][c] = None
                return r, c
            board[r][c] = None
    if board[1][1] is None:
        return 1, 1
    for r, c in ((0, 0), (0, 2), (2, 0), (2, 2)):
        if board[r][c] is None:
            return r, c
    return empty[0]


def _finish(st: dict, winner: str, line: list) -> None:
    st["winner"] = winner
    st["line"] = line
    if winner == "X":
        st["score"]["wins"] += 1
    elif winner == "O":
        st["score"]["losses"] += 1
    else:
        st["score"]["draws"] += 1


def parse_cell_cmd(cmd: str) -> tuple[int, int]:
    """'ttt:cell:0:1' -> (0, 1)."""
    r, c = cmd.removeprefix("ttt:cell:").split(":")
    return int(r), int(c)


def player_move(st: dict, r: int, c: int) -> str | None:
    """Player move; returns a hint (or None)."""
    if st["winner"]:
        return "Game over — press 🔄 New game"
    if st["turn"] != "X":
        return "It's the bot's turn…"
    if st["board"][r][c] is not None:
        return "Cell is taken — pick another"
    st["board"][r][c] = "X"
    st["turn"] = "O"
    winner, line = check_winner(st["board"])
    if winner:
        _finish(st, winner, line)
    return None


def bot_move(st: dict) -> tuple[int, int] | None:
    """Bot move; returns the cell (or None if it cannot move)."""
    if st["winner"] or st["turn"] != "O":
        return None
    move = choose_bot_move(st["board"])
    if move is None:
        return None
    r, c = move
    st["board"][r][c] = "O"
    st["turn"] = "X"
    winner, line = check_winner(st["board"])
    if winner:
        _finish(st, winner, line)
    return r, c


# ---------------------------------------------------------------- message text


def _header(text: str) -> str:
    """Bold header stretched across the message bubble (em-spaces U+2003 are
    not collapsed by the HTML parser, unlike regular spaces)."""
    pad = "\u2003" * max(0, 60 - len(text))
    return f"<b>{text}{pad}</b>"


def ttt_state_text(st: dict) -> str:
    s = st["score"]
    score = f"Score {s['wins']}:{s['losses']}:{s['draws']}"
    if st["winner"] == "X":
        line2 = f"🏆 You win! · {score}"
    elif st["winner"] == "O":
        line2 = f"🤖 Bot wins · {score}"
    elif st["winner"] == "draw":
        line2 = f"🤝 Draw · {score}"
    elif st["turn"] == "O":
        line2 = f"🤖 Bot is thinking… · {score}"
    else:
        line2 = f"Your turn · you \u274c / bot \u26ab\ufe0f · {score}"
    return _header("Tic-Tac-Toe") + "<br>" + line2


# ---------------------------------------------------------------- keyboard


def ttt_board_markup(st: dict) -> InlineKeyboardMarkup:
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            cell = st["board"][r][c]
            text = "\u274c" if cell == "X" else "\u26ab\ufe0f" if cell == "O" else "·"
            style = ButtonStyle.SUCCESS if (r, c) in st["line"] else ButtonStyle.DEFAULT
            row.append(InlineKeyboardButton(text=text, command=f"ttt:cell:{r}:{c}", style=style))
        rows.append(row)
    s = st["score"]
    rows.append(
        [
            InlineKeyboardButton(text="🔄 New game", command="ttt:new", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text=f"📊 {s['wins']}:{s['losses']}:{s['draws']}", command="ttt:score"),
        ]
    )
    return InlineKeyboardMarkup(buttons=rows)


# ---------------------------------------------------------------- handlers


@ttt_r.message(Command("ttt"))
async def open_ttt(event: Message):
    st = ttt_state.setdefault(event.chat.chat_id, fresh_ttt_state())
    await bot.send_message(
        chat_id=event.chat.chat_id,
        text=ttt_state_text(st),
        parse_mode=ParseMode.HTML,
        buttons=ttt_board_markup(st),
    )
    print("Tic-tac-toe opened")


@ttt_r.callback_query(F.command.startswith("ttt:"))
async def on_ttt(callback: CallbackQuery):
    st = ttt_state.setdefault(callback.chat.chat_id, fresh_ttt_state())
    cmd = callback.command
    print("CLICK:", cmd)
    hint = None
    if cmd == "ttt:new":
        st.update(board=[[None] * 3 for _ in range(3)], turn="X", winner=None, line=[])
    elif cmd.startswith("ttt:cell:"):
        r, c = parse_cell_cmd(cmd)
        hint = player_move(st, r, c)
        if hint is None and not st["winner"]:
            # bot move: show "thinking" first, then the move itself
            await callback.edit_message(
                text=ttt_state_text(st), parse_mode=ParseMode.HTML, buttons=ttt_board_markup(st)
            )
            await asyncio.sleep(0.7)
            bot_move(st)
    # ttt:score — just a re-render (score is visible in the badge and the text)
    text = ttt_state_text(st)
    if hint:
        text = f"{text}<br>{hint}"
    await callback.edit_message(text=text, parse_mode=ParseMode.HTML, buttons=ttt_board_markup(st))


# ==================================================================== /calendar


CALENDAR_TEXT = "Which day shall we book the table for?"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Per-chat state: {"year": int, "month": int, "selected": str | None}
# selected is the "YYYY-MM-DD" of the chosen day (defaults to today).
calendar_state: dict[str, dict] = {}


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    """Shift the month by delta (forward/back) across year boundaries."""
    index = year * 12 + (month - 1) + delta
    return divmod(index, 12)[0], divmod(index, 12)[1] + 1


def calendar_markup(year: int, month: int, selected: str | None) -> InlineKeyboardMarkup:
    """Calendar keyboard: month header, weekday row, date grid, bottom row."""
    prev_year, prev_month = shift_month(year, month, -1)
    next_year, next_month = shift_month(year, month, +1)
    today_iso = datetime.date.today().isoformat()

    header = [
        InlineKeyboardButton(
            text=f"📅 {MONTHS[month - 1]} {year}",
            command=f"calendar:month:{year}-{month:02d}",
        )
    ]

    weekday_row = [InlineKeyboardButton(text=day, command="calendar:header") for day in WEEKDAYS]

    date_rows = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                # TrueConf has no empty/inert cells — use a placeholder button.
                row.append(InlineKeyboardButton(text="•", command="calendar:blank"))
                continue
            iso = f"{year}-{month:02d}-{day:02d}"
            text = f"[{day}]" if iso == selected else str(day)
            # Style priority: selected day > today > weekend > regular day.
            if iso == selected:
                style = ButtonStyle.PRIMARY
            elif iso == today_iso:
                style = ButtonStyle.SUCCESS
            elif datetime.date(year, month, day).weekday() >= 5:
                style = ButtonStyle.DANGER
            else:
                style = ButtonStyle.DEFAULT
            row.append(InlineKeyboardButton(text=text, command=f"calendar:day:{iso}", style=style))
        date_rows.append(row)

    bottom = [
        InlineKeyboardButton(text=f"{MONTHS[prev_month - 1][:3]}. {prev_year}", command="calendar:prev"),
        InlineKeyboardButton(text="🔍", command="calendar:search"),
        InlineKeyboardButton(text=f"{MONTHS[next_month - 1][:3]}. {next_year}", command="calendar:next"),
    ]

    return InlineKeyboardMarkup(buttons=[header, weekday_row, *date_rows, bottom])


@calendar_r.message(Command("calendar"))
async def open_calendar(event: Message):
    today = datetime.date.today()
    calendar_state[event.chat.chat_id] = {
        "year": today.year,
        "month": today.month,
        "selected": today.isoformat(),
    }
    await bot.send_message(
        chat_id=event.chat.chat_id,
        text=CALENDAR_TEXT,
        buttons=calendar_markup(today.year, today.month, today.isoformat()),
    )
    print(f"Calendar opened: {MONTHS[today.month - 1]} {today.year}")


async def _cal_render(callback: CallbackQuery, year: int, month: int, selected: str | None):
    await callback.edit_message(
        text=CALENDAR_TEXT,
        buttons=calendar_markup(year, month, selected),
    )


def _cal_chat_state(callback: CallbackQuery) -> dict:
    chat_id = callback.chat.chat_id
    today = datetime.date.today()
    return calendar_state.setdefault(
        chat_id,
        {"year": today.year, "month": today.month, "selected": today.isoformat()},
    )


@calendar_r.callback_query(F.command.startswith("calendar:day:"))
async def on_cal_day(callback: CallbackQuery):
    iso = callback.command.removeprefix("calendar:day:")
    chat_state = _cal_chat_state(callback)
    chat_state["selected"] = iso
    print("CLICK: day", iso)
    await _cal_render(callback, chat_state["year"], chat_state["month"], iso)


@calendar_r.callback_query(F.command == "calendar:next")
async def on_cal_next(callback: CallbackQuery):
    chat_state = _cal_chat_state(callback)
    chat_state["year"], chat_state["month"] = shift_month(chat_state["year"], chat_state["month"], +1)
    print("CLICK: next month ->", MONTHS[chat_state["month"] - 1], chat_state["year"])
    await _cal_render(callback, chat_state["year"], chat_state["month"], chat_state["selected"])


@calendar_r.callback_query(F.command == "calendar:prev")
async def on_cal_prev(callback: CallbackQuery):
    chat_state = _cal_chat_state(callback)
    chat_state["year"], chat_state["month"] = shift_month(chat_state["year"], chat_state["month"], -1)
    print("CLICK: previous month ->", MONTHS[chat_state["month"] - 1], chat_state["year"])
    await _cal_render(callback, chat_state["year"], chat_state["month"], chat_state["selected"])


@calendar_r.callback_query(F.command == "calendar:search")
async def on_cal_search(callback: CallbackQuery):
    print("CLICK: 🔍 date search")


@calendar_r.callback_query(F.command == "calendar:header")
async def on_cal_header(callback: CallbackQuery):
    print("CLICK: weekday header (Mon..Sun)")


@calendar_r.callback_query(F.command == "calendar:blank")
async def on_cal_blank(callback: CallbackQuery):
    print("CLICK: empty cell •")


@calendar_r.callback_query(F.command.startswith("calendar:month:"))
async def on_cal_month_title(callback: CallbackQuery):
    print("CLICK: month title:", callback.command)


# ====================================================================== /chess


PIECES = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟\ufe0e",  # VS15: force the text presentation (otherwise iOS renders it as a color emoji)
}
PIECE_NAMES = {"P": "pawn", "N": "knight", "B": "bishop", "R": "rook", "Q": "queen", "K": "king"}

KNIGHT_OFFSETS = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
KING_OFFSETS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
RAY_DIRECTIONS = {
    "B": ((-1, -1), (-1, 1), (1, -1), (1, 1)),
    "R": ((-1, 0), (1, 0), (0, -1), (0, 1)),
    "Q": ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)),
}

# Per-chat state — see fresh_chess_state().
chess_state: dict[str, dict] = {}


def on_board(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def sq_to_rc(sq: str) -> tuple[int, int]:
    """'e4' -> (4, 4): row = 8 - rank, column = file."""
    return 8 - int(sq[1]), ord(sq[0]) - ord("a")


def rc_to_sq(r: int, c: int) -> str:
    return f"{chr(ord('a') + c)}{8 - r}"


def piece_color(p: str) -> str:
    return "w" if p.isupper() else "b"


def opposite(turn: str) -> str:
    return "b" if turn == "w" else "w"


def initial_board() -> list[list[str | None]]:
    back = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    board = [[None] * 8 for _ in range(8)]
    board[0] = [p.lower() for p in back]
    board[1] = ["p"] * 8
    board[6] = ["P"] * 8
    board[7] = back[:]
    return board


def fresh_chess_state() -> dict:
    return {
        "board": initial_board(),
        "turn": "w",
        "castling": {"K": True, "Q": True, "k": True, "q": True},
        "ep": None,  # en passant target cell (after a double pawn push)
        "selected": None,
        "status": ("playing", None),  # ("checkmate", "w"|"b") | ("stalemate", None)
        "move_count": 0,
        "last_move": None,
        "promoted": False,
    }


def find_king(board: list[list[str | None]], turn: str) -> str | None:
    king = "K" if turn == "w" else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return rc_to_sq(r, c)
    return None


def _slider_attacks(board: list[list[str | None]], r: int, c: int, by: str) -> bool:
    """Does a queen/rook/bishop attack cell (r, c) along a ray."""
    for dr, dc in RAY_DIRECTIONS["Q"]:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            p = board[nr][nc]
            if p is not None:
                if piece_color(p) == by and p.upper() in ("B", "R", "Q"):
                    diagonal = dr != 0 and dc != 0
                    if diagonal and p.upper() in ("B", "Q"):
                        return True
                    if not diagonal and p.upper() in ("R", "Q"):
                        return True
                break
            nr += dr
            nc += dc
    return False


def is_attacked(board: list[list[str | None]], sq: str, by: str) -> bool:
    """Is square sq attacked by a piece of color by (ignoring the move)."""
    r, c = sq_to_rc(sq)

    # Pawns: a white pawn at (r+1, c±1) attacks (r, c); a black one at (r-1, c±1).
    pawn_row = r + (1 if by == "w" else -1)
    for dc in (-1, 1):
        if on_board(pawn_row, c + dc):
            p = board[pawn_row][c + dc]
            if p is not None and p.upper() == "P" and piece_color(p) == by:
                return True

    # Knight.
    for dr, dc in KNIGHT_OFFSETS:
        nr, nc = r + dr, c + dc
        if on_board(nr, nc) and board[nr][nc] == ("N" if by == "w" else "n"):
            return True

    # King (adjacent cells only).
    for dr, dc in KING_OFFSETS:
        nr, nc = r + dr, c + dc
        if on_board(nr, nc) and board[nr][nc] == ("K" if by == "w" else "k"):
            return True

    # Lines: queen, rook, bishop.
    return _slider_attacks(board, r, c, by)


def is_in_check(board: list[list[str | None]], turn: str) -> bool:
    king_sq = find_king(board, turn)
    if king_sq is None:
        return False
    return is_attacked(board, king_sq, opposite(turn))


def castling_moves(board: list[list[str | None]], turn: str, castling: dict) -> list[tuple[str, str]]:
    """Possible castlings (as king moves) if all conditions are met."""
    moves = []
    enemy = opposite(turn)
    if turn == "w":
        row, k_sq = 7, "e1"
        oo_squares, ooo_squares = ("f1", "g1"), ("b1", "c1", "d1")
        oo_path, ooo_path = ("f1", "g1"), ("d1", "c1")
    else:
        row, k_sq = 0, "e8"
        oo_squares, ooo_squares = ("f8", "g8"), ("b8", "c8", "d8")
        oo_path, ooo_path = ("f8", "g8"), ("d8", "c8")

    def side(key: str, rook_col: int, empty: tuple[str, ...], path: tuple[str, ...]) -> None:
        if not castling.get(key):
            return
        if board[row][4] != ("K" if turn == "w" else "k") or board[row][rook_col] != ("R" if turn == "w" else "r"):
            return
        if any(board[sq_to_rc(sq)[0]][sq_to_rc(sq)[1]] is not None for sq in empty):
            return
        if is_in_check(board, turn) or any(is_attacked(board, sq, enemy) for sq in path):
            return
        moves.append((k_sq, rc_to_sq(row, 6 if rook_col == 7 else 2)))

    side("K" if turn == "w" else "k", 7, oo_squares, oo_path)
    side("Q" if turn == "w" else "q", 0, ooo_squares, ooo_path)
    return moves


def _leaper_moves(
    board: list[list[str | None]],
    r: int,
    c: int,
    enemy: str,
    offsets: tuple[tuple[int, int], ...],
    frm: str,
    moves: list[tuple[str, str]],
) -> None:
    """Knight/king moves: jump to an empty cell or an enemy piece."""
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if on_board(nr, nc):
            p = board[nr][nc]
            if p is None or piece_color(p) == enemy:
                moves.append((frm, rc_to_sq(nr, nc)))


def _slider_moves(
    board: list[list[str | None]],
    r: int,
    c: int,
    kind: str,
    enemy: str,
    frm: str,
    moves: list[tuple[str, str]],
) -> None:
    """Bishop/rook/queen moves along rays up to the first piece."""
    for dr, dc in RAY_DIRECTIONS[kind]:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            p = board[nr][nc]
            if p is None:
                moves.append((frm, rc_to_sq(nr, nc)))
            else:
                if piece_color(p) == enemy:
                    moves.append((frm, rc_to_sq(nr, nc)))
                break
            nr += dr
            nc += dc


def _pawn_moves(
    board: list[list[str | None]],
    r: int,
    c: int,
    turn: str,
    ep: str | None,
    frm: str,
    moves: list[tuple[str, str]],
) -> None:
    """Pawn moves: step, double from the start rank, captures and en passant."""
    enemy = opposite(turn)
    step = -1 if turn == "w" else 1
    start_row = 6 if turn == "w" else 1

    nr = r + step
    if on_board(nr, c) and board[nr][c] is None:
        moves.append((frm, rc_to_sq(nr, c)))
        if r == start_row and board[r + 2 * step][c] is None:
            moves.append((frm, rc_to_sq(r + 2 * step, c)))

    for dc in (-1, 1):
        nr, nc = r + step, c + dc
        if not on_board(nr, nc):
            continue
        target = rc_to_sq(nr, nc)
        if (board[nr][nc] is not None and piece_color(board[nr][nc]) == enemy) or (ep is not None and target == ep):
            moves.append((frm, target))


def gen_pseudo(
    board: list[list[str | None]],
    turn: str,
    castling: dict,
    ep: str | None,
) -> list[tuple[str, str]]:
    """Pseudo-legal moves: correct trajectories, no check filtering."""
    moves: list[tuple[str, str]] = []
    enemy = opposite(turn)
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p is None or piece_color(p) != turn:
                continue
            frm = rc_to_sq(r, c)
            kind = p.upper()

            if kind == "P":
                _pawn_moves(board, r, c, turn, ep, frm, moves)
            elif kind == "N":
                _leaper_moves(board, r, c, enemy, KNIGHT_OFFSETS, frm, moves)
            elif kind in RAY_DIRECTIONS:
                _slider_moves(board, r, c, kind, enemy, frm, moves)
            else:  # king
                _leaper_moves(board, r, c, enemy, KING_OFFSETS, frm, moves)

    moves.extend(castling_moves(board, turn, castling))
    return moves


def make_move(board: list[list[str | None]], frm: str, to: str) -> list[list[str | None]]:
    """Returns the new board after the move (castling, en passant, promotion)."""
    fr, fc = sq_to_rc(frm)
    tr, tc = sq_to_rc(to)
    nb = [row[:] for row in board]
    piece = nb[fr][fc]
    nb[fr][fc] = None
    nb[tr][tc] = piece

    if piece.upper() == "K" and abs(tc - fc) == 2:  # castling — move the rook
        if tc > fc:
            nb[tr][5], nb[tr][7] = nb[tr][7], None
        else:
            nb[tr][3], nb[tr][0] = nb[tr][0], None

    if piece.upper() == "P" and abs(tc - fc) == 1 and board[tr][tc] is None:  # en passant
        nb[fr][tc] = None

    if piece.upper() == "P" and tr in (0, 7):  # promotion — automatically to queen
        nb[tr][tc] = "Q" if piece_color(piece) == "w" else "q"

    return nb


def update_castling(castling: dict, frm: str, to: str) -> dict:
    """Update castling rights after a move."""
    corner_rooks = {"h1": "K", "a1": "Q", "h8": "k", "a8": "q"}
    new_cast = dict(castling)
    if frm == "e1":
        new_cast["K"] = new_cast["Q"] = False
    elif frm == "e8":
        new_cast["k"] = new_cast["q"] = False
    if frm in corner_rooks:  # the rook left its starting square
        new_cast[corner_rooks[frm]] = False
    if to in corner_rooks:  # the rook was captured on its starting square
        new_cast[corner_rooks[to]] = False
    return new_cast


def ep_target(board: list[list[str | None]], frm: str, to: str) -> str | None:
    """The en passant target cell after a double pawn push, otherwise None."""
    fr, fc = sq_to_rc(frm)
    tr, _ = sq_to_rc(to)
    piece = board[fr][fc]
    if piece is not None and piece.upper() == "P" and abs(tr - fr) == 2:
        return rc_to_sq((fr + tr) // 2, fc)
    return None


def legal_moves(
    board: list[list[str | None]],
    turn: str,
    castling: dict,
    ep: str | None,
) -> list[tuple[str, str]]:
    """Moves after which own king stays out of check."""
    return [
        (frm, to)
        for frm, to in gen_pseudo(board, turn, castling, ep)
        if not is_in_check(make_move(board, frm, to), turn)
    ]


def game_status(
    board: list[list[str | None]],
    turn: str,
    castling: dict,
    ep: str | None,
) -> tuple[str, str | None]:
    if legal_moves(board, turn, castling, ep):
        return "playing", None
    if is_in_check(board, turn):
        return "checkmate", opposite(turn)
    return "stalemate", None


# ---------------------------------------------------------------- controller


def handle_square(st: dict, sq: str) -> str | None:
    """Handle a square tap. Returns a hint text if no move was made."""
    if st["status"][0] != "playing":
        return "Game over — new game: /chess"

    turn = st["turn"]
    board = st["board"]
    r, c = sq_to_rc(sq)
    piece = board[r][c]

    if st["selected"] is None:
        if piece is not None and piece_color(piece) == turn:
            st["selected"] = sq
            print("Selected piece:", sq, "->", PIECE_NAMES[piece.upper()])
            return None
        return "Choose your piece."

    frm = st["selected"]
    if sq == frm:
        st["selected"] = None
        print("Selection cleared:", sq)
        return None

    if piece is not None and piece_color(piece) == turn:
        st["selected"] = sq
        print("Piece reselected:", sq)
        return None

    moves = legal_moves(board, turn, st["castling"], st["ep"])
    if (frm, sq) in moves:
        do_move(st, frm, sq)
        return None
    return "That's not a legal move."


def do_move(st: dict, frm: str, to: str) -> None:
    board = st["board"]
    r, c = sq_to_rc(frm)
    piece = board[r][c]
    moved = piece is not None and piece.upper() == "P" and to[1] in ("1", "8")

    st["board"] = make_move(board, frm, to)
    st["castling"] = update_castling(st["castling"], frm, to)
    st["ep"] = ep_target(board, frm, to)
    st["turn"] = opposite(st["turn"])
    st["selected"] = None
    st["move_count"] += 1
    st["last_move"] = (frm, to)
    st["promoted"] = moved
    st["status"] = game_status(st["board"], st["turn"], st["castling"], st["ep"])

    print(
        f"Move {st['move_count']}: {frm}-{to}"
        + (" (promoted to queen)" if moved else "")
        + f" | status: {st['status']}"
    )


# ---------------------------------------------------------------- rendering


def chess_board_markup(st: dict) -> InlineKeyboardMarkup:
    board = st["board"]
    turn = st["turn"]
    selected = st["selected"]
    game_over = st["status"][0] != "playing"

    moves_from: set[str] = set()
    if selected is not None and not game_over:
        moves_from = {to for frm, to in legal_moves(board, turn, st["castling"], st["ep"]) if frm == selected}

    check_king: str | None = None
    if not game_over and is_in_check(board, turn):
        check_king = find_king(board, turn)

    rows = []
    for r in range(8):
        row = []
        for c in range(8):
            sq = rc_to_sq(r, c)
            p = board[r][c]
            # white — outlined glyphs, black — filled glyphs: side is told by the glyph shape
            text = PIECES[p] if p is not None else ("·" if (r + c) % 2 == 0 else "•")

            if sq == selected:
                # selected piece — green button (glyph without brackets,
                # since brackets + a wide glyph do not fit into one button)
                style = ButtonStyle.SUCCESS
            elif sq in moves_from:
                # legal move: empty cell — SUCCESS, enemy piece — DANGER
                style = ButtonStyle.DANGER if p is not None else ButtonStyle.SUCCESS
            elif sq == check_king:
                style = ButtonStyle.DANGER
            else:
                style = ButtonStyle.DEFAULT
            row.append(InlineKeyboardButton(text=text, command=f"chess:{sq}", style=style))
        rows.append(row)
    return InlineKeyboardMarkup(buttons=rows)


def chess_status_text(st: dict) -> str:
    status, winner = st["status"]
    if status == "checkmate":
        wname = "White ♔" if winner == "w" else "Black ♚"
        return f"<b>♟ Chess — Checkmate! {wname} win.</b><br>New game — /chess"
    if status == "stalemate":
        return "<b>♟ Chess — Stalemate, draw.</b><br>New game — /chess"

    turn = "White" if st["turn"] == "w" else "Black"
    lines = [_header(f"♟ Chess — {turn} to move"), _position_info(st)]
    # the client folds "\n" into a space, so newlines are done with <br> (parse_mode=HTML)
    return "<br>".join(lines)


def _position_info(st: dict) -> str:
    """The status line under the header: en passant, last move, check, selection."""
    info = []
    if st["ep"]:
        info.append(f"En passant: {st['ep']}")
    if st["last_move"]:
        frm, to = st["last_move"]
        mv = f"Move: {frm}-{to}"
        if st["promoted"]:
            mv += " · promoted to queen ♛"
        info.append(mv)
    if is_in_check(st["board"], st["turn"]):
        info.append("⚠️ Check!")
    if st["selected"]:
        r, c = sq_to_rc(st["selected"])
        p = st["board"][r][c]
        if p is not None:
            color = "white" if piece_color(p) == "w" else "black"
            info.append(f"Selected: {st['selected']} ({color} {PIECE_NAMES[p.upper()]})")
    return " · ".join(info) if info else "Tap your piece to make a move"


# ---------------------------------------------------------------- handlers


@chess_r.message(Command("chess"))
async def new_game(event: Message):
    st = fresh_chess_state()
    chess_state[event.chat.chat_id] = st
    await bot.send_message(
        chat_id=event.chat.chat_id,
        text=chess_status_text(st),
        parse_mode=ParseMode.HTML,
        buttons=chess_board_markup(st),
    )
    print("New game: White moves first")


def _chess_state(callback: CallbackQuery) -> dict:
    chat_id = callback.chat.chat_id
    return chess_state.setdefault(chat_id, fresh_chess_state())


@chess_r.callback_query(F.command.startswith("chess:"))
async def on_square(callback: CallbackQuery):
    sq = callback.command.removeprefix("chess:")
    st = _chess_state(callback)
    hint = handle_square(st, sq)
    text = chess_status_text(st)
    if hint:
        text = f"{text}<br>{hint}"
    print("CLICK:", sq, ("| " + hint) if hint else "")
    await callback.edit_message(text=text, parse_mode=ParseMode.HTML, buttons=chess_board_markup(st))


# =================================================================== fallback

# Root routers are independent, so this catch-all also sees the other
# features' callbacks — log only buttons none of the routers above own.
KNOWN_BUTTON_PREFIXES = ("btn:", "menu:", "ttt:", "calendar:", "chess:")


@chess_r.callback_query()
async def on_unknown(callback: CallbackQuery):
    command = callback.command or ""
    if not command.startswith(KNOWN_BUTTON_PREFIXES):
        print("Unknown button:", command)


if __name__ == "__main__":
    asyncio.run(bot.run())
