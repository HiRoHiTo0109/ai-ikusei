// AI育成ノート スマホ版
// 教科書は data/lessons.json、採点は worker.js（ブラウザの中の Python）、セーブはこのブラウザの中
"use strict";

var D = null;                 // 教科書
var S = null;                 // セーブ
var cur = 0;                  // 開いているレベル
var reviewMode = false, helped = false, hintIdx = 0;
var quizQs = [], lastNeedQuiz = false;

// ================================================================ セーブ
var SAVE_KEY = "aiku_m_save";
var DEFAULT_SAVE = { name: null, yomi: null, user: "宏仁", level: 0, best: {}, passed: [], peeked: [],
                     provisional: [], exams: [], stars: [], voice: true, kaiVoice: true };

function store(k, v){ try { localStorage.setItem(k, v); } catch(e){} }
function fetchStore(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
function loadSave(){
  var s = {};
  try { s = JSON.parse(fetchStore(SAVE_KEY) || "{}") || {}; } catch(e){ s = {}; }
  var out = JSON.parse(JSON.stringify(DEFAULT_SAVE));
  Object.keys(s).forEach(function(k){ out[k] = s[k]; });
  return out;
}
function save(){ store(SAVE_KEY, JSON.stringify(S)); }
function codeKey(id){ return "aiku_m_code_" + id; }
function has(a, v){ return a.indexOf(v) >= 0; }
function add(a, v){ if(!has(a, v)) a.push(v); }

// {name} {user} を置き換える
function fill(t){
  var nm = (S && (S.yomi || S.name)) || "弟子";
  return String(t).split("{name}").join(nm).split("{user}").join((S && S.user) || "あなた");
}
function $(id){ return document.getElementById(id); }
function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text !== undefined) e.textContent = text; return e; }
function pick(a){ return a[Math.floor(Math.random() * a.length)]; }

// ================================================================ 試験官（ワーカー）
var worker = null, wReady = false, wWaiting = [], wSeq = 0, wPending = {}, wLoadStart = 0;

function startWorker(){
  wReady = false;
  worker = new Worker("worker.js?v=" + D.version);
  wLoadStart = Date.now();
  showLoad("🐍 Pythonを準備しています（初回は30秒ほど。2回目からは速くなります）");
  worker.onmessage = function(e){
    var m = e.data;
    if(m.type === "ready"){
      wReady = true; hideLoad();
      var q = wWaiting; wWaiting = [];
      q.forEach(function(f){ f(); });
    } else if(m.type === "init_error"){
      showLoad("⚠ Pythonの準備に失敗しました。電波の良いところで、ページを読み込み直してください。\n（" + m.error + "）");
      $("runBtn").disabled = false; $("runBtn").textContent = "試験を受けさせる";
    } else if(wPending[m.id]){
      var p = wPending[m.id]; delete wPending[m.id];
      clearTimeout(p.timer); p.resolve(m);
    }
  };
  worker.onerror = function(e){ showLoad("⚠ 試験官でエラーが起きました：" + (e.message || "")); };
  worker.postMessage({ type: "init", files: D.py_files, version: D.version });
}

// ワーカーに仕事を頼む（時間切れなら、ワーカーごと作り直す）
function ask(msg, seconds){
  return new Promise(function(resolve){
    var go = function(){
      var id = ++wSeq;
      msg.id = id;
      var timer = setTimeout(function(){
        delete wPending[id];
        worker.terminate();
        startWorker();
        resolve({ type: "timeout" });
      }, seconds * 1000);
      wPending[id] = { resolve: resolve, timer: timer };
      worker.postMessage(msg);
    };
    if(wReady) go(); else wWaiting.push(go);
  });
}
function showLoad(t){ var b = $("loadBox"); b.style.display = "block"; b.style.whiteSpace = "pre-wrap"; b.textContent = t; }
function hideLoad(){ $("loadBox").style.display = "none"; }

// ================================================================ HARIIのセリフ（スマホ版は決まり文句）
var LINES = {
  name:     [["{name}？ ふーん、悪くないじゃん。名前負けしないように育ててよね。", "confident"],
             ["{name}ね。まあ、呼びやすいからいいんじゃない？", "normal"]],
  rename:   [["今さら名前変えるとか。まあ、{name}のほうがマシか。", "confident"]],
  pass:     [["ふーん、やるじゃん。でも本当にわかってるか、クイズで確かめるからね。", "happy"],
             ["合格。{name}にしては上出来じゃん。解説、ちゃんと読みなよ。", "happy"],
             ["ちゃんと動いたね。じゃあ、なんで動いたのか説明できる？", "confident"]],
  passAgain:[["合格。前にもできたんだから、当然でしょ。", "confident"]],
  star:     [["何も見ずに書けたの？ ……やるじゃん。⭐あげる。", "happy"],
             ["自力で合格。これでやっと、本当に覚えたって言えるね。", "happy"]],
  fail:     [["まだまだだね。×のついた問題を、よーく見比べてみなよ。", "confident"],
             ["惜しいんだけどね。授業をもう一回読んでから考えてみな。", "normal"],
             ["それじゃ合格ラインに届かないよ。どこで間違えてるか見てみな。", "pout"]],
  error:    [["ほら、エラー。", "pout"], ["動かないじゃん。", "pout"], ["はい、エラー。落ち着いて読みなよ。", "pout"]],
  timeout:  [["時間切れ。無限ループになってない？ for や while の終わり方を見直しな。", "pout"]],
  peek:     [["答え見たね？ 写すだけじゃ育たないよ。どこが違うか見比べときなよ。", "pout"]],
  quizOk:   [["全問正解。ちゃんとわかってるじゃん。次、行くよ。", "happy"],
             ["やるじゃん。この調子で次のレベルもいこ。", "happy"]],
  quizNg:   [["間違えたところ、解説を読んでからもう一回ね。", "pout"],
             ["わかってないでしょ。解説、ちゃんと読みなよ。", "pout"]],
  grad:     [["卒業おめでとう、とは言ってあげる。{name}もちょっとは成長したじゃん。", "happy"]],
  final:    [["全部卒業……ほんとにやりきったんだ。おめでとう、{user}。ちょっとだけ見直したよ。", "happy"]],
  hello:    [["で、今日は何を教えるの？", "confident"], ["お、来たね。{name}が待ちくたびれてるよ。", "normal"],
             ["ゆっくりでいいから、確実にね。", "normal"]]
};
function line(kind){ var x = pick(LINES[kind]); return { text: fill(x[0]), mood: x[1] }; }

var CHILD = { ok: ["できたー！ほめて！", "ちゃんと覚えたよ！", "ぼく、賢くなったでしょ？"],
              ng: ["うぅ、まちがえちゃった…", "あれ？なんでだろう…", "……？（きょとんとしている）"] };

// ================================================================ 表情・口パク・読み上げ
var MOODS = ["normal", "happy", "confident", "pout"];
MOODS.forEach(function(m){ [m, m + "_open"].forEach(function(n){ new Image().src = "img/harii/" + n + ".webp"; }); });
var hariiMood = "normal", mouthOpen = false, flapTimer = null, endTimer = null, talkId = 0;

function setHarii(mood, open){
  hariiMood = mood; mouthOpen = open;
  var src = "img/harii/" + mood + (open ? "_open" : "") + ".webp";
  var img = $("hariiImg");
  if(img.getAttribute("src") !== src) img.setAttribute("src", src);
}
function stopTalk(){
  talkId++;
  clearInterval(flapTimer); clearTimeout(endTimer);
  try { if(window.speechSynthesis) speechSynthesis.cancel(); } catch(e){}
  $("hariiBox").classList.remove("talking");
  setHarii(hariiMood, false);
}
var jaVoice = null;
function findVoice(){
  try {
    var vs = speechSynthesis.getVoices().filter(function(v){ return /^ja/i.test(v.lang); });
    jaVoice = vs.filter(function(v){ return /female|kyoko|o-ren|nanami|haruka|ayumi/i.test(v.name); })[0] || vs[0] || null;
  } catch(e){ jaVoice = null; }
}
if(window.speechSynthesis){ findVoice(); speechSynthesis.onvoiceschanged = findVoice; }

// HARIIが話す：吹き出し＋口パク（＋読み上げがONなら声）
function talk(text, mood, onEnd){
  stopTalk();
  var my = talkId;
  $("hariiText").textContent = text;
  setHarii(mood || "normal", false);
  $("hariiBox").classList.add("talking");
  flapTimer = setInterval(function(){ setHarii(hariiMood, !mouthOpen); }, 150);
  var done = false;
  function end(){
    if(done || my !== talkId) return; done = true;
    clearInterval(flapTimer); clearTimeout(endTimer);
    $("hariiBox").classList.remove("talking");
    setHarii(hariiMood, false);
    if(onEnd) onEnd();
  }
  var guess = Math.min(20000, 700 + text.length * 120);
  if(S.voice && window.speechSynthesis && window.SpeechSynthesisUtterance){
    try {
      var u = new SpeechSynthesisUtterance(text.replace(/[🎓🎉⭐📖💡]/g, ""));
      u.lang = "ja-JP"; if(jaVoice) u.voice = jaVoice;
      u.rate = 1.1; u.pitch = 1.15;
      u.onend = end; u.onerror = end;
      speechSynthesis.speak(u);
      endTimer = setTimeout(end, guess + 15000);   // 念のため
      return;
    } catch(e){}
  }
  endTimer = setTimeout(end, Math.min(guess, 6000));
}
function say(l, childText){
  talk(l.text, l.mood);
  if(childText) $("childText").textContent = childText;
}
function childReact(kind){
  var box = $("childBox");
  box.classList.remove("react-happy", "react-confused");
  void box.offsetWidth;
  if(kind) box.classList.add("react-" + kind);
}

// ================================================================ 画面の組み立て
function mark(l){
  if(l.id > S.level) return "🔒 ";
  if(l.id === S.level && has(S.passed, l.id)) return "❓ ";
  if(l.id < S.level) return has(S.stars, l.id) ? "⭐ " : has(S.provisional, l.id) ? "🔸 " : "✓ ";
  return "";
}

function refresh(){
  var n = D.lessons.length, lv = S.level;
  $("childName").textContent = S.name || "？？？";
  $("progress").textContent = "覚えたこと " + Math.min(lv, n) + " / " + n + "　⭐ " + S.stars.length;
  var ch = D.lessons[cur].chapter;

  var cb = $("chapters"); cb.innerHTML = "";
  Object.keys(D.chapters).forEach(function(k){
    k = Number(k);
    var first = D.lessons.filter(function(l){ return l.chapter === k; })[0];
    var b = el("button", k === ch ? "active" : "", (has(S.exams, k) ? "🎓 " : first.id > lv ? "🔒 " : "") + D.chapters[k]);
    b.disabled = first.id > lv;
    b.onclick = function(){
      var list = D.lessons.filter(function(l){ return l.chapter === k && l.id <= S.level; });
      openLesson(list[list.length - 1].id);
    };
    cb.appendChild(b);
  });
  var tb = $("tabs"); tb.innerHTML = "";
  D.lessons.filter(function(l){ return l.chapter === ch; }).forEach(function(l){
    var b = el("button", l.id === cur ? "active" : "", mark(l) + l.title);
    b.disabled = l.id > lv;
    b.onclick = function(){ openLesson(l.id); };
    tb.appendChild(b);
    if(l.id === cur) setTimeout(function(){ b.scrollIntoView({ inline: "center", block: "nearest" }); }, 0);
  });

  var l = D.lessons[cur];
  $("quizBtn").style.display = (cur === lv && has(S.passed, cur)) ? "" : "none";
  $("hintBtn").style.display = (l.hints.length && reviewMode) ? "" : "none";
  $("ansBtn").style.display = l.answer ? "" : "none";
  $("talkBox").style.display = (lv > D.lessons.length - 1 || (cur === n - 1 && has(S.passed, n - 1))) ? "block" : "none";
  drawNotes();
}

function openLesson(id){
  cur = id; hintIdx = 0;
  var l = D.lessons[id];
  reviewMode = id < S.level;
  helped = false;
  $("lTitle").textContent = l.title;
  $("lStory").textContent = fill(l.story);
  $("mobileBadge").style.display = l.mobile_only ? "" : "none";
  ["errBox", "kaisetsu", "levelup", "note", "printed"].forEach(function(k){ $(k).style.display = "none"; });
  $("goal").style.left = (l.clear_rate * 100) + "%";
  $("accText").textContent = "－"; $("fill").style.width = "0";
  $("result").querySelector("tbody").innerHTML = "";

  var bar = $("modeBar");
  bar.className = reviewMode ? "review" : "";
  bar.style.display = (l.exam && !reviewMode) ? "none" : "flex";
  $("modeText").textContent = reviewMode ? "🔁 復習モード：授業もヒントも見ずに合格できたら ⭐"
                                         : "🔰 はじめてモード：授業と手順ヒントを見ながら書こう";
  $("oldCodeBtn").style.display = reviewMode ? "" : "none";

  drawGuide(l);
  var g = $("guide");
  g.style.display = l.guide.length ? "" : "none";
  g.open = !reviewMode;

  var hb = $("hintBox");
  if(!reviewMode && l.hints.length){
    hb.style.display = "block";
    hb.textContent = l.hints.map(function(h, i){ return "💡 手順ヒント" + (i + 1) + "：" + fill(h); }).join("\n\n");
  } else hb.style.display = "none";

  $("code").value = reviewMode ? l.template : (fetchStore(codeKey(id)) || l.template);
  drawSamples(l); drawAlbum(l);
  refresh();
}

function drawGuide(l){
  var body = $("guideBody"); body.innerHTML = "";
  l.guide.forEach(function(st, i){
    var d = el("div", "gstep"), h = el("h3"), num = el("span", "", String(i + 1));
    h.append(num, st.t);
    d.append(h, el("p", "", fill(st.x)));
    if(st.code) d.appendChild(el("pre", "", st.code));
    body.appendChild(d);
  });
}

function drawSamples(l){
  var box = $("samplesBox"), row = $("samples"); row.innerHTML = "";
  box.style.display = l.samples.length ? "" : "none";
  l.samples.forEach(function(sm){
    var c = document.createElement("canvas"); c.width = sm.w; c.height = sm.h;
    var z = sm.w <= 5 ? 8 : 4;
    c.style.width = (sm.w * z) + "px"; c.style.height = (sm.h * z) + "px";
    var ctx = c.getContext && c.getContext("2d");
    if(!ctx) return;
    var im = ctx.createImageData(sm.w, sm.h);
    sm.px.forEach(function(v, i){
      var g = Math.round(Math.max(0, Math.min(1, v)) * 255);
      im.data[i * 4] = g; im.data[i * 4 + 1] = g; im.data[i * 4 + 2] = g; im.data[i * 4 + 3] = 255;
    });
    ctx.putImageData(im, 0, 0);
    var f = el("figure"); f.append(c, el("figcaption", "", sm.label)); row.appendChild(f);
  });
}

function drawAlbum(l){
  var t = $("album"); t.innerHTML = "";
  $("albumBox").style.display = l.memory.length ? "" : "none";
  if(!l.memory.length) return;
  var cols = ["名前"].concat(D.features, ["答え"]);
  var tr = el("tr"); cols.forEach(function(h){ tr.appendChild(el("th", "", h)); }); t.appendChild(tr);
  l.memory.forEach(function(a){
    var r = el("tr", a["名前"] === "いたずら猫" ? "trick" : "");
    cols.forEach(function(k){ r.appendChild(el("td", has(D.features, k) ? "num" : "", String(a[k]))); });
    t.appendChild(r);
  });
}

function drawNotes(){
  var box = $("noteList"); box.innerHTML = "";
  var got = D.lessons.filter(function(l){ return l.id < S.level; });
  if(!got.length){ box.appendChild(el("p", "small", "レベルをクリアすると用語カードが増えていきます。")); return; }
  got.forEach(function(l){
    l.terms.forEach(function(t){
      var d = el("div", "term");
      d.append(el("b", "", t.word), el("div", "rei", "例え：" + t.rei), el("div", "", t.imi), el("div", "small", l.title));
      box.appendChild(d);
    });
  });
}

// ================================================================ 記号キー（スマホで打ちにくい記号）
var KEYS = [["⇥", "    ", "wide"], [":", ":"], ["(", "("], [")", ")"], ["[", "["], ["]", "]"], ["\"", "\""], ["=", "="],
            ["+", "+"], ["-", "-"], ["*", "*"], ["/", "/"], ["<", "<"], [">", ">"], ["_", "_"], [".", "."], [",", ","],
            ["{", "{"], ["}", "}"], ["#", "#"], ["@", "@"], ["'", "'"], ["←", "LEFT", "wide"], ["→", "RIGHT", "wide"]];
function buildKeys(){
  var box = $("keys");
  KEYS.forEach(function(k){
    var b = el("button", k[2] || "", k[0]);
    b.type = "button";
    b.setAttribute("aria-label", k[1] === "    " ? "字下げ" : k[0]);
    b.addEventListener("pointerdown", function(e){ e.preventDefault(); });   // キーボードを閉じない
    b.addEventListener("click", function(){ typeKey(k[1]); });
    box.appendChild(b);
  });
}
function typeKey(v){
  var t = $("code"), s = t.selectionStart, e = t.selectionEnd;
  t.focus();
  if(v === "LEFT"){ t.setSelectionRange(Math.max(0, s - 1), Math.max(0, s - 1)); return; }
  if(v === "RIGHT"){ t.setSelectionRange(s + 1, s + 1); return; }
  insertText(v);
}
function insertText(v){
  var t = $("code"), s = t.selectionStart, e = t.selectionEnd;
  t.value = t.value.slice(0, s) + v + t.value.slice(e);
  t.setSelectionRange(s + v.length, s + v.length);
  onCodeInput();
}
function onCodeInput(){ if(!reviewMode) store(codeKey(cur), $("code").value); }

// 改行したら、前の行と同じだけ字下げ（「:」で終わる行なら、さらに4つ）
$("code").addEventListener("beforeinput", function(e){
  if(e.inputType !== "insertLineBreak" && e.inputType !== "insertParagraph") return;
  var t = e.target, before = t.value.slice(0, t.selectionStart);
  var lineText = before.slice(before.lastIndexOf("\n") + 1);
  var indent = (lineText.match(/^ */) || [""])[0];
  if(/:\s*$/.test(lineText)) indent += "    ";
  e.preventDefault();
  insertText("\n" + indent);
});
$("code").addEventListener("keydown", function(e){
  if(e.key === "Tab"){ e.preventDefault(); insertText("    "); }
});
$("code").addEventListener("input", onCodeInput);

// iPhone の「スマート句読点」などで記号が化けたのを直す（文字列の中の日本語はそのまま）
function cleanCode(c){
  return c.replace(/[“”]/g, "\"").replace(/[‘’]/g, "'").replace(/ /g, " ").replace(/\t/g, "    ");
}

// ================================================================ 試験
function run(){
  var btn = $("runBtn");
  btn.disabled = true; btn.textContent = wReady ? "試験中…" : "Pythonを準備中…";
  ["errBox", "levelup", "kaisetsu", "note", "printed"].forEach(function(k){ $(k).style.display = "none"; });
  var l = D.lessons[cur];
  var code = cleanCode($("code").value);
  if(code !== $("code").value){ $("code").value = code; onCodeInput(); }
  var started = Date.now();
  ask({ type: "run", code: code, lid: cur }, l.timeout + 10).then(function(m){
    btn.disabled = false; btn.textContent = "試験を受けさせる";
    if(m.type === "timeout"){ showError({ error: (l.timeout + 10) + "秒たっても終わらなかった（無限ループかも）" }); say(line("timeout"), pick(CHILD.ng)); return; }
    if(m.type === "fail"){ showError({ error: m.error }); say(line("error"), pick(CHILD.ng)); return; }
    showPrinted(m.printed);
    var r; try { r = JSON.parse(m.data); } catch(e){ r = { error: "結果が読めなかった" }; }
    if(r.error){
      showError(r);
      var e = line("error");
      e.text += r.error_ja ? " " + r.error_ja + "。" : " 何行目で止まったか見てみな。";
      say(e, pick(CHILD.ng)); childReact("confused");
      return;
    }
    judge(r, l);
  });
}

function showError(r){
  var b = $("errBox"); b.style.display = "block";
  b.textContent = "⚠ " + r.error + (r.error_ja ? "\n💡 " + r.error_ja : "");
  b.scrollIntoView({ behavior: "smooth", block: "center" });
}
function showPrinted(p){
  var b = $("printed");
  if(p && p.trim()){ b.style.display = "block"; b.textContent = "🖨 print の出力\n" + p.slice(0, 3000); }
}

function judge(r, l){
  var lid = l.id;
  var cleared = r.accuracy >= l.clear_rate;
  S.best[lid] = Math.max(r.accuracy, S.best[lid] || 0);
  var needQuiz = cleared && lid === S.level;
  if(needQuiz) add(S.passed, lid);
  var star = cleared && lid < S.level && reviewMode && !helped && !has(S.stars, lid);
  if(star) add(S.stars, lid);
  save();
  lastNeedQuiz = needQuiz;

  var pct = Math.round(r.accuracy * 100);
  $("accText").textContent = "正解率 " + pct + "%";
  $("fill").style.width = pct + "%";
  var tb = $("result").querySelector("tbody"); tb.innerHTML = "";
  r.results.forEach(function(x){
    var tr = el("tr");
    [x.name, x.pred, x.answer].forEach(function(v){ tr.appendChild(el("td", "", String(v))); });
    tr.appendChild(el("td", x.ok ? "ok" : "ng", x.ok ? "○" : "×"));
    tb.appendChild(tr);
  });
  if(r.note){ $("note").style.display = "block"; $("note").textContent = r.note; }
  refresh();

  if(star){ $("levelup").style.display = "block"; $("levelup").textContent = "⭐ 復習クリア！ 何も見ずに自分の力で書けた！"; }
  if(cleared){
    childReact("happy");
    showKaisetsu(needQuiz);
    var c = line(star ? "star" : needQuiz ? "pass" : "passAgain");
    $("childText").textContent = pick(CHILD.ok);
    talk(c.text, c.mood, function(){ if(S.kaiVoice && l.kaisetsu) talk(fill(l.kaisetsu), "confident"); });
    $("resultCard").scrollIntoView({ behavior: "smooth", block: "start" });
  } else {
    childReact("confused");
    var f = line("fail");
    f.text = "正解率" + pct + "%。" + f.text;
    say(f, pick(CHILD.ng));
    $("resultCard").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function showKaisetsu(needQuiz){
  var l = D.lessons[cur];
  if(!l.kaisetsu) { if(needQuiz) setTimeout(openQuiz, 1500); return; }
  $("kText").textContent = fill(l.kaisetsu);
  $("kQuiz").style.display = needQuiz ? "" : "none";
  $("kaisetsu").style.display = "block";
}
function readKaisetsu(){ talk(fill(D.lessons[cur].kaisetsu), "confident"); }

// ================================================================ ヒント・答え
function markHelped(){
  if(reviewMode && !helped){
    helped = true;
    $("modeText").textContent = "🔁 復習モード：ヒントを見たので今回は ⭐ なし。タブを押し直すと再挑戦できるよ";
  }
}
function nextHint(){
  markHelped();
  var l = D.lessons[cur], i = Math.min(hintIdx, l.hints.length - 1);
  var b = $("hintBox"); b.style.display = "block";
  b.textContent = "💡 ヒント" + (i + 1) + "：" + fill(l.hints[i]);
  hintIdx++;
}
function loadOldCode(){
  markHelped();
  var c = fetchStore(codeKey(cur));
  if(c) $("code").value = c; else alert("前に書いたコードは残っていないよ");
}
function showAnswer(){
  if(!confirm(reviewMode ? "答えを見ると、今回は⭐がつきません。見る？"
     : "答えを見てクリアすると「仮合格🔸」になります。卒業試験に合格すると正式合格になります。見る？")) return;
  markHelped();
  add(S.peeked, cur); save();
  $("code").value = D.lessons[cur].answer; onCodeInput();
  say(line("peek"));
}
function resetCode(){
  if(!confirm("書き出しの状態に戻すよ。いい？")) return;
  $("code").value = D.lessons[cur].template; onCodeInput();
}

// ================================================================ 理解クイズ
function shuffle(a){ a = a.slice(); for(var i = a.length - 1; i > 0; i--){ var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }

function openQuiz(){
  var l = D.lessons[cur];
  if(!(cur === S.level && has(S.passed, cur))) return;
  var pool;
  if(l.quiz === "review"){
    pool = [];
    D.lessons.forEach(function(x){
      if(x.chapter === l.chapter && Array.isArray(x.quiz)) x.quiz.forEach(function(q){ pool.push(q); });
    });
    pool = shuffle(pool).slice(0, 5);
  } else pool = l.quiz;
  quizQs = pool.map(function(q){ return { q: q.q, right: q.c[q.a], why: q.why, choices: shuffle(q.c) }; });
  $("quizTitle").textContent = l.quiz === "review" ? "抜き打ち復習" : "理解クイズ";
  $("quizNote").textContent = l.quiz === "review" ? "HARIIがこの章から" + quizQs.length + "問ランダムに出題。全問正解で卒業！" : "全問正解で次のレベルに進めます。";
  var body = $("quizBody"); body.innerHTML = "";
  quizQs.forEach(function(q, i){
    var d = el("div", "qa"); d.id = "qa" + i;
    d.appendChild(el("p", "", "Q" + (i + 1) + ". " + q.q));
    q.choices.forEach(function(c){
      var lab = el("label"), r = document.createElement("input");
      r.type = "radio"; r.name = "q" + i; r.value = c;
      lab.append(r, el("span", "", c)); d.appendChild(lab);
    });
    body.appendChild(d);
  });
  $("quizSubmit").style.display = ""; $("quizClose").style.display = "none";
  $("quizDlg").style.display = "flex";
  $("quizDlg").querySelector(".box").scrollTop = 0;
}

function submitQuiz(){
  var picks = [];
  for(var i = 0; i < quizQs.length; i++){
    var sel = document.querySelector("input[name=q" + i + "]:checked");
    if(!sel){ alert("全部の問題に答えてね"); return; }
    picks.push(sel.value);
  }
  var wrong = [];
  quizQs.forEach(function(q, i){
    var ok = picks[i] === q.right;
    if(!ok) wrong.push(q);
    $("qa" + i).appendChild(el("div", "why" + (ok ? "" : " ng"), (ok ? "○ " : "× 正解は「" + q.right + "」　") + q.why));
  });
  document.querySelectorAll("#quizBody input").forEach(function(x){ x.disabled = true; });
  $("quizSubmit").style.display = "none";
  var close = $("quizClose"); close.style.display = ""; close.textContent = wrong.length ? "閉じてもう一度" : "閉じる";

  var l = D.lessons[cur], allOk = !wrong.length;
  var isGrad = l.exam || l.final;
  if(allOk && cur === S.level && has(S.passed, cur)){
    S.level = cur + 1;
    if(has(S.peeked, cur) && !isGrad) add(S.provisional, cur);
    if(isGrad){
      add(S.exams, l.chapter);
      S.provisional = S.provisional.filter(function(p){ return D.lessons[p].chapter !== l.chapter; });
    }
    save();
    var lu = $("levelup"); lu.style.display = "block";
    lu.textContent = l.final ? "🎉 全レベル卒業！ " + S.name + "は、あなたの手で一人前のAIになった！"
                   : isGrad ? "🎓 " + S.name + "は卒業して成長した！ 🔸仮合格もすべて正式合格に！"
                   : "🎉 " + S.name + "は「" + l.skill + "」ができるようになった！";
    childReact("happy");
    say(line(l.final ? "final" : isGrad ? "grad" : "quizOk"), pick(CHILD.ok));
  } else if(allOk){
    say(line("quizOk"));
  } else {
    var teach = wrong.map(function(q){ return "「" + q.q + "」の正解は、" + q.right + "。" + q.why; }).join(" ");
    var ng = line("quizNg");
    talk(ng.text, ng.mood, function(){ talk("じゃあ解説するね。" + teach, "confident"); });
  }
  refresh();
}

function closeQuiz(){
  closeDlg("quizDlg");
  if(S.level > cur && S.level < D.lessons.length) openLesson(S.level);
  else refresh();
}

// ================================================================ ハリリと話す（Lv43）
function talkSend(){
  var inp = $("talkInput"), text = inp.value.trim();
  if(!text) return;
  inp.value = "";
  var log = $("talkLog");
  log.appendChild(el("div", "msg me", text));
  var code = fetchStore(codeKey(D.lessons.length - 1)) || D.lessons[D.lessons.length - 1].answer;
  ask({ type: "chat", code: cleanCode(code), text: text }, 15).then(function(m){
    var r = { reply: "……（考えすぎて止まっちゃった）", face: "pout" };
    if(m.type === "chat"){ try { r = JSON.parse(m.data); } catch(e){} }
    log.appendChild(el("div", "msg bot", (S.name || "弟子") + "：" + r.reply));
    log.scrollTop = log.scrollHeight;
    $("childText").textContent = r.reply;
    childReact(r.face === "happy" ? "happy" : r.face === "pout" ? "confused" : "");
  });
}
$("talkInput").addEventListener("keydown", function(e){ if(e.key === "Enter" && !e.isComposing) talkSend(); });

// ================================================================ 名付け・設定
function openName(rename){
  closeDlg("menuDlg");
  $("nameQ").innerHTML = rename ? "<b>HARII：</b>え、名前変えんの？ 今さら？" : "<b>HARII：</b>で、こいつの名前どうすんの？";
  $("nameInput").value = rename ? (S.name || "") : "";
  $("yomiInput").value = rename ? (S.yomi || "") : "";
  $("userInput").value = S.user || "";
  $("nameCancel").style.display = rename ? "" : "none";
  $("nameDlg").style.display = "flex";
}
function giveName(){
  var n = $("nameInput").value.trim();
  if(!n){ alert("名前を入れてね"); return; }
  var renamed = !!S.name && S.name !== n;
  S.name = n; S.yomi = $("yomiInput").value.trim() || n; S.user = $("userInput").value.trim() || "あなた";
  save(); closeDlg("nameDlg"); refresh();
  say(line(renamed ? "rename" : "name"), "……！（" + S.yomi + "って呼ばれて、うれしそうにこっちを見た）");
  childReact("happy");
}
function closeDlg(id){ $(id).style.display = "none"; }
function openMenu(){ $("voiceSw").checked = S.voice; $("kaiSw").checked = S.kaiVoice; $("menuDlg").style.display = "flex"; }
function setVoice(v){ S.voice = v; save(); if(!v) stopTalk(); else talk("読み上げ、オンにしたよ。", "confident"); }
function setKaiVoice(v){ S.kaiVoice = v; save(); }
function resetAll(){
  if(!confirm("名前もレベルも書いたコードも、全部消えます。本当に最初から？")) return;
  try {
    Object.keys(localStorage).forEach(function(k){ if(k.indexOf("aiku_m_") === 0) localStorage.removeItem(k); });
  } catch(e){}
  location.reload();
}
["nameInput", "yomiInput", "userInput"].forEach(function(id){
  $(id).addEventListener("keydown", function(e){ if(e.key === "Enter" && !e.isComposing) giveName(); });
});

// ================================================================ はじまり
fetch("data/lessons.json?t=" + Date.now()).then(function(r){ return r.json(); }).then(function(d){
  D = d; S = loadSave();
  S.level = Math.min(S.level, D.lessons.length);
  buildKeys();
  startWorker();
  cur = Math.min(S.level, D.lessons.length - 1);
  openLesson(cur);
  if(!S.name) openName(false);
  else say(line("hello"), "……（" + (S.yomi || S.name) + "がこっちを見ている）");
}).catch(function(e){
  $("hariiText").textContent = "教科書（data/lessons.json）が読み込めなかった。ページを読み込み直してみて。";
});
