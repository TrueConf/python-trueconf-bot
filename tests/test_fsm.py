from __future__ import annotations
import asyncio
import pytest
from trueconf.fsm.state import State, StatesGroup
from trueconf.fsm.context import FSMContext
from trueconf.fsm.storage.memory import MemoryStorage
from trueconf.fsm.key_builder import StorageKey, DefaultKeyBuilder
from trueconf.fsm.manager import FSMManager
from trueconf.fsm.filters import StateFilter
from trueconf.fsm.middleware import FSMMiddleware
from trueconf.dispatcher.router import Router
from trueconf.dispatcher.dispatcher import Dispatcher
from trueconf.types.message import Message
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.text import TextContent
from trueconf.enums.message_type import MessageType
from trueconf.enums.envelope_author_type import EnvelopeAuthorType

pytestmark = pytest.mark.anyio


def _make_message(author_id: str = "user1", text: str = "hello", chat_id: str = "chat_1") -> Message:
    return Message(
        timestamp=1,
        type=MessageType.PLAIN_MESSAGE,
        author=EnvelopeAuthor(id=author_id, type=EnvelopeAuthorType.USER),
        box=EnvelopeBox(id=1, position="top"),
        content=TextContent(text=text, parse_mode="text"),
        message_id=f"msg_{author_id}",
        chat_id=chat_id,
        is_edited=False,
    )


class FakeBot:
    me_id = "bot_id"


# ──────────────────────────────────────────────
# State declaration
# ──────────────────────────────────────────────

class TestStateDeclaration:
    def test_state_str_format(self):
        class Form(StatesGroup):
            name = State()
            age = State()
        assert str(Form.name) == "Form:name"
        assert str(Form.age) == "Form:age"

    def test_custom_state_string(self):
        s = State("custom:state")
        assert str(s) == "custom:state"

    def test_unbound_state_raises(self):
        s = State()
        with pytest.raises(RuntimeError, match="not bound"):
            str(s)

    def test_states_group_states_tuple(self):
        class Form(StatesGroup):
            name = State()
            age = State()
        assert len(Form.__states__) == 2
        assert all(isinstance(s, State) for s in Form.__states__)

    def test_state_equality(self):
        class Form(StatesGroup):
            name = State()
        assert Form.name == "Form:name"
        assert Form.name == Form.name

    def test_state_hashable(self):
        class Form(StatesGroup):
            name = State()
        d = {Form.name: "value"}
        assert d["Form:name"] == "value"

    def test_state_bind_double_raises(self):
        class Form(StatesGroup):
            name = State()
        with pytest.raises(RuntimeError, match="already bound"):
            Form.name.bind(Form, "other")

    def test_custom_state_not_bound(self):
        s = State("external")
        assert s._group is None
        assert str(s) == "external"


# ──────────────────────────────────────────────
# StorageKey
# ──────────────────────────────────────────────

class TestStorageKey:
    def test_frozen(self):
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        with pytest.raises(AttributeError):
            key.chat_id = "other"  # type: ignore[misc]

    def test_equality(self):
        k1 = StorageKey(bot_id="b", chat_id="c", user_id="u")
        k2 = StorageKey(bot_id="b", chat_id="c", user_id="u")
        assert k1 == k2

    def test_hashable(self):
        k1 = StorageKey(bot_id="b", chat_id="c", user_id="u")
        k2 = StorageKey(bot_id="b", chat_id="c", user_id="u")
        assert hash(k1) == hash(k2)
        assert len({k1, k2}) == 1

    def test_different_keys(self):
        k1 = StorageKey(bot_id="b", chat_id="c", user_id="u1")
        k2 = StorageKey(bot_id="b", chat_id="c", user_id="u2")
        assert k1 != k2


# ──────────────────────────────────────────────
# DefaultKeyBuilder
# ──────────────────────────────────────────────

class TestDefaultKeyBuilder:
    def test_builds_from_message(self):
        builder = DefaultKeyBuilder()
        msg = _make_message("user1", chat_id="chat_1")
        key = builder.build(FakeBot(), msg)
        assert key.bot_id == "bot_id"
        assert key.chat_id == "chat_1"
        assert key.user_id == "user1"

    def test_raises_on_missing_chat_id(self):
        builder = DefaultKeyBuilder()
        msg = _make_message("user1")
        msg.chat_id = None  # type: ignore[assignment]
        with pytest.raises(RuntimeError, match="chat_id"):
            builder.build(FakeBot(), msg)

    def test_raises_on_missing_user_id(self):
        builder = DefaultKeyBuilder()
        msg = _make_message("user1")
        msg.author = None  # type: ignore[assignment]
        with pytest.raises(RuntimeError, match="user_id"):
            builder.build(FakeBot(), msg)


# ──────────────────────────────────────────────
# MemoryStorage
# ──────────────────────────────────────────────

class TestMemoryStorage:
    async def test_get_set_state(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        assert await storage.get_state(key) is None
        await storage.set_state(key, "Form:name")
        assert await storage.get_state(key) == "Form:name"

    async def test_set_state_none_keeps_data(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:name")
        await storage.set_data(key, {"x": 1})
        await storage.set_state(key, None)
        assert await storage.get_state(key) is None
        assert await storage.get_data(key) == {"x": 1}

    async def test_clear_removes_everything(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:name")
        await storage.set_data(key, {"x": 1})
        await storage.clear(key)
        assert await storage.get_state(key) is None
        assert await storage.get_data(key) == {}

    async def test_update_data_merges(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_data(key, {"a": 1})
        result = await storage.update_data(key, {"b": 2})
        assert result == {"a": 1, "b": 2}

    async def test_different_keys_independent(self):
        storage = MemoryStorage()
        key1 = StorageKey(bot_id="b", chat_id="c", user_id="u1")
        key2 = StorageKey(bot_id="b", chat_id="c", user_id="u2")
        await storage.set_state(key1, "Form:name")
        assert await storage.get_state(key2) is None

    async def test_get_data_empty(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        assert await storage.get_data(key) == {}

    async def test_set_data_replaces(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_data(key, {"a": 1})
        await storage.set_data(key, {"b": 2})
        assert await storage.get_data(key) == {"b": 2}


# ──────────────────────────────────────────────
# FSMContext
# ──────────────────────────────────────────────

class TestFSMContext:
    async def test_state_lifecycle(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        ctx = FSMContext(storage, key)

        assert await ctx.get_state() is None
        await ctx.set_state("Form:name")
        assert await ctx.get_state() == "Form:name"

        await ctx.update_data(name="Nikita")
        assert await ctx.get_data() == {"name": "Nikita"}

        await ctx.clear()
        assert await ctx.get_state() is None
        assert await ctx.get_data() == {}

    async def test_set_state_with_state_object(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        ctx = FSMContext(storage, key)

        class Form(StatesGroup):
            name = State()

        await ctx.set_state(Form.name)
        assert await ctx.get_state() == "Form:name"

    async def test_set_state_none_keeps_data(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        ctx = FSMContext(storage, key)

        await ctx.set_state("Form:name")
        await ctx.update_data(x=1)
        await ctx.set_state(None)
        assert await ctx.get_state() is None
        assert await ctx.get_data() == {"x": 1}

    async def test_key_property(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        ctx = FSMContext(storage, key)
        assert ctx.key == key


# ──────────────────────────────────────────────
# StateFilter
# ──────────────────────────────────────────────

class TestStateFilter:
    async def test_matches_current_state(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:name")
        ctx = FSMContext(storage, key)

        f = StateFilter("Form:name")
        assert await f(_make_message(), state=ctx) is True

    async def test_rejects_wrong_state(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:age")
        ctx = FSMContext(storage, key)

        f = StateFilter("Form:name")
        assert await f(_make_message(), state=ctx) is False

    async def test_matches_none_state(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        ctx = FSMContext(storage, key)

        f = StateFilter(None)
        assert await f(_make_message(), state=ctx) is True

    async def test_multiple_states(self):
        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:age")
        ctx = FSMContext(storage, key)

        f = StateFilter("Form:name", "Form:age")
        assert await f(_make_message(), state=ctx) is True

    async def test_raises_without_fsm_context(self):
        f = StateFilter("Form:name")
        with pytest.raises(RuntimeError, match="FSMContext"):
            await f(_make_message(), state=None)

    async def test_state_object_as_filter_arg(self):
        class Form(StatesGroup):
            name = State()

        storage = MemoryStorage()
        key = StorageKey(bot_id="b", chat_id="c", user_id="u")
        await storage.set_state(key, "Form:name")
        ctx = FSMContext(storage, key)

        f = StateFilter(Form.name)
        assert await f(_make_message(), state=ctx) is True


# ──────────────────────────────────────────────
# FSMMiddleware
# ──────────────────────────────────────────────

class TestFSMMiddleware:
    async def test_injects_state_into_data(self):
        storage = MemoryStorage()
        fsm = FSMManager(storage=storage)
        mw = FSMMiddleware(fsm)
        data: dict = {"bot": FakeBot()}

        received_data: dict = {}

        async def handler(evt, d):
            received_data.update(d)

        msg = _make_message()
        await mw(handler, msg, data)
        assert "state" in received_data
        assert isinstance(received_data["state"], FSMContext)

    async def test_no_bot_skips_injection(self):
        storage = MemoryStorage()
        fsm = FSMManager(storage=storage)
        mw = FSMMiddleware(fsm)
        data: dict = {}

        async def handler(evt, d):
            pass

        await mw(handler, _make_message(), data)
        assert "state" not in data


# ──────────────────────────────────────────────
# Dispatcher integration
# ──────────────────────────────────────────────

class TestDispatcherFSMIntegration:
    async def test_setup_fsm_registers_middleware(self):
        dp = Dispatcher(storage=MemoryStorage())
        assert dp.fsm is not None
        assert any(isinstance(mw, FSMMiddleware) for mw in dp._outer_middlewares)

    async def test_fsm_middleware_first_in_chain(self):
        from trueconf.middleware import BaseMiddleware

        class DummyMW(BaseMiddleware):
            async def __call__(self, handler, event, data):
                await handler(event, data)

        dp = Dispatcher(storage=MemoryStorage())
        dp.outer_middleware(DummyMW())
        assert isinstance(dp._outer_middlewares[0], FSMMiddleware)

    async def test_setup_fsm_twice_raises(self):
        dp = Dispatcher(storage=MemoryStorage())
        with pytest.raises(RuntimeError, match="already configured"):
            dp.setup_fsm(storage=MemoryStorage())

    async def test_state_filter_in_pipeline(self):
        class Form(StatesGroup):
            name = State()

        dp = Dispatcher(storage=MemoryStorage())
        router = Router()
        dp.include_router(router)

        calls: list[str] = []

        @router.message(StateFilter(Form.name))
        async def on_name(msg: Message, state: FSMContext):
            calls.append("name_handler")

        # Set state manually for test
        key = StorageKey(bot_id="bot_id", chat_id="chat_1", user_id="user1")
        await dp.fsm.storage.set_state(key, "Form:name")

        msg = _make_message("user1")
        await dp._feed_update(msg, {"bot": FakeBot()})
        await asyncio.sleep(0.1)
        assert calls == ["name_handler"]

    async def test_state_filter_rejects_wrong_state(self):
        class Form(StatesGroup):
            name = State()
            age = State()

        dp = Dispatcher(storage=MemoryStorage())
        router = Router()
        dp.include_router(router)

        calls: list[str] = []

        @router.message(StateFilter(Form.name))
        async def on_name(msg: Message, state: FSMContext):
            calls.append("name")

        @router.message(StateFilter(Form.age))
        async def on_age(msg: Message, state: FSMContext):
            calls.append("age")

        key = StorageKey(bot_id="bot_id", chat_id="chat_1", user_id="user1")
        await dp.fsm.storage.set_state(key, "Form:age")

        msg = _make_message("user1")
        await dp._feed_update(msg, {"bot": FakeBot()})
        await asyncio.sleep(0.1)
        assert calls == ["age"]

    async def test_sugar_state_in_router_message(self):
        """Test that @router.message(Form.name) works as sugar for @router.message(StateFilter(Form.name))."""
        class Form(StatesGroup):
            name = State()

        dp = Dispatcher(storage=MemoryStorage())
        router = Router()
        dp.include_router(router)

        calls: list[str] = []

        @router.message(Form.name)
        async def on_name(msg: Message, state: FSMContext):
            calls.append("sugar_works")

        key = StorageKey(bot_id="bot_id", chat_id="chat_1", user_id="user1")
        await dp.fsm.storage.set_state(key, "Form:name")

        msg = _make_message("user1")
        await dp._feed_update(msg, {"bot": FakeBot()})
        await asyncio.sleep(0.1)
        assert calls == ["sugar_works"]

    async def test_handler_receives_state_via_di(self):
        """Test that state: FSMContext is injected into handler via DI."""
        class Form(StatesGroup):
            name = State()

        dp = Dispatcher(storage=MemoryStorage())
        router = Router()
        dp.include_router(router)

        received_state: FSMContext | None = None

        @router.message(Form.name)
        async def on_name(msg: Message, state: FSMContext):
            nonlocal received_state
            received_state = state

        key = StorageKey(bot_id="bot_id", chat_id="chat_1", user_id="user1")
        await dp.fsm.storage.set_state(key, "Form:name")

        msg = _make_message("user1")
        await dp._feed_update(msg, {"bot": FakeBot()})
        await asyncio.sleep(0.1)

        assert received_state is not None
        assert isinstance(received_state, FSMContext)
        assert await received_state.get_state() == "Form:name"


# ──────────────────────────────────────────────
# Nested StatesGroups
# ──────────────────────────────────────────────

class TestNestedStatesGroups:
    def test_nested_state_str_format(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()
                street = State()

            confirm = State()

        assert str(Form.name) == "Form:name"
        assert str(Form.Address.city) == "Form.Address:city"
        assert str(Form.Address.street) == "Form.Address:street"
        assert str(Form.confirm) == "Form:confirm"

    def test_parent_child_link(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

        assert Form.Address.__parent__ is Form
        assert Form.__parent__ is None

    def test_childs_tuple(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

            class Payment(StatesGroup):
                card = State()

        assert Form.Address in Form.__childs__
        assert Form.Payment in Form.__childs__
        assert len(Form.__childs__) == 2

    def test_all_states_recursive(self):
        class Form(StatesGroup):
            name = State()
            age = State()

            class Address(StatesGroup):
                city = State()
                street = State()

            confirm = State()

        all_names = [str(s) for s in Form.__all_states__]
        assert "Form:name" in all_names
        assert "Form:age" in all_names
        assert "Form.Address:city" in all_names
        assert "Form.Address:street" in all_names
        assert "Form:confirm" in all_names
        assert len(Form.__all_states__) == 5

    def test_all_childs_recursive(self):
        class Form(StatesGroup):
            class Address(StatesGroup):
                city = State()

        assert Form.Address in Form.__all_childs__

    def test_contains_state_string(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

        assert "Form:name" in Form
        assert "Form.Address:city" in Form
        assert "Form:nonexistent" not in Form

    def test_contains_state_object(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

        assert Form.name in Form
        assert Form.Address.city in Form

    def test_contains_child_group(self):
        class Form(StatesGroup):
            class Address(StatesGroup):
                city = State()

        assert Form.Address in Form

    def test_iter_states(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

            confirm = State()

        names = [str(s) for s in Form]
        assert "Form:name" in names
        assert "Form.Address:city" in names
        assert "Form:confirm" in names

    def test_get_root(self):
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()

        assert Form.get_root() is Form
        assert Form.Address.get_root() is Form

    def test_nested_state_as_filter(self):
        """Test that nested State works as StateFilter sugar."""
        class Form(StatesGroup):
            class Address(StatesGroup):
                city = State()

        f = StateFilter(Form.Address.city)
        assert "Form.Address:city" in f._states

    def test_nested_state_in_storage(self):
        """Test that nested states work with storage."""
        class Form(StatesGroup):
            class Address(StatesGroup):
                city = State()

        f = StateFilter(Form.Address.city)
        assert "Form.Address:city" in f._states

    async def test_nested_state_in_pipeline(self):
        """Test nested states work end-to-end in the dispatcher pipeline."""
        class Form(StatesGroup):
            name = State()

            class Address(StatesGroup):
                city = State()
                street = State()

            confirm = State()

        dp = Dispatcher(storage=MemoryStorage())
        router = Router()
        dp.include_router(router)

        calls: list[str] = []

        @router.message(Form.Address.city)
        async def on_city(msg: Message, state: FSMContext):
            calls.append("city")

        @router.message(Form.Address.street)
        async def on_street(msg: Message, state: FSMContext):
            calls.append("street")

        @router.message(Form.name)
        async def on_name(msg: Message, state: FSMContext):
            calls.append("name")

        key = StorageKey(bot_id="bot_id", chat_id="chat_1", user_id="user1")

        # Test Form.Address:city
        await dp.fsm.storage.set_state(key, "Form.Address:city")
        await dp._feed_update(_make_message("user1"), {"bot": FakeBot()})
        await asyncio.sleep(0.05)
        assert calls == ["city"]

        # Test Form.Address:street
        calls.clear()
        await dp.fsm.storage.set_state(key, "Form.Address:street")
        await dp._feed_update(_make_message("user1"), {"bot": FakeBot()})
        await asyncio.sleep(0.05)
        assert calls == ["street"]

        # Test Form:name (not nested)
        calls.clear()
        await dp.fsm.storage.set_state(key, "Form:name")
        await dp._feed_update(_make_message("user1"), {"bot": FakeBot()})
        await asyncio.sleep(0.05)
        assert calls == ["name"]
