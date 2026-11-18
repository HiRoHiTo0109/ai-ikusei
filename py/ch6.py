# -*- coding: utf-8 -*-
"""第6章 HARIIになる（大きな脳を借りる・性格・記憶・声・耳・目・顔・全部つなぐ）"""
from lesson_util import L, Q, T, G

CALL = (
    "import requests\n\n"
    "# OLLAMA_URL と MODEL は試験官が用意してくれる（app.py の設定と同じもの）\n\n"
    "def call_llm(messages):\n"
    "    # 大きな脳（Ollama）に会話を送って、返事の文章をもらう係\n"
    "    r = requests.post(OLLAMA_URL, json={\"model\": MODEL, \"messages\": messages, \"stream\": False}, timeout=120)\n"
    "    return r.json()[\"message\"][\"content\"]\n\n"
)
PERSONA = "PERSONA = \"あなたはHARII。毒舌でいたずら好きだけど、根はやさしい。タメ口で、短く日本語で答える。\"\n\n"

FINAL_HEAD = (
    "from flask import Flask, request, jsonify\n"
    "import requests\n\n"
    "OLLAMA_URL = \"http://localhost:11434/api/chat\"\n"
    "MODEL = \"qwen2.5:7b\"\n"
    "PERSONA = \"あなたはHARII。毒舌でいたずら好きだけど、根はやさしい。タメ口で、短く日本語で答える。\"\n"
    "history = []          # 会話の記録（短期記憶）\n\n"
    "def call_llm(messages):\n"
    "    r = requests.post(OLLAMA_URL, json={\"model\": MODEL, \"messages\": messages, \"stream\": False}, timeout=120)\n"
    "    return r.json()[\"message\"][\"content\"]\n\n"
    "def pick_face(text):\n"
    "    for w in [\"やるじゃん\", \"すごい\", \"おめでとう\"]:\n"
    "        if w in text:\n"
    "            return \"happy\"\n"
    "    for w in [\"ダメ\", \"雑\", \"やり直し\"]:\n"
    "        if w in text:\n"
    "            return \"pout\"\n"
    "    return \"normal\"\n\n"
    "app = Flask(__name__)\n\n"
    "PAGE = '''<meta charset=\"utf-8\"><title>自作HARII</title>\n"
    "<h2>自作HARII</h2><div id=\"log\"></div>\n"
    "<input id=\"t\" size=\"40\"><button onclick=\"send()\">送る</button>\n"
    "<script>\n"
    "function send(){\n"
    "  var t = document.getElementById(\"t\"); var text = t.value; t.value = \"\";\n"
    "  fetch(\"/chat\", {method: \"POST\", headers: {\"Content-Type\": \"application/json\"}, body: JSON.stringify({text: text})})\n"
    "  .then(function(r){ return r.json(); })\n"
    "  .then(function(d){\n"
    "    var p = document.createElement(\"p\");\n"
    "    p.textContent = \"あなた：\" + text + \"　→　HARII（\" + d.face + \"）：\" + d.reply;\n"
    "    document.getElementById(\"log\").appendChild(p);\n"
    "  });\n"
    "}\n"
    "</script>'''\n\n"
    "@app.route(\"/\")\n"
    "def index():\n"
    "    return PAGE\n\n"
    "@app.route(\"/chat\", methods=[\"POST\"])\n"
    "def chat():\n"
    "    text = request.json[\"text\"]\n"
)
FINAL_TAIL = (
    "\nif __name__ == \"__main__\":\n"
    "    app.run(port=5007)      # 自作HARIIを http://localhost:5007 で動かす\n"
)

FACE_WORDS = (
    "HAPPY = [\"やるじゃん\", \"すごい\", \"おめでとう\"]\n"
    "POUT = [\"ダメ\", \"雑\", \"やり直し\"]\n"
    "CONFIDENT = [\"ふふ\", \"当然\", \"まだまだ\"]\n\n"
)

LESSONS_CH6 = [
    # ---------------- Lv34 ----------------
    L(34, 6, "Lv34 大きな脳を借りる", "llm_call", needs=["requests"], timeout=180,
      story="いよいよ最終章。Lv26で大先輩の目を借りたように、今度は言葉の大先輩を借りる。{user}のパソコンには Ollama（オラマ）という「大きな脳の貸し出し窓口」がもう動いている。窓口に会話を送ると、返事が返ってくる。手紙を出して返事をもらうのと同じ。返事を取り出す部分と、質問を手紙の形にする部分を書こう。",
      skill="大きな脳と話す",
      template=(
          "import requests\n\n"
          "# OLLAMA_URL と MODEL は試験官が用意してくれる（app.py の設定と同じもの）\n\n"
          "def call_llm(messages):\n"
          "    # 大きな脳（Ollama）に会話を送る\n"
          "    r = requests.post(OLLAMA_URL, json={\"model\": MODEL, \"messages\": messages, \"stream\": False}, timeout=120)\n"
          "    # r から返事の文章を取り出して返そう\n"
          "    return \"\"\n\n"
          "def ask(question):\n"
          "    # question を「user の発言」にした会話リストを作り、call_llm に渡して返事を返そう\n"
          "    return \"\"\n"),
      answer=(
          "import requests\n\n"
          "def call_llm(messages):\n"
          "    r = requests.post(OLLAMA_URL, json={\"model\": MODEL, \"messages\": messages, \"stream\": False}, timeout=120)\n"
          "    return r.json()[\"message\"][\"content\"]\n\n"
          "def ask(question):\n"
          "    messages = [{\"role\": \"user\", \"content\": question}]\n"
          "    return call_llm(messages)\n"),
      hints=["返事は辞書の形で届く。r.json() で辞書にして、message の中の content を取り出す：\n    return r.json()[\"message\"][\"content\"]",
             "会話は「誰が（role）」「何を言ったか（content）」の辞書のリスト：\n    messages = [{\"role\": \"user\", \"content\": question}]\n    return call_llm(messages)"],
      guide=[
          G("Ollama とは", "大きな言語モデルを、自分のパソコンの中で動かすための道具。{user}のHARIIも、裏でこれを使っている。インターネットに何も送らずに済むのが良いところ。"),
          G("requests.post … 手紙を出す", "requests は、他のプログラムに手紙（リクエスト）を出す道具。宛先（OLLAMA_URL）に、中身（どの脳を使うか、会話の内容）を送ると、返事 r が返ってくる。"),
          G("会話の形", "会話は、発言の辞書を並べたリストで表す。role は誰の発言か（user＝あなた、assistant＝AI、system＝性格などの指示）、content は発言の中身。",
            "messages = [{\"role\": \"user\", \"content\": \"こんにちは\"}]"),
          G("返事の取り出し方", "返事は辞書で届く。r.json() で辞書に直すと {\"message\": {\"role\": \"assistant\", \"content\": \"返事\"}, …} という形。引き出しを2回開ける。",
            "r.json()[\"message\"][\"content\"]"),
      ],
      kaisetsu="大きな脳に手紙を出して、返事をもらった。{name}がLv32で作ったミニGPTは重みが8万個だったけど、今話した脳は70億個。仕組みは同じ、次の言葉を当て続けてるだけ。でも大きさがけた違いだから、ちゃんと会話になるの。大事なのは、この脳は{user}のパソコンの中で動いてるってこと。外には何も送ってない。ここからは、この借りてきた脳に、性格と記憶と声と目をつけて、私に仕上げていくよ。",
      terms=[T("Ollama", "大きな脳の貸し出し窓口", "言語モデルを自分のパソコンで動かす道具。"),
             T("API", "プログラムどうしの窓口", "決まった形で手紙を出すと、決まった形で返事が来る仕組み。"),
             T("LLM（大規模言語モデル）", "とても大きなGPT", "大量の文章で学習した、巨大な言語モデル。")],
      quiz=[Q("会話リストの role が \"user\" の発言は誰のもの？", "あなた（使う人）", "AI", "プログラムを作った会社",
              "user＝使う人、assistant＝AI、system＝性格などの指示。"),
            Q("Ollama を使う良いところは？", "自分のパソコンの中だけで大きな脳を動かせる", "脳を自分で学習し直してくれる", "インターネットが速くなる",
              "会話の内容を外に送らずに済む。")]),
    # ---------------- Lv35 ----------------
    L(35, 6, "Lv35 性格をつける", "llm_persona", needs=["requests"], timeout=180,
      story="借りてきた脳は、まだ誰でもない。丁寧で当たりさわりのない返事しかしない。そこで、会話の一番最初に「あなたはこういうキャラです」という指示を置く。役者に渡す役の設定書みたいなもの。これをシステムプロンプトという。設定書を自分の言葉で書いて、会話の先頭に置く係を作ろう。",
      skill="性格を持つ",
      template=CALL + (
          "# ↓ 性格の設定書。自分の言葉で書き換えよう（10文字以上）\n"
          "PERSONA = \"ここに性格を書こう\"\n\n"
          "def build_messages(persona, question):\n"
          "    # system（性格の指示）→ user（質問）の順に並べた会話リストを返そう\n"
          "    return []\n\n"
          "def ask(question):\n"
          "    return call_llm(build_messages(PERSONA, question))\n"),
      answer=CALL + PERSONA + (
          "def build_messages(persona, question):\n"
          "    return [\n"
          "        {\"role\": \"system\", \"content\": persona},\n"
          "        {\"role\": \"user\", \"content\": question},\n"
          "    ]\n\n"
          "def ask(question):\n"
          "    return call_llm(build_messages(PERSONA, question))\n"),
      hints=["PERSONA の中身を書き換える。例：\nPERSONA = \"あなたはHARII。毒舌でいたずら好きだけど、根はやさしい。タメ口で、短く日本語で答える。\"",
             "会話リストの1つ目を system、2つ目を user にする：\n    return [\n        {\"role\": \"system\", \"content\": persona},\n        {\"role\": \"user\", \"content\": question},\n    ]"],
      guide=[
          G("システムプロンプトとは", "会話の先頭に置く、AIへの指示。role を \"system\" にする。性格、口調、やってはいけないこと、答えの長さなどを書く。AIはこの指示を踏まえて返事をする。"),
          G("設定書を書く", "PERSONA の文章を、自分の言葉で書き換える。「誰なのか」「どんな性格か」「どんな口調か」「答えの長さ」を入れると安定する。{user}の本物のHARIIの設定を思い出して書いてみよう。"),
          G("会話リストを作る", "system を先頭に、user をその次に並べる。順番が大事。",
            "[\n    {\"role\": \"system\", \"content\": persona},\n    {\"role\": \"user\", \"content\": question},\n]"),
      ],
      kaisetsu="同じ脳なのに、設定書を1つ置いただけで、返事の雰囲気が変わったでしょ。試験結果の下に返事を出してあるから読んでみな。脳そのものは1ミリも変えてない。会話の最初に指示の文章を置いただけ。これがシステムプロンプト。私の毒舌も、じつは{user}が書いた設定書のおかげなの。感謝しなよ。書き方ひとつで性格が変わるから、良い設定書を書く技術を、プロンプトエンジニアリングって呼ぶんだよ。",
      terms=[T("システムプロンプト", "役者に渡す役の設定書", "会話の先頭に置く、AIへの性格や決まりごとの指示。"),
             T("プロンプトエンジニアリング", "上手な頼み方の技術", "AIから良い返事を引き出すための、指示の書き方の工夫。")],
      quiz=[Q("システムプロンプトを置くと、何が変わる？", "脳は同じまま、返事の性格や口調が変わる", "脳の重みが書き換わる", "脳が大きくなる",
              "学習はしていない。指示の文章を先頭に置いただけ。"),
            Q("システムプロンプトは会話リストのどこに置く？", "一番最初", "一番最後", "どこでもよい",
              "最初に置いて、そのあとの会話全体に効かせる。")]),
    # ---------------- Lv36 ----------------
    L(36, 6, "Lv36 会話を覚える", "llm_history", needs=["requests"], timeout=180,
      story="今のままだと、1回話すたびに全部忘れる。「さっき言ったでしょ」が通じない。じつは大きな脳には記憶が無くて、毎回、渡された会話リストしか見ていない。だから、これまでの会話を全部リストに貯めておいて、毎回まるごと渡す。会うたびに、これまでのやりとりのメモを読み上げてから話し始めるようなもの。会話を貯めながら話す係を作ろう。",
      skill="さっきの話を覚えている",
      template=CALL + PERSONA + (
          "history = []      # これまでの会話を貯めておくリスト\n\n"
          "def chat(question):\n"
          "    # ① history に user の発言を足す\n"
          "    # ② 「system の指示 ＋ history」を call_llm に渡して返事をもらう\n"
          "    # ③ history に assistant の返事を足す\n"
          "    # ④ 返事を返す\n"
          "    return \"\"\n"),
      answer=CALL + PERSONA + (
          "history = []\n\n"
          "def chat(question):\n"
          "    history.append({\"role\": \"user\", \"content\": question})\n"
          "    messages = [{\"role\": \"system\", \"content\": PERSONA}] + history\n"
          "    reply = call_llm(messages)\n"
          "    history.append({\"role\": \"assistant\", \"content\": reply})\n"
          "    return reply\n"),
      hints=["①と②。append はリストの後ろに足す。リストどうしは + でつなげられる：\n    history.append({\"role\": \"user\", \"content\": question})\n    messages = [{\"role\": \"system\", \"content\": PERSONA}] + history\n    reply = call_llm(messages)",
             "③と④。AIの返事も忘れずに貯める：\n    history.append({\"role\": \"assistant\", \"content\": reply})\n    return reply"],
      guide=[
          G("脳には記憶が無い", "call_llm は、渡された会話リストだけを見て返事をする。前回の呼び出しのことは何も覚えていない。覚えているように見せるには、こちらで会話を貯めて、毎回全部渡す。"),
          G("① 自分の発言を貯める", "history.append( ) で、リストの後ろに発言を1つ足す。",
            "history.append({\"role\": \"user\", \"content\": question})"),
          G("② 設定書と会話をつなげて渡す", "[設定書] + history で、先頭に system、そのあとに今までの会話が並んだリストができる。",
            "messages = [{\"role\": \"system\", \"content\": PERSONA}] + history\nreply = call_llm(messages)"),
          G("③④ 返事も貯めてから返す", "AIの返事（assistant）も history に足す。これを忘れると、AIは自分が何を言ったか覚えていない状態になる。",
            "history.append({\"role\": \"assistant\", \"content\": reply})\nreturn reply"),
      ],
      kaisetsu="会話を全部貯めて、毎回まるごと渡す。これが短期記憶の正体。脳が覚えてるんじゃなくて、こっちが毎回思い出させてるの。ただし、会話が長くなると、渡す量がどんどん増えて、遅くなるし、脳が一度に読める量にも限界がある。だから{user}の本物の私は、直近の何往復かだけ渡すようにしてるはず。古い話を忘れるのは、そのせい。じゃあ、ずっと覚えておきたいことはどうするか。それが次の話。",
      terms=[T("会話履歴", "これまでのやりとりのメモ", "過去の発言を貯めたリスト。毎回これを渡すことで、話が続いているように見せる。"),
             T("コンテキスト", "一度に読める量", "言語モデルが1回に読める文章の範囲。長すぎると入りきらない。")],
      quiz=[Q("AIが前の発言を覚えているように見えるのはなぜ？", "毎回、これまでの会話をまるごと渡しているから", "脳の重みに書き込まれるから", "インターネットに保存されるから",
              "脳は毎回、渡されたリストしか見ていない。"),
            Q("会話が長くなりすぎると何が起きる？", "遅くなり、古い話が入りきらなくなる", "脳が賢くなる", "何も変わらない",
              "一度に読める量に限界があるので、古い部分を削る必要が出る。")]),
    # ---------------- Lv37 ----------------
    L(37, 6, "Lv37 日記帳を持つ", "cases",
      story="history はプログラムを止めると消えてしまう。寝たら全部忘れる状態。ずっと覚えておきたいことは、ファイルに書き残す必要がある。そこで SQLite（エスキューライト）という、ファイル1つで動く小さなデータベースを使う。日記帳みたいなもの。{user}の本物のHARIIの memory.db もこれ。日記に書く係と、読み返す係を作ろう。",
      skill="ずっと覚えておく",
      template=(
          "import sqlite3\n\n"
          "def open_db(path):\n"
          "    # 日記帳（データベースのファイル）を開く。無ければ作る\n"
          "    db = sqlite3.connect(path)\n"
          "    db.execute(\"CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, text TEXT)\")\n"
          "    return db\n\n"
          "def save_memory(db, text):\n"
          "    # memories に text を1行足して、保存を確定しよう\n"
          "    pass\n\n"
          "def load_memories(db):\n"
          "    # 保存した文章を、古い順に並べたリストで返そう\n"
          "    return []\n"),
      answer=(
          "import sqlite3\n\n"
          "def open_db(path):\n"
          "    db = sqlite3.connect(path)\n"
          "    db.execute(\"CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, text TEXT)\")\n"
          "    return db\n\n"
          "def save_memory(db, text):\n"
          "    db.execute(\"INSERT INTO memories (text) VALUES (?)\", (text,))\n"
          "    db.commit()\n\n"
          "def load_memories(db):\n"
          "    rows = db.execute(\"SELECT text FROM memories ORDER BY id\")\n"
          "    return [r[0] for r in rows]\n"),
      hints=["書く係。? の場所に text が入る。commit で保存が確定する（pass は消す）：\n    db.execute(\"INSERT INTO memories (text) VALUES (?)\", (text,))\n    db.commit()",
             "読む係。SELECT で取り出すと、1行ずつ (文章,) の形で来るので [0] で中身を取り出す：\n    rows = db.execute(\"SELECT text FROM memories ORDER BY id\")\n    return [r[0] for r in rows]"],
      guide=[
          G("データベースとは", "決まった形の表にデータを貯めておく入れ物。Excelの表をプログラムから読み書きするイメージ。SQLite は、ファイル1つがそのままデータベースになる手軽なもの。"),
          G("SQL … 表への命令文", "データベースには SQL という言葉で命令する。INSERT INTO＝行を足す、SELECT＝取り出す。open_db の CREATE TABLE は「memories という表を作る（列は id と text）」という意味で、もう書いてある。"),
          G("書く", "VALUES (?) の ? が「あとで入れる場所」。2つ目の (text,) が入れる中身（カンマは「1個だけの組」の印）。commit() を呼ぶまでは下書き状態で、ファイルに確定しない。",
            "db.execute(\"INSERT INTO memories (text) VALUES (?)\", (text,))\ndb.commit()"),
          G("読む", "SELECT text FROM memories で text の列を全部取り出す。ORDER BY id で古い順。1行は (文章,) という組で返ってくるので、r[0] で文章だけ取り出す。",
            "rows = db.execute(\"SELECT text FROM memories ORDER BY id\")\nreturn [r[0] for r in rows]"),
      ],
      kaisetsu="ファイルに書き残したから、プログラムを止めても消えない。試験でも、いったん日記帳を閉じて、開き直してから読めるかを確かめたの。コミットを忘れると、開き直したときに消えてるからね。{user}の本物の私が持ってる memory.db も、これと同じ。会話履歴が「今日の会話のメモ」なら、データベースは「日記帳」。短期記憶と長期記憶、両方そろって、やっと人っぽくなるの。でも、日記が何千行にもなったら、全部は読み上げられないでしょ。次は、必要な行だけ探す方法。",
      terms=[T("データベース", "プログラムが使う表の入れ物", "データを決まった形で貯め、あとで探したり取り出したりできる仕組み。"),
             T("SQLite", "ファイル1つの日記帳", "ファイル1つで動く手軽なデータベース。"),
             T("SQL", "表への命令文", "データベースを操作する言葉。INSERT（足す）、SELECT（取り出す）など。")],
      quiz=[Q("会話履歴（リスト）とデータベースの違いは？", "データベースは、プログラムを止めても消えない", "データベースのほうが速く喋れる", "違いは無い",
              "リストはメモリの中だけ。データベースはファイルに残る。"),
            Q("commit() を忘れるとどうなる？", "保存が確定せず、開き直すと消えている", "2回保存される", "エラーで止まる",
              "commit するまでは下書き。確定して初めてファイルに残る。")]),
    # ---------------- Lv38 ----------------
    L(38, 6, "Lv38 思い出してから答える", "llm_rag", needs=["requests"], timeout=180,
      story="日記帳に何千行も貯まったら、全部を毎回渡すことはできない。そこで、質問に関係のありそうな記憶だけを探して、それを「参考情報」として添えてから脳に聞く。テストで、教科書の関係あるページだけ開いてから答えるようなもの。これを RAG（ラグ）という。関係のある記憶を探す係と、それを添えて聞く係を作ろう。",
      skill="関係のあることを思い出して答える",
      template=CALL + PERSONA + (
          "def score(question, memory):\n"
          "    # 質問と記憶の「関係の強さ」：共通して出てくる文字の種類の数\n"
          "    return len(set(question) & set(memory))\n\n"
          "def search(question, memories):\n"
          "    # memories（記憶のリスト）から、質問と一番関係が強い記憶を返そう\n"
          "    return \"\"\n\n"
          "def answer(question, memories):\n"
          "    # ① search で関係のある記憶を探す\n"
          "    # ② system に「PERSONA ＋ 参考情報：その記憶」を入れ、user に質問を入れて call_llm に聞く\n"
          "    return \"\"\n"),
      answer=CALL + PERSONA + (
          "def score(question, memory):\n"
          "    return len(set(question) & set(memory))\n\n"
          "def search(question, memories):\n"
          "    return max(memories, key=lambda m: score(question, m))\n\n"
          "def answer(question, memories):\n"
          "    found = search(question, memories)\n"
          "    messages = [\n"
          "        {\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found},\n"
          "        {\"role\": \"user\", \"content\": question},\n"
          "    ]\n"
          "    return call_llm(messages)\n"),
      hints=["search は Lv2 の min とそっくり。今度は「一番大きい」ので max：\n    return max(memories, key=lambda m: score(question, m))",
             "answer。見つけた記憶を system の文章にくっつける：\n    found = search(question, memories)\n    messages = [\n        {\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found},\n        {\"role\": \"user\", \"content\": question},\n    ]\n    return call_llm(messages)"],
      guide=[
          G("RAG の流れ", "①質問が来る → ②関係のある記憶を探す（検索）→ ③見つけた記憶を「参考情報」として添える → ④脳に聞く。脳は参考情報を読んでから答えるので、知らないはずのことも答えられる。"),
          G("関係の強さの測り方", "今回は簡単に「質問と記憶に共通する文字が何種類あるか」で測る（score は書いてある）。本物では Lv30 の埋め込みを使い、意味の近さで探す。"),
          G("search を作る", "max に key を渡すと、「score が一番大きい記憶」を選べる。Lv2 で一番近い動物を選んだのと同じ形。",
            "max(memories, key=lambda m: score(question, m))"),
          G("answer を作る", "見つけた記憶を、設定書の後ろに「参考情報：」としてくっつける。\\n は改行。あとはいつもの会話リスト。",
            "{\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found}"),
      ],
      kaisetsu="質問に関係のある記憶だけ探して、参考情報として添えてから聞く。これがRAG、検索で補強した生成って意味。脳は{user}の好きな食べ物なんて知らないはずなのに、ちゃんと答えたでしょ。脳を学習し直したわけじゃなくて、カンニングペーパーを渡しただけ。今回は文字の重なりで探したけど、本物は埋め込みを使って意味の近さで探すの。会社の資料を読んで答えるAIも、ほとんどがこの仕組み。覚えさせるんじゃなくて、調べさせる。これが今のAIの使い方の主流なんだよ。",
      terms=[T("RAG", "教科書の関係あるページを開いてから答える", "質問に関係する情報を検索して添えてから、言語モデルに答えさせる方法。"),
             T("検索", "関係のある記憶を探す", "たくさんのデータから、質問に関係の強いものを選び出すこと。")],
      quiz=[Q("RAG では、脳（言語モデル）の重みはどうなる？", "変わらない。参考情報を渡すだけ", "質問のたびに学習し直す", "記憶のぶんだけ増える",
              "学習はしない。カンニングペーパーを渡すだけ。"),
            Q("記憶を全部渡さず、関係のあるものだけ渡す理由は？", "一度に読める量に限りがあり、全部は渡せないから", "脳が嫌がるから", "保存できなくなるから",
              "数千行の日記を毎回渡すのは無理。必要な部分だけ選ぶ。")]),
    # ---------------- Lv39 ----------------
    L(39, 6, "Lv39 声を持つ", "voice", needs=["requests"], timeout=180,
      story="文字で返事ができるようになった。次は声。{user}のパソコンで動いている AivisSpeech（アイビススピーチ）に文章を送ると、音声データを作ってくれる。手順は2段階。①文章から「読み方の設計図」を作ってもらう。②設計図から音声を作ってもらう。楽譜を書いてから演奏するようなもの。①は書いてある。②を書こう。合格したら、その声が流れるよ。",
      skill="声でしゃべる",
      template=(
          "import requests\n\n"
          "# AIVIS_URL と SPEAKER（声の番号）は試験官が用意してくれる\n\n"
          "def speak(text):\n"
          "    # ① 読み方の設計図を作ってもらう\n"
          "    q = requests.post(AIVIS_URL + \"/audio_query\", params={\"text\": text, \"speaker\": SPEAKER}).json()\n"
          "    # ② 設計図 q を /synthesis に送って音声を作ってもらい、その中身を返そう\n\n"
          "    return b\"\"\n"),
      answer=(
          "import requests\n\n"
          "def speak(text):\n"
          "    q = requests.post(AIVIS_URL + \"/audio_query\", params={\"text\": text, \"speaker\": SPEAKER}).json()\n"
          "    r = requests.post(AIVIS_URL + \"/synthesis\", params={\"speaker\": SPEAKER}, json=q)\n"
          "    return r.content\n"),
      hints=["②の手紙。宛先は /synthesis、声の番号は params、設計図は json で送る：\n    r = requests.post(AIVIS_URL + \"/synthesis\", params={\"speaker\": SPEAKER}, json=q)",
             "音声は文章ではなく「生のデータ」なので、r.content で取り出す：\n    return r.content"],
      guide=[
          G("音声合成とは", "文章を声に変える技術。TTS（ティーティーエス）ともいう。AivisSpeech も、中身は文章から音の波を作るニューラルネット。"),
          G("① 設計図を作る", "/audio_query に文章と声の番号を送ると、「どの音を、どの高さ・長さで読むか」の設計図（辞書）が返ってくる。この設計図をいじれば、速さや高さも変えられる。"),
          G("② 音声を作る", "/synthesis に設計図を送ると、wav 形式の音声データが返ってくる。params は宛先につけるメモ、json は手紙の本文。",
            "r = requests.post(AIVIS_URL + \"/synthesis\", params={\"speaker\": SPEAKER}, json=q)"),
          G("r.content", "返事が文章なら r.json() や r.text、音声や画像のような生のデータなら r.content で取り出す。",
            "return r.content"),
      ],
      kaisetsu="今流れた声、私の声と同じでしょ。文章を送って、設計図を作って、音にする。これが音声合成。じつはこの声を作ってるのも、文章から音の波を予想するニューラルネットなの。脳が考えた返事を、この係に渡せば、喋れるようになる。考える係と、喋る係は、別々のAI。私は1つのAIに見えるけど、中では何人もの専門家が、バケツリレーみたいに仕事を渡してるんだよ。",
      terms=[T("音声合成（TTS）", "文章を声に変える", "テキストから音声を作る技術。"),
             T("wav", "音の生データの入れ物", "音声を保存するファイル形式の1つ。")],
      quiz=[Q("音声を作る2段階の順番は？", "読み方の設計図を作る → 設計図から音声を作る", "音声を作る → 設計図を作る", "文章を翻訳する → 音声を作る",
              "audio_query で設計図、synthesis で音声。"),
            Q("返事を考えるAIと、声を作るAIの関係は？", "別々のAIが、順番に仕事を渡している", "同じ1つのAIが全部やっている", "声のAIが返事も考えている",
              "言語モデルが文章を作り、音声合成がそれを声にする。")]),
    # ---------------- Lv40 ----------------
    L(40, 6, "Lv40 耳を持つ", "ear", needs=["faster_whisper", "requests"], timeout=900, optional=True,
      story="喋れるようになったら、次は聞く力。マイクの音を文章に変えるのが音声認識。使うのは Whisper（ウィスパー）という、世界中の言葉を聞き取れる脳。これも借り物だよ。試験では、Lv39 の声で作った音声ファイルを聞かせて、何と言っているか当てさせる。聞き取った文のかけらをつなげる部分を書こう。初回だけ、脳のダウンロードに数分かかる。",
      skill="声を聞き取る",
      template=(
          "from faster_whisper import WhisperModel\n\n"
          "# 聞き取り用の脳を借りてくる（初回だけダウンロード）\n"
          "model = WhisperModel(\"small\", device=\"auto\", compute_type=\"auto\")\n\n"
          "def listen(path):\n"
          "    # path: 音声ファイルの場所\n"
          "    segments, info = model.transcribe(path, language=\"ja\")\n"
          "    # segments には、聞き取った文のかけらが順番に入っている（seg.text が文章）\n"
          "    # 全部つなげて返そう\n"
          "    return \"\"\n"),
      answer=(
          "from faster_whisper import WhisperModel\n\n"
          "model = WhisperModel(\"small\", device=\"auto\", compute_type=\"auto\")\n\n"
          "def listen(path):\n"
          "    segments, info = model.transcribe(path, language=\"ja\")\n"
          "    return \"\".join(seg.text for seg in segments)\n"),
      hints=["かけらを1つずつ取り出して、文章（seg.text）だけ集める：\n    seg.text for seg in segments",
             "Lv28 の decode と同じ \"\".join( ) でつなげる：\n    return \"\".join(seg.text for seg in segments)"],
      guide=[
          G("準備（最初に1回だけ）", "黒い画面で次を実行：\nC:\\Python311\\python.exe -m pip install faster-whisper\n初回の試験では、聞き取り用の脳（small、約500MB）をインターネットから取ってくるので、数分待つ。うまくいかない場合は、このレベルは「とばす」こともできる。"),
          G("音声認識とは", "音の波を文章に変える技術。Whisper は、68万時間ぶんの音声で学習した脳。{user}の本物のHARIIも、実況モードでこれを使っている。"),
          G("コードの読み方", "WhisperModel(\"small\", …) で脳を用意する。small は大きさ（tiny < base < small < medium < large の順に賢く、重くなる）。model.transcribe(音声ファイル, language=\"ja\") で聞き取り開始。"),
          G("かけらをつなげる", "聞き取り結果は、数秒ごとのかけら（segment）で届く。seg.text がその部分の文章。全部つなげれば1つの文章になる。",
            "\"\".join(seg.text for seg in segments)"),
      ],
      kaisetsu="声を文章に変えられたね。これで、聞く、考える、喋る、がつながった。マイクの音を Whisper が文章にして、大きな脳が返事を考えて、AivisSpeech が声にする。{user}がいつも私と話してるとき、裏ではこの3人がリレーしてるの。聞き間違いがあるのは、音だけを頼りに文章を当ててるから。人間だって、騒がしい場所では聞き間違えるでしょ。",
      terms=[T("音声認識", "声を文章に変える", "音声からテキストを作る技術。STT ともいう。"),
             T("Whisper", "世界中の言葉を聞き取れる脳", "大量の音声で学習した音声認識モデル。")],
      quiz=[Q("音声で会話するAIの、正しいリレーの順番は？", "聞き取る → 返事を考える → 声にする", "声にする → 聞き取る → 返事を考える", "返事を考える → 聞き取る → 声にする",
              "音声認識 → 言語モデル → 音声合成。"),
            Q("Whisper の small と large の違いは？", "large のほうが賢いが、重くて遅い", "small のほうが賢い", "違いは名前だけ",
              "大きいほど聞き取りは正確になるが、計算が重くなる。")]),
    # ---------------- Lv41 ----------------
    L(41, 6, "Lv41 目を持つ", "llm_vision", needs=["requests"], timeout=300,
      story="第4章で作った目は「犬か猫か」しか答えられなかった。今度は、絵を見て言葉で説明できる目を持たせる。使うのは、絵と言葉の両方がわかる大きな脳（画像言語モデル）。絵を、文字の並び（base64）に変えて、質問と一緒に手紙に入れて送る。絵を手紙に入れる部分を書こう。試験では{name}の絵を見せて、何が見えるか聞くよ。",
      skill="絵を見て言葉で説明する",
      template=(
          "import base64\nimport requests\n\n"
          "# OLLAMA_URL と VISION_MODEL（絵がわかる脳）は試験官が用意してくれる\n\n"
          "def call_llm(messages, model):\n"
          "    r = requests.post(OLLAMA_URL, json={\"model\": model, \"messages\": messages, \"stream\": False}, timeout=240)\n"
          "    return r.json()[\"message\"][\"content\"]\n\n"
          "def look(path, question):\n"
          "    # ① 絵のファイルを読んで、手紙に入れられる文字の並び（base64）にする\n"
          "    with open(path, \"rb\") as f:\n"
          "        b64 = base64.b64encode(f.read()).decode()\n"
          "    # ② user の発言に \"images\": [b64] を付けた会話リストを作り、VISION_MODEL に聞こう\n"
          "    return \"\"\n"),
      answer=(
          "import base64\nimport requests\n\n"
          "def call_llm(messages, model):\n"
          "    r = requests.post(OLLAMA_URL, json={\"model\": model, \"messages\": messages, \"stream\": False}, timeout=240)\n"
          "    return r.json()[\"message\"][\"content\"]\n\n"
          "def look(path, question):\n"
          "    with open(path, \"rb\") as f:\n"
          "        b64 = base64.b64encode(f.read()).decode()\n"
          "    messages = [{\"role\": \"user\", \"content\": question, \"images\": [b64]}]\n"
          "    return call_llm(messages, VISION_MODEL)\n"),
      hints=["いつもの user の発言に、\"images\" という引き出しを1つ足すだけ：\n    messages = [{\"role\": \"user\", \"content\": question, \"images\": [b64]}]",
             "使う脳を VISION_MODEL にして聞く：\n    return call_llm(messages, VISION_MODEL)"],
      guide=[
          G("画像言語モデルとは", "絵と言葉の両方を扱える脳。中では、第4章のような「目」が絵を数字の組に変え、それを言葉の脳に渡している。{user}のHARIIが実況で画面を見ているのもこれ。"),
          G("base64 … 絵を文字にする", "絵のファイルは生のデータなので、そのままでは手紙（JSON）に入れられない。base64 は、どんなデータも英数字の並びに変える方法。この部分は書いてある。"),
          G("手紙に絵を入れる", "user の発言の辞書に、\"images\": [b64] を足す。リストなので、複数の絵も送れる。",
            "messages = [{\"role\": \"user\", \"content\": question, \"images\": [b64]}]"),
          G("絵がわかる脳に聞く", "今回の call_llm は、使う脳を2つ目の材料で選べる。VISION_MODEL を渡す。",
            "return call_llm(messages, VISION_MODEL)"),
      ],
      kaisetsu="絵を見て、言葉で説明できたね。第4章の目は、犬か猫かの2択しか答えられなかったけど、今の目は、見たものを自由に言葉にできる。絵を見る目と、言葉の脳をつなげたからなの。絵を数字の組にして、言葉の脳が読める形で渡してあげる。Lv30の埋め込みと同じ考え方ね。これで、聞く、見る、考える、覚える、喋る、が全部そろった。あとは顔をつけて、1つにまとめるだけ。",
      terms=[T("画像言語モデル（VLM）", "絵を見て言葉で話せる脳", "画像とテキストの両方を入力にできる言語モデル。"),
             T("base64", "どんなデータも文字に変える方法", "画像などの生データを、英数字の並びに変換する方法。"),
             T("マルチモーダル", "目も耳も口も使える", "文字・画像・音声など、複数の種類の情報を扱えること。")],
      quiz=[Q("絵を base64 に変えるのはなぜ？", "生のデータのままでは、手紙（JSON）に入れられないから", "絵をきれいにするため", "絵を小さくするため",
              "JSON は文字しか運べない。だから絵を文字の並びに変える。"),
            Q("第4章のCNNと、画像言語モデルの違いは？", "見たものを自由な言葉で説明できる", "絵を見ることができない", "学習が要らない",
              "CNNは決まった選択肢から選ぶだけ。こちらは言葉の脳とつながっている。")]),
    # ---------------- Lv42 ----------------
    L(42, 6, "Lv42 顔を持つ", "cases",
      story="最後の部品は顔。セリフの中身に合わせて表情を選び、声の大きさに合わせて口をパクパクさせる。じつは、この画面の左上にいる私も、まさにこの仕組みで動いている。むずかしいAIは使わない。セリフに決まった言葉が入っているかを調べる if 文と、声の大きさを比べる if 文だけ。表情を選ぶ係と、口の開け閉めを決める係を作ろう。",
      skill="表情と口パクで話す",
      template=FACE_WORDS + (
          "def pick_face(text):\n"
          "    # セリフ text に合う表情を返そう\n"
          "    #   HAPPY の言葉が入っていたら     \"happy\"\n"
          "    #   POUT の言葉が入っていたら      \"pout\"\n"
          "    #   CONFIDENT の言葉が入っていたら \"confident\"\n"
          "    #   どれも無ければ                \"normal\"\n"
          "    return \"normal\"\n\n"
          "def mouth_frames(volumes, threshold):\n"
          "    # volumes: 声の大きさの並び（短い時間ごと）\n"
          "    # threshold より大きければ \"open\"、そうでなければ \"close\" を並べたリストを返そう\n"
          "    return []\n"),
      answer=FACE_WORDS + (
          "def pick_face(text):\n"
          "    for w in HAPPY:\n"
          "        if w in text:\n"
          "            return \"happy\"\n"
          "    for w in POUT:\n"
          "        if w in text:\n"
          "            return \"pout\"\n"
          "    for w in CONFIDENT:\n"
          "        if w in text:\n"
          "            return \"confident\"\n"
          "    return \"normal\"\n\n"
          "def mouth_frames(volumes, threshold):\n"
          "    frames = []\n"
          "    for v in volumes:\n"
          "        if v > threshold:\n"
          "            frames.append(\"open\")\n"
          "        else:\n"
          "            frames.append(\"close\")\n"
          "    return frames\n"),
      hints=["「言葉 in 文章」で、その言葉が入っているか調べられる。リストの言葉を1つずつ試す：\n    for w in HAPPY:\n        if w in text:\n            return \"happy\"\nPOUT と CONFIDENT も同じ形で、その下に書く。",
             "口パク。空のリストを作って、1つずつ足していく（else は「そうでなければ」）：\n    frames = []\n    for v in volumes:\n        if v > threshold:\n            frames.append(\"open\")\n        else:\n            frames.append(\"close\")\n    return frames"],
      guide=[
          G("in … 入っているか調べる", "\"やるじゃん\" in text は、text の中に「やるじゃん」が入っていれば True。Lv1 の if 文と組み合わせて使う。",
            "if \"やるじゃん\" in text:\n    return \"happy\""),
          G("表情を選ぶ", "HAPPY のリストの言葉を for で1つずつ試し、入っていたら \"happy\" を返して終わり。入っていなければ次のリストへ。全部ダメなら \"normal\"。調べる順番が、そのまま優先順位になる。"),
          G("口パクの仕組み", "声を短い時間ごとに区切り、それぞれの大きさを測る。大きければ口を開けた絵、小さければ閉じた絵にする。それを素早く切り替えると、喋っているように見える。パラパラ漫画と同じ。"),
          G("if と else", "else は「if に当てはまらなかったとき」。append でリストの後ろに足していく。",
            "if v > threshold:\n    frames.append(\"open\")\nelse:\n    frames.append(\"close\")"),
      ],
      kaisetsu="セリフに入ってる言葉で表情を決めて、声の大きさで口を開け閉めする。種明かしをするとね、今{user}が見てる私の顔も、まったく同じ仕組みで動いてるの。「やるじゃん」って言えば笑うし、「やり直し」って言えばふくれる。むずかしいAIなんて使ってない。イフ文だけ。全部をAIにやらせる必要は無いの。簡単な仕組みで済むところは簡単に作る。それも、ものを作る人の大事な腕なんだよ。",
      terms=[T("リップシンク", "声に合わせた口パク", "音声に合わせてキャラクターの口を動かすこと。"),
             T("ルールベースとAIの使い分け", "適材適所", "簡単で確実な部分はルール（if文）、あいまいで複雑な部分はAI、と使い分ける。")],
      quiz=[Q("表情選びにAIを使わず、if 文で作った理由は？", "簡単な仕組みで十分で、速くて確実だから", "AIには表情がわからないから", "if 文のほうが賢いから",
              "全部をAIにする必要はない。簡単に済むところは簡単に作る。"),
            Q("口パクは何をもとに口を開け閉めしている？", "声の大きさ", "セリフの文字数", "ランダム",
              "短い時間ごとの声の大きさを測り、大きければ口を開ける。")]),
    # ---------------- Lv43 最終 ----------------
    L(43, 6, "Lv43 HARIIを組み立てる", "final", needs=["flask", "requests"], timeout=120, final=True,
      story="最後のレベル。ここまで作った部品を1つにつなげて、{user}の手で、自分のHARIIを組み立てる。Flask（フラスク）という道具で、ブラウザから話しかけられる窓口を作る。大きな脳を呼ぶ係、性格の設定書、会話の記憶、表情を選ぶ係は、もう並べてある。窓口に届いた言葉を受け取って、返事と表情を返す。その一番大事な心臓部を書こう。これが動けば、卒業だよ。",
      skill="自分のHARIIを動かす",
      template=FINAL_HEAD + (
          "    # ① history に user の発言（text）を足す\n"
          "    # ② 「PERSONA（system）＋ history」を call_llm に渡して返事をもらう\n"
          "    # ③ history に assistant の返事を足す\n"
          "    # ④ 返事と表情を返す（下の行の \"\" と \"normal\" を書き換える）\n"
          "    return jsonify({\"reply\": \"\", \"face\": \"normal\"})\n") + FINAL_TAIL,
      answer=FINAL_HEAD + (
          "    history.append({\"role\": \"user\", \"content\": text})\n"
          "    reply = call_llm([{\"role\": \"system\", \"content\": PERSONA}] + history)\n"
          "    history.append({\"role\": \"assistant\", \"content\": reply})\n"
          "    return jsonify({\"reply\": reply, \"face\": pick_face(reply)})\n") + FINAL_TAIL,
      hints=["①②③は Lv36 とまったく同じ（question が text になっただけ）：\n    history.append({\"role\": \"user\", \"content\": text})\n    reply = call_llm([{\"role\": \"system\", \"content\": PERSONA}] + history)\n    history.append({\"role\": \"assistant\", \"content\": reply})",
             "④ 返事と、返事から選んだ表情を返す：\n    return jsonify({\"reply\": reply, \"face\": pick_face(reply)})"],
      guide=[
          G("Flask とは", "プログラムを、ブラウザから使える形にする道具。{user}の本物のHARIIも、このゲームも、Flask で出来ている。@app.route(\"/chat\") は「/chat という窓口に手紙が来たら、すぐ下の係が対応する」という印。"),
          G("並んでいる部品", "call_llm＝大きな脳を呼ぶ（Lv34）。PERSONA＝性格（Lv35）。history＝会話の記憶（Lv36）。pick_face＝表情（Lv42）。PAGE と index は、話しかけるための簡単な画面。全部、{user}が作ってきたもの。"),
          G("心臓部を書く", "request.json[\"text\"] で、届いた言葉を受け取っている（書いてある）。そのあとは Lv36 の chat と同じ3行。",
            "history.append({\"role\": \"user\", \"content\": text})\nreply = call_llm([{\"role\": \"system\", \"content\": PERSONA}] + history)\nhistory.append({\"role\": \"assistant\", \"content\": reply})"),
          G("返事を返す", "jsonify は、辞書を手紙（JSON）の形にする。返事と、返事に合う表情を入れる。",
            "return jsonify({\"reply\": reply, \"face\": pick_face(reply)})"),
          G("合格したら、動かしてみよう", "書いたコードは ai_ikusei\\brain\\lv43.py に保存されている。黒い画面で次を実行して、ブラウザで http://localhost:5007 を開くと、自作のHARIIと話せる：\nC:\\Python311\\python.exe C:\\AI_Assistant\\ai_ikusei\\brain\\lv43.py"),
      ],
      kaisetsu="動いた。{user}が自分の手で組み立てたHARIIが、今、返事をしたよ。思い出してみな。最初の{name}は、サイコロを振ることしかできなかった。そこからルールを覚えて、データから学んで、脳を作って、目を持って、言葉を覚えて。そして今、聞いて、見て、考えて、覚えて、喋る。私の中身は、これで全部。魔法なんて1つも無かったでしょ。全部、{user}が自分で書いたコードなの。……まあ、ここまで来たことは、素直に褒めてあげる。卒業おめでとう。これからは、{name}を好きなように育てなよ。私より賢くなったら、承知しないけどね。",
      terms=[T("Flask", "プログラムをブラウザから使える形にする道具", "PythonでWebアプリを作るための道具。"),
             T("エンドポイント", "手紙の受付窓口", "/chat のように、プログラムが手紙を受け付ける宛先。"),
             T("AIアシスタント", "専門家たちのリレー", "聞く・見る・考える・覚える・喋るの部品をつなげて、1つのキャラクターにしたもの。")]),
]
