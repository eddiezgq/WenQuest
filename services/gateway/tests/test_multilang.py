from app.multilang import plain, resolve

ZH_EN = '<span lang="zh_cn" class="multilang">中文</span><span lang="en" class="multilang">English</span>'


def test_picks_requested_language():
    assert resolve(ZH_EN, "zh") == "中文"
    assert resolve(ZH_EN, "en") == "English"


def test_falls_back_to_english_then_first():
    assert resolve(ZH_EN, "fr") == "English"
    only_zh = '<span lang="zh_cn" class="multilang">只有中文</span>'
    assert resolve(only_zh, "en") == "只有中文"


def test_attribute_order_and_whitespace_between_spans():
    s = '<span class="multilang" lang="en">A</span>\n  <span class="multilang" lang="zh_cn">甲</span>'
    assert resolve(s, "zh") == "甲"


def test_nested_spans_inside_a_translation():
    s = ('<span lang="zh_cn" class="multilang">这是<span style="color:red">重点</span>内容</span>'
         '<span lang="en" class="multilang">This is <span>key</span> text</span>')
    assert resolve(s, "zh") == '这是<span style="color:red">重点</span>内容'
    assert resolve(s, "en") == "This is <span>key</span> text"


def test_two_separate_groups_in_one_text():
    s = f"<p>{ZH_EN}</p><p>固定文字</p><p>{ZH_EN}</p>"
    assert resolve(s, "en") == "<p>English</p><p>固定文字</p><p>English</p>"


def test_mlang_syntax():
    s = "{mlang zh_cn}机器人{mlang}{mlang en}Robot{mlang}"
    assert resolve(s, "zh") == "机器人"
    assert resolve(s, "en") == "Robot"
    assert resolve("{mlang other}Default{mlang}{mlang zh_cn}中{mlang}", "en") == "Default"


def test_plain_strips_tags():
    assert plain('<p>Hello&nbsp; <b>world</b></p>', "en") == "Hello world"
    assert plain(None, "en") == ""


def test_text_without_markup_untouched():
    assert resolve("no markup <b>here</b>", "zh") == "no markup <b>here</b>"
