AI育成ノート スマホ版　―　GitHub Pages への載せ方

■ このフォルダの中身
  index.html / app.js / worker.js … 画面と、ブラウザの中で Python を動かす係
  data/lessons.json               … 教科書（全44レベル）
  py/                             … 試験官（採点用の Python）
  img/                            … HARII とハリリの画像（スマホ用に軽くしたもの）
  ※ PC版（ai_ikusei フォルダ）とは別物です。PC版はそのまま使えます。

■ 初めて載せるとき
  1. GitHub にログインして、右上の「＋」→「New repository」
       Repository name：ai-ikusei（好きな名前でOK）
       Public を選ぶ（無料プランで GitHub Pages を使うには Public が必要）
       「Create repository」
  2. できたページの「uploading an existing file」をクリック
  3. このフォルダの「中身」を全部まとめてドラッグ＆ドロップ
       （index.html が一番上の階層に来るように。data・py・img はフォルダごと）
       下の「Commit changes」を押す
  4. 「Settings」→ 左の「Pages」
       Branch：main　フォルダ：/(root) を選んで「Save」
  5. 1〜3分待つと、Pages の画面に URL が出ます
       例：https://（あなたのユーザー名）.github.io/ai-ikusei/
  6. スマホでその URL を開く。Safari なら「共有」→「ホーム画面に追加」、
     Chrome なら「︙」→「ホーム画面に追加」で、アプリのように使えます

■ 中身を新しくするとき
  同じリポジトリで「Add file」→「Upload files」から、新しい中身をまるごと上書きアップロード。
  反映されないときは、スマホでページを再読み込みしてください。

■ 知っておいてほしいこと
  ・初回は Python（約10MB）を読み込むので 30 秒ほどかかります。2回目からは速くなります。
  ・インターネットにつながっている必要があります（Python をネットから読み込むため）。
  ・セーブはスマホのブラウザの中だけ。PC版とはつながっていません。
    ブラウザの「履歴とデータを消去」をするとセーブも消えます。
  ・Public のリポジトリなので、URL を知っている人なら誰でも開けます（答えのコードも見られます）。
  ・HARII の声は、スマホに入っている読み上げの声です（⚙ でオン・オフ）。
    AivisSpeech の「るな」の声は PC版だけです。

■ PC版との違い（スマホで動かない部分を、numpy だけで学べる内容に差し替え）
  Lv17  PyTorch を使う        → 自動微分の仕組み（loss.backward の中身）を自分で作る
  Lv18  PyTorch で数字を読む  → numpy で同じ2段の脳を作る
  Lv19  GPU に引っ越す        → ミニバッチ学習（少しずつ何度も直す）
  Lv20  卒業試験              → numpy で白紙から脳を作る
  Lv24  PyTorch の CNN        → 畳み込み＋プーリングで「目」を組み立てる
  Lv25  PyTorch で転移学習    → 先輩の目を借りる（numpy 版）
  Lv26  本物の写真            → 絵の中から犬を探す（物体検出）
  Lv27  卒業試験              → 画像の特徴を自分で作る
  Lv32  PyTorch のミニGPT     → numpy で小さな言語モデルを作り、HARII 口調で文を書かせる
  Lv34  Ollama を呼ぶ         → 大きな脳への手紙（JSON）を書く
  Lv35・36・38               → 本物の脳のかわりに「まねっこ脳」で、手紙の形を確かめる
  Lv39  声（AivisSpeech）     → 意味の近さで記憶を探す（ベクトル検索）
  Lv40  耳（Whisper）         → 話している区間を見つける（無音検知）
  Lv41  目（画像言語モデル）  → 目の答えを言葉にする
  Lv43  Flask で HARII        → スマホの中だけで動く「ハリリ」を組み立てて、実際に話せる
  それ以外のレベル（第1章・第2章の全部など）は PC版と同じ内容です。
