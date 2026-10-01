from trueconf.utils.split_text import safe_split_text, visible_len


def test_empty_input_returns_empty_list():
    assert safe_split_text("") == []


def test_short_text_returned_as_single_chunk():
    assert safe_split_text("hello") == ["hello"]


def test_visible_len_ignores_br():
    assert visible_len("a<br>b") == 2


def test_visible_len_ignores_quote_wrapper():
    assert visible_len('<quote class="reply">цитата</quote>') == 6


def test_br_stays_intact_and_is_used_as_break_point():
    chunks = safe_split_text("aaaa<br>bbbb<br>cccc<br>dddd<br>eeee", limit=15)
    assert all("<br" in c for c in chunks)
    assert all("br>" in c for c in chunks)
    assert "".join(chunks).replace("</quote>", "").count("<br>") == 3


def test_br_never_split_mid_tag():
    chunks = safe_split_text("xxxx<br>yyyy zzzz wwww vvvv uuuu tttt ssss rrrr qqqq pppp oooo", limit=30)
    assert "<br>" in chunks[0]
    for chunk in chunks:
        assert chunk.count("<br") == chunk.count("<br>")


def test_br_render_visible_zero_at_chunk_boundary():
    chunks = safe_split_text("aaaa<br>bbbb", limit=4)
    assert chunks == ["aaaa", "bbbb"]
    assert visible_len("aaaa<br>bbbb") == 8


def test_no_chunk_starts_or_ends_with_br():
    text = "Абзац с текстом несколько слов для переноса строк. Ещё предложение тут.<br><br>" * 60
    for chunk in safe_split_text(text, limit=4096):
        assert not chunk.lstrip().startswith("<br")
        assert not chunk.rstrip().endswith("br>")
        assert visible_len(chunk) <= 4096


def test_boundary_br_paragraph_separator_dropped():
    chunks = safe_split_text("абзац один<br><br>абзац два<br><br>абзац три", limit=20)
    assert "".join(chunks).count("<br>") == 2
    assert not any(c.lstrip().startswith("<br") for c in chunks)
    assert not any(c.rstrip().endswith("br>") for c in chunks)


def test_br_boundary_keeps_word_spacing():
    chunks = safe_split_text("hello\nworld more text here", limit=12)
    assert chunks == ["hello", "world more", "text here"]


def test_quote_container_reopens_across_chunks():
    text = '<quote class="reply">' + "цитата текст " * 30 + "</quote><br><br>ответ"
    chunks = safe_split_text(text, limit=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.count('<quote class="reply">') == chunk.count("</quote>")


def test_quote_attributes_preserved_on_reopen():
    text = '<quote class="reply">' + "q" * 100 + "</quote><br><br>ответ"
    chunks = safe_split_text(text, limit=30)
    assert all(chunk.startswith('<quote class="reply">') for chunk in chunks)
    assert all(chunk.rstrip().endswith("</quote>") for chunk in chunks[:-1])


def test_quote_plus_br_reply_body_splits_safely():
    text = '<quote class="reply">line1<br>line2<br>line3<br>line4<br>line5</quote><br><br>rest'
    chunks = safe_split_text(text, limit=18)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.count('<quote class="reply">') == chunk.count("</quote>")
    assert visible_len("".join(chunks)) == visible_len(text)


def test_split_inside_plain_html_produces_balanced_tags():
    chunks = safe_split_text("<b>aaaaaaa</b> <i>bbbbbb</i> cc", limit=12)
    assert chunks == ["<b>aaaaaaa</b>", "<i>bbbbbb</i> cc"]


def test_split_inside_nested_html_is_balanced():
    chunks = safe_split_text("<b>bold <i>italic</i></b> more text here", limit=12)
    for chunk in chunks:
        assert chunk.count("<b>") == chunk.count("</b>")
        assert chunk.count("<i>") == chunk.count("</i>")


def test_md_bold_markers_stay_balanced_after_split():
    chunks = safe_split_text("aaa **bold** ccc", limit=4)
    assert chunks == ["aaa ****", "**bold**", " ccc"]


def test_md_italic_markers_stay_balanced_after_split():
    chunks = safe_split_text("aaa *bold* ccc", limit=4)
    assert chunks == ["aaa **", "*bold*", " ccc"]


def test_md_underline_markers_stay_balanced_after_split():
    chunks = safe_split_text("aaa __bold__ ccc", limit=4)
    assert chunks == ["aaa ____", "__bold__", " ccc"]


def test_unknown_tag_is_never_split_mid_tag():
    chunks = safe_split_text("<code>" + "y" * 100 + "</code>", limit=10)
    assert chunks[0] == "<code>yyyy"
    assert chunks[-1] == "</code>"
    assert all("<code>" in chunks[0] for _ in [1])
    assert "".join(chunks).count("<code>") == 1
    assert "".join(chunks).count("</code>") == 1


def test_entity_not_split_mid_entity():
    chunks = safe_split_text("aaaaaaaa&amp;bbbbbbbbbb cccc dddd", limit=12)
    assert "".join(chunks).count("&amp;") == 1
    assert all("&amp;" in c or "&amp;" not in c for c in chunks)


def test_literal_underscores_kept_in_link_visible_len():
    chunks = safe_split_text("[a_b c](https://example.com) some more text here", limit=20)
    assert "a_b" in "".join(chunks)


def test_single_word_hard_split():
    chunks = safe_split_text("x" * 100, limit=20)
    assert chunks == ["x" * 20] * 5


def test_newline_at_boundary_is_dropped():
    chunks = safe_split_text("hello\nworld more text here", limit=12)
    assert chunks == ["hello", "world more", "text here"]


def test_short_text_below_limit_keeps_markup():
    assert safe_split_text("<b>hi</b>") == ["<b>hi</b>"]


def test_all_chunks_within_visible_limit():
    text = ("<b>bold</b> text with [link](https://example.com) and <i>italic</i>. " * 5) + " tail"
    for limit in (10, 16, 33, 64):
        for chunk in safe_split_text(text, limit):
            assert visible_len(chunk) <= limit


def test_carry_boundary_literal_underscore_does_not_overflow():
    for chunk in safe_split_text("<b> <br>x_y <br> <i>i</i>", limit=3):
        assert visible_len(chunk) <= 3


def test_oversized_link_inside_open_tags_does_not_hang():
    text = "bold</b>a*b <br></quote>x_y [link](https://x.y)x_yx_y *em* <br> <b> [link](https://x.y) **bold** [link](https://x.y)</quote>"
    chunks = safe_split_text(text, limit=13)
    assert chunks
    for chunk in chunks:
        assert visible_len(chunk) <= 13


def test_link_alone_inside_open_tag_does_not_hang():
    chunks = safe_split_text("<b> text [some long link text](https://example.com) more", limit=10)
    assert chunks
    for chunk in chunks:
        assert visible_len(chunk) <= 10


def test_md_quote_marker_invisible():
    assert visible_len(">цитата") == 6
    assert visible_len(">цитата\n\nответ") == 13


def test_md_quote_reopens_across_chunks():
    chunks = safe_split_text(">" + "q" * 50 + "\n\nrest", limit=15)
    assert all(chunk.startswith(">") for chunk in chunks)
    for chunk in chunks:
        assert visible_len(chunk) <= 15


def test_md_quote_blank_line_closes_quote():
    chunks = safe_split_text(">quoted text\n\nplain text longer", limit=10)
    assert chunks[:2] == [">quoted", ">text"]
    assert not chunks[2].startswith(">")
    assert "".join(chunks).count("\n\n") == 0


def test_md_quote_multiline_quote_lines():
    chunks = safe_split_text(">line one\n>line two longer text here\n\nrest", limit=14)
    assert all(chunk.startswith(">") for chunk in chunks[:-1])
    assert any("line two" in chunk for chunk in chunks)
    for chunk in chunks:
        assert visible_len(chunk) <= 14


def test_md_quote_with_bold_stays_balanced():
    chunks = safe_split_text(">Длинная цитата **важная** текст\n\nпродолжение", limit=16)
    for chunk in chunks:
        assert visible_len(chunk) <= 16
        assert chunk.count("**") % 2 == 0


def test_literal_gt_in_text_stays_visible():
    assert visible_len("a > b") == 5
    assert safe_split_text("a > b and more text here", limit=8) == ["a > b", "and", "more", "text", "here"]


def test_md_quote_fragment_boundary_gt_does_not_overflow():
    for chunk in safe_split_text("   *em*\n\n>here ", limit=5):
        assert visible_len(chunk) <= 5


def test_md_quote_prefix_visible_accounted():
    for chunk in safe_split_text("x >quote", limit=5):
        assert visible_len(chunk) <= 5
