# -*- coding: utf-8 -*-
"""
スマホ版の試験官。ブラウザの中の Python（Pyodide）で動く。
PC版と同じレベルは checks.py の試験をそのまま使い、
差し替えたレベル（check="m"）はこのファイルの MCASES で試験する。
"""
import copy
import json
import re
import traceback

try:
    import numpy as np
except ImportError:      # 読み込み前の試し用（スマホでは必ず入っている）
    np = None

import checks
from checks import Fail, row, table, need, make_digits, make_faces, draw_face, FEATURES
from m_lessons import LESSONS

MCASES = {}


def mcase(lid):
    def deco(fn):
        MCASES[lid] = fn
        return fn
    return deco


def _out(x):
    return x if isinstance(x, dict) else table(x)


# ================================================================ 第3章
@mcase(17)
def _m17(ns):
    need(ns, "Value")
    V = ns["Value"]
    a, b = V(2.0), V(3.0)
    c = a * b
    c.backward()
    rows = [row("c = a × b（a=2, b=3）の a の傾き", a.grad, 3.0),
            row("同じ式の b の傾き", b.grad, 2.0)]
    a, b = V(2.0), V(3.0)
    c = a * b + a
    c.backward()
    rows.append(row("c = a × b + a の a の傾き", a.grad, 4.0))
    x = V(3.0)
    y = x * x
    y.backward()
    rows.append(row("y = x × x（x=3）の x の傾き", x.grad, 6.0))
    note = None
    if all(r["ok"] for r in rows):            # おまけ：Value だけで重みを学習してみる
        w = V(0.0)
        for _ in range(60):
            loss = None
            for xv, yv in [(1.0, 2.0), (2.0, 4.0), (3.0, 6.0)]:
                d = w * V(xv) + V(-yv)
                loss = d * d if loss is None else loss + d * d
            w.grad = 0.0
            loss.backward()
            w = V(w.data - 0.02 * w.grad)
        note = f"🧠 この箱だけで「y = w × x」の w を学習させたら、w = {round(w.data, 3)}（正解は 2）になったよ"
    return table(rows, note)


def _digit_acc(P):
    Xt, yt = make_digits(300, seed=999)
    h = np.maximum(0, Xt @ np.asarray(P["W1"]) + np.asarray(P["b1"]))
    pred = np.argmax(h @ np.asarray(P["W2"]) + np.asarray(P["b2"]), axis=1)
    return float((pred == yt).mean())


def _check_params(P):
    if not isinstance(P, dict) or not all(k in P for k in ("W1", "b1", "W2", "b2")):
        raise Fail("train は {\"W1\": …, \"b1\": …, \"W2\": …, \"b2\": …} の辞書を返してね")


@mcase(18)
def _m18(ns):
    need(ns, "train")
    X, y = make_digits(800, seed=1)
    P = ns["train"](X.astype(float), y)
    _check_params(P)
    acc = _digit_acc(P)
    return [row("初めて見る字300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9)]


@mcase(19)
def _m19(ns):
    need(ns, "train", "step")
    calls = {"n": 0, "size": 0}
    orig = ns["step"]

    def counted(P, Xb, yb, lr):
        calls["n"] += 1
        calls["size"] = max(calls["size"], len(Xb))
        return orig(P, Xb, yb, lr)
    ns["step"] = counted
    X, y = make_digits(800, seed=1)
    P = ns["train"](X.astype(float), y)
    ns["step"] = orig
    _check_params(P)
    acc = _digit_acc(P)
    rows = [row("重みを直した回数", f"{calls['n']}回", "300回以上", ok=calls["n"] >= 300),
            row("1回に使った絵の枚数（いちばん多いとき）", f"{calls['size']}枚", "64枚以下", ok=0 < calls["size"] <= 64),
            row("初めて見る字300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9)]
    return table(rows, f"📊 30周のあいだに重みを {calls['n']}回 直したよ（全部まとめてだと30回だけ）")


@mcase(20)
def _m20(ns):
    need(ns, "train")
    X, y = make_digits(800, seed=1)
    P = ns["train"](X.astype(float), y)
    _check_params(P)
    s1, s2 = np.shape(P["W1"]), np.shape(P["W2"])
    shape_ok = len(s1) == 2 and len(s2) == 2 and s1[0] == 35 and s2[1] == 10 and s1[1] == s2[0]
    acc = _digit_acc(P) if shape_ok else 0.0
    return [row("W1 と W2 の形", f"W1{tuple(s1)}　W2{tuple(s2)}", "W1(35, 中間)　W2(中間, 10)", ok=shape_ok),
            row("初めて見る字300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9)]


# ================================================================ 第4章
def _imgs(n, seed, kinds=("dog", "cat")):
    X, y = make_faces(n, seed, kinds)
    return X[:, 0].astype(float), y


def train_head(F, y, n=2):
    F = np.asarray(F, dtype=float)
    mu, sd = F.mean(axis=0), F.std(axis=0) + 1e-6
    Z = (F - mu) / sd
    W = np.zeros((Z.shape[1], n)); b = np.zeros(n); Y = np.eye(n)[y]
    for _ in range(500):
        z = Z @ W + b
        p = np.exp(z - z.max(axis=1, keepdims=True)); p /= p.sum(axis=1, keepdims=True)
        d = (p - Y) / len(Z)
        W -= 0.5 * Z.T @ d; b -= 0.5 * d.sum(axis=0)

    def predict(G, prob=False):
        z = ((np.asarray(G, dtype=float) - mu) / sd) @ W + b
        if prob:
            p = np.exp(z - z.max(axis=1, keepdims=True))
            return p / p.sum(axis=1, keepdims=True)
        return np.argmax(z, axis=1)
    return predict


@mcase(24)
def _m24(ns):
    need(ns, "train", "features")
    X, y = _imgs(400, 2)
    Xt, yt = _imgs(300, 998)
    need(ns, "pool")
    m = np.array([[1, 2, 0, 0], [3, 4, 0, 5], [0, 0, 7, 0], [6, 0, 0, 8]], dtype=float)
    rows = [row("pool：4×4 → 2×2（2×2ごとの一番大きい数字）", np.asarray(ns["pool"](m.copy()), dtype=float), np.array([[4.0, 5.0], [6.0, 8.0]])),
            row("pool：5×5 → 2×2（はみ出す端は切りそろえる）", np.shape(ns["pool"](np.ones((5, 5)))), (2, 2))]
    n = len(np.ravel(ns["features"](X[0])))
    rows.append(row("特徴の数（4種類の虫眼鏡 × 縮めた地図）", f"{n}個", "36個", ok=n == 36))
    if not all(r["ok"] for r in rows):
        return rows
    model = ns["train"](X, y)
    acc = float((np.asarray(model(Xt)) == yt).mean())
    rows.append(row("初めて見る絵300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9))
    return table(rows, f"🔍 1枚の絵（256個の点）を、{n}個の手がかりにまとめて判断したよ")


class Senpai:
    """犬と猫をたくさん見て育った先輩（2段の脳）"""

    def __init__(self):
        X, y = _imgs(400, 3)
        rng = np.random.default_rng(0)
        Xr = X.reshape(len(X), -1)
        self.W1 = rng.normal(0, 0.1, (256, 32)); self.b1 = np.zeros(32)
        W2 = rng.normal(0, 0.1, (32, 2)); b2 = np.zeros(2)
        Y = np.eye(2)[y]
        for _ in range(300):
            h = np.maximum(0, Xr @ self.W1 + self.b1)
            z = h @ W2 + b2
            p = np.exp(z - z.max(axis=1, keepdims=True)); p /= p.sum(axis=1, keepdims=True)
            d2 = (p - Y) / len(Xr); d1 = (d2 @ W2.T) * (h > 0)
            W2 -= 0.5 * h.T @ d2; b2 -= 0.5 * d2.sum(axis=0)
            self.W1 -= 0.5 * Xr.T @ d1; self.b1 -= 0.5 * d1.sum(axis=0)
        self.W2, self.b2 = W2, b2

    def eyes(self, Xs):
        Xs = np.asarray(Xs, dtype=float)
        return np.maximum(0, Xs.reshape(len(Xs), -1) @ self.W1 + self.b1)


@mcase(25)
def _m25(ns):
    need(ns, "transfer")
    kinds = ("rabbit", "bear")
    senpai = Senpai()
    W1_before = senpai.W1.copy()
    X, y = _imgs(16, 11, kinds)
    Xt, yt = _imgs(300, 997, kinds)
    predict = ns["transfer"](senpai, X, y)
    acc = float((np.asarray(predict(Xt)) == yt).mean())
    kept = bool(np.array_equal(W1_before, senpai.W1))
    return table([row("うさぎ・くま 300枚の正解率", f"{round(acc * 100)}%", "85%以上", ok=acc >= 0.85),
                  row("先輩の目はそのまま使った", "そのまま" if kept else "変わってしまった", "そのまま")],
                 f"📊 先輩の脳の重みは {256 * 32 + 32 + 32 * 2 + 2:,}個。今回新しく学習したのは判断係の {32 * 2 + 2}個だけ")


_DOG_T = {}


def dog_score(patch):
    if "t" not in _DOG_T:
        dogs, _ = make_faces(200, 40, ("dog", "dog"))
        T = dogs[:, 0].mean(axis=0)
        _DOG_T["t"] = T - T.mean()
    T = _DOG_T["t"]
    q = np.asarray(patch, dtype=float)
    q = q - q.mean()
    return float((q * T).sum() / (np.linalg.norm(q) * np.linalg.norm(T) + 1e-9))


def make_scene(seed):
    r = np.random.default_rng(seed)
    img = r.normal(0.1, 0.08, (28, 28)).clip(0, 1)
    top, left = int(r.integers(0, 13)), int(r.integers(0, 13))
    face = draw_face("dog", r)
    img[top:top + 16, left:left + 16] = np.maximum(img[top:top + 16, left:left + 16], face)
    return img, (top, left)


@mcase(26)
def _m26(ns):
    need(ns, "find_dog")
    rows = []
    for i, seed in enumerate([3, 8, 15, 21, 30], 1):
        img, (t, l) = make_scene(seed)
        got = ns["find_dog"](img.copy(), dog_score)
        ok = isinstance(got, (tuple, list)) and len(got) == 2 and abs(int(got[0]) - t) <= 1 and abs(int(got[1]) - l) <= 1
        shown = tuple(int(g) for g in got) if isinstance(got, (tuple, list)) and len(got) == 2 else got
        rows.append(row(f"絵{i}：犬がいる場所（上, 左）", shown, (t, l), ok=ok))
    return rows


@mcase(27)
def _m27(ns):
    need(ns, "features")
    X, y = _imgs(400, 2)
    Xt, yt = _imgs(300, 998)
    F = [np.ravel(ns["features"](img.copy())) for img in X]
    n = len(F[0])
    if n > 64:
        return [row("特徴の数", f"{n}個", "64個以下", ok=False)]
    head = train_head(F, y)
    acc = float((head([np.ravel(ns["features"](img.copy())) for img in Xt]) == yt).mean())
    return [row("特徴の数", f"{n}個", "64個以下", ok=True),
            row("初めて見る絵300枚の正解率", f"{round(acc * 100)}%", "90%以上", ok=acc >= 0.9)]


# ================================================================ 第5章
@mcase(32)
def _m32(ns):
    from ch5 import CORPUS
    need(ns, "train", "generate", "forward")
    vocab = sorted(set(CORPUS))
    ids = [vocab.index(c) for c in CORPUS]
    P = ns["train"](list(ids), len(vocab))
    C = int(ns.get("C", 2))
    ctx = np.array([ids[i:i + C] for i in range(len(ids) - C)])
    nxt = np.array(ids[C:])
    p = ns["forward"](P, ctx)[2]
    loss = float(-np.log(p[np.arange(len(nxt)), nxt] + 1e-12).mean())
    start = [vocab.index(c) for c in "ふー"[:C]]
    out = ns["generate"](P, list(start), 40)
    n_out = len(out) if isinstance(out, (list, tuple)) else 0
    text = "".join(vocab[int(t)] for t in out) if n_out else ""
    n_param = sum(np.size(v) for v in P.values())
    rows = [row("学習後の損失（最初は約4.8。小さいほど良い）", round(loss, 2), "1.0 以下", ok=loss <= 1.0),
            row("書いた文の長さ（書き出し＋続き40文字）", f"{n_out}文字", f"{C + 40}文字", ok=n_out == C + 40)]
    return table(rows, f"✍ 書いた文：{text.replace(chr(10), '／')}　（脳の重み {n_param:,}個）" if n_out == C + 40 else None)


# ================================================================ 第6章
def _fake(ns, reply="にせ返事"):
    rec = []

    def fake(messages, *a, **k):
        rec.append(copy.deepcopy(messages))
        return reply
    ns["call_llm"] = fake
    return rec


def _letter(messages):
    return "📨 大きな脳へ送る手紙：" + json.dumps({"model": "qwen2.5:7b", "messages": messages, "stream": False}, ensure_ascii=False)


@mcase(34)
def _m34(ns):
    need(ns, "make_request", "read_reply")
    want = {"model": "qwen2.5:7b", "messages": [{"role": "user", "content": "こんにちは"}], "stream": False}
    got = ns["make_request"]("こんにちは")
    rows = [row("make_request(\"こんにちは\") の手紙", got, want, ok=got == want)]
    for text in ["やあ、宏仁", "ふーん、やるじゃん。"]:
        resp = {"model": "qwen2.5:7b", "message": {"role": "assistant", "content": text}, "done": True}
        rows.append(row(f"返事の手紙から文章を取り出す（中身：{text}）", ns["read_reply"](copy.deepcopy(resp)), text))
    note = ("📨 作った手紙：" + json.dumps(got, ensure_ascii=False)) if rows[0]["ok"] else None
    return table(rows, note)


@mcase(35)
def _m35(ns):
    need(ns, "build_messages", "ask", "PERSONA")
    persona = ns["PERSONA"]
    msgs = ns["build_messages"]("性格", "質問")
    rows = [row("build_messages(\"性格\", \"質問\")", msgs,
                [{"role": "system", "content": "性格"}, {"role": "user", "content": "質問"}]),
            row("PERSONA を自分の言葉で書いた", str(persona)[:30], "10文字以上で、書き出しのままではない",
                ok=isinstance(persona, str) and len(persona) >= 10 and persona != "ここに性格を書こう")]
    note = None
    if all(r["ok"] for r in rows):
        note = _letter(ns["build_messages"](persona, "自己紹介して"))
    return table(rows, note)


@mcase(36)
def _m36(ns):
    need(ns, "chat", "history", "PERSONA", "call_llm")
    mock = ns["call_llm"]
    ns["history"].clear()
    rec = _fake(ns)
    r1 = ns["chat"]("A")
    ns["chat"]("B")
    sysm = {"role": "system", "content": ns["PERSONA"]}
    want2 = [sysm, {"role": "user", "content": "A"}, {"role": "assistant", "content": "にせ返事"}, {"role": "user", "content": "B"}]
    want_h = want2[1:] + [{"role": "assistant", "content": "にせ返事"}]
    rows = [row("1回目：返事を返した", r1, "にせ返事"),
            row("2回目に脳へ渡した会話（設定書＋1回目のやりとり＋今の質問）",
                [m.get("role") for m in rec[1]] if len(rec) > 1 else "（呼ばれなかった）",
                [m["role"] for m in want2], ok=len(rec) > 1 and rec[1] == want2),
            row("history に貯まった発言の数", len(ns["history"]), 4, ok=ns["history"] == want_h)]
    ns["call_llm"] = mock
    ns["history"].clear()
    note = None
    if all(r["ok"] for r in rows):
        replies = [ns["chat"](q) for q in ["好きな食べ物はカレー", "覚えた？", "何が好きだっけ？"]]
        note = "💬 3回話したときの、まねっこ脳の報告：" + "　／　".join(replies)
    ns["history"].clear()
    return table(rows, note)


RAG_MEMS = ["宏仁の好きな食べ物はカレー", "ハリリの誕生日は11月3日", "犬は鼻が長くて、猫はひげが長い"]


@mcase(38)
def _m38(ns):
    need(ns, "search", "build_messages", "PERSONA")
    rows = [row("「好きな食べ物は何？」で探す", ns["search"]("好きな食べ物は何？", list(RAG_MEMS)), RAG_MEMS[0]),
            row("「誕生日はいつ？」で探す", ns["search"]("誕生日はいつ？", list(RAG_MEMS)), RAG_MEMS[1])]
    msgs = ns["build_messages"]("誕生日はいつ？", list(RAG_MEMS))
    sys_text = " ".join(m.get("content", "") for m in msgs if isinstance(m, dict) and m.get("role") == "system")
    user = [m.get("content") for m in msgs if isinstance(m, dict) and m.get("role") == "user"]
    rows.append(row("system に、見つけた記憶が参考情報として入っている", "入っている" if RAG_MEMS[1] in sys_text else "入っていない", "入っている"))
    rows.append(row("system に、性格の設定書も入っている", "入っている" if ns["PERSONA"] in sys_text else "入っていない", "入っている"))
    rows.append(row("user に質問が入っている", user, ["誕生日はいつ？"]))
    return table(rows, _letter(msgs) if all(r["ok"] for r in rows) else None)


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(a @ b / (na * nb))


def _vec(t, vocab):
    v = np.zeros(len(vocab))
    for ch in t:
        if ch in vocab:
            v[vocab.index(ch)] += 1
    return v


VEC_CASES = [
    ("犬の鼻は？", ["今日の夕飯は何？犬の散歩のあと鼻歌", "犬の鼻は長い"]),
    ("好きな色は？", ["好きな食べ物は何？色々あるけど、好きなのはカレー", "好きな色は紫"]),
]


@mcase(39)
def _m39(ns):
    need(ns, "to_vec", "search")
    vocab = ["い", "ぬ", "ね", "こ"]
    rows = [row("「いぬいぬ」をベクトルに（名簿：い・ぬ・ね・こ）", np.asarray(ns["to_vec"]("いぬいぬ", list(vocab)), dtype=float), np.array([2.0, 2.0, 0.0, 0.0])),
            row("「ねこいぬ」をベクトルに", np.asarray(ns["to_vec"]("ねこいぬ", list(vocab)), dtype=float), np.array([1.0, 1.0, 1.0, 1.0]))]
    lines = []
    for q, mems in VEC_CASES:
        V = sorted(set("".join(mems + [q])))
        want = max(mems, key=lambda m: _cos(_vec(q, V), _vec(m, V)))
        old = max(mems, key=lambda m: len(set(q) & set(m)))
        rows.append(row(f"「{q}」で探す", ns["search"](q, list(mems)), want))
        lines.append(f"「{q}」→ Lv38の数え方：{old[:12]}…　／　今回：{want}")
    return table(rows, "🔎 " + "　｜　".join(lines))


@mcase(40)
def _m40(ns):
    need(ns, "find_speech")
    f = ns["find_speech"]
    cases = [
        ("しゃべって、黙る", [0.0, 0.5, 0.6, 0.7, 0.0, 0.0], 0.2, 2, [(1, 4)]),
        ("2回しゃべる", [0.5, 0.5, 0.0, 0.0, 0.6, 0.6, 0.6, 0.1], 0.2, 2, [(0, 2), (4, 7)]),
        ("短い物音は無視", [0.0, 0.9, 0.0, 0.0, 0.5, 0.5, 0.5], 0.2, 2, [(4, 7)]),
        ("ずっと静か", [0.0, 0.1, 0.05], 0.2, 1, []),
    ]
    rows = []
    for name, vol, th, ml, want in cases:
        got = f(list(vol), th, ml)
        got = [tuple(int(x) for x in s) for s in got] if isinstance(got, list) else got
        rows.append(row(f"{name}：{vol}", got, want))
    return rows


_SEE = {}


def real_see():
    """犬・猫・うさぎ・くまを見分ける目（畳み込みの手がかり＋判断係）"""
    if "f" not in _SEE:
        from numpy.lib.stride_tricks import sliding_window_view as swv
        Ks = [np.array([[-1, 0, 1]] * 3, float), np.array([[-1, 0, 1]] * 3, float).T,
              np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]], float), np.array([[0, 1, 1], [-1, 0, 1], [-1, -1, 0]], float)]

        def pool(m):
            h, w = m.shape[0] // 2 * 2, m.shape[1] // 2 * 2
            return m[:h, :w].reshape(h // 2, 2, w // 2, 2).max(axis=(1, 3))

        def feat(img):
            return np.concatenate([pool(pool(np.maximum(0, np.einsum("ijkl,kl->ij", swv(img, k.shape), k)))).ravel() for k in Ks]
                                  + [pool(pool(img)).ravel()])
        kinds = ("dog", "cat", "rabbit", "bear")
        X, y = _imgs(400, 4, kinds)
        head = train_head([feat(x) for x in X], y, n=4)
        names = ["犬", "猫", "うさぎ", "くま"]

        def see(img):
            p = head([feat(np.asarray(img, dtype=float))], prob=True)[0]
            return {n: round(float(v), 3) for n, v in zip(names, p)}
        _SEE["f"] = see
    return _SEE["f"]


@mcase(41)
def _m41(ns):
    need(ns, "describe")
    fakes = [({"犬": 0.8, "猫": 0.1, "うさぎ": 0.05, "くま": 0.05}, "犬の顔が見えるよ"),
             ({"犬": 0.1, "猫": 0.05, "うさぎ": 0.15, "くま": 0.7}, "くまの顔が見えるよ"),
             ({"犬": 0.4, "猫": 0.35, "うさぎ": 0.15, "くま": 0.1}, "よく見えない…"),
             ({"犬": 0.0, "猫": 0.6, "うさぎ": 0.4, "くま": 0.0}, "猫の顔が見えるよ")]
    rows = [row(f"目の答えが {p}", ns["describe"](None, lambda img, p=p: dict(p)), want) for p, want in fakes]
    note = None
    if all(r["ok"] for r in rows):
        see = real_see()
        names = {"dog": "犬", "cat": "猫", "rabbit": "うさぎ", "bear": "くま"}
        r = np.random.default_rng(77)
        said = []
        for kind in ["dog", "cat", "rabbit", "bear"]:
            img = draw_face(kind, r).astype(float)
            said.append(f"{names[kind]}の絵 →「{ns['describe'](img, see)}」")
        note = "👁 本物の目につないだ結果：" + "　".join(said)
    return table(rows, note)


@mcase(43)
def _m43(ns):
    need(ns, "chat", "memory", "pick_face")
    ns["memory"].clear()
    rows = []
    fact = "宏仁の好きな食べ物はカレー"
    r1 = ns["chat"]("覚えて：" + fact)
    rep1 = r1.get("reply", "") if isinstance(r1, dict) else ""
    rows.append(row("「覚えて：…」→ 記憶帳に入った", list(ns["memory"]), [fact]))
    rows.append(row("「覚えて：…」の返事に「覚えた」と、覚えた内容が入っている", rep1,
                    "「覚えた」と内容を含む", ok="覚えた" in rep1 and fact in rep1))
    r2 = ns["chat"]("宏仁の好きな食べ物は？")
    rep2 = r2.get("reply", "") if isinstance(r2, dict) else ""
    rows.append(row("「好きな食べ物は？」→ 思い出して答えた", rep2, "「カレー」を含む", ok="カレー" in rep2))
    r3 = ns["chat"]("明日の天気は？")
    rep3 = r3.get("reply", "") if isinstance(r3, dict) else ""
    rows.append(row("知らないこと →「知らない」と正直に答えた", rep3, "「知らない」を含む", ok="知らない" in rep3))
    faces_ok = all(isinstance(r, dict) and r.get("face") == ns["pick_face"](r.get("reply", "")) for r in (r1, r2, r3))
    rows.append(row("返事に合う表情を選んだ", "選んでいる" if faces_ok else "選んでいない", "選んでいる"))
    ns["memory"].clear()
    note = "🎉 画面の下で、あなたが作ったハリリと話せるよ" if all(r["ok"] for r in rows) else None
    return table(rows, note)


# ================================================================ 実行
ERROR_GUIDE = [
    (r"list indices must be integers", "リストの番号に文字を使っている。リストは [0] のように数字で、辞書は [\"ひげ\"] のように名前で取り出す"),
    (r"string indices must be integers", "文字に [\"名前\"] を使っている。辞書だと思っている変数が、実はただの文字になっている"),
    (r"NameError: name '(.+?)' is not defined", "「{0}」という名前が見つからない。つづり間違いか、まだ作っていない変数"),
    (r"UnboundLocalError", "変数を作る前に使っている。先に 変数 = 0 のように用意する"),
    (r"expected ':'", "行の終わりのコロン（:）を忘れている。if・for・def の行の最後に必要"),
    (r"was never closed", "カッコの閉じ忘れ。( や [ の数と ) や ] の数が合っているか確認"),
    (r"unterminated string", "引用符（\"）の閉じ忘れ"),
    (r"IndentationError|unexpected indent|expected an indented block", "字下げ（行の頭の空白）がずれている。if・for・def の中の行は空白4つぶん下げる"),
    (r"invalid character", "全角の記号や空白がまざっている。記号は画面下のボタンで入れると安全"),
    (r"SyntaxError", "書き方の間違い。コロン忘れ、カッコや引用符の閉じ忘れ、= と == の取り違えが多い"),
    (r"KeyError: '(.+?)'", "辞書に「{0}」という名前がない。名前のつづりを確認"),
    (r"ZeroDivisionError", "0で割り算している"),
    (r"IndexError", "リストの長さより大きい番号を使っている"),
    (r"shapes .* not aligned|matmul: Input operand|operands could not be broadcast", "表の形が合っていない。@ の左の列の数と、右の行の数を同じにする"),
    (r"NoneType", "中身が空（None）のものを使っている。関数の return を忘れていないか確認"),
    (r"positional argument", "関数に渡す数が合っていない。def の行のカッコの中を書き換えていないか確認"),
    (r"unsupported operand|can only concatenate|not supported between", "数字と文字など、計算や比較ができない組み合わせになっている"),
    (r"AttributeError", "その変数には、その機能（.○○）がない。変数の中身が思っているものと違うかも"),
    (r"TypeError", "データの種類が合っていない（数字のはずが文字、など）"),
]


def explain_error(err):
    for pat, ja in ERROR_GUIDE:
        m = re.search(pat, err)
        if m:
            return ja.format(*m.groups())
    return ""


def short_error(e, path):
    line = None
    if isinstance(e, SyntaxError):
        line = e.lineno
    else:
        for f in reversed(traceback.extract_tb(e.__traceback__)):
            if f.filename == path:
                line = f.lineno
                break
    return (f"{line}行目: " if line else "") + f"{type(e).__name__}: {e}"


def _plain(x):
    """結果を JSON にできる形にそろえる"""
    if isinstance(x, dict):
        return {k: _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if np is not None and isinstance(x, np.generic):
        return x.item()
    if np is not None and isinstance(x, np.ndarray):
        return x.tolist()
    return x


def run(code, lid):
    """書いたコードで試験する。結果は JSON の文字列で返す"""
    lesson = LESSONS[lid]
    path = f"brain_lv{lid}.py"
    ns = {"__name__": "brain", "__code__": code, "OLLAMA_URL": "", "MODEL": "qwen2.5:7b",
          "VISION_MODEL": "qwen2.5vl:7b", "AIVIS_URL": "", "SPEAKER": None}
    try:
        exec(compile(code, path, "exec"), ns)
        if lesson["check"] == "m":
            res = _out(MCASES[lid](ns))
        else:
            res = checks.CHECKS[lesson["check"]](ns, lesson)
    except Fail as e:
        res = {"error": str(e)}
    except Exception as e:
        res = {"error": short_error(e, path)}
    if "error" in res:
        res["error_ja"] = res.get("error_ja") or explain_error(res["error"])
    return json.dumps(_plain(res), ensure_ascii=False)


_CHAT = {}


def chat(code, text):
    """Lv43 で作ったハリリと話す（書いたコードを1回だけ読み込んで使い回す）"""
    if _CHAT.get("code") != code:
        ns = {"__name__": "brain"}
        exec(compile(code, "brain_lv43.py", "exec"), ns)
        _CHAT.update(code=code, ns=ns)
    try:
        r = _CHAT["ns"]["chat"](text)
        return json.dumps(_plain(r if isinstance(r, dict) else {"reply": str(r), "face": "normal"}), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"reply": "（エラー）" + short_error(e, "brain_lv43.py"), "face": "pout"}, ensure_ascii=False)
