# -*- coding: utf-8 -*-
"""
試験のやり方をまとめたファイル。
それぞれ「書いたコード(ns)」を受け取り、結果の表と正解率を返す。
  results : [{"name": 問題, "pred": 返ってきた値, "answer": 期待する値, "ok": 合否}]
  accuracy: 0〜1
  note    : 画面に出すひとこと（任意）
"""
import copy
import json
import math
import os

from lessons import MEMORIES, TEST_SETS, FEATURES, ACCURACY_CASES, MEMORY, TESTS, EXAM, TRICK_MEMORY

BASE = os.path.dirname(os.path.abspath(__file__))


class Fail(Exception):
    """試験できない理由を、そのまま画面に出すためのエラー"""


def need(ns, *names):
    for n in names:
        if n not in ns:
            raise Fail(f"{n} という関数（または変数）が見つからないよ")


def short(v, limit=60):
    """結果表に出すための短い文字列"""
    try:
        import numpy as np
        if isinstance(v, np.ndarray):
            v = np.round(v, 3).tolist()
        elif isinstance(v, (np.floating, np.integer)):
            v = v.item()
    except ImportError:
        pass
    if isinstance(v, float):
        v = round(v, 3)
    if isinstance(v, (list, tuple)):
        v = [round(x, 3) if isinstance(x, float) else x for x in v]
    s = str(v)
    return s if len(s) <= limit else s[:limit] + "…"


def same(got, expect, tol=1e-6):
    """答えが合っているか（数字は少しの誤差を許す）"""
    try:
        import numpy as np
        if isinstance(got, np.ndarray) or isinstance(expect, np.ndarray):
            g, e = np.asarray(got, dtype=float), np.asarray(expect, dtype=float)
            return g.shape == e.shape and bool(np.allclose(g, e, atol=tol))
    except (TypeError, ValueError):
        return False
    try:
        import numpy as np
        if isinstance(got, (np.floating, np.integer)):
            got = got.item()
    except (ImportError, TypeError, ValueError):
        pass
    if isinstance(expect, bool) or isinstance(expect, str) or expect is None:
        return got == expect
    if isinstance(expect, (int, float)):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and abs(got - expect) <= tol
    if isinstance(expect, (list, tuple)):
        return (isinstance(got, (list, tuple)) and len(got) == len(expect)
                and all(same(g, e, tol) for g, e in zip(got, expect)))
    if isinstance(expect, dict):
        return isinstance(got, dict) and got.keys() == expect.keys() and all(same(got[k], expect[k], tol) for k in expect)
    return got == expect


def table(rows, note=None, **extra):
    acc = sum(r["ok"] for r in rows) / len(rows) if rows else 0
    return {"results": rows, "accuracy": acc, "learned": None, "note": note, **extra}


def row(name, got, expect, ok=None, tol=1e-6):
    return {"name": name, "pred": short(got), "answer": short(expect),
            "ok": same(got, expect, tol) if ok is None else bool(ok)}


# ---------------------------------------------------------------- 第1章
def check_classify(ns, lesson):
    need(ns, "guess")
    memory = MEMORIES[lesson["memory"]]
    brain, note = memory, None
    learned = None
    if "learn" in ns:                                   # 学習するタイプのAI
        brain = ns["learn"](copy.deepcopy(memory))
        try:
            json.dumps(brain)
            learned = brain
        except Exception:
            pass
    rows = []
    for t in TEST_SETS[lesson["tests"]]:
        animal = {k: t[k] for k in ["名前"] + FEATURES}   # 答えは見せない
        pred = ns["guess"](animal, copy.deepcopy(brain))
        rows.append({"name": t["名前"], "answer": t["答え"], "pred": str(pred), "ok": pred == t["答え"]})
    if isinstance(learned, dict) and "w" in learned:
        note = "🧠 自分で見つけた重み　" + "　".join(f"{k}：{round(v, 2)}" for k, v in zip(FEATURES, learned["w"])) \
               + f"　基礎点：{round(learned.get('b', 0), 2)}"
    out = table(rows, note)
    out["learned"] = learned
    return out


def check_accuracy(ns, lesson):
    need(ns, "accuracy")
    rows = []
    for i, (preds, answers, expect) in enumerate(ACCURACY_CASES, 1):
        got = ns["accuracy"](list(preds), list(answers))
        rows.append(row(f"ケース{i}：{preds} と {answers}", got, expect))
    return table(rows)


# ---------------------------------------------------------------- 関数の答え合わせ（cases）
# CASES[レベル番号] = 関数。ns を受け取り row のリストを返す
CASES = {}


def cases(lid):
    def deco(fn):
        CASES[lid] = fn
        return fn
    return deco


def check_cases(ns, lesson):
    out = CASES[lesson["id"]](ns)
    if isinstance(out, dict):
        return out
    return table(out)


# ---------------------------------------------------------------- 第2章
@cases(8)
def _lv8(ns):
    import numpy as np
    need(ns, "scores")
    f = ns["scores"]
    X1 = np.array([[9, 6, 4, 3], [9, 2, 2, 9]])
    X2 = np.array([[m[k] for k in FEATURES] for m in MEMORY])
    tests = [("柴犬と三毛猫、重み [1, 2, 1, -2]", X1, np.array([1, 2, 1, -2])),
             ("柴犬と三毛猫、重み [0, 1, 0, -1]", X1, np.array([0, 1, 0, -1])),
             ("思い出アルバム16匹ぶん", X2, np.array([1, 2, 1, -2]))]
    return [row(n, f(X, w), X @ w) for n, X, w in tests]


@cases(9)
def _lv9(ns):
    import numpy as np
    need(ns, "loss")
    f = ns["loss"]
    tests = [("予想 [0.9, 0.2]　正解 [1, 0]", [0.9, 0.2], [1.0, 0.0]),
             ("予想 [1, 0, 1]　正解 [1, 0, 1]（全問ぴったり）", [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]),
             ("予想 [0.5, 0.5]　正解 [1, 0]", [0.5, 0.5], [1.0, 0.0]),
             ("予想 [3, -1]　正解 [1, 1]（プラスとマイナスのズレ）", [3.0, -1.0], [1.0, 1.0])]
    return [row(n, f(np.array(p), np.array(t)), float(np.mean((np.array(p) - np.array(t)) ** 2))) for n, p, t in tests]


@cases(10)
def _lv10(ns):
    need(ns, "descend")
    f = ns["descend"]

    def ref(w, lr, steps):
        for _ in range(steps):
            w = w - lr * 2 * (w - 3)
        return w
    tests = [("0 から歩幅0.1で1歩", 0.0, 0.1, 1), ("0 から歩幅0.1で100歩", 0.0, 0.1, 100),
             ("10 から歩幅0.1で100歩", 10.0, 0.1, 100), ("0 から歩幅0.5で1歩", 0.0, 0.5, 1),
             ("0 から歩幅0.1で0歩（動かない）", 0.0, 0.1, 0)]
    return [row(n, f(w, lr, st), ref(w, lr, st), tol=1e-3) for n, w, lr, st in tests]


def _ref_knn(animal, memory, k):
    d = lambda a, b: math.sqrt(sum((a[x] - b[x]) ** 2 for x in FEATURES))
    votes = [m["答え"] for m in sorted(memory, key=lambda m: d(m, animal))[:k]]
    return "犬" if votes.count("犬") > votes.count("猫") else "猫"


def _ref_validate(train, val, k):
    return sum(_ref_knn(v, train, k) == v["答え"] for v in val) / len(val)


@cases(12)
def _lv12(ns):
    need(ns, "validate", "choose_k")
    train = copy.deepcopy(TRICK_MEMORY)
    val = copy.deepcopy(TESTS + EXAM)
    rows = [row(f"k={k} のときの練習試合の正解率", ns["validate"](copy.deepcopy(train), copy.deepcopy(val), k),
                _ref_validate(train, val, k)) for k in [1, 3, 5]]
    best_k, best = 1, 0
    for k in [1, 3, 5, 7]:
        a = _ref_validate(train, val, k)
        if a > best:
            best, best_k = a, k
    rows.append(row("choose_k が選んだ k", ns["choose_k"](copy.deepcopy(train), copy.deepcopy(val)), best_k))
    small_train, small_val = train[:9], val[:6]
    b2, bb = 1, 0
    for k in [1, 3, 5, 7]:
        a = _ref_validate(small_train, small_val, k)
        if a > bb:
            bb, b2 = a, k
    rows.append(row("別のデータで choose_k が選んだ k", ns["choose_k"](copy.deepcopy(small_train), copy.deepcopy(small_val)), b2))
    return rows


@cases(13)
def _lv13(ns):
    import numpy as np
    need(ns, "fit_line")
    rows = []
    for name, a, b in [("y = 2x + 1 の点", 2.0, 1.0), ("y = -1x + 4 の点", -1.0, 4.0), ("y = 0.5x - 2 の点", 0.5, -2.0)]:
        xs = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        got = ns["fit_line"](xs.copy(), a * xs + b)
        ok = (isinstance(got, (tuple, list)) and len(got) == 2
              and abs(float(got[0]) - a) < 0.1 and abs(float(got[1]) - b) < 0.1)
        shown = tuple(round(float(g), 2) for g in got) if isinstance(got, (tuple, list)) and len(got) == 2 else got
        rows.append(row(name, shown, (a, b), ok=ok))
    return rows


CHECKS = {"classify": check_classify, "accuracy": check_accuracy, "cases": check_cases}


# ---------------------------------------------------------------- 第3章
XOR_IN = [[0, 0], [0, 1], [1, 0], [1, 1]]
XOR_OUT = [0, 1, 1, 0]


@cases(14)
def _lv14(ns):
    import numpy as np
    need(ns, "forward")
    return [row(f"スイッチ {x} のとき", float(ns["forward"](np.array(x, dtype=float))), float(t))
            for x, t in zip(XOR_IN, XOR_OUT)]


@cases(15)
def _lv15(ns):
    import numpy as np
    need(ns, "relu", "sigmoid")
    a = np.array([-2.0, 0.0, 3.0])
    return [row("relu([-2, 0, 3])", ns["relu"](a.copy()), np.maximum(0, a)),
            row("relu([5, -0.5])", ns["relu"](np.array([5.0, -0.5])), np.array([5.0, 0.0])),
            row("sigmoid(0)", float(ns["sigmoid"](np.array(0.0))), 0.5),
            row("sigmoid([-2, 2])", ns["sigmoid"](np.array([-2.0, 2.0])), 1 / (1 + np.exp(-np.array([-2.0, 2.0]))))]


@cases(16)
def _lv16(ns):
    import numpy as np
    need(ns, "train", "predict")
    params = ns["train"]()
    out = ns["predict"](params, np.array(XOR_IN, dtype=float)).reshape(-1)
    return [row(f"スイッチ {x} のとき（学習後の答え {round(float(o), 2)}）", float(round(float(o))), float(t))
            for x, o, t in zip(XOR_IN, out, XOR_OUT)]


@cases(17)
def _lv17(ns):
    import torch
    need(ns, "train")
    model = ns["train"]()
    with torch.no_grad():
        out = model(torch.tensor(XOR_IN, dtype=torch.float32)).reshape(-1).tolist()
    return [row(f"スイッチ {x} のとき（学習後の答え {round(o, 2)}）", float(round(o)), float(t))
            for x, o, t in zip(XOR_IN, out, XOR_OUT)]


# ドット絵の数字（5×7）。# が黒
FONT = {
    0: ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"],
    1: ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    2: ["#####", "....#", "....#", "#####", "#....", "#....", "#####"],
    3: ["#####", "....#", "....#", ".####", "....#", "....#", "#####"],
    4: ["#...#", "#...#", "#...#", "#####", "....#", "....#", "....#"],
    5: ["#####", "#....", "#....", "#####", "....#", "....#", "#####"],
    6: ["#####", "#....", "#....", "#####", "#...#", "#...#", "#####"],
    7: ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    8: ["#####", "#...#", "#...#", "#####", "#...#", "#...#", "#####"],
    9: ["#####", "#...#", "#...#", "#####", "....#", "....#", "#####"],
}


def make_digits(n, seed, noise=0.08):
    """汚れたドット絵の数字を n 枚作る → (X[n,35], y[n])"""
    import numpy as np
    rng = np.random.default_rng(seed)
    base = np.array([[1.0 if c == "#" else 0.0 for line in FONT[d] for c in line] for d in range(10)])
    y = rng.integers(0, 10, size=n)
    X = base[y].copy()
    flip = rng.random(X.shape) < noise          # ところどころドットを反転
    X[flip] = 1 - X[flip]
    return X.astype("float32"), y.astype("int64")


def _digit_score(model, device="cpu"):
    import torch
    Xt, yt = make_digits(300, seed=999)
    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(Xt).to(device)).argmax(dim=1).cpu().numpy()
    return float((pred == yt).mean())


def _n_linear(model):
    import torch.nn as nn
    return sum(isinstance(m, nn.Linear) for m in model.modules())


def check_digits(ns, lesson):
    import torch
    need(ns, "train")
    X, y = make_digits(800, seed=1)
    model = ns["train"](torch.tensor(X), torch.tensor(y))
    if model is None or not hasattr(model, "parameters"):
        raise Fail("train が学習した脳（model）を返していないよ。最後に return model が必要")
    device = next(model.parameters()).device
    acc = _digit_score(model, device)
    n = _n_linear(model)
    rows = [row("初めて見る字300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9),
            row("中間層がある（Linear が2つ以上）", f"Linear {n}個", "2個以上", ok=n >= 2)]
    return table(rows)


def check_gpu(ns, lesson):
    import torch
    need(ns, "pick_device", "train")
    want = "cuda" if torch.cuda.is_available() else "cpu"
    got = ns["pick_device"]()
    X, y = make_digits(800, seed=1)
    model = ns["train"](torch.tensor(X), torch.tensor(y))
    if model is None or not hasattr(model, "parameters"):
        raise Fail("train が学習した脳（model）を返していないよ")
    dev = next(model.parameters()).device
    acc = _digit_score(model, dev)
    code = ns.get("__code__", "")
    rows = [row("pick_device の答え", got, want),
            row("torch.cuda.is_available() で確かめている", "書いてある" if "is_available" in code else "書いていない", "書いてある"),
            row("脳・X・y を .to(device) で引っ越し", f".to( が {code.count('.to(')}か所", "3か所以上", ok=code.count(".to(") >= 3),
            row("脳がいる場所", dev.type, want),
            row("初めて見る字300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9)]
    name = torch.cuda.get_device_name(0) if dev.type == "cuda" else "CPU（GPU版のPyTorchが入っていないか、GPUが無い）"
    return table(rows, note=f"🖥 使った装置：{dev.type}（{name}）")


CHECKS.update({"digits": check_digits, "gpu": check_gpu})


# ---------------------------------------------------------------- 見本の絵（画面に表示する用）
def samples(kind):
    """[{label, w, h, px:[0〜1 …]}] を返す"""
    if kind == "digits":
        X, y = make_digits(10, seed=7)
        return [{"label": str(int(t)), "w": 5, "h": 7, "px": x.tolist()} for x, t in zip(X, y)]
    if kind in SAMPLE_MAKERS:
        return SAMPLE_MAKERS[kind]()
    return []


SAMPLE_MAKERS = {}


# ---------------------------------------------------------------- 第4章：動物の顔イラスト（16×16）
def _disk(img, cx, cy, r, v):
    import numpy as np
    yy, xx = np.mgrid[0:16, 0:16]
    img[(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r] = v


def _rect(img, x0, y0, x1, y1, v):
    img[max(0, y0):max(0, y1 + 1), max(0, x0):max(0, x1 + 1)] = v


def draw_face(kind, rng, noise=0.08, jitter=1):
    """kind: dog / cat / rabbit / bear / fox / tanuki の顔を1枚描く"""
    import numpy as np
    img = np.zeros((16, 16), dtype="float32")
    cx, cy = 8 + int(rng.integers(-jitter, jitter + 1)), 10 + int(rng.integers(-1, 2))
    r = 4
    if kind in ("cat", "fox"):   # とがった三角の耳
        for side in (-1, 1):
            for k in range(4):
                w = k // 2
                _rect(img, cx + side * 3 - w, cy - r - 3 + k, cx + side * 3 + w, cy - r - 3 + k, 0.8)
    elif kind == "dog":          # 横にたれた耳
        for side in (-1, 1):
            x = cx + side * 5
            _rect(img, min(x, x + side), cy - 3, max(x, x + side), cy + 2, 0.8)
    elif kind == "rabbit":       # 上に長くのびた耳
        for side in (-1, 1):
            x = cx + side * 2
            _rect(img, x - (1 if side < 0 else 0), cy - r - 6, x + (1 if side > 0 else 0), cy - r, 0.8)
    elif kind in ("bear", "tanuki"):   # 小さくて丸い耳
        for side in (-1, 1):
            _disk(img, cx + side * 4, cy - r, 1.6, 0.8)
    _disk(img, cx, cy, r, 0.6)                              # 顔
    img[cy - 1, cx - 2] = 0.0; img[cy - 1, cx + 2] = 0.0    # 目
    if kind in ("cat", "tanuki"):                           # 横に伸びるひげ
        _rect(img, cx - 7, cy + 1, cx - 5, cy + 1, 0.9); _rect(img, cx + 5, cy + 1, cx + 7, cy + 1, 0.9)
    if kind in ("dog", "fox"):
        _rect(img, cx - 1, cy + 1, cx + 1, cy + 3, 1.0)     # 長い鼻先
    img += rng.normal(0, noise, size=img.shape).astype("float32")
    return np.clip(img, 0, 1)


def make_faces(n, seed, kinds=("dog", "cat"), noise=0.08, jitter=1):
    """顔イラストを n 枚 → (X[n,1,16,16], y[n])  y は kinds の番号"""
    import numpy as np
    rng = np.random.default_rng(seed)
    y = rng.integers(0, len(kinds), size=n)
    X = np.stack([draw_face(kinds[int(t)], rng, noise, jitter) for t in y])[:, None, :, :]
    return X.astype("float32"), y.astype("int64")


LABELS = {"dog": "犬", "cat": "猫", "rabbit": "うさぎ", "bear": "くま", "fox": "きつね", "tanuki": "たぬき"}


def _face_samples(kinds, seed):
    X, y = make_faces(10, seed, kinds)
    return [{"label": LABELS[kinds[int(t)]], "w": 16, "h": 16, "px": x[0].reshape(-1).tolist()} for x, t in zip(X, y)]


SAMPLE_MAKERS["faces"] = lambda: _face_samples(("dog", "cat"), 5)
SAMPLE_MAKERS["faces2"] = lambda: _face_samples(("rabbit", "bear"), 6)


# ---------------------------------------------------------------- 第4章：試験
@cases(21)
def _lv21(ns):
    import numpy as np
    need(ns, "brightness", "flip")
    a = np.array([[0.0, 1.0], [1.0, 1.0]])
    b = np.array([[0.0, 0.5, 1.0], [0.2, 0.4, 0.6]])
    face = make_faces(1, 5)[0][0, 0]
    return [row("2×2の絵の明るさ", float(ns["brightness"](a.copy())), 0.75),
            row("顔の絵の明るさ", float(ns["brightness"](face.copy())), float(face.mean()), tol=1e-4),
            row("2×3の絵を左右反転", np.asarray(ns["flip"](b.copy())), b[:, ::-1]),
            row("顔の絵を左右反転（16×16）", "合っている" if same(np.asarray(ns["flip"](face.copy())), face[:, ::-1]) else "違う", "合っている")]


def _ref_conv(img, k):
    import numpy as np
    kh, kw = k.shape
    out = np.zeros((img.shape[0] - kh + 1, img.shape[1] - kw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = np.sum(img[i:i + kh, j:j + kw] * k)
    return out


@cases(22)
def _lv22(ns):
    import numpy as np
    need(ns, "conv2d")
    f = ns["conv2d"]
    img1 = np.array([[0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1]], dtype=float)
    edge = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=float)
    ones = np.ones((2, 2))
    face = make_faces(1, 5)[0][0, 0].astype(float)
    got = np.asarray(f(face.copy(), edge.copy()))
    return [row("左が暗く右が明るい絵 × 縦の境目を探す虫眼鏡", np.asarray(f(img1.copy(), edge.copy())), _ref_conv(img1, edge)),
            row("同じ絵 × 2×2の全部1の虫眼鏡", np.asarray(f(img1.copy(), ones.copy())), _ref_conv(img1, ones)),
            row("顔の絵（16×16）× 縦の境目の虫眼鏡 → 地図の大きさ", got.shape, (14, 14)),
            row("顔の絵の地図の中身", "合っている" if same(got, _ref_conv(face, edge), 1e-4) else "違う", "合っている")]


@cases(23)
def _lv23(ns):
    import numpy as np
    need(ns, "augment")
    a = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    out = ns["augment"](a.copy())
    if not isinstance(out, (list, tuple)):
        raise Fail("augment はリスト [ ] で返してね")
    get = lambda i: np.asarray(out[i]) if len(out) > i else "（無い）"
    return [row("返ってきた枚数", len(out), 3),
            row("1枚目：元のまま", get(0), a),
            row("2枚目：左右反転", get(1), a[:, ::-1]),
            row("3枚目：右に1マスずらす", get(2), np.roll(a, 1, axis=1))]


def _dev():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def _face_score(model, kinds, seed, device):
    import torch
    Xt, yt = make_faces(300, seed, kinds)
    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(Xt).to(device)).argmax(dim=1).cpu().numpy()
    return float((pred == yt).mean())


def check_cnn(ns, lesson):
    import torch
    import torch.nn as nn
    need(ns, "train")
    dev = _dev()
    X, y = make_faces(600, seed=2)
    model = ns["train"](torch.tensor(X).to(dev), torch.tensor(y).to(dev))
    if model is None or not hasattr(model, "parameters"):
        raise Fail("train が学習した脳（model）を返していないよ。最後に return model が必要")
    acc = _face_score(model, ("dog", "cat"), 998, next(model.parameters()).device)
    n = sum(isinstance(m, nn.Conv2d) for m in model.modules())
    return table([row("初めて見る絵300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9),
                  row("畳み込みの層（Conv2d）の数", f"{n}個", "2個以上", ok=n >= 2)])


def make_senpai(device):
    """犬と猫をたくさん見て育った先輩の脳"""
    import torch
    import torch.nn as nn

    class Senpai(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten())
            self.head = nn.Linear(256, 2)

        def forward(self, x):
            return self.head(self.features(x))

    torch.manual_seed(1)
    m = Senpai().to(device)
    X, y = make_faces(800, seed=3)
    X, y = torch.tensor(X).to(device), torch.tensor(y).to(device)
    opt = torch.optim.Adam(m.parameters(), lr=0.01)
    for _ in range(60):
        loss = nn.functional.cross_entropy(m(X), y)
        opt.zero_grad(); loss.backward(); opt.step()
    return m, Senpai


def check_transfer(ns, lesson):
    import torch
    import torch.nn as nn
    need(ns, "transfer")
    dev = _dev()
    kinds = ("rabbit", "bear")
    senpai, Senpai = make_senpai(dev)
    before = [p.detach().clone() for p in senpai.features.parameters()]
    old_head = senpai.head
    X, y = make_faces(16, seed=11, kinds=kinds)
    X, y = torch.tensor(X).to(dev), torch.tensor(y).to(dev)
    model = ns["transfer"](senpai, X, y)
    if model is None or not hasattr(model, "features"):
        raise Fail("transfer が先輩の脳（senpai）を返していないよ。最後に return senpai が必要")
    acc = _face_score(model, kinds, 997, dev)
    frozen = all(torch.equal(a, b) for a, b in zip(before, model.features.parameters()))
    swapped = model.head is not old_head

    n_head = sum(p.numel() for p in model.head.parameters())
    n_all = sum(p.numel() for p in model.parameters())
    return table([row("うさぎ・くま 300枚の正解率", f"{round(acc * 100)}%", "85%以上", ok=acc >= 0.85),
                  row("先輩の目（features）を固定した", "変わっていない" if frozen else "変わってしまった", "変わっていない"),
                  row("判断係（head）を新品に取り替えた", "取り替えた" if swapped else "そのまま", "取り替えた")],
                 note=f"📊 今回の学習で直した重みは {n_head}個だけ（脳全体は {n_all}個）。目の部分は先輩のものをそのまま使った")


def check_realphoto(ns, lesson):
    need(ns, "look")
    rows = []
    for folder, label in [("dog", "犬"), ("cat", "猫")]:
        d = os.path.join(BASE, "photos", folder)
        os.makedirs(d, exist_ok=True)
        files = sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")))
        if len(files) < 2:
            raise Fail(f"写真が足りないよ。ai_ikusei\\photos\\{folder} フォルダに{label}の写真を2枚以上入れてね（今は{len(files)}枚）")
        for f in files[:10]:
            rows.append(row(f"photos\\{folder}\\{f}", ns["look"](os.path.join(d, f)), label))
    return table(rows)


CHECKS.update({"cnn": check_cnn, "transfer": check_transfer, "realphoto": check_realphoto})


# ---------------------------------------------------------------- 第5章
@cases(28)
def _lv28(ns):
    need(ns, "make_vocab", "encode", "decode")
    rows = []
    for text in ["ねこねこ", "やるじゃん。", "まだまだだね"]:
        vocab = sorted(set(text))
        ids = [vocab.index(c) for c in text]
        rows.append(row(f"「{text}」を番号に", ns["encode"](text, list(vocab)), ids))
        rows.append(row(f"{ids} を文字に戻す", ns["decode"](list(ids), list(vocab)), text))
    return rows


def _ref_counts(text):
    counts = {}
    for a, b in zip(text, text[1:]):
        counts.setdefault(a, {})
        counts[a][b] = counts[a].get(b, 0) + 1
    return counts


@cases(29)
def _lv29(ns):
    from ch5 import CORPUS
    need(ns, "count_pairs", "predict_next")
    rows = []
    for text, ch in [("ねこねこねずみ", "ね"), ("あいあいあう", "あ"), ("ふむふむふーん", "ふ")]:
        ref = _ref_counts(text)
        got = ns["count_pairs"](text)
        rows.append(row(f"「{text}」を数える", got, ref))
        nxt = ref[ch]
        rows.append(row(f"「{ch}」の次に来る文字", ns["predict_next"](copy.deepcopy(ref), ch), max(nxt, key=nxt.get)))
    note = None
    try:                                         # おまけ：セリフ集から文を作ってみる
        counts = ns["count_pairs"](CORPUS)
        out = "ふ"
        for _ in range(24):
            out += ns["predict_next"](counts, out[-1])
        note = "✍ 直前の1文字だけ見て書いた文：" + out.replace("\n", "／")
    except Exception:
        pass
    return table(rows, note)


WORD_VECS = {
    "犬": [0.9, 0.1, 0.0], "猫": [0.85, 0.05, 0.1], "うさぎ": [0.8, 0.0, 0.25],
    "車": [0.05, 0.95, 0.0], "バス": [0.1, 0.9, 0.05], "電車": [0.0, 0.92, 0.1],
    "りんご": [0.1, 0.0, 0.9], "みかん": [0.05, 0.05, 0.92],
}


@cases(30)
def _lv30(ns):
    import numpy as np
    need(ns, "similarity", "nearest")
    V = {k: np.array(v) for k, v in WORD_VECS.items()}
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    rows = [row("同じ向き [1, 0] と [3, 0]", float(ns["similarity"](np.array([1.0, 0.0]), np.array([3.0, 0.0]))), 1.0),
            row("直角 [1, 0] と [0, 2]", float(ns["similarity"](np.array([1.0, 0.0]), np.array([0.0, 2.0]))), 0.0),
            row("犬 と 猫", float(ns["similarity"](V["犬"], V["猫"])), cos(V["犬"], V["猫"]), tol=1e-4),
            row("犬 と 車", float(ns["similarity"](V["犬"], V["車"])), cos(V["犬"], V["車"]), tol=1e-4)]
    for w in ["犬", "車", "りんご"]:
        best = max((x for x in V if x != w), key=lambda x: cos(V[w], V[x]))
        rows.append(row(f"「{w}」に一番似ている言葉", ns["nearest"](w, {k: v.copy() for k, v in V.items()}), best))
    return rows


@cases(31)
def _lv31(ns):
    import numpy as np
    need(ns, "attention")

    def ref(q, K, Vv):
        s = K @ q
        e = np.exp(s - s.max())
        return (e / e.sum()) @ Vv
    K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    Vv = np.array([[10.0, 0.0], [0.0, 10.0], [5.0, 5.0]])
    tests = [("1番目の言葉と関係が強い質問", np.array([5.0, 0.0])),
             ("2番目の言葉と関係が強い質問", np.array([0.0, 5.0])),
             ("どれとも同じくらいの質問", np.array([0.0, 0.0])),
             ("少しだけ1番目寄りの質問", np.array([1.0, 0.5]))]
    return [row(n, np.asarray(ns["attention"](q.copy(), K.copy(), Vv.copy())), ref(q, K, Vv), tol=1e-4) for n, q in tests]


def check_minigpt(ns, lesson):
    import torch
    from ch5 import CORPUS
    need(ns, "train", "generate")
    dev = _dev()
    vocab = sorted(set(CORPUS))
    data = torch.tensor([vocab.index(c) for c in CORPUS], dtype=torch.long, device=dev)
    model = ns["train"](data, len(vocab))
    if model is None or not hasattr(model, "parameters"):
        raise Fail("train が学習した脳（model）を返していないよ")
    block = ns.get("BLOCK", 16)
    model.eval()
    g = torch.Generator().manual_seed(123)
    with torch.no_grad():
        i = torch.randint(0, len(data) - block - 1, (128,), generator=g)
        x = torch.stack([data[j:j + block] for j in i])
        y = torch.stack([data[j + 1:j + block + 1] for j in i])
        loss = float(torch.nn.functional.cross_entropy(model(x).reshape(-1, len(vocab)), y.reshape(-1)))
        start = torch.tensor([[vocab.index("ふ")]], dtype=torch.long, device=dev)
        torch.manual_seed(5)
        out = ns["generate"](model, start, 40)
    n_out = int(out.shape[1]) if hasattr(out, "shape") and out.dim() == 2 else 0
    text = "".join(vocab[int(t)] for t in out[0]) if n_out else ""
    n_param = sum(p.numel() for p in model.parameters())
    rows = [row("学習後の損失（最初は約4.8。小さいほど良い）", round(loss, 2), "2.0 以下", ok=loss <= 2.0),
            row("書いた文の長さ（書き出し1文字＋続き40文字）", f"{n_out}文字", "41文字", ok=n_out == 41)]
    note = (f"✍ 書いた文：{text.replace(chr(10), '／')}　（脳の重み {n_param:,}個）" if n_out == 41 else None)
    return table(rows, note)


def _ref_generate(text, start, n):
    counts = _ref_counts(text)
    out = start
    for _ in range(n):
        nxt = counts[out[-1]]
        out += max(nxt, key=nxt.get)
    return out


@cases(33)
def _lv33(ns):
    need(ns, "generate")
    tests = [("ねこねこねずみ", "ね", 3), ("あいあいあう", "あ", 4), ("ふむふむふーん", "ふ", 2), ("ねこねこねずみ", "こ", 1)]
    return [row(f"「{t}」を読んで「{s}」の続きを{n}文字", ns["generate"](t, s, n), _ref_generate(t, s, n)) for t, s, n in tests]


CHECKS["minigpt"] = check_minigpt


# ---------------------------------------------------------------- 第6章
def inject():
    """第6章のコードに渡す設定（app.py の設定と同じもの）"""
    sp = os.environ.get("AIKU_SPEAKER", "")
    return {
        "OLLAMA_URL": os.environ.get("AIKU_OLLAMA", "http://localhost:11434/api/chat"),
        "MODEL": os.environ.get("AIKU_MODEL", "qwen2.5:7b"),
        "VISION_MODEL": os.environ.get("AIKU_VISION", "qwen2.5vl:7b"),
        "AIVIS_URL": os.environ.get("AIKU_AIVIS", "http://127.0.0.1:10101"),
        "SPEAKER": int(sp) if sp.isdigit() else None,
    }


def _real(fn, what="Ollama"):
    """本物のサービスを呼ぶ。繋がらないときは、わかりやすい言葉で止める"""
    import requests
    try:
        return fn()
    except requests.exceptions.ConnectionError:
        raise Fail(f"{what} に繋がらないよ。{what} が起動しているか確認してね")
    except requests.exceptions.Timeout:
        raise Fail(f"{what} の返事が時間切れになったよ。もう一度試してみてね")
    except KeyError as e:
        raise Fail(f"{what} の返事に {e} が無かったよ。app.py の CHAT_MODEL の名前が、入れてあるモデルと合っているか確認してね")


def _fake(ns, reply):
    """本物の脳のかわりに、渡された会話を記録するだけの「にせもの」を差し込む"""
    rec = []

    def fake(messages, *args, **kw):
        rec.append({"messages": copy.deepcopy(messages), "args": args})
        return reply
    ns["call_llm"] = fake
    return rec


def _is_text(v):
    return isinstance(v, str) and v.strip() != ""


def _clip(s, n=90):
    s = str(s).replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"


def check_llm_call(ns, lesson):
    need(ns, "call_llm", "ask")
    real = _real(lambda: ns["call_llm"]([{"role": "user", "content": "1たす1は？ 数字だけで答えて"}]))
    rows = [row("call_llm：大きな脳から返事の文章が返ってきた", _clip(real, 30) if _is_text(real) else repr(real), "空でない文章", ok=_is_text(real))]
    rec = _fake(ns, "にせものの返事")
    got = ns["ask"]("テスト")
    sent = rec[0]["messages"] if rec else "（call_llm が呼ばれなかった）"
    rows.append(row("ask：質問を user の発言にして送った", sent, [{"role": "user", "content": "テスト"}]))
    rows.append(row("ask：返事をそのまま返した", got, "にせものの返事"))
    return table(rows, note=f"💬 大きな脳の返事：{_clip(real)}" if _is_text(real) else None)


def check_llm_persona(ns, lesson):
    need(ns, "call_llm", "build_messages", "ask", "PERSONA")
    persona = ns["PERSONA"]
    rows = [row("build_messages(\"性格\", \"質問\")", ns["build_messages"]("性格", "質問"),
                [{"role": "system", "content": "性格"}, {"role": "user", "content": "質問"}]),
            row("PERSONA を自分の言葉で書いた", _clip(persona, 30), "10文字以上で、書き出しのままではない",
                ok=isinstance(persona, str) and len(persona) >= 10 and persona != "ここに性格を書こう")]
    real = _real(lambda: ns["ask"]("自己紹介して")) if all(r["ok"] for r in rows) else "（上の2つを先に直そう）"
    rows.append(row("性格つきで返事が返ってきた", _clip(real, 30), "空でない文章", ok=_is_text(real) and all(r["ok"] for r in rows)))
    return table(rows, note=f"💬 「自己紹介して」への返事：{_clip(real, 140)}" if all(r["ok"] for r in rows) else None)


def check_llm_history(ns, lesson):
    need(ns, "call_llm", "chat", "history", "PERSONA")
    real_llm = ns["call_llm"]
    ns["history"].clear()
    rec = _fake(ns, "にせ返事")
    r1 = ns["chat"]("A")
    ns["chat"]("B")
    sysm = {"role": "system", "content": ns["PERSONA"]}
    want2 = [sysm, {"role": "user", "content": "A"}, {"role": "assistant", "content": "にせ返事"}, {"role": "user", "content": "B"}]
    want_h = want2[1:] + [{"role": "assistant", "content": "にせ返事"}]
    rows = [row("1回目：返事を返した", r1, "にせ返事"),
            row("2回目に脳へ渡した会話（設定書＋1回目のやりとり＋今の質問）",
                [m.get("role") for m in rec[1]["messages"]] if len(rec) > 1 else "（呼ばれなかった）",
                [m["role"] for m in want2], ok=len(rec) > 1 and rec[1]["messages"] == want2),
            row("history に貯まった発言の数", len(ns["history"]), 4, ok=ns["history"] == want_h)]
    ns["call_llm"] = real_llm
    ns["history"].clear()
    good = all(r["ok"] for r in rows)
    real = "（上を先に直そう）"
    if good:
        _real(lambda: ns["chat"]("私の好きな食べ物はカレーです。覚えておいて。"))
        real = _real(lambda: ns["chat"]("私の好きな食べ物は何だった？"))
    rows.append(row("本物の脳と2往復できた", _clip(real, 30), "空でない文章", ok=good and _is_text(real)))
    return table(rows, note=f"💬 「カレーが好き」と教えたあと「好きな食べ物は？」と聞いた返事：{_clip(real, 120)}" if good and _is_text(real) else None)


@cases(37)
def _lv37(ns):
    import tempfile
    need(ns, "open_db", "save_memory", "load_memories")
    path = os.path.join(tempfile.mkdtemp(), "nikki.db")
    db = ns["open_db"](path)
    first = ns["load_memories"](db)
    ns["save_memory"](db, "宏仁の好きな食べ物はカレー")
    ns["save_memory"](db, "今日はLv37をクリアした")
    same_conn = ns["load_memories"](db)
    db.close()
    db2 = ns["open_db"](path)                    # 日記帳を閉じて、開き直す
    reopened = ns["load_memories"](db2)
    db2.close()
    want = ["宏仁の好きな食べ物はカレー", "今日はLv37をクリアした"]
    return [row("何も書いていない日記帳を読む", first, []),
            row("2行書いて、すぐ読む", same_conn, want),
            row("日記帳を閉じて、開き直してから読む（commit できているか）", reopened, want)]


RAG_MEMS = ["宏仁の好きな食べ物はカレー", "ハリリの誕生日は11月3日", "犬は鼻が長くて、猫はひげが長い"]


def check_llm_rag(ns, lesson):
    need(ns, "call_llm", "search", "answer", "PERSONA")
    real_llm = ns["call_llm"]
    rows = [row("「好きな食べ物は何？」で探す", ns["search"]("好きな食べ物は何？", list(RAG_MEMS)), RAG_MEMS[0]),
            row("「誕生日はいつ？」で探す", ns["search"]("誕生日はいつ？", list(RAG_MEMS)), RAG_MEMS[1])]
    rec = _fake(ns, "にせ返事")
    got = ns["answer"]("誕生日はいつ？", list(RAG_MEMS))
    msgs = rec[0]["messages"] if rec else []
    sys_text = " ".join(m.get("content", "") for m in msgs if m.get("role") == "system")
    user_text = [m.get("content") for m in msgs if m.get("role") == "user"]
    rows.append(row("system に、見つけた記憶が参考情報として入っている", "入っている" if RAG_MEMS[1] in sys_text else "入っていない", "入っている"))
    rows.append(row("user に質問が入っていて、返事を返した", (user_text, got), (["誕生日はいつ？"], "にせ返事")))
    ns["call_llm"] = real_llm
    good = all(r["ok"] for r in rows)
    real = _real(lambda: ns["answer"]("宏仁の好きな食べ物は何？", list(RAG_MEMS))) if good else "（上を先に直そう）"
    rows.append(row("本物の脳が、記憶を見て答えた", _clip(real, 30), "空でない文章", ok=good and _is_text(real)))
    return table(rows, note=f"💬 「好きな食べ物は何？」への返事：{_clip(real, 120)}" if good and _is_text(real) else None)


def _out_dir():
    d = os.path.join(BASE, "static", "out")
    os.makedirs(d, exist_ok=True)
    return d


def check_voice(ns, lesson):
    need(ns, "speak")
    if ns.get("SPEAKER") is None:
        raise Fail("AivisSpeech が起動していないか、声が見つからないよ。AivisSpeech を起動してから、もう一度試験してね")
    wav = _real(lambda: ns["speak"]("こんにちは。声が出せるようになったよ。"), "AivisSpeech")
    is_bytes = isinstance(wav, (bytes, bytearray))
    is_wav = is_bytes and bytes(wav[:4]) == b"RIFF"
    rows = [row("音声の生データが返ってきた", f"{len(wav)}バイト" if is_bytes else type(wav).__name__, "1000バイト以上のデータ", ok=is_bytes and len(wav) >= 1000),
            row("wav形式の音声になっている", "wav" if is_wav else "wavではない", "wav")]
    extra = {}
    if is_wav:
        with open(os.path.join(_out_dir(), "lv39.wav"), "wb") as f:
            f.write(wav)
        extra["audio"] = "/static/out/lv39.wav"
    return table(rows, note="🔊 作った声を再生するよ" if is_wav else None, **extra)


def check_ear(ns, lesson):
    import requests
    need(ns, "listen")
    conf = inject()
    if conf["SPEAKER"] is None:
        raise Fail("聞かせる音声を作るのに AivisSpeech を使うよ。AivisSpeech を起動してから、もう一度試験してね")

    def make():
        q = requests.post(conf["AIVIS_URL"] + "/audio_query", params={"text": "こんにちは。今日はいい天気ですね。", "speaker": conf["SPEAKER"]}, timeout=30).json()
        return requests.post(conf["AIVIS_URL"] + "/synthesis", params={"speaker": conf["SPEAKER"]}, json=q, timeout=120).content
    path = os.path.join(_out_dir(), "lv40.wav")
    with open(path, "wb") as f:
        f.write(_real(make, "AivisSpeech"))
    text = ns["listen"](path)
    return table([row("聞き取った文章が返ってきた（聞かせた声：こんにちは。今日はいい天気ですね。）", _clip(text, 40) if _is_text(text) else repr(text), "空でない文章", ok=_is_text(text))],
                 note=f"👂 聞き取った文章：{_clip(text)}" if _is_text(text) else None, audio="/static/out/lv40.wav")


def check_llm_vision(ns, lesson):
    import base64
    need(ns, "call_llm", "look")
    real_llm = ns["call_llm"]
    img = os.path.join(BASE, "static", "img", "child", "base.png")
    if not os.path.exists(img):
        img = os.path.join(BASE, "static", "img", "harii", "normal.png")
    if not os.path.exists(img):
        raise Fail("見せる絵が見つからないよ。static\\img\\child\\base.png を置いてね")
    with open(img, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    rec = _fake(ns, "にせ返事")
    got = ns["look"](img, "何が見える？")
    m = rec[0]["messages"][-1] if rec and rec[0]["messages"] else {}
    rows = [row("user の発言に質問が入っている", (m.get("role"), m.get("content")), ("user", "何が見える？")),
            row("\"images\" に絵（base64）が入っている", "入っている" if m.get("images") == [b64] else "入っていない", "入っている"),
            row("絵がわかる脳（VISION_MODEL）に聞いた", rec[0]["args"][0] if rec and rec[0]["args"] else "（脳の指定なし）", ns["VISION_MODEL"]),
            row("返事を返した", got, "にせ返事")]
    ns["call_llm"] = real_llm
    note = None
    if all(r["ok"] for r in rows):
        try:
            real = ns["look"](img, "この絵には何が描かれている？日本語で短く答えて。")
            note = f"👁 絵を見た感想：{_clip(real, 140)}"
        except Exception as e:
            note = (f"👁 コードは合格。ただ、絵がわかる脳「{ns['VISION_MODEL']}」に繋がらなかったよ（{type(e).__name__}）。"
                    "app.py の VISION_MODEL を、Ollama に入れてあるモデル名に合わせると、絵の感想が出るようになる")
    return table(rows, note)


@cases(42)
def _lv42(ns):
    need(ns, "pick_face", "mouth_frames")
    faces = [("ふーん、やるじゃん。", "happy"), ("雑すぎるんだけど。", "pout"), ("ふふ、当然でしょ。", "confident"),
             ("今日はここまでにする？", "normal"), ("おめでとう。でもまだまだだね。", "happy")]
    rows = [row(f"「{t}」の表情", ns["pick_face"](t), f) for t, f in faces]
    rows.append(row("声の大きさ [0.1, 0.5, 0.02, 0.3]、境目 0.2 の口パク", ns["mouth_frames"]([0.1, 0.5, 0.02, 0.3], 0.2), ["close", "open", "close", "open"]))
    rows.append(row("声の大きさ [0.2, 0.21]、境目 0.2 の口パク", ns["mouth_frames"]([0.2, 0.21], 0.2), ["close", "open"]))
    return rows


def check_final(ns, lesson):
    need(ns, "app", "call_llm", "history", "PERSONA")
    ns["history"].clear()
    rec = _fake(ns, "ふーん、やるじゃん。")
    client = ns["app"].test_client()
    r1 = client.post("/chat", json={"text": "A"}).get_json() or {}
    client.post("/chat", json={"text": "B"})
    sysm = {"role": "system", "content": ns["PERSONA"]}
    want2 = [sysm, {"role": "user", "content": "A"}, {"role": "assistant", "content": "ふーん、やるじゃん。"}, {"role": "user", "content": "B"}]
    rows = [row("話しかけたら返事が返ってきた", r1.get("reply"), "ふーん、やるじゃん。"),
            row("返事に合う表情を選んだ", r1.get("face"), "happy"),
            row("2回目は、1回目のやりとりを覚えたうえで脳に聞いた",
                [m.get("role") for m in rec[1]["messages"]] if len(rec) > 1 else "（呼ばれなかった）",
                [m["role"] for m in want2], ok=len(rec) > 1 and rec[1]["messages"] == want2),
            row("話しかける画面（/）が開ける", client.get("/").status_code, 200)]
    ns["history"].clear()
    if not all(r["ok"] for r in rows):
        return table(rows)
    return table(rows, note="🎉 これがあなたの自作HARII。黒い画面で「C:\\Python311\\python.exe C:\\AI_Assistant\\ai_ikusei\\brain\\lv43.py」を実行して、"
                            "ブラウザで http://localhost:5007 を開くと、本物の脳につながって話せるよ")


CHECKS.update({"llm_call": check_llm_call, "llm_persona": check_llm_persona, "llm_history": check_llm_history,
               "llm_rag": check_llm_rag, "voice": check_voice, "ear": check_ear,
               "llm_vision": check_llm_vision, "final": check_final})
