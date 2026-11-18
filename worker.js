// 試験官（ブラウザの中で Python を動かす係）
// 画面とは別の場所（ワーカー）で動くので、無限ループしても画面は固まらない
// （固まったら画面側がこのワーカーごと作り直す）
var PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";
importScripts(PYODIDE_URL + "pyodide.js");

var py = null;
var printed = [];

async function init(files, version) {
  py = await loadPyodide({ indexURL: PYODIDE_URL });
  py.setStdout({ batched: function (s) { printed.push(s); } });
  py.setStderr({ batched: function (s) { printed.push(s); } });
  await py.loadPackage(["numpy"]);
  try { await py.loadPackage(["sqlite3"]); } catch (e) { /* 入っている版なら不要 */ }
  py.FS.mkdirTree("/home/pyodide/aiku");
  for (var i = 0; i < files.length; i++) {
    var res = await fetch("py/" + files[i] + "?v=" + version);
    if (!res.ok) throw new Error(files[i] + " を読み込めなかった（" + res.status + "）");
    py.FS.writeFile("/home/pyodide/aiku/" + files[i], await res.text());
  }
  py.runPython("import sys, os\nsys.path.insert(0, '/home/pyodide/aiku')\nos.chdir('/home/pyodide')\nimport m_checks");
}

self.onmessage = async function (e) {
  var m = e.data;
  try {
    if (m.type === "init") {
      await init(m.files, m.version);
      self.postMessage({ type: "ready" });
    } else if (m.type === "run") {
      printed = [];
      py.globals.set("_aiku_code", m.code);
      var out = py.runPython("m_checks.run(_aiku_code, " + Number(m.lid) + ")");
      self.postMessage({ type: "result", id: m.id, data: out, printed: printed.join("\n") });
    } else if (m.type === "chat") {
      printed = [];
      py.globals.set("_aiku_code", m.code);
      py.globals.set("_aiku_text", m.text);
      var r = py.runPython("m_checks.chat(_aiku_code, _aiku_text)");
      self.postMessage({ type: "chat", id: m.id, data: r });
    }
  } catch (err) {
    self.postMessage({ type: m.type === "init" ? "init_error" : "fail", id: m.id, error: String(err && err.message || err) });
  }
};
