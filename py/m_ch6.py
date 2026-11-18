# -*- coding: utf-8 -*-
"""スマホ版 第6章の差し替え：大きな脳・声・耳が無くても、HARIIの仕組みを全部自分で作る"""
from lesson_util import L, Q, T, G

MOCK = (
    "def call_llm(messages):\n"
    "    # スマホ版の「まねっこ脳」：本物の大きな脳のかわりに、届いた手紙の中身を報告するだけ\n"
    "    # （パソコン版では、ここで Ollama の大きな脳に手紙を送って、本物の返事をもらう）\n"
    "    roles = \" → \".join(m[\"role\"] for m in messages)\n"
    "    return \"（まねっこ脳）\" + str(len(messages)) + \"通の手紙を受け取ったよ：\" + roles\n\n"
)
PERSONA = "PERSONA = \"あなたはHARII。毒舌でいたずら好きだけど、根はやさしい。タメ口で、短く日本語で答える。\"\n\n"

SIM = (
    "import numpy as np\n\n"
    "def make_vocab(texts):\n"
    "    # 出てくる文字の名簿（Lv28 と同じ）\n"
    "    return sorted(set(\"\".join(texts)))\n\n"
)
SIM_FUNC = (
    "def similarity(a, b):\n"
    "    # 似ている度（Lv30 のコサイン類似度）。どちらかが空なら0\n"
    "    na, nb = np.linalg.norm(a), np.linalg.norm(b)\n"
    "    if na == 0 or nb == 0:\n"
    "        return 0.0\n"
    "    return float(a @ b / (na * nb))\n\n"
)
TO_VEC_ANS = (
    "def to_vec(text, vocab):\n"
    "    v = np.zeros(len(vocab))\n"
    "    for ch in text:\n"
    "        if ch in vocab:\n"
    "            v[vocab.index(ch)] += 1\n"
    "    return v\n\n"
)

FINAL_PARTS = SIM + TO_VEC_ANS + SIM_FUNC + (
    "def search_best(question, memory):\n"
    "    # 記憶の中から一番似ているものと、その似ている度を返す（Lv39 で作ったもの）\n"
    "    if not memory:\n"
    "        return \"\", 0.0\n"
    "    vocab = make_vocab(memory + [question])\n"
    "    q = to_vec(question, vocab)\n"
    "    best = max(memory, key=lambda m: similarity(q, to_vec(m, vocab)))\n"
    "    return best, similarity(q, to_vec(best, vocab))\n\n"
    "def pick_face(text):\n"
    "    # 表情を選ぶ係（Lv42 で作ったもの）\n"
    "    for w in [\"やるじゃん\", \"すごい\", \"覚えた\"]:\n"
    "        if w in text:\n"
    "            return \"happy\"\n"
    "    for w in [\"知らない\", \"ダメ\"]:\n"
    "        if w in text:\n"
    "            return \"pout\"\n"
    "    for w in [\"たしか\", \"当然\"]:\n"
    "        if w in text:\n"
    "            return \"confident\"\n"
    "    return \"normal\"\n\n"
    "memory = []      # ハリリの記憶帳\n\n"
)

LESSONS_M6 = [
    # ---------------- Lv34 ----------------
    L(34, 6, "Lv34 大きな脳へ手紙を書く", "m",
      story="いよいよ最終章。本物のHARIIは、Ollama（オラマ）という「大きな脳の貸し出し窓口」に手紙を送って、返事をもらっている。手紙はJSON（ジェイソン）という決まった形で書く。スマホには大きな脳が入らないので、この章では「手紙の書き方」と「HARIIの仕組み」を全部自分で作る。まずは、大きな脳へ送る手紙を作る係と、届いた返事の手紙から文章を取り出す係を書こう。",
      skill="大きな脳と手紙をやりとりする",
      template=(
          "MODEL = \"qwen2.5:7b\"     # 使う脳の名前\n\n"
          "def make_request(question):\n"
          "    # 大きな脳へ送る手紙（辞書）を作って返そう\n"
          "    #   \"model\"   : 使う脳の名前（MODEL）\n"
          "    #   \"messages\": 会話のリスト（question を user の発言にしたもの1つ）\n"
          "    #   \"stream\"  : False（返事を一度にまとめてもらう）\n"
          "    return {}\n\n"
          "def read_reply(resp):\n"
          "    # 大きな脳から届いた返事の手紙（辞書）から、返事の文章を取り出そう\n"
          "    # resp の例：{\"model\": \"qwen2.5:7b\", \"message\": {\"role\": \"assistant\", \"content\": \"こんにちは\"}, \"done\": True}\n"
          "    return \"\"\n"),
      answer=(
          "MODEL = \"qwen2.5:7b\"\n\n"
          "def make_request(question):\n"
          "    return {\n"
          "        \"model\": MODEL,\n"
          "        \"messages\": [{\"role\": \"user\", \"content\": question}],\n"
          "        \"stream\": False,\n"
          "    }\n\n"
          "def read_reply(resp):\n"
          "    return resp[\"message\"][\"content\"]\n"),
      hints=["手紙は辞書。会話は「誰が（role）」「何を言ったか（content）」の辞書のリスト：\n    return {\n        \"model\": MODEL,\n        \"messages\": [{\"role\": \"user\", \"content\": question}],\n        \"stream\": False,\n    }",
             "返事は引き出しの中にもう1つ引き出しがある形。2回開ける：\n    return resp[\"message\"][\"content\"]"],
      guide=[
          G("API と JSON", "プログラムどうしは、決まった形の手紙（JSON）でやりとりする。この窓口のことを API という。JSON の中身は、Python の辞書とリストとほぼ同じ形。"),
          G("会話の形", "会話は、発言の辞書を並べたリスト。role は誰の発言か（user＝あなた、assistant＝AI、system＝性格などの指示）、content は発言の中身。",
            "[{\"role\": \"user\", \"content\": \"こんにちは\"}]"),
          G("送る手紙", "どの脳を使うか（model）、会話（messages）、返事の受け取り方（stream）を辞書にまとめる。本物のHARIIは、これを requests.post で Ollama に送っている。"),
          G("届く返事", "返事は {\"message\": {\"role\": \"assistant\", \"content\": \"返事\"}, …} という形。resp[\"message\"] で内側の辞書、さらに [\"content\"] で文章が取り出せる。",
            "resp[\"message\"][\"content\"]"),
      ],
      kaisetsu="大きな脳への手紙の書き方と、返事の読み方を覚えたね。私が{user}と話すとき、裏では毎回この形の手紙が行ったり来たりしてるの。大きな脳の中身は、第5章で作った言語モデルと同じ仕組みで、重みが70億個あるだけ。それを動かすのは大変だけど、使う側は手紙を書くだけでいい。ここからは、この手紙に性格と記憶をつけて、私に仕上げていくよ。スマホでは本物の脳のかわりに「まねっこ脳」が返事をするけど、手紙の中身はパソコン版とまったく同じだからね。",
      terms=[T("API", "プログラムどうしの窓口", "決まった形で手紙を出すと、決まった形で返事が来る仕組み。"),
             T("JSON", "プログラム用の手紙の書式", "辞書とリストで中身を表す、データのやりとりの書き方。"),
             T("LLM（大規模言語モデル）", "とても大きな言語モデル", "大量の文章で学習した巨大な言語モデル。HARIIの頭脳。")],
      quiz=[Q("会話リストの role が \"user\" の発言は誰のもの？", "あなた（使う人）", "AI", "プログラムを作った会社",
              "user＝使う人、assistant＝AI、system＝性格などの指示。"),
            Q("返事の文章を取り出す正しい書き方は？", "resp[\"message\"][\"content\"]", "resp[\"content\"]", "resp[\"user\"]",
              "返事の文章は message の引き出しの中の content に入っている。")]),
    # ---------------- Lv35 ----------------
    L(35, 6, "Lv35 性格をつける", "m",
      story="大きな脳は、まだ誰でもない。丁寧で当たりさわりのない返事しかしない。そこで、会話の一番最初に「あなたはこういうキャラです」という指示を置く。役者に渡す役の設定書みたいなもの。これをシステムプロンプトという。設定書を自分の言葉で書いて、会話の先頭に置く係を作ろう。",
      skill="性格を持つ",
      template=MOCK + (
          "# ↓ 性格の設定書。自分の言葉で書き換えよう（10文字以上）\n"
          "PERSONA = \"ここに性格を書こう\"\n\n"
          "def build_messages(persona, question):\n"
          "    # system（性格の指示）→ user（質問）の順に並べた会話リストを返そう\n"
          "    return []\n\n"
          "def ask(question):\n"
          "    return call_llm(build_messages(PERSONA, question))\n"),
      answer=MOCK + PERSONA + (
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
          G("設定書を書く", "PERSONA の文章を、自分の言葉で書き換える。「誰なのか」「どんな性格か」「どんな口調か」「答えの長さ」を入れると安定する。"),
          G("会話リストを作る", "system を先頭に、user をその次に並べる。順番が大事。",
            "[\n    {\"role\": \"system\", \"content\": persona},\n    {\"role\": \"user\", \"content\": question},\n]"),
          G("まねっこ脳", "call_llm は、スマホ版では「受け取った手紙の通数と、誰の発言が並んでいるか」を報告するだけ。パソコン版では、同じ手紙が本物の大きな脳に届く。"),
      ],
      kaisetsu="設定書を1つ置くだけで、同じ脳が別人みたいな話し方になるの。脳そのものは1ミリも変えずに、会話の最初に指示の文章を置くだけ。これがシステムプロンプト。私の毒舌も、じつは{user}が書いた設定書のおかげなの。感謝しなよ。書き方ひとつで性格が変わるから、良い設定書を書く技術を、プロンプトエンジニアリングって呼ぶんだよ。パソコン版のLv35で、同じ設定書を本物の脳に送ってみると、違いがよくわかるからね。",
      terms=[T("システムプロンプト", "役者に渡す役の設定書", "会話の先頭に置く、AIへの性格や決まりごとの指示。"),
             T("プロンプトエンジニアリング", "上手な頼み方の技術", "AIから良い返事を引き出すための、指示の書き方の工夫。")],
      quiz=[Q("システムプロンプトを置くと、何が変わる？", "脳は同じまま、返事の性格や口調が変わる", "脳の重みが書き換わる", "脳が大きくなる",
              "学習はしていない。指示の文章を先頭に置いただけ。"),
            Q("システムプロンプトは会話リストのどこに置く？", "一番最初", "一番最後", "どこでもよい",
              "最初に置いて、そのあとの会話全体に効かせる。")]),
    # ---------------- Lv36 ----------------
    L(36, 6, "Lv36 会話を覚える", "m",
      story="大きな脳には、じつは記憶が無い。毎回、渡された会話リストしか見ていない。だから「さっき言ったでしょ」が通じない。覚えているように見せるには、これまでの会話を全部リストに貯めておいて、毎回まるごと渡す。会うたびに、これまでのやりとりのメモを読み上げてから話し始めるようなもの。会話を貯めながら話す係を作ろう。",
      skill="さっきの話を覚えている",
      template=MOCK + PERSONA + (
          "history = []      # これまでの会話を貯めておくリスト\n\n"
          "def chat(question):\n"
          "    # ① history に user の発言を足す\n"
          "    # ② 「system の指示 ＋ history」を call_llm に渡して返事をもらう\n"
          "    # ③ history に assistant の返事を足す\n"
          "    # ④ 返事を返す\n"
          "    return \"\"\n"),
      answer=MOCK + PERSONA + (
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
          G("脳には記憶が無い", "call_llm は、渡された会話リストだけを見て返事をする。前回のことは何も覚えていない。覚えているように見せるには、こちらで会話を貯めて、毎回全部渡す。"),
          G("① 自分の発言を貯める", "history.append( ) で、リストの後ろに発言を1つ足す。",
            "history.append({\"role\": \"user\", \"content\": question})"),
          G("② 設定書と会話をつなげて渡す", "[設定書] + history で、先頭に system、そのあとに今までの会話が並んだリストができる。",
            "messages = [{\"role\": \"system\", \"content\": PERSONA}] + history\nreply = call_llm(messages)"),
          G("③④ 返事も貯めてから返す", "AIの返事（assistant）も history に足す。これを忘れると、AIは自分が何を言ったか覚えていない状態になる。",
            "history.append({\"role\": \"assistant\", \"content\": reply})\nreturn reply"),
      ],
      kaisetsu="会話を全部貯めて、毎回まるごと渡す。これが短期記憶の正体。脳が覚えてるんじゃなくて、こっちが毎回思い出させてるの。試験結果を見てみな。話すたびに、まねっこ脳に届く手紙の通数が増えていくでしょ。ただし、会話が長くなると、渡す量がどんどん増えて、遅くなるし、脳が一度に読める量にも限界がある。だから本物の私は、直近の何往復かだけ渡してるの。じゃあ、ずっと覚えておきたいことはどうするか。それが次の話。",
      terms=[T("会話履歴", "これまでのやりとりのメモ", "過去の発言を貯めたリスト。毎回これを渡すことで、話が続いているように見せる。"),
             T("コンテキスト", "一度に読める量", "言語モデルが1回に読める文章の範囲。長すぎると入りきらない。")],
      quiz=[Q("AIが前の発言を覚えているように見えるのはなぜ？", "毎回、これまでの会話をまるごと渡しているから", "脳の重みに書き込まれるから", "インターネットに保存されるから",
              "脳は毎回、渡されたリストしか見ていない。"),
            Q("会話が長くなりすぎると何が起きる？", "遅くなり、古い話が入りきらなくなる", "脳が賢くなる", "何も変わらない",
              "一度に読める量に限界があるので、古い部分を削る必要が出る。")]),
    # ---------------- Lv38 ----------------
    L(38, 6, "Lv38 思い出してから答える", "m",
      story="日記帳に何千行も貯まったら、全部を毎回渡すことはできない。そこで、質問に関係のありそうな記憶だけを探して、それを「参考情報」として添えてから脳に聞く。テストで、教科書の関係あるページだけ開いてから答えるようなもの。これを RAG（ラグ）という。関係のある記憶を探す係と、それを添えて聞く係を作ろう。",
      skill="関係のあることを思い出して答える",
      template=MOCK + PERSONA + (
          "def score(question, memory):\n"
          "    # 質問と記憶の「関係の強さ」：共通して出てくる文字の種類の数\n"
          "    return len(set(question) & set(memory))\n\n"
          "def search(question, memories):\n"
          "    # memories（記憶のリスト）から、質問と一番関係が強い記憶を返そう\n"
          "    return \"\"\n\n"
          "def build_messages(question, memories):\n"
          "    # ① search で関係のある記憶を探す\n"
          "    # ② system に「PERSONA ＋ 参考情報：その記憶」、user に質問を入れた会話リストを返す\n"
          "    return []\n\n"
          "def answer(question, memories):\n"
          "    return call_llm(build_messages(question, memories))\n"),
      answer=MOCK + PERSONA + (
          "def score(question, memory):\n"
          "    return len(set(question) & set(memory))\n\n"
          "def search(question, memories):\n"
          "    return max(memories, key=lambda m: score(question, m))\n\n"
          "def build_messages(question, memories):\n"
          "    found = search(question, memories)\n"
          "    return [\n"
          "        {\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found},\n"
          "        {\"role\": \"user\", \"content\": question},\n"
          "    ]\n\n"
          "def answer(question, memories):\n"
          "    return call_llm(build_messages(question, memories))\n"),
      hints=["search は Lv2 の min とそっくり。今度は「一番大きい」ので max：\n    return max(memories, key=lambda m: score(question, m))",
             "見つけた記憶を system の文章にくっつける（\\n は改行）：\n    found = search(question, memories)\n    return [\n        {\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found},\n        {\"role\": \"user\", \"content\": question},\n    ]"],
      guide=[
          G("RAG の流れ", "①質問が来る → ②関係のある記憶を探す（検索）→ ③見つけた記憶を「参考情報」として添える → ④脳に聞く。脳は参考情報を読んでから答えるので、知らないはずのことも答えられる。"),
          G("関係の強さの測り方", "今回は簡単に「質問と記憶に共通する文字が何種類あるか」で測る（score は書いてある）。次のレベルで、もっと良い測り方に作り直す。"),
          G("search を作る", "max に key を渡すと、「score が一番大きい記憶」を選べる。Lv2 で一番近い動物を選んだのと同じ形。",
            "max(memories, key=lambda m: score(question, m))"),
          G("会話リストを作る", "見つけた記憶を、設定書の後ろに「参考情報：」としてくっつける。あとはいつもの会話リスト。",
            "{\"role\": \"system\", \"content\": PERSONA + \"\\n参考情報：\" + found}"),
      ],
      kaisetsu="質問に関係のある記憶だけ探して、参考情報として添えてから聞く。これがRAG、検索で補強した生成って意味。脳は{user}の好きな食べ物なんて知らないはずなのに、手紙に参考情報が入っていれば、それを読んで答えられる。脳を学習し直したわけじゃなくて、カンニングペーパーを渡しただけ。会社の資料を読んで答えるAIも、ほとんどがこの仕組み。覚えさせるんじゃなくて、調べさせる。これが今のAIの使い方の主流なんだよ。",
      terms=[T("RAG", "教科書の関係あるページを開いてから答える", "質問に関係する情報を検索して添えてから、言語モデルに答えさせる方法。"),
             T("検索", "関係のある記憶を探す", "たくさんのデータから、質問に関係の強いものを選び出すこと。")],
      quiz=[Q("RAG では、脳（言語モデル）の重みはどうなる？", "変わらない。参考情報を渡すだけ", "質問のたびに学習し直す", "記憶のぶんだけ増える",
              "学習はしない。カンニングペーパーを渡すだけ。"),
            Q("記憶を全部渡さず、関係のあるものだけ渡す理由は？", "一度に読める量に限りがあり、全部は渡せないから", "脳が嫌がるから", "保存できなくなるから",
              "数千行の日記を毎回渡すのは無理。必要な部分だけ選ぶ。")]),
    # ---------------- Lv39 ----------------
    L(39, 6, "Lv39 意味の近さで探す", "m",
      story="Lv38の探し方は「共通する文字の種類を数える」だった。でもこれだと、長い記憶ほど文字が多いので、関係なくても選ばれやすい。声の大きい人の意見ばかり通るようなもの。そこで Lv30 の考え方を使う。文章を「文字ごとの回数」の数字の並び（ベクトル）に変えて、向きの近さ（コサイン類似度）で比べる。長さに関係なく、中身の似かたで選べるようになる。文章をベクトルにする係と、探す係を書こう。",
      skill="意味の近さで記憶を探す",
      template=SIM + (
          "def to_vec(text, vocab):\n"
          "    # 文章を「名簿の文字が、それぞれ何回出てくるか」の並びにしよう\n"
          "    v = np.zeros(len(vocab))\n\n"
          "    return v\n\n") + SIM_FUNC + (
          "def search(question, memories):\n"
          "    vocab = make_vocab(memories + [question])\n"
          "    q = to_vec(question, vocab)\n"
          "    # 似ている度（similarity）が一番大きい記憶を返そう\n"
          "    return memories[0]\n"),
      answer=SIM + TO_VEC_ANS + SIM_FUNC + (
          "def search(question, memories):\n"
          "    vocab = make_vocab(memories + [question])\n"
          "    q = to_vec(question, vocab)\n"
          "    return max(memories, key=lambda m: similarity(q, to_vec(m, vocab)))\n"),
      hints=["文章の文字を1つずつ見て、名簿の何番目かを調べ、その場所を1増やす：\n    for ch in text:\n        if ch in vocab:\n            v[vocab.index(ch)] += 1",
             "記憶もそれぞれベクトルにして、似ている度が一番大きいものを max で選ぶ：\n    return max(memories, key=lambda m: similarity(q, to_vec(m, vocab)))"],
      guide=[
          G("文章をベクトルにする", "名簿が [\"い\", \"ぬ\", \"ね\", \"こ\"] なら、「いぬいぬ」は [2, 2, 0, 0]、「ねこ」は [0, 0, 1, 1]。文字ごとの回数を並べるだけで、文章が数字の並びになる。",
            "for ch in text:\n    if ch in vocab:\n        v[vocab.index(ch)] += 1"),
          G("向きで比べる", "similarity は Lv30 のコサイン類似度（用意済み）。矢印の長さではなく向きで比べるので、記憶が長くても短くても公平に比べられる。"),
          G("一番似ている記憶を探す", "記憶を1つずつ to_vec でベクトルにして、質問との似ている度を出し、max で一番を選ぶ。",
            "max(memories, key=lambda m: similarity(q, to_vec(m, vocab)))"),
          G("本物との違い", "本物のHARIIのような検索では、文字の回数ではなく、言語モデルが作った「意味の地図」（埋め込み）を使う。そうすると「ワンちゃん」と「犬」のように、文字が違っても意味が同じなら近くなる。"),
      ],
      kaisetsu="文章を数字の並びに変えて、向きの近さで比べる。これがベクトル検索。試験結果の下に、Lv38の数え方との違いを出しておいたから見てみな。長い記憶に引っぱられなくなったでしょ。今回は文字の回数で作ったけど、本物は Lv30 でやった埋め込み、つまり意味の地図を使うの。そうすると、文字が全然違っても、意味が近ければ見つけられる。本物のRAGの検索係は、ほとんどこの仕組み。地図の上で、質問の近くにいる記憶を探してるだけなんだよ。",
      terms=[T("ベクトル検索", "地図の上で近くの記憶を探す", "文章を数字の並びに変えて、似ている度で検索する方法。"),
             T("Bag of Words", "文字や単語の回数表", "語順を無視して、出てくる回数だけで文章を表す方法。")],
      quiz=[Q("「共通する文字の数」で探す方法の弱点は？", "長い記憶ほど、関係なくても選ばれやすい", "短い記憶しか探せない", "計算できない",
              "文字が多いと、たまたま共通する文字も増えてしまう。"),
            Q("コサイン類似度で比べる良さは？", "文章の長さに関係なく、中身の似かたで比べられる", "必ず100%正しい", "名簿が要らない",
              "矢印の向きだけを見るので、長さの影響を受けない。"),
            Q("本物の検索では、何を使うと「犬」と「ワンちゃん」を近くできる？", "埋め込み（意味の地図）", "文字の回数", "文字の数",
              "文字が違っても、意味が近い言葉は地図の上で近くに置かれる。")]),
    # ---------------- Lv40 ----------------
    L(40, 6, "Lv40 話している所を見つける", "m",
      story="HARIIの実況モードは、{user}の声を聞きながら「今しゃべってる？終わった？」を判断している。声が途切れたら「話し終わった」と考えて、聞き取りに回すの。これを無音検知という。声の大きさを0.1秒ごとに測った並びから、「大きい音が続いている区間」を見つける係を作ろう。ちょっとした物音（短い音）は無視するのがコツ。",
      skill="話している区間を見つける",
      template=(
          "def find_speech(volumes, threshold, min_len):\n"
          "    # volumes  : 0.1秒ごとの声の大きさの並び\n"
          "    # threshold: これより大きければ「声がある」\n"
          "    # min_len  : これより短い音は物音として無視する\n"
          "    # 声が続いた区間を (はじめ, おわり) のリストで返そう（おわりの番号は区間に含まない）\n"
          "    segments = []\n"
          "    start = None      # 声が始まった番号（今は声が無いので None）\n"
          "    for i, v in enumerate(volumes):\n"
          "        # ここに：声が始まったら start を覚え、声が途切れたら区間を記録する\n"
          "        pass\n"
          "    # 最後まで声が続いていた場合（用意済み）\n"
          "    if start is not None and len(volumes) - start >= min_len:\n"
          "        segments.append((start, len(volumes)))\n"
          "    return segments\n"),
      answer=(
          "def find_speech(volumes, threshold, min_len):\n"
          "    segments = []\n"
          "    start = None\n"
          "    for i, v in enumerate(volumes):\n"
          "        if v > threshold and start is None:            # 声が始まった\n"
          "            start = i\n"
          "        elif v <= threshold and start is not None:     # 声が途切れた\n"
          "            if i - start >= min_len:                   # 十分長ければ記録\n"
          "                segments.append((start, i))\n"
          "            start = None\n"
          "    if start is not None and len(volumes) - start >= min_len:\n"
          "        segments.append((start, len(volumes)))\n"
          "    return segments\n"),
      hints=["声が始まった瞬間＝「大きい音」で「まだ start が None」：\n        if v > threshold and start is None:\n            start = i",
             "声が途切れた瞬間＝「小さい音」で「start がある」。長さを測って、十分なら記録して start を戻す：\n        elif v <= threshold and start is not None:\n            if i - start >= min_len:\n                segments.append((start, i))\n            start = None"],
      guide=[
          G("音は数字の並び", "マイクの音を0.1秒ごとに区切って大きさを測ると、[0.01, 0.02, 0.5, 0.6, 0.4, 0.01, …] のような並びになる。大きいところが声。"),
          G("enumerate", "for i, v in enumerate(volumes): で、番号 i と値 v を同時に取り出せる。"),
          G("2つの瞬間を見つける", "①声が始まった瞬間：大きい音で、まだ start が None → start に番号を覚える。②声が途切れた瞬間：小さい音で、start がある → 区間を記録して start を None に戻す。elif は「そうでなくて、もし〜なら」。"),
          G("物音を無視する", "区間の長さ i − start が min_len より短ければ、咳や机をたたく音とみなして記録しない。",
            "if i - start >= min_len:\n    segments.append((start, i))"),
      ],
      kaisetsu="音の大きさの並びから、しゃべっている区間を見つけられたね。これが無音検知。{user}の本物の私は、実況モードでこれを使って、{user}が話し終わったタイミングで聞き取りを始めてるの。短い物音を無視しないと、机をたたいただけで返事しちゃうからね。区切った声は、Whisper っていう聞き取りの脳に渡して文章にする。音の波を文章に変える脳も、中身は第5章と同じ「次を当てる」仕組みなんだよ。パソコン版のLv40では、その聞き取りの脳を実際に使うよ。",
      terms=[T("無音検知（VAD）", "しゃべり始めと終わりを見つける", "音の大きさなどから、声がある区間を判定すること。"),
             T("音声認識", "声を文章に変える", "区切った音声を文章にする技術。Whisper など。")],
      quiz=[Q("短い音（min_len より短い）を無視するのはなぜ？", "咳や物音を、話し声と間違えないため", "計算を速くするため", "声を大きくするため",
              "一瞬の音まで拾うと、関係ない音で反応してしまう。"),
            Q("音声で会話するAIの、正しいリレーの順番は？", "声の区間を見つける → 聞き取る → 返事を考える → 声にする", "返事を考える → 聞き取る → 声にする", "声にする → 聞き取る → 返事を考える",
              "無音検知 → 音声認識 → 言語モデル → 音声合成。")]),
    # ---------------- Lv41 ----------------
    L(41, 6, "Lv41 見たものを言葉にする", "m", samples="faces4", timeout=60,
      story="第4章で作った目は「犬か猫か」を数字で答えるだけだった。HARIIのように「犬の顔が見えるよ」と言葉で話すには、目の答えを言葉に変えてあげる必要がある。目の係（see）は先輩が用意した。絵を渡すと、動物ごとの確率が返ってくる。一番確率が高い動物を選び、自信があるときは言い切り、自信が無いときは正直に「よく見えない」と言う係を作ろう。",
      skill="見たものを言葉で伝える",
      template=(
          "def describe(img, see):\n"
          "    probs = see(img)     # 例：{\"犬\": 0.8, \"猫\": 0.1, \"うさぎ\": 0.05, \"くま\": 0.05}\n"
          "    # 一番確率が高い動物を選び、\n"
          "    #   確率が 0.6 以上なら「（動物）の顔が見えるよ」\n"
          "    #   0.6 より小さければ「よく見えない…」を返そう\n"
          "    return \"よく見えない…\"\n"),
      answer=(
          "def describe(img, see):\n"
          "    probs = see(img)\n"
          "    label = max(probs, key=probs.get)        # 一番確率が高い動物\n"
          "    if probs[label] >= 0.6:\n"
          "        return label + \"の顔が見えるよ\"\n"
          "    return \"よく見えない…\"\n"),
      hints=["辞書の中で値が一番大きい名前は、Lv29 と同じ形で選べる：\n    label = max(probs, key=probs.get)",
             "自信（確率）で言い方を変える：\n    if probs[label] >= 0.6:\n        return label + \"の顔が見えるよ\"\n    return \"よく見えない…\""],
      guide=[
          G("目の係（see）", "第4章と同じ仕組みの目（畳み込み＋判断係）で、犬・猫・うさぎ・くまの4種類を見分ける。返ってくるのは動物ごとの確率の辞書。"),
          G("一番を選ぶ", "max(probs, key=probs.get) で、確率が一番大きい動物の名前が取れる。",
            "label = max(probs, key=probs.get)"),
          G("自信で言い方を変える", "確率が低いのに言い切ると、間違ったことを自信満々に話してしまう。わからないときは「わからない」と言えるのも、良いAIの条件。",
            "if probs[label] >= 0.6:\n    return label + \"の顔が見えるよ\"\nreturn \"よく見えない…\""),
          G("本物のHARIIとの違い", "本物の実況モードは、絵と言葉の両方がわかる大きな脳（画像言語モデル）に絵をそのまま渡して、自由な言葉で話させている。今回は、目と言葉を自分の手でつないでみる。"),
      ],
      kaisetsu="目の答えを、言葉に変えてつないだね。数字だった確率が、「犬の顔が見えるよ」って言葉になった。しかも自信が無いときは、正直に「よく見えない」って言える。これ、大事なのよ。AIが自信満々に間違えることを、幻覚、ハルシネーションって言うんだけど、確率を見て言い方を変えるのは、それを防ぐ基本の工夫なの。本物の私は、絵と言葉の両方がわかる大きな脳に絵を直接渡して、もっと自由に話してる。中では、目が絵を数字の並びにして、言葉の脳に渡してるんだよ。今{user}がやったことと、同じ発想ね。",
      terms=[T("画像言語モデル（VLM）", "絵を見て言葉で話せる脳", "画像とテキストの両方を扱える言語モデル。HARIIの実況モードで使っている。"),
             T("ハルシネーション", "自信満々の間違い", "AIが、事実と違うことをもっともらしく答えてしまうこと。"),
             T("マルチモーダル", "目も耳も口も使える", "文字・画像・音声など、複数の種類の情報を扱えること。")],
      quiz=[Q("確率が低いときに「よく見えない」と答えるのはなぜ？", "自信が無いのに言い切ると、間違いを広めてしまうから", "計算が遅いから", "言葉が足りないから",
              "わからないときに正直に言えるのは、信頼できるAIの条件。"),
            Q("max(probs, key=probs.get) は何を返す？", "確率が一番大きい動物の名前", "一番大きい確率の数字", "動物の数",
              "key に probs.get を渡すと、値で比べて、名前のほうを返す。")]),
    # ---------------- Lv43 最終 ----------------
    L(43, 6, "Lv43 ハリリを組み立てる", "m", final=True,
      story="最後のレベル。ここまで作った部品をつなげて、スマホの中だけで動く「ハリリ」を組み立てる。大きな脳は無いけど、記憶帳（Lv37）、意味の近さで探す係（Lv39）、表情を選ぶ係（Lv42）は、もう並べてある。話しかけられた言葉を受け取って、覚える・思い出す・返事と表情を返す。その心臓部を書こう。合格したら、画面の下で、{user}が作ったハリリと実際に話せるよ。",
      skill="自分のアシスタントを動かす",
      template=FINAL_PARTS + (
          "def chat(text):\n"
          "    # ①「覚えて：」で始まっていたら、そのあとの部分を memory に足して、\n"
          "    #    「覚えた」という言葉と、覚えた内容が入った返事にする\n"
          "    # ② それ以外は search_best で一番似ている記憶と、似ている度を探す\n"
          "    # ③ 似ている度が 0.5 以上なら、その記憶が入った返事にする（例：「たしか、〇〇だよね」）\n"
          "    #    そうでなければ「知らない」という言葉が入った返事にする\n"
          "    # ④ 返事と表情を辞書で返す\n"
          "    reply = \"……\"\n"
          "    return {\"reply\": reply, \"face\": \"normal\"}\n"),
      answer=FINAL_PARTS + (
          "def chat(text):\n"
          "    if text.startswith(\"覚えて：\"):\n"
          "        fact = text[len(\"覚えて：\"):]\n"
          "        memory.append(fact)\n"
          "        reply = \"覚えたよ。\" + fact + \"ね。\"\n"
          "    else:\n"
          "        best, sim = search_best(text, memory)\n"
          "        if sim >= 0.5:\n"
          "            reply = \"たしか、\" + best + \"だよね。\"\n"
          "        else:\n"
          "            reply = \"それは知らないなぁ。「覚えて：〜」って教えてよ。\"\n"
          "    return {\"reply\": reply, \"face\": pick_face(reply)}\n"),
      hints=["①「〜で始まる」は startswith。後ろの部分は、文字数ぶん飛ばして切り出す：\n    if text.startswith(\"覚えて：\"):\n        fact = text[len(\"覚えて：\"):]\n        memory.append(fact)\n        reply = \"覚えたよ。\" + fact + \"ね。\"",
             "②③④。else の中で探して、似ている度で返事を変える。最後に表情を選んで返す：\n    else:\n        best, sim = search_best(text, memory)\n        if sim >= 0.5:\n            reply = \"たしか、\" + best + \"だよね。\"\n        else:\n            reply = \"それは知らないなぁ。「覚えて：〜」って教えてよ。\"\n    return {\"reply\": reply, \"face\": pick_face(reply)}"],
      guide=[
          G("並んでいる部品", "make_vocab・to_vec・similarity・search_best＝意味の近さで探す係（Lv39）。pick_face＝表情を選ぶ係（Lv42）。memory＝記憶帳（Lv37 の日記帳の、スマホ版の簡易版）。全部、{user}が作ってきたもの。"),
          G("① 覚える", "startswith(\"覚えて：\") で、その言葉で始まっているか調べられる。text[len(\"覚えて：\"):] は「覚えて：」の4文字を飛ばした残り。",
            "if text.startswith(\"覚えて：\"):\n    fact = text[len(\"覚えて：\"):]\n    memory.append(fact)\n    reply = \"覚えたよ。\" + fact + \"ね。\""),
          G("②③ 思い出して答える", "search_best は、一番似ている記憶と、その似ている度を2つ同時に返す。似ている度が低ければ、知らないふりをせず正直に「知らない」と言う（Lv41 と同じ考え方）。",
            "best, sim = search_best(text, memory)\nif sim >= 0.5:\n    reply = \"たしか、\" + best + \"だよね。\""),
          G("④ 返事と表情", "返事の言葉から pick_face で表情を選んで、辞書で返す。画面はこの辞書を見て、吹き出しと表情を切り替える。",
            "return {\"reply\": reply, \"face\": pick_face(reply)}"),
          G("返事の言葉は自由", "「覚えた」「知らない」と、覚えた内容・思い出した内容が入っていれば、言い回しは自分の好きなようにしてOK。ハリリらしい口調にしてみよう。"),
      ],
      kaisetsu="動いた。{user}が自分の手で組み立てたハリリが、覚えて、思い出して、表情を変えて返事をしたよ。思い出してみな。最初の{name}は、サイコロを振ることしかできなかった。そこからルールを覚えて、データから学んで、脳を作って、目を持って、言葉を覚えて。そして今、覚えて、探して、話す。本物の私は、ここに大きな脳と、声と、耳がつながってるだけ。中身の考え方は、全部{user}がもう知ってるの。魔法なんて1つも無かったでしょ。……まあ、ここまで来たことは、素直に褒めてあげる。卒業おめでとう。パソコン版の最終章で、本物の大きな脳につないでみなよ。{name}が、もっとおしゃべりになるからさ。",
      terms=[T("AIアシスタント", "専門家たちのリレー", "覚える・探す・考える・話す・表情などの部品をつなげて、1つのキャラクターにしたもの。"),
             T("パイプライン", "流れ作業の組み立てライン", "いくつもの処理を、決まった順番につなげたもの。")]),
]
