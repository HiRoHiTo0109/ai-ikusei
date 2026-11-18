# -*- coding: utf-8 -*-
"""
スマホ版の教科書。PC版の教科書をもとに、スマホで動かないレベルだけ差し替える。
（PC版の lessons.py などは一切書き換えない）
"""
import copy

import checks
from lessons import LESSONS as PC_LESSONS, CHAPTERS, MEMORIES, FEATURES  # noqa: F401
from m_ch3 import LESSONS_M3
from m_ch4 import LESSONS_M4
from m_ch5 import LESSONS_M5
from m_ch6 import LESSONS_M6

REPLACED = {l["id"]: l for l in LESSONS_M3 + LESSONS_M4 + LESSONS_M5 + LESSONS_M6}

LESSONS = []
for _l in PC_LESSONS:
    _m = copy.deepcopy(REPLACED.get(_l["id"], _l))
    _m["needs"] = []            # スマホ版は numpy などが最初から入っている
    _m.pop("optional", None)    # とばす必要のあるレベルは無い
    LESSONS.append(_m)

# 置き換えたレベル（スマホ版オリジナル）の印
for _m in LESSONS:
    _m["mobile_only"] = _m["id"] in REPLACED

# 4種類の動物の見本（Lv41）
checks.SAMPLE_MAKERS["faces4"] = lambda: checks._face_samples(("dog", "cat", "rabbit", "bear"), 8)

assert [l["id"] for l in LESSONS] == list(range(len(LESSONS)))
