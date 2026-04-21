import re
from dataclasses import dataclass
from typing import List, Optional


HTML_TAG_RE = re.compile(
    r'^<(?P<closing>/)?(?P<tag>[biusa])(?P<attrs>\s+[^>]*)?>',
    re.IGNORECASE
)

MD_LINK_RE = re.compile(
    r'^\[([^]]+)\]\(([^)]+)\)'
)

HTML_ANCHOR_RE = re.compile(
    r'^<a(?P<attrs>\s+[^>]*)>(?P<inner>.*?)</a>',
    re.IGNORECASE | re.DOTALL
)

HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

@dataclass
class StackItem:
    kind: str          # 'html' | 'md'
    name: str          # tag name or marker id
    open_token: str    # exact opener to reopen
    close_token: str   # exact closer to close

@dataclass
class Token:
    kind: str          # 'text', 'space', 'html_open', 'html_close', 'md_marker', 'md_link', 'html_anchor'
    raw: str
    name: Optional[str] = None
    open_token: Optional[str] = None
    close_token: Optional[str] = None
    visible_len: Optional[int] = None
    href: Optional[str] = None
    inner_text: Optional[str] = None


def safe_split_text(text: str, limit: int = 4096) -> List[str]:
    if not text:
        return []
    if visible_len(text) <= limit:
        return [text]

    tokens = _tokenize(text)
    result: List[str] = []

    idx = 0
    carry_stack: List[StackItem] = []
    carry_raw = ''

    while idx < len(tokens):
        prefix = ''.join(item.open_token for item in carry_stack)
        current = prefix + carry_raw
        stack = carry_stack.copy()
        carry_visible_text, carry_raw_positions = _scan_visible(carry_raw)
        visible_used = len(carry_visible_text)
        tail_visible_chars = list(carry_visible_text[-20:])
        tail_raw_positions = [len(prefix) + pos for pos in carry_raw_positions[-20:]]
        last_break_save: Optional[tuple[int, str, List[StackItem], int, str]] = None
        carry_raw = ''

        while idx < len(tokens):
            token = tokens[idx]
            token_visible = _token_visible_len(token)
            next_stack = _apply_token_to_stack(stack, token)
            projected_visible = visible_used + token_visible

            if projected_visible <= limit:
                raw_start = len(current)
                current += token.raw
                stack = next_stack
                visible_used = projected_visible
                _extend_visible_window(tail_visible_chars, tail_raw_positions, token, raw_start)

                break_save = _make_break_save(
                    current=current,
                    visible_used=visible_used,
                    next_idx=idx + 1,
                    token=token,
                    safe_stack=stack.copy(),
                    tail_visible_chars=tail_visible_chars,
                    tail_raw_positions=tail_raw_positions,
                )
                if break_save is not None:
                    last_break_save = break_save

                idx += 1
                continue

            if token.kind in ('md_link', 'html_anchor'):
                break

            available_visible = limit - visible_used
            if available_visible <= 0:
                break

            if token.kind in ('text', 'space'):
                head, tail = _split_visible_text_for_limit(token.raw, available_visible)
                if head:
                    raw_start = len(current)
                    current += head
                    visible_used += len(head)
                    head_token = Token(kind=token.kind, raw=head, visible_len=len(head))
                    _extend_visible_window(tail_visible_chars, tail_raw_positions, head_token, raw_start)

                    break_save = _make_break_save(
                        current=current,
                        visible_used=visible_used,
                        next_idx=idx,
                        token=head_token,
                        safe_stack=stack.copy(),
                        tail_visible_chars=tail_visible_chars,
                        tail_raw_positions=tail_raw_positions,
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
            chunk = current + _closing_suffix(stack)
            if chunk:
                result.append(chunk)
            break

        if last_break_save is not None:
            next_idx, safe_current, safe_stack, safe_visible, raw_tail = last_break_save
            chunk = safe_current + _closing_suffix(safe_stack)
            if chunk:
                result.append(chunk)

            idx = next_idx
            carry_stack = safe_stack
            carry_raw = raw_tail
            continue

        token = tokens[idx]

        if token.kind in ('md_link', 'html_anchor'):
            if current:
                chunk = current + _closing_suffix(stack)
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
                    tokens[idx] = Token(kind='text', raw=tail_raw, visible_len=len(_strip_markup(tail_raw)))
                else:
                    idx += 1
            carry_stack = []
            continue

        if current:
            chunk = current + _closing_suffix(stack)
            if chunk:
                result.append(chunk)
            carry_stack = stack
            continue

        raw = token.raw
        head, tail = _split_visible_text_for_limit(raw, limit)
        if head:
            result.append(head)
        if tail:
            tokens[idx] = Token(kind='text', raw=tail, visible_len=len(tail))
        else:
            idx += 1
        carry_stack = []

    return [chunk for chunk in result if chunk]


def _tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(text)

    while i < n:
        chunk = text[i:]

        m = HTML_ANCHOR_RE.match(chunk)
        if m:
            raw = m.group(0)
            attrs = m.group('attrs') or ''
            inner = m.group('inner') or ''
            href_match = HREF_RE.search(attrs)
            href = href_match.group(1) if href_match else ''
            visible = len(_strip_markup(inner)) + (1 + len(href) if href else 0)
            tokens.append(Token(
                kind='html_anchor',
                raw=raw,
                visible_len=visible,
                href=href,
                inner_text=inner,
            ))
            i += len(raw)
            continue

        m = HTML_TAG_RE.match(chunk)
        if m:
            raw = m.group(0)
            tag = m.group('tag').lower()
            closing = bool(m.group('closing'))

            if closing:
                tokens.append(Token(
                    kind='html_close',
                    raw=raw,
                    name=tag,
                    close_token=f'</{tag}>'
                ))
            else:
                tokens.append(Token(
                    kind='html_open',
                    raw=raw,
                    name=tag,
                    open_token=raw,
                    close_token=f'</{tag}>'
                ))

            i += len(raw)
            continue

        m = MD_LINK_RE.match(chunk)
        if m:
            raw = m.group(0)
            link_text = m.group(1)
            href = m.group(2)
            visible = len(_strip_markup(link_text)) + (1 + len(href) if href else 0)
            tokens.append(Token(
                kind='md_link',
                raw=raw,
                visible_len=visible,
                href=href,
                inner_text=link_text,
            ))
            i += len(raw)
            continue

        if chunk.startswith('__'):
            prev_char = text[i - 1] if i > 0 else ''
            next_char = text[i + 2] if i + 2 < n else ''

            if prev_char.isalnum() and next_char.isalnum():
                tokens.append(Token(kind='text', raw='__', visible_len=2))
            else:
                tokens.append(Token(
                    kind='md_marker',
                    raw='__',
                    name='__',
                    open_token='__',
                    close_token='__',
                    visible_len=0,
                ))
            i += 2
            continue

        if chunk[0] in '*_~':
            marker = chunk[0]
            prev_char = text[i - 1] if i > 0 else ''
            next_char = text[i + 1] if i + 1 < n else ''

            # Если символ внутри слова/идентификатора, это обычный текст, а не markdown
            if prev_char.isalnum() and next_char.isalnum():
                tokens.append(Token(kind='text', raw=marker, visible_len=1))
            else:
                tokens.append(Token(
                    kind='md_marker',
                    raw=marker,
                    name=marker,
                    open_token=marker,
                    close_token=marker,
                    visible_len=0,
                ))
            i += 1
            continue

        if chunk[0].isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            raw = text[i:j]
            tokens.append(Token(kind='space', raw=raw, visible_len=len(raw)))
            i = j
            continue

        # Неизвестный HTML-тег — просто как текст
        if chunk[0] == '<':
            gt = text.find('>', i + 1)
            if gt != -1:
                raw = text[i:gt + 1]
                tokens.append(Token(kind='text', raw=raw, visible_len=len(raw)))
                i = gt + 1
            else:
                raw = text[i]
                tokens.append(Token(kind='text', raw=raw, visible_len=1))
                i += 1
            continue

        j = i
        while j < n:
            c = text[j]
            if c.isspace() or c in '<[*_~':
                break
            j += 1

        if j == i:
            raw = text[i]
            tokens.append(Token(kind='text', raw=raw, visible_len=1))
            i += 1
        else:
            raw = text[i:j]
            tokens.append(Token(kind='text', raw=raw, visible_len=len(raw)))
            i = j

    return tokens


def _apply_token_to_stack(stack: List[StackItem], token: Token) -> List[StackItem]:
    new_stack = stack.copy()

    if token.kind == 'html_open':
        new_stack.append(StackItem(
            kind='html',
            name=token.name or '',
            open_token=token.open_token or '',
            close_token=token.close_token or ''
        ))
        return new_stack

    if token.kind == 'html_close':
        _pop_last_matching(new_stack, kind='html', name=token.name or '')
        return new_stack

    if token.kind == 'md_marker':
        if new_stack and new_stack[-1].kind == 'md' and new_stack[-1].name == token.name:
            new_stack.pop()
        else:
            new_stack.append(StackItem(
                kind='md',
                name=token.name or '',
                open_token=token.open_token or '',
                close_token=token.close_token or ''
            ))
        return new_stack

    return new_stack


# Helper functions for visible length, markup stripping, splitting, etc.
def _token_visible_len(token: Token) -> int:
    if token.visible_len is not None:
        return token.visible_len

    if token.kind in ('html_open', 'html_close', 'md_marker'):
        return 0

    return len(_strip_markup(token.raw))

def visible_len(text: str) -> int:
    visible_text, _ = _scan_visible(text)
    return len(visible_text)

def _token_visible_text(token: Token) -> str:
    if token.kind in ('html_open', 'html_close', 'md_marker'):
        return ''
    if token.kind in ('md_link', 'html_anchor'):
        inner = token.inner_text or ''
        href = token.href or ''
        return f'{_strip_markup(inner)} {href}'.strip()
    return token.raw


def _extend_visible_window(
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
    token: Token,
    raw_start: int,
) -> None:
    visible_text = _token_visible_text(token)
    if not visible_text:
        return

    if token.kind in ('md_link', 'html_anchor'):
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


def _strip_markup(raw: str) -> str:
    raw = re.sub(r'</?[biusa](?:\s+[^>]*)?>', '', raw, flags=re.IGNORECASE)
    raw = raw.replace('__', '')
    raw = raw.replace('*', '')
    raw = raw.replace('_', '')
    raw = raw.replace('~', '')
    return raw

def _scan_visible(raw: str) -> tuple[str, List[int]]:
    visible_chars: List[str] = []
    raw_positions: List[int] = []
    i = 0
    n = len(raw)

    while i < n:
        chunk = raw[i:]

        m = HTML_ANCHOR_RE.match(chunk)
        if m:
            full_raw = m.group(0)
            attrs = m.group('attrs') or ''
            inner = m.group('inner') or ''
            href_match = HREF_RE.search(attrs)
            href = href_match.group(1) if href_match else ''
            rendered = f'{_strip_markup(inner)} {href}'.strip()
            end_pos = i + len(full_raw)
            for ch in rendered:
                visible_chars.append(ch)
                raw_positions.append(end_pos)
            i = end_pos
            continue

        m = MD_LINK_RE.match(chunk)
        if m:
            full_raw = m.group(0)
            inner = m.group(1) or ''
            href = m.group(2) or ''
            rendered = f'{_strip_markup(inner)} {href}'.strip()
            end_pos = i + len(full_raw)
            for ch in rendered:
                visible_chars.append(ch)
                raw_positions.append(end_pos)
            i = end_pos
            continue

        m = HTML_TAG_RE.match(chunk)
        if m:
            i += len(m.group(0))
            continue

        if chunk.startswith('__'):
            prev_char = raw[i - 1] if i > 0 else ''
            next_char = raw[i + 2] if i + 2 < n else ''
            if prev_char.isalnum() and next_char.isalnum():
                visible_chars.extend(['_', '_'])
                raw_positions.extend([i + 2, i + 2])
            i += 2
            continue

        if raw[i] in '*_~':
            prev_char = raw[i - 1] if i > 0 else ''
            next_char = raw[i + 1] if i + 1 < n else ''
            if prev_char.isalnum() and next_char.isalnum():
                visible_chars.append(raw[i])
                raw_positions.append(i + 1)
            i += 1
            continue

        visible_chars.append(raw[i])
        raw_positions.append(i + 1)
        i += 1

    return ''.join(visible_chars), raw_positions


def _visible_text_for_breaks(raw: str) -> str:
    visible_text, _ = _scan_visible(raw)
    return visible_text



def _find_last_break_pos(
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
) -> Optional[tuple[int, str]]:
    if not tail_visible_chars:
        return None

    window = ''.join(tail_visible_chars)

    for offset, ch in enumerate(window):
        if ch == '\n':
            raw_pos = tail_raw_positions[offset]
            return raw_pos - 1, 'before_newline'

    punctuation = '.,!?;:)]}'
    for offset, ch in enumerate(window):
        if ch in punctuation:
            raw_pos = tail_raw_positions[offset]
            return raw_pos, 'after_punctuation'

    space_pos = window.rfind(' ')
    if space_pos != -1:
        raw_pos = tail_raw_positions[space_pos]
        return raw_pos, 'after_space'

    return None


def _make_break_save(
    current: str,
    visible_used: int,
    next_idx: int,
    token: Token,
    safe_stack: List[StackItem],
    tail_visible_chars: List[str],
    tail_raw_positions: List[int],
) -> Optional[tuple[int, str, List[StackItem], int, str]]:
    if token.kind in ('md_link', 'html_anchor'):
        return next_idx, current.rstrip(), safe_stack, visible_used, ''

    break_info = _find_last_break_pos(tail_visible_chars, tail_raw_positions)
    if break_info is None:
        return None

    break_pos, break_kind = break_info
    safe_current = current[:break_pos]
    raw_tail = current[break_pos:]

    if break_kind == 'before_newline' and raw_tail.startswith('\n'):
        raw_tail = raw_tail[1:]

    if not safe_current.strip():
        return None

    removed_visible = sum(1 for pos in tail_raw_positions if pos > break_pos)
    safe_visible = visible_used - removed_visible
    return next_idx, safe_current, safe_stack, safe_visible, raw_tail


def _split_visible_text_for_limit(raw: str, available_visible: int) -> tuple[str, str]:
    if available_visible <= 0:
        return '', raw

    if len(raw) <= available_visible:
        return raw, ''

    head = raw[:available_visible]
    tail = raw[available_visible:]
    return head, tail


def _split_atomic_token_raw(token: Token, limit: int) -> tuple[str, str]:
    if token.kind == 'md_link':
        inner = token.inner_text or ''
        href = token.href or ''
        visible_prefix = f'{inner} {href}'.strip()
        if len(visible_prefix) <= limit:
            return token.raw, ''
        return visible_prefix[:limit], visible_prefix[limit:]

    if token.kind == 'html_anchor':
        inner = token.inner_text or ''
        href = token.href or ''
        visible_prefix = f'{_strip_markup(inner)} {href}'.strip()
        if len(visible_prefix) <= limit:
            return token.raw, ''
        return visible_prefix[:limit], visible_prefix[limit:]

    raw = token.raw
    if len(raw) <= limit:
        return raw, ''
    return raw[:limit], raw[limit:]




def _pop_last_matching(stack: List[StackItem], kind: str, name: str) -> None:
    for i in range(len(stack) - 1, -1, -1):
        if stack[i].kind == kind and stack[i].name == name:
            del stack[i]
            return


def _closing_suffix(stack: List[StackItem]) -> str:
    return ''.join(item.close_token for item in reversed(stack))