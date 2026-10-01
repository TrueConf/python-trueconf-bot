import re
from dataclasses import dataclass
from typing import List

HTML_TAG_RE = re.compile(
    r"<(?P<closing>/)?(?P<tag>quote|br|[biusa])(?P<attrs>\s+[^>]*)?(?P<self_close>\s*/)?>",
    re.IGNORECASE,
)

MD_LINK_RE = re.compile(r"\[([^]]+)\]\(([^)]+)\)")

HTML_ANCHOR_RE = re.compile(r"<a(?P<attrs>\s+[^>]*)>(?P<inner>.*?)</a>", re.IGNORECASE | re.DOTALL)

HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


@dataclass
class StackItem:
    kind: str  # 'html' | 'md'
    name: str  # tag name or marker id
    open_token: str  # exact opener to reopen
    close_token: str  # exact closer to close


@dataclass
class Token:
    kind: str  # 'text', 'space', 'html_open', 'html_close', 'md_marker', 'md_quote', 'md_link', 'html_anchor'
    raw: str
    name: str | None = None
    open_token: str | None = None
    close_token: str | None = None
    visible_len: int | None = None
    href: str | None = None
    inner_text: str | None = None
    close_quote: bool = False


def safe_split_text(text: str, limit: int = 4096) -> List[str]:  # noqa: C901
    if not text:
        return []
    if visible_len(text) <= limit:
        return [text]

    tokens = _tokenize(text)
    result: List[str] = []

    idx = 0
    carry_stack: List[StackItem] = []
    carry_raw = ""

    while idx < len(tokens):
        prefix = "".join(item.open_token for item in carry_stack)
        current = prefix + carry_raw
        stack = carry_stack.copy()
        stack_history: List[tuple[int, int, str, List[StackItem]]] = [(0, 0, "", stack.copy())]
        prefix_visible_text, prefix_raw_positions = _scan_visible(prefix)
        carry_visible_text, carry_raw_positions = _scan_visible(carry_raw, fragment=True)
        visible_used = len(prefix_visible_text) + len(carry_visible_text)
        tail_visible_chars = list(prefix_visible_text[-20:]) + list(carry_visible_text[-20:])
        tail_raw_positions = list(prefix_raw_positions[-20:]) + [len(prefix) + pos for pos in carry_raw_positions[-20:]]
        last_break_save: tuple[int, str, List[StackItem], str] | None = None
        carry_raw = ""

        while idx < len(tokens):
            token = tokens[idx]
            token_visible = _token_visible_len(token)
            prev_stack = stack
            next_stack = _apply_token_to_stack(stack, token)
            projected_visible = visible_used + token_visible

            if projected_visible <= limit:
                raw_start = len(current)
                current += token.raw
                stack = next_stack
                visible_used = projected_visible
                if next_stack != prev_stack or token.kind == "md_quote":
                    stack_history.append((len(current) - len(token.raw), len(current), token.kind, stack.copy()))
                _extend_visible_window(tail_visible_chars, tail_raw_positions, token, raw_start)

                break_save = _make_break_save(
                    current=current,
                    next_idx=idx + 1,
                    token=token,
                    stack_history=stack_history,
                    tail_visible_chars=tail_visible_chars,
                    tail_raw_positions=tail_raw_positions,
                    limit=limit,
                )
                if break_save is not None:
                    last_break_save = break_save

                idx += 1
                continue

            if token.kind in ("md_link", "html_anchor"):
                break

            available_visible = limit - visible_used
            if available_visible <= 0:
                break

            if token.kind in ("text", "space"):
                head, tail = _split_visible_text_for_limit(token.raw, available_visible)
                if head:
                    raw_start = len(current)
                    current += head
                    visible_used += len(head)
                    head_token = Token(
                        kind=token.kind,
                        raw=head,
                        visible_len=len(head),
                        close_quote=token.close_quote if "\n" in head else False,
                    )
                    head_stack = _apply_token_to_stack(stack, head_token)
                    if head_stack != stack:
                        stack = head_stack
                        stack_history.append((len(current) - len(head), len(current), head_token.kind, stack.copy()))
                    _extend_visible_window(tail_visible_chars, tail_raw_positions, head_token, raw_start)

                    break_save = _make_break_save(
                        current=current,
                        next_idx=idx,
                        token=head_token,
                        stack_history=stack_history,
                        tail_visible_chars=tail_visible_chars,
                        tail_raw_positions=tail_raw_positions,
                        limit=limit,
                    )
                    if break_save is not None:
                        last_break_save = break_save

                    if tail:
                        tokens[idx] = Token(kind=token.kind, raw=tail, visible_len=len(tail))
                    else:
                        idx += 1
                break

            break

        if idx >= len(tokens):
            chunk = _strip_br_edges(current) + _closing_suffix(stack)
            if chunk:
                result.append(chunk)
            break

        if last_break_save is not None:
            next_idx, safe_current, safe_stack, raw_tail = last_break_save
            chunk = safe_current + _closing_suffix(safe_stack)
            if chunk:
                result.append(chunk)

            idx = next_idx
            carry_stack = safe_stack
            carry_raw = raw_tail
            continue

        token = tokens[idx]

        if token.kind in ("md_link", "html_anchor"):
            if current != prefix:
                chunk = _strip_br_edges(current) + _closing_suffix(stack)
                if chunk:
                    result.append(chunk)
                carry_stack = stack
                continue

            raw = token.raw
            if _token_visible_len(token) <= limit:
                result.append(raw)
                idx += 1
            else:
                head_raw, tail_raw = _split_atomic_token_raw(token, limit)
                if head_raw:
                    result.append(head_raw)
                if tail_raw:
                    tokens[idx] = Token(kind="text", raw=tail_raw, visible_len=len(tail_raw))
                else:
                    idx += 1
            carry_stack = stack
            continue

        if current != prefix:
            chunk = _strip_br_edges(current) + _closing_suffix(stack)
            if chunk:
                result.append(chunk)
            carry_stack = stack
            continue

        raw = token.raw
        head, tail = _split_visible_text_for_limit(raw, limit, allow_defer=False)
        if head:
            result.append(head)
        if tail:
            tokens[idx] = Token(kind="text", raw=tail, visible_len=len(tail))
        else:
            idx += 1
        carry_stack = []

    return [chunk for chunk in result if chunk and visible_len(chunk) > 0]


def _tokenize(text: str) -> List[Token]:  # noqa: C901
    tokens: List[Token] = []
    i = 0
    n = len(text)

    while i < n:
        m = HTML_ANCHOR_RE.match(text, i)
        if m:
            raw = m.group(0)
            attrs = m.group("attrs") or ""
            inner = m.group("inner") or ""
            href_match = HREF_RE.search(attrs)
            href = href_match.group(1) if href_match else ""
            visible = len(_visible_text_for_breaks(inner)) + (1 + len(href) if href else 0)
            tokens.append(
                Token(
                    kind="html_anchor",
                    raw=raw,
                    visible_len=visible,
                    href=href,
                    inner_text=inner,
                )
            )
            i += len(raw)
            continue

        m = HTML_TAG_RE.match(text, i)
        if m:
            raw = m.group(0)
            tag = m.group("tag").lower()
            closing = bool(m.group("closing"))

            if tag == "br":
                if closing:
                    tokens.append(Token(kind="text", raw=raw, visible_len=len(raw)))
                else:
                    tokens.append(Token(kind="br", raw=raw, visible_len=0))
            elif closing:
                tokens.append(Token(kind="html_close", raw=raw, name=tag, close_token=f"</{tag}>"))
            else:
                tokens.append(Token(kind="html_open", raw=raw, name=tag, open_token=raw, close_token=f"</{tag}>"))

            i += len(raw)
            continue

        m = MD_LINK_RE.match(text, i)
        if m:
            raw = m.group(0)
            link_text = m.group(1)
            href = m.group(2)
            visible = len(_visible_text_for_breaks(link_text)) + (1 + len(href) if href else 0)
            tokens.append(
                Token(
                    kind="md_link",
                    raw=raw,
                    visible_len=visible,
                    href=href,
                    inner_text=link_text,
                )
            )
            i += len(raw)
            continue

        if text.startswith("__", i):
            prev_char = text[i - 1] if i > 0 else ""
            next_char = text[i + 2] if i + 2 < n else ""

            if prev_char.isalnum() and next_char.isalnum():
                tokens.append(Token(kind="text", raw="__", visible_len=2))
            else:
                tokens.append(
                    Token(
                        kind="md_marker",
                        raw="__",
                        name="__",
                        open_token="__",
                        close_token="__",
                        visible_len=0,
                    )
                )
            i += 2
            continue

        if text[i] in "*_~":
            marker = text[i]
            prev_char = text[i - 1] if i > 0 else ""
            next_char = text[i + 1] if i + 1 < n else ""

            # Если символ внутри слова/идентификатора, это обычный текст, а не markdown
            if prev_char.isalnum() and next_char.isalnum():
                tokens.append(Token(kind="text", raw=marker, visible_len=1))
                i += 1
                continue

            if i + 1 < n and text[i + 1] == marker:
                raw = marker * 2
                tokens.append(
                    Token(
                        kind="md_marker",
                        raw=raw,
                        name=raw,
                        open_token=raw,
                        close_token=raw,
                        visible_len=0,
                    )
                )
                i += 2
                continue

            tokens.append(
                Token(
                    kind="md_marker",
                    raw=marker,
                    name=marker,
                    open_token=marker,
                    close_token=marker,
                    visible_len=0,
                )
            )
            i += 1
            continue

        if text[i] == ">" and (i == 0 or text[i - 1] == "\n"):
            tokens.append(
                Token(
                    kind="md_quote",
                    raw=">",
                    name=">",
                    open_token=">",
                    close_token="",
                    visible_len=0,
                )
            )
            i += 1
            continue

        if text[i].isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            raw = text[i:j]
            close_quote = "\n" in raw and (j >= n or text[j] != ">")
            tokens.append(Token(kind="space", raw=raw, visible_len=len(raw), close_quote=close_quote))
            i = j
            continue

        # Неизвестный HTML-тег — просто как текст
        if text[i] == "<":
            gt = text.find(">", i + 1)
            if gt != -1:
                raw = text[i : gt + 1]
                tokens.append(Token(kind="text", raw=raw, visible_len=len(raw)))
                i = gt + 1
            else:
                raw = text[i]
                tokens.append(Token(kind="text", raw=raw, visible_len=1))
                i += 1
            continue

        j = i
        while j < n:
            c = text[j]
            if c.isspace() or c in "<[*_~":
                break
            j += 1

        if j == i:
            raw = text[i]
            tokens.append(Token(kind="text", raw=raw, visible_len=1))
            i += 1
        else:
            raw = text[i:j]
            tokens.append(Token(kind="text", raw=raw, visible_len=len(raw)))
            i = j

    return tokens


def _apply_token_to_stack(stack: List[StackItem], token: Token) -> List[StackItem]:
    new_stack = stack.copy()

    if token.kind == "html_open":
        new_stack.append(
            StackItem(
                kind="html",
                name=token.name or "",
                open_token=token.open_token or "",
                close_token=token.close_token or "",
            )
        )
        return new_stack

    if token.kind == "html_close":
        _pop_last_matching(new_stack, kind="html", name=token.name or "")
        return new_stack

    if token.kind == "md_marker":
        if new_stack and new_stack[-1].kind == "md" and new_stack[-1].name == token.name:
            new_stack.pop()
        else:
            new_stack.append(
                StackItem(
                    kind="md",
                    name=token.name or "",
                    open_token=token.open_token or "",
                    close_token=token.close_token or "",
                )
            )
        return new_stack

    if token.kind == "md_quote":
        if not (new_stack and new_stack[-1].kind == "md" and new_stack[-1].name == ">"):
            new_stack.append(StackItem(kind="md", name=">", open_token=">", close_token=""))
        return new_stack

    if token.kind == "space":
        if token.close_quote:
            _pop_last_matching(new_stack, kind="md", name=">")
        return new_stack

    return new_stack


# Helper functions for visible length, markup stripping, splitting, etc.
def _token_visible_len(token: Token) -> int:
    if token.visible_len is not None:
        return token.visible_len

    if token.kind in ("html_open", "html_close", "md_marker", "md_quote", "br"):
        return 0

    return len(_visible_text_for_breaks(token.raw))


def visible_len(text: str) -> int:
    visible_text, _ = _scan_visible(text)
    return len(visible_text)


def _token_visible_text(token: Token) -> str:
    if token.kind in ("html_open", "html_close", "md_marker", "md_quote", "br"):
        return ""
    if token.kind in ("md_link", "html_anchor"):
        inner = token.inner_text or ""
        href = token.href or ""
        return f"{_visible_text_for_breaks(inner)} {href}".strip()
    return token.raw


def _extend_visible_window(
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
    token: Token,
    raw_start: int,
) -> None:
    if token.kind == "br":
        tail_visible_chars.append("\n")
        tail_raw_positions.append(raw_start + len(token.raw))
    else:
        visible_text = _token_visible_text(token)
        if not visible_text:
            return

        if token.kind in ("md_link", "html_anchor"):
            raw_pos = raw_start + len(token.raw)
            for ch in visible_text:
                tail_visible_chars.append(ch)
                tail_raw_positions.append(raw_pos)
        else:
            for idx, ch in enumerate(visible_text, start=1):
                tail_visible_chars.append(ch)
                tail_raw_positions.append(raw_start + idx)

    if len(tail_visible_chars) > 20:
        extra = len(tail_visible_chars) - 20
        del tail_visible_chars[:extra]
        del tail_raw_positions[:extra]


def _scan_visible(raw: str, fragment: bool = False) -> tuple[str, List[int]]:  # noqa: C901
    visible_chars: List[str] = []
    raw_positions: List[int] = []
    i = 0
    n = len(raw)

    while i < n:
        m = HTML_ANCHOR_RE.match(raw, i)
        if m:
            full_raw = m.group(0)
            attrs = m.group("attrs") or ""
            inner = m.group("inner") or ""
            href_match = HREF_RE.search(attrs)
            href = href_match.group(1) if href_match else ""
            rendered = f"{_visible_text_for_breaks(inner)} {href}".strip()
            end_pos = i + len(full_raw)
            for ch in rendered:
                visible_chars.append(ch)
                raw_positions.append(end_pos)
            i = end_pos
            continue

        m = MD_LINK_RE.match(raw, i)
        if m:
            full_raw = m.group(0)
            inner = m.group(1) or ""
            href = m.group(2) or ""
            rendered = f"{_visible_text_for_breaks(inner)} {href}".strip()
            end_pos = i + len(full_raw)
            for ch in rendered:
                visible_chars.append(ch)
                raw_positions.append(end_pos)
            i = end_pos
            continue

        m = HTML_TAG_RE.match(raw, i)
        if m:
            i += len(m.group(0))
            continue

        if raw[i] == ">" and ((i == 0 and not fragment) or (i > 0 and raw[i - 1] == "\n")):
            i += 1
            continue

        if raw.startswith("__", i):
            prev_char = raw[i - 1] if i > 0 else ("a" if fragment else "")
            next_char = raw[i + 2] if i + 2 < n else ("a" if fragment else "")
            if prev_char.isalnum() and next_char.isalnum():
                visible_chars.extend(["_", "_"])
                raw_positions.extend([i + 2, i + 2])
            i += 2
            continue

        if raw[i] in "*_~":
            prev_char = raw[i - 1] if i > 0 else ("a" if fragment else "")
            next_char = raw[i + 1] if i + 1 < n else ("a" if fragment else "")
            if prev_char.isalnum() and next_char.isalnum():
                visible_chars.append(raw[i])
                raw_positions.append(i + 1)
            i += 1
            continue

        visible_chars.append(raw[i])
        raw_positions.append(i + 1)
        i += 1

    return "".join(visible_chars), raw_positions


def _visible_text_for_breaks(raw: str) -> str:
    visible_text, _ = _scan_visible(raw)
    return visible_text


def _find_last_break_pos(
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
) -> int | None:
    if not tail_visible_chars:
        return None

    window = "".join(tail_visible_chars)

    nl_pos = window.rfind("\n")
    if nl_pos != -1:
        return tail_raw_positions[nl_pos]

    punctuation = ".,!?;:)]}"
    for offset, ch in enumerate(window):
        if ch in punctuation:
            return tail_raw_positions[offset]

    space_pos = window.rfind(" ")
    if space_pos != -1:
        return tail_raw_positions[space_pos]

    return None


def _advance_past_markers(
    break_pos: int,
    stack_history: List[tuple[int, int, str, List[StackItem]]],
) -> int:
    markers = [(start, end) for start, end, kind, _ in stack_history if kind in ("md_marker", "md_quote")]
    while True:
        next_pos = None
        for start, end in markers:
            if start == break_pos and end > break_pos:
                next_pos = end
                break
        if next_pos is None:
            return break_pos
        break_pos = next_pos


def _stack_at_break(
    break_pos: int,
    stack_history: List[tuple[int, int, str, List[StackItem]]],
) -> List[StackItem]:
    for _, end, _, snapshot in reversed(stack_history):
        if end <= break_pos:
            return snapshot
    return []


def _strip_br_edges(raw: str) -> str:
    """Trim <br> runs (and edge whitespace) for a finished chunk."""
    s = re.sub(r"^(?:\s*<br\s*/?>\s*)+", "", raw, flags=re.IGNORECASE)
    s = re.sub(r"(?:\s*<br\s*/?>\s*)+$", "", s, flags=re.IGNORECASE)
    return s.rstrip()


def _lstrip_carry(raw: str) -> str:
    """Trim leading <br> runs and whitespace from a carry fragment."""
    return re.sub(r"^(?:\s*<br\s*/?>\s*)+", "", raw, flags=re.IGNORECASE).lstrip()


def _make_break_save(
    current: str,
    next_idx: int,
    token: Token,
    stack_history: List[tuple[int, int, str, List[StackItem]]],
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
    limit: int,
) -> tuple[int, str, List[StackItem], str] | None:
    if token.kind in ("md_link", "html_anchor"):
        safe_stack = stack_history[-1][3] if stack_history else []
        return next_idx, _strip_br_edges(current), safe_stack, ""

    break_pos = _find_last_break_pos(tail_visible_chars, tail_raw_positions)
    if break_pos is None:
        return None

    break_pos = _advance_past_markers(break_pos, stack_history)

    safe_current = _strip_br_edges(current[:break_pos])
    raw_tail = _lstrip_carry(current[break_pos:])

    if not safe_current.strip():
        return None

    carry_visible = sum(1 for pos in tail_raw_positions if pos >= break_pos)
    if carry_visible > limit:
        return None

    safe_stack = _stack_at_break(break_pos, stack_history)
    return next_idx, safe_current, safe_stack, raw_tail


def _adjust_split_pos(raw: str, n: int) -> int:
    head = raw[:n]
    lt = head.rfind("<")
    if lt != -1 and ">" not in head[lt + 1 :]:
        return lt
    amp = head.rfind("&")
    if amp != -1 and ";" not in head[amp + 1 :]:
        return amp
    return n


def _split_visible_text_for_limit(
    raw: str,
    available_visible: int,
    allow_defer: bool = True,
) -> tuple[str, str]:
    if available_visible <= 0:
        return "", raw

    if len(raw) <= available_visible:
        return raw, ""

    if allow_defer:
        head_len = _adjust_split_pos(raw, available_visible)
        if head_len <= 0:
            return "", raw
    else:
        head_len = available_visible

    return raw[:head_len], raw[head_len:]


def _split_atomic_token_raw(token: Token, limit: int) -> tuple[str, str]:
    if token.kind in ("md_link", "html_anchor"):
        inner = token.inner_text or ""
        href = token.href or ""
        visible_prefix = f"{_visible_text_for_breaks(inner)} {href}".strip()
        if len(visible_prefix) <= limit:
            return token.raw, ""
        return visible_prefix[:limit], visible_prefix[limit:]

    raw = token.raw
    if len(raw) <= limit:
        return raw, ""
    return raw[:limit], raw[limit:]


def _pop_last_matching(stack: List[StackItem], kind: str, name: str) -> None:
    for i in range(len(stack) - 1, -1, -1):
        if stack[i].kind == kind and stack[i].name == name:
            del stack[i]
            return


def _closing_suffix(stack: List[StackItem]) -> str:
    return "".join(item.close_token for item in reversed(stack))
