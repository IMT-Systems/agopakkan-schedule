# -*- coding: utf-8 -*-
import calendar
import json
import os
from urllib.parse import quote
from events import EVENTS
from config import GOOGLE_CALENDAR_API_KEY, GOOGLE_CALENDAR_ID

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "assets", "logo_b64.txt")) as f:
    LOGO_B64 = f.read().strip()

with open(os.path.join(SCRIPT_DIR, "assets", "avatar_b64.txt")) as f:
    AVATAR_B64 = f.read().strip()

YEAR, MONTH = 2026, 8
WEEKDAY_LABELS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
WEEKDAY_JP = ["日", "月", "火", "水", "木", "金", "土"]

cal = calendar.Calendar(firstweekday=6)  # Sunday-start
weeks = cal.monthdatescalendar(YEAR, MONTH)

PIN_SVG = (
    '<svg class="pin" viewBox="0 0 24 24" width="10" height="10" aria-hidden="true">'
    '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" '
    'fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<circle cx="12" cy="9" r="2.2" fill="currentColor"/>'
    '</svg>'
)

def maps_url(query):
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"

def day_cell(d):
    if d.month != MONTH:
        return '<td class="day-cell empty"></td>'
    day_num = d.day
    wd = d.weekday()  # Mon=0..Sun=6
    wd_idx = (wd + 1) % 7  # convert to Sun=0..Sat=6
    is_sun = wd_idx == 0
    is_sat = wd_idx == 6
    cls = "day-cell"
    if is_sun:
        cls += " is-sun"
    if is_sat:
        cls += " is-sat"

    events = EVENTS.get(day_num, [])
    events_html = ""
    if events:
        real_events = [e for e in events if not e.get("deco_only")]
        for e in real_events:
            link = maps_url(e["maps"]) if e.get("maps") else None
            name_html = (
                f'<a class="event-name" href="{link}" target="_blank" rel="noopener">{PIN_SVG}<span>{e["name"]}</span></a>'
                if link else f'<span class="event-name plain">{e["name"]}</span>'
            )
            events_html += (
                f'<div class="event">'
                f'{name_html}'
                f'<div class="event-time">{e["time"]}</div>'
                f'</div>'
            )

    num_color = "sun" if is_sun else ("sat" if is_sat else "")
    wd_label = f'<span class="wd-label">{WEEKDAY_JP[wd_idx]}</span>' if events else ""
    has_event_cls = " has-event" if events else ""
    return (
        f'<td class="{cls}{has_event_cls}" data-day="{day_num}" data-wd="{WEEKDAY_JP[wd_idx]}">'
        f'<div class="date-row"><span class="date-num {num_color}">{day_num:02d}</span>{wd_label}</div>'
        f'<div class="events">{events_html}</div>'
        f'</td>'
    )

weeks_html = ""
for week in weeks:
    weeks_html += "<tr>" + "".join(day_cell(d) for d in week) + "</tr>\n"

header_html = "".join(
    f'<th class="{"sat-head" if i==6 else ("sun-head" if i==0 else "")}">{lbl}</th>'
    for i, lbl in enumerate(WEEKDAY_LABELS)
)

# Fallback event data exposed to JS (name/time/maps only) so month navigation
# can re-show the originally curated August schedule even without a live API key.
FALLBACK_EVENTS_JSON = json.dumps(
    {
        str(day): [
            {"name": e["name"], "time": e["time"], "maps": e.get("maps", "")}
            for e in evs
            if not e.get("deco_only")
        ]
        for day, evs in EVENTS.items()
    },
    ensure_ascii=False,
)

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>あごぱっかーん {MONTH}月 出店スケジュール</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Noto+Sans+JP:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #F3F3F1;
    --card: #FFFFFF;
    --ink: #1A1A1A;
    --gray: #767676;
    --line: #EAEAEA;
    --accent: #FF5A1F;
    --accent-soft: #FFF0E8;
    --sat: #2563EB;
    --sat-soft: #EEF3FE;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 40px 16px;
    background: var(--bg);
    font-family: 'Plus Jakarta Sans', 'Noto Sans JP', sans-serif;
    color: var(--ink);
    display: flex;
    justify-content: center;
  }}
  .poster {{
    max-width: 920px;
    width: 100%;
    background: var(--card);
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--line);
    box-shadow: 0 20px 50px rgba(0,0,0,0.06);
  }}

  /* ---------- Header ---------- */
  .hero {{
    padding: 34px 32px 26px;
    text-align: center;
    border-bottom: 1px solid var(--line);
  }}
  .avatar {{
    width: 76px; height: 76px;
    margin: 0 auto 14px;
    border-radius: 50%;
    border: 1px solid var(--line);
    overflow: hidden;
  }}
  .avatar img {{
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
  }}
  .brand {{
    font-family: 'Plus Jakarta Sans', 'Noto Sans JP', sans-serif;
    font-weight: 800;
    color: var(--ink);
    font-size: clamp(28px, 5vw, 40px);
    letter-spacing: -0.5px;
    margin: 0 0 12px;
  }}
  .month-banner {{
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    padding: 7px 20px;
    border-radius: 20px;
    min-width: 150px;
  }}
  .month-nav {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }}
  .nav-btn {{
    width: 30px; height: 30px;
    border-radius: 50%;
    border: 1px solid var(--line);
    background: var(--card);
    color: var(--ink);
    font-size: 15px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 0;
    transition: background 0.15s, color 0.15s;
  }}
  .nav-btn:hover {{ background: var(--accent); color: #fff; border-color: var(--accent); }}

  .body-pad {{ padding: 26px 30px 30px; }}

  .subnote {{
    text-align: center;
    font-size: 11px;
    color: var(--gray);
    background: #FAFAFA;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 0 0 22px;
    line-height: 1.9;
  }}

  /* ---------- Calendar ---------- */
  table.calendar {{
    width: 100%;
    table-layout: fixed;
    border-collapse: separate;
    border-spacing: 5px;
  }}
  table.calendar th {{
    color: var(--gray);
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 2px;
    padding: 0 0 10px;
    text-align: center;
  }}
  table.calendar th.sun-head {{ color: var(--accent); }}
  table.calendar th.sat-head {{ color: var(--sat); }}

  td.day-cell {{
    vertical-align: top;
    width: 14.28%;
    height: 120px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 8px 8px 6px;
    position: relative;
  }}
  td.day-cell.empty {{ background: transparent; border: 1px dashed var(--line); }}
  td.day-cell.is-sun {{ background: var(--accent-soft); }}
  td.day-cell.is-sat {{ background: var(--sat-soft); }}
  td.day-cell.has-event {{ border-color: #DDD; }}

  .date-row {{ display: flex; align-items: baseline; justify-content: space-between; }}
  .date-num {{
    font-family: 'Plus Jakarta Sans', 'Noto Sans JP', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--ink);
  }}
  .date-num.sun {{ color: var(--accent); }}
  .date-num.sat {{ color: var(--sat); }}
  .wd-label {{ font-size: 9px; color: var(--gray); }}

  .events {{ margin-top: 7px; }}
  .event {{ margin-bottom: 7px; }}
  .event-name {{
    display: flex;
    align-items: flex-start;
    gap: 4px;
    font-size: 10.5px;
    line-height: 1.35;
    font-weight: 600;
    color: var(--ink);
    text-decoration: none;
  }}
  .event-name .pin {{ flex: 0 0 auto; margin-top: 3px; color: var(--accent); }}
  a.event-name:hover span {{ color: var(--accent); text-decoration: underline; }}
  .event-name.plain {{ color: var(--gray); font-weight: 400; }}
  .event-time {{
    font-size: 9.5px;
    color: var(--gray);
    margin-top: 2px;
  }}

  /* ---------- Footer ---------- */
  .footer {{ margin-top: 20px; text-align: center; }}
  .footer .line {{
    height: 1px; width: 100%; background: var(--line); margin-bottom: 16px;
  }}
  .signoff {{
    font-weight: 700;
    font-size: 14px;
    color: var(--accent);
    margin-bottom: 8px;
  }}
  .footnotes {{
    font-size: 10.5px;
    color: var(--gray);
    line-height: 1.9;
  }}
  .credit {{
    text-align: right;
    margin-top: 16px;
  }}
  .credit-logo {{
    height: 15.6px;
    width: auto;
    opacity: 0.7;
  }}

  /* ---------- Mobile: keep all 7 columns on one screen width ---------- */
  @media (max-width: 480px) {{
    body {{ padding: 20px 6px; }}
    .poster {{ border-radius: 16px; }}
    .hero {{ padding: 22px 14px 18px; }}
    .avatar {{ width: 60px; height: 60px; margin-bottom: 10px; }}
    .brand {{ font-size: clamp(22px, 8vw, 28px); margin-bottom: 8px; }}
    .month-banner {{ font-size: 11px; padding: 5px 14px; min-width: 120px; }}
    .nav-btn {{ width: 26px; height: 26px; font-size: 13px; }}
    .month-nav {{ gap: 6px; }}
    .body-pad {{ padding: 16px 8px 18px; }}
    .subnote {{ font-size: 9.5px; padding: 8px 8px; margin: 0 0 14px; }}

    table.calendar {{ border-spacing: 2px; }}
    table.calendar th {{ font-size: 8px; letter-spacing: 0.5px; padding: 0 0 6px; }}

    td.day-cell {{ height: 88px; padding: 3px 3px 2px; border-radius: 6px; }}
    .date-num {{ font-size: 10px; }}
    .wd-label {{ font-size: 6.5px; }}
    .events {{ margin-top: 2px; }}
    .event {{ margin-bottom: 3px; }}
    .event-name {{ font-size: 6.8px; gap: 1px; line-height: 1.15; }}
    .event-name .pin {{ width: 6px; height: 6px; margin-top: 1px; }}
    .event-time {{ font-size: 6px; margin-top: 0; }}

    .footer {{ margin-top: 10px; }}
    .signoff {{ font-size: 13px; }}
    .footnotes {{ font-size: 8.5px; }}
    .credit {{ margin-top: 10px; }}
    .credit-logo {{ height: 12px; }}
  }}
</style>
</head>
<body>
  <div class="poster">
    <div class="hero">
      <div class="avatar"><img src="data:image/png;base64,{AVATAR_B64}" alt="agopakkan"></div>
      <h1 class="brand">あごぱっかーん</h1>
      <div class="month-nav">
        <button type="button" class="nav-btn" id="prevMonthBtn" aria-label="前の月">‹</button>
        <div class="month-banner" id="monthBanner">{YEAR}年{MONTH}月 出店スケジュール</div>
        <button type="button" class="nav-btn" id="nextMonthBtn" aria-label="次の月">›</button>
      </div>
    </div>

    <div class="body-pad">
      <div class="subnote">
        出店場所名をタップ／クリックすると、Google マップで場所を確認できます（別タブで開きます）。<br>
        ※ ‹ › ボタンで表示する月を切り替えられます。Googleカレンダー連携時は、切り替えた月の最新の予定を自動取得します。
      </div>

      <table class="calendar">
        <thead><tr>{header_html}</tr></thead>
        <tbody id="calendarBody">
          {weeks_html}
        </tbody>
      </table>

      <div class="footer">
        <div class="line"></div>
        <div class="signoff">Have a good burger time.</div>
        <div class="footnotes">
          天候や状況により、変更・中止となる場合がございます。<br>
          最新情報はSNSをご確認ください。
        </div>
        <div class="credit">
          <img class="credit-logo" src="data:image/png;base64,{LOGO_B64}" alt="IMT-Systems">
        </div>
      </div>
    </div>
  </div>

  <script>
  // ---------------------------------------------------------------
  // Googleカレンダー自動連携設定
  // 1. Google Cloud Consoleで「Google Calendar API」を有効化したAPIキーを発行
  // 2. 下の apiKey に貼り付けて保存すれば、ページを開く・月を切り替えるたびに
  //    その月のGoogleカレンダーの予定を自動取得してこのカレンダーに反映します。
  // 3. APIキーが未設定の間は、8月のみ生成時点の予定（フォールバック）を表示し、
  //    他の月は空欄のカレンダー枠だけを表示します。
  // ---------------------------------------------------------------
  const CONFIG = {{
    apiKey: "{GOOGLE_CALENDAR_API_KEY}", // config.py の GOOGLE_CALENDAR_API_KEY を編集してください
    calendarId: "{GOOGLE_CALENDAR_ID}"
  }};

  const FALLBACK_YEAR = {YEAR};
  const FALLBACK_MONTH = {MONTH};
  const FALLBACK_EVENTS = {FALLBACK_EVENTS_JSON};
  const WD_JP = ["日", "月", "火", "水", "木", "金", "土"];

  var currentYear = FALLBACK_YEAR;
  var currentMonth = FALLBACK_MONTH;
  var requestSeq = 0;

  function mapsUrl(q) {{
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(q);
  }}

  function pinSvg() {{
    return '<svg class="pin" viewBox="0 0 24 24" width="10" height="10" aria-hidden="true">'
      + '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
      + '<circle cx="12" cy="9" r="2.2" fill="currentColor"/></svg>';
  }}

  function escapeHtml(s) {{
    return String(s).replace(/[&<>"']/g, function(c) {{
      return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c];
    }});
  }}

  function pad2(n) {{ return String(n).padStart(2, "0"); }}

  function parseEvent(ev) {{
    var day, timeLabel;
    if (ev.start && ev.start.dateTime) {{
      var m = ev.start.dateTime.match(/^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})T(\\d{{2}}):(\\d{{2}})/);
      if (!m) return null;
      day = parseInt(m[3], 10);
      var startHM = m[4] + ":" + m[5];
      var endHM = "";
      if (ev.end && ev.end.dateTime) {{
        var m2 = ev.end.dateTime.match(/T(\\d{{2}}):(\\d{{2}})/);
        if (m2) endHM = m2[1] + ":" + m2[2];
      }}
      timeLabel = endHM ? (startHM + "〜" + endHM) : startHM;
    }} else if (ev.start && ev.start.date) {{
      var md = ev.start.date.match(/^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})/);
      if (!md) return null;
      day = parseInt(md[3], 10);
      timeLabel = "終日";
    }} else {{
      return null;
    }}
    return {{
      day: day,
      name: ev.summary || "(無題の予定)",
      time: timeLabel,
      mapsQuery: ev.location || ev.summary || ""
    }};
  }}

  function renderCell(td, evs) {{
    var wd = td.dataset.wd || "";
    var day = parseInt(td.dataset.day, 10);
    var numColor = td.classList.contains("is-sun") ? "sun" : (td.classList.contains("is-sat") ? "sat" : "");
    var eventsHtml = "";
    evs.forEach(function(e) {{
      var link = e.mapsQuery ? mapsUrl(e.mapsQuery) : null;
      var nameHtml = link
        ? '<a class="event-name" href="' + link + '" target="_blank" rel="noopener">' + pinSvg() + '<span>' + escapeHtml(e.name) + '</span></a>'
        : '<span class="event-name plain">' + escapeHtml(e.name) + '</span>';
      eventsHtml += '<div class="event">' + nameHtml + '<div class="event-time">' + escapeHtml(e.time) + '</div></div>';
    }});
    var wdLabel = evs.length ? ('<span class="wd-label">' + wd + '</span>') : "";
    td.classList.toggle("has-event", evs.length > 0);
    td.innerHTML = '<div class="date-row"><span class="date-num ' + numColor + '">' + pad2(day) + '</span>' + wdLabel + '</div>'
      + '<div class="events">' + eventsHtml + '</div>';
  }}

  function buildGridHtml(year, month) {{
    var first = new Date(year, month - 1, 1);
    var startWd = first.getDay(); // 0=Sun..6=Sat
    var daysInMonth = new Date(year, month, 0).getDate();
    var cells = [];
    for (var i = 0; i < startWd; i++) cells.push(null);
    for (var d = 1; d <= daysInMonth; d++) cells.push(d);
    while (cells.length % 7 !== 0) cells.push(null);

    var html = "";
    for (var r = 0; r < cells.length; r += 7) {{
      html += "<tr>";
      for (var c = 0; c < 7; c++) {{
        var day = cells[r + c];
        if (day === null) {{
          html += '<td class="day-cell empty"></td>';
        }} else {{
          var isSun = c === 0, isSat = c === 6;
          var cls = "day-cell" + (isSun ? " is-sun" : "") + (isSat ? " is-sat" : "");
          var numColor = isSun ? "sun" : (isSat ? "sat" : "");
          html += '<td class="' + cls + '" data-day="' + day + '" data-wd="' + WD_JP[c] + '">'
            + '<div class="date-row"><span class="date-num ' + numColor + '">' + pad2(day) + '</span></div>'
            + '<div class="events"></div></td>';
        }}
      }}
      html += "</tr>";
    }}
    return html;
  }}

  function loadMonth(year, month) {{
    currentYear = year;
    currentMonth = month;
    document.getElementById("calendarBody").innerHTML = buildGridHtml(year, month);
    document.getElementById("monthBanner").textContent = year + "年" + month + "月 出店スケジュール";

    if (year === FALLBACK_YEAR && month === FALLBACK_MONTH) {{
      document.querySelectorAll("td.day-cell[data-day]").forEach(function(td) {{
        var raw = FALLBACK_EVENTS[td.dataset.day] || [];
        var evs = raw.map(function(e) {{ return {{ name: e.name, time: e.time, mapsQuery: e.maps || e.name }}; }});
        renderCell(td, evs);
      }});
    }}

    refreshForMonth(year, month);
  }}

  function prevMonth() {{
    var y = currentMonth === 1 ? currentYear - 1 : currentYear;
    var m = currentMonth === 1 ? 12 : currentMonth - 1;
    loadMonth(y, m);
  }}

  function nextMonth() {{
    var y = currentMonth === 12 ? currentYear + 1 : currentYear;
    var m = currentMonth === 12 ? 1 : currentMonth + 1;
    loadMonth(y, m);
  }}

  // Googleカレンダーへの問い合わせは「JST（日本時間）で日付が変わってから最初の1回」だけ行い、
  // 結果はブラウザのlocalStorageにその日の日付付きでキャッシュします。
  // 同じ日のうちに再訪・月切り替えをしてもキャッシュを使い回すことで、
  // 実質「1日1回、0:00以降に更新」という挙動になります。
  function todayJst() {{
    return new Intl.DateTimeFormat("en-CA", {{
      timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit"
    }}).format(new Date()); // "YYYY-MM-DD"
  }}

  function cacheKey(year, month) {{
    return "agopakkan_cache_" + year + "-" + pad2(month);
  }}

  function readCache(year, month) {{
    try {{
      var raw = localStorage.getItem(cacheKey(year, month));
      return raw ? JSON.parse(raw) : null;
    }} catch (e) {{ return null; }}
  }}

  function writeCache(year, month, byDay) {{
    try {{
      localStorage.setItem(cacheKey(year, month), JSON.stringify({{ date: todayJst(), byDay: byDay }}));
    }} catch (e) {{ /* localStorage無効時は無視してその都度取得 */ }}
  }}

  function renderByDay(byDay) {{
    document.querySelectorAll("td.day-cell[data-day]").forEach(function(td) {{
      var day = parseInt(td.dataset.day, 10);
      renderCell(td, byDay[day] || []);
    }});
  }}

  async function refreshForMonth(year, month) {{
    if (!CONFIG.apiKey || CONFIG.apiKey.indexOf("YOUR_") === 0) {{
      console.log("[あごぱっかーんカレンダー] Google Calendar APIキー未設定のため、" + year + "年" + month + "月はフォールバック／空欄表示です。");
      return;
    }}
    var today = todayJst();
    var cached = readCache(year, month);
    if (cached && cached.date === today) {{
      renderByDay(cached.byDay);
      console.log("[あごぱっかーんカレンダー] " + year + "年" + month + "月は本日(" + today + ")取得済みのキャッシュを表示中です。");
      return;
    }}

    var mySeq = ++requestSeq;
    try {{
      var nextY = month === 12 ? year + 1 : year;
      var nextM = month === 12 ? 1 : month + 1;
      var timeMin = year + "-" + pad2(month) + "-01T00:00:00+09:00";
      var timeMax = nextY + "-" + pad2(nextM) + "-01T00:00:00+09:00";
      var url = "https://www.googleapis.com/calendar/v3/calendars/"
        + encodeURIComponent(CONFIG.calendarId) + "/events"
        + "?key=" + encodeURIComponent(CONFIG.apiKey)
        + "&timeMin=" + encodeURIComponent(timeMin)
        + "&timeMax=" + encodeURIComponent(timeMax)
        + "&singleEvents=true&orderBy=startTime&timeZone=" + encodeURIComponent("Asia/Tokyo");
      var res = await fetch(url);
      if (!res.ok) throw new Error("HTTP " + res.status);
      var data = await res.json();
      if (mySeq !== requestSeq) return; // ユーザーが別の月に移動済み。古い結果は破棄。
      var byDay = {{}};
      (data.items || []).forEach(function(ev) {{
        var info = parseEvent(ev);
        if (!info) return;
        (byDay[info.day] = byDay[info.day] || []).push(info);
      }});
      writeCache(year, month, byDay);
      renderByDay(byDay);
      console.log("[あごぱっかーんカレンダー] " + year + "年" + month + "月の最新の予定を取得し、本日分としてキャッシュしました。");
    }} catch (err) {{
      if (mySeq !== requestSeq) return;
      console.warn("[あごぱっかーんカレンダー] Googleカレンダーの取得に失敗しました。", err);
      if (cached) {{
        renderByDay(cached.byDay); // 取得失敗時は古いキャッシュがあればそれで表示
      }}
    }}
  }}

  document.getElementById("prevMonthBtn").addEventListener("click", prevMonth);
  document.getElementById("nextMonthBtn").addEventListener("click", nextMonth);

  // 初回表示はサーバー側で生成済みのHTML（{MONTH}月）をそのまま使い、
  // ちらつきを避けつつGoogleカレンダーの最新情報だけを上書き取得します。
  document.addEventListener("DOMContentLoaded", function() {{
    refreshForMonth(currentYear, currentMonth);
  }});
  </script>
</body>
</html>
"""

out_path = os.path.join(SCRIPT_DIR, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print("saved", out_path)
