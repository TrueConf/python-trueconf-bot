from trueconf.utils.formatting import LineBreak, Text


def test_line_break_html():
    assert LineBreak().as_html() == "<br>"


def test_line_break_markdown():
    assert LineBreak().as_markdown() == "\n"


def test_line_break_inside_text_html():
    assert Text("a", LineBreak(), "b").as_html() == "a<br>b"


def test_line_break_inside_text_markdown():
    assert Text("a", LineBreak(), "b").as_markdown() == "a\nb"
