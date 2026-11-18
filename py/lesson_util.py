# -*- coding: utf-8 -*-
"""レッスンを短く書くための道具"""


def Q(q, right, wrong1, wrong2, why):
    """3択クイズ（最初に書いたものが正解。画面ではシャッフルされる）"""
    return {"q": q, "c": [right, wrong1, wrong2], "a": 0, "why": why}


def T(word, rei, imi):
    """用語カード"""
    return {"word": word, "rei": rei, "imi": imi}


def G(t, x, code=None):
    """授業の1ステップ"""
    d = {"t": t, "x": x}
    if code:
        d["code"] = code
    return d


def L(id, chapter, title, check, story, skill, template, answer=None, hints=None,
      guide=None, kaisetsu="", terms=None, quiz=None, clear_rate=1.0, exam=False, **extra):
    """レッスン1つ分の辞書を作る"""
    d = {
        "id": id, "chapter": chapter, "title": title, "check": check,
        "memory": "none", "tests": "test", "exam": exam,
        "story": story, "skill": skill, "clear_rate": clear_rate,
        "template": template, "answer": answer, "hints": hints or [],
        "guide": guide or [], "kaisetsu": kaisetsu, "terms": terms or [],
        "quiz": quiz if quiz is not None else "review",
    }
    d.update(extra)
    return d
