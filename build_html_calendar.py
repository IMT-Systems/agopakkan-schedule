# -*- coding: utf-8 -*-
import datetime
import json
import os
from urllib.parse import quote
from events import EVENTS
from config import GOOGLE_CALENDAR_API_KEY, GOOGLE_CALENDAR_ID

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "assets", "top_b64.txt")) as f:
    TOP_LOGO_B64 = f.read().strip()

with open(os.path.join(SCRIPT_DIR, "assets", "photo1_b64.txt")) as f:
    PHOTO1_B64 = f.read().strip()

with open(os.path.join(SCRIPT_DIR, "assets", "photo2_b64.txt")) as f:
    PHOTO2_B64 = f.read().strip()

YEAR, MONTH = 2026, 8
WEEKDAY_JP = ["日", "月", "火", "水", "木", "金", "土"]

PIN_SVG = (
    '<svg class="pin" viewBox="0 0 24 24" width="10" height="10" aria-hidden="true">'
    '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" '
    'fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<circle cx="12" cy="9" r="2.2" fill="currentColor"/>'
    '</svg>'
)

def maps_url(query):
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"

def day_card_html(day, wd_label, wd_idx, events):
    num_cls = "sun" if wd_idx == 0 else ("sat" if wd_idx == 6 else "")
    rows = ""
    for e in events:
        link = maps_url(e["maps"]) if e.get("maps") else None
        place_html = (
            f'<a class="place-link" href="{link}" target="_blank" rel="noopener">{PIN_SVG}<span>{e["name"]}</span></a>'
            if link else f'<span class="place-link plain">{e["name"]}</span>'
        )
        rows += (
            f'<div class="event-row">'
            f'<span class="time">{e["time"]}</span>'
            f'{place_html}'
            f'</div>'
        )
    return (
        f'<div class="day-card">'
        f'<div class="day-card-head"><span class="daynum {num_cls}">{day:02d}</span><span class="wd">({wd_label})</span></div>'
        f'<div class="day-card-body">{rows}</div>'
        f'</div>'
    )

schedule_html = ""
for day in sorted(EVENTS.keys()):
    real_events = [e for e in EVENTS[day] if not e.get("deco_only")]
    if not real_events:
        continue
    wd_idx = (datetime.date(YEAR, MONTH, day).weekday() + 1) % 7
    wd_label = WEEKDAY_JP[wd_idx]
    schedule_html += day_card_html(day, wd_label, wd_idx, real_events)

if not schedule_html:
    schedule_html = '<div class="empty-state">この月の出店予定はまだありません。</div>'

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
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Kalam:wght@400;700&family=Noto+Sans+JP:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #F3EFE7;
    --ink: #241A10;
    --gray: #767676;
    --line: #EAEAEA;
    --accent: #FF5A1F;
    --sat: #2563EB;
    --green: #23814B;
    --grad-bottom: #FF9A1E;
    --schedule-bg: #FFF7DC;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    font-family: "Arial Black", "Noto Sans JP", sans-serif;
    color: var(--ink);
  }}

  /* ---------- Hero (burger poster) ---------- */
  .hero {{
    position: relative;
    width: 100%;
    max-width: 1100px;
    min-height: 700px;
    margin: 30px auto;
    overflow: hidden;
    background: linear-gradient(135deg, #d87513 0%, #f7b82a 45%, #ffe14d 100%);
    border-radius: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,.18);
  }}
  .hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-conic-gradient(from -10deg, rgba(255,255,255,.08) 0deg 12deg, transparent 12deg 30deg);
    opacity: .7;
    pointer-events: none;
  }}
  .hero::after {{
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(80,40,0,.18) 1px, transparent 1px);
    background-size: 6px 6px;
    opacity: .25;
    pointer-events: none;
  }}
  .catch {{
    position: absolute;
    top: 40px;
    left: 45px;
    color: #214d28;
    font-family: 'Kalam', cursive;
    font-size: 32px;
    font-weight: bold;
    transform: rotate(-3deg);
    z-index: 3;
  }}
  .stars {{
    margin-top: 8px;
    color: #c92e1f;
    font-size: 24px;
    letter-spacing: 8px;
  }}
  .avatar {{
    position: absolute;
    top: 30px;
    right: 320px;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: #f6d36c;
    border: 8px solid #f8e6b5;
    overflow: hidden;
    z-index: 5;
  }}
  .avatar img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .beef {{
    position: absolute;
    right: 35px;
    top: 35px;
    z-index: 5;
    padding: 18px 30px;
    color: #8e2618;
    background: #f5d47c;
    border: 5px solid #8e2618;
    font-size: 25px;
    font-weight: 900;
    transform: rotate(-7deg);
    text-align: center;
  }}
  .burger {{
    position: absolute;
    left: -30px;
    bottom: -40px;
    width: 57%;
    max-width: 850px;
    z-index: 2;
    filter: drop-shadow(12px 18px 12px rgba(0,0,0,.35));
  }}
  .burger img {{ display: block; width: 100%; height: auto; border-radius: 20px; }}
  .title {{
    position: absolute;
    top: 230px;
    right: 50px;
    z-index: 5;
    margin: 0;
    color: #7d2016;
    font-size: clamp(45px, 6vw, 90px);
    font-weight: 900;
    letter-spacing: -4px;
    text-shadow: 4px 4px 0 #f8e6b5, 7px 7px 0 rgba(100,30,0,.35);
    white-space: nowrap;
  }}
  .burger-time {{
    position: absolute;
    right: 50px;
    top: 370px;
    z-index: 5;
    min-width: 460px;
    padding: 24px 45px;
    background: #bd2419;
    color: white;
    text-align: center;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 2px;
    transform: rotate(-2deg);
    border: 7px solid #f8e6b5;
    box-shadow: 0 8px 0 rgba(100,30,0,.35);
    clip-path: polygon(3% 0, 97% 0, 100% 50%, 97% 100%, 3% 100%, 0 50%);
  }}
  .schedule {{
    position: absolute;
    right: 60px;
    bottom: 45px;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .schedule button {{
    width: 56px;
    height: 56px;
    border: 0;
    border-radius: 50%;
    background: #f8e6b5;
    color: #222;
    font-size: 34px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,.25);
    transition: .2s;
  }}
  .schedule button:hover {{ transform: scale(1.1); }}
  .schedule-title {{
    padding: 20px 40px;
    min-width: 400px;
    border-radius: 50px;
    background: #126b38;
    color: white;
    text-align: center;
    font-size: 26px;
    font-weight: 900;
    box-shadow: 0 6px 10px rgba(0,0,0,.25);
  }}

  /* ---------- Content panel ---------- */
  .panel {{
    max-width: 1100px;
    margin: 0 auto 30px;
    background: #fff;
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--line);
    box-shadow: 0 20px 50px rgba(0,0,0,0.06);
    font-family: 'Plus Jakarta Sans', 'Noto Sans JP', sans-serif;
  }}
  .body-pad {{ padding: 26px 30px 30px; }}

  .subnote {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-align: left;
    font-size: 15px;
    color: var(--gray);
    background: #FAFAFA;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 16px;
    margin: 0 0 22px;
    line-height: 1.6;
  }}
  .subnote .subnote-pin {{
    flex: 0 0 auto;
    width: 22px; height: 22px;
    margin-top: 1px;
    color: var(--green);
  }}

  /* ---------- Schedule list (1 card per day) ---------- */
  .day-card {{
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--schedule-bg);
    padding: 14px 18px;
    margin-bottom: 12px;
  }}
  .day-card:last-child {{ margin-bottom: 0; }}
  .day-card-head {{
    display: flex;
    align-items: baseline;
    gap: 7px;
    font-weight: 800;
    font-size: 16px;
    color: var(--ink);
    padding-bottom: 9px;
    margin-bottom: 9px;
    border-bottom: 1px solid var(--line);
  }}
  .day-card-head .daynum.sun {{ color: #E2402D; }}
  .day-card-head .daynum.sat {{ color: var(--sat); }}
  .day-card-head .wd {{
    font-size: 11px;
    font-weight: 500;
    color: var(--gray);
  }}
  .day-card-body .event-row {{
    display: flex;
    align-items: baseline;
    gap: 14px;
    padding: 6px 0;
  }}
  .day-card-body .event-row + .event-row {{
    border-top: 1px dashed var(--line);
  }}
  .event-row .time {{
    flex: 0 0 auto;
    min-width: 92px;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--gray);
  }}
  .place-link {{
    display: flex;
    align-items: flex-start;
    gap: 5px;
    font-size: 13px;
    line-height: 1.4;
    font-weight: 600;
    color: var(--ink);
    text-decoration: none;
  }}
  .place-link .pin {{ flex: 0 0 auto; margin-top: 3px; color: var(--green); }}
  a.place-link:hover span {{ color: var(--accent); text-decoration: underline; }}
  .place-link.plain {{ color: var(--gray); font-weight: 400; }}
  .empty-state {{
    text-align: center;
    color: var(--gray);
    font-size: 13px;
    padding: 40px 0;
  }}

  /* ---------- Footer (poster style) ---------- */
  .footer-bar {{
    margin-top: 24px;
    background: var(--grad-bottom);
    color: #fff;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    text-align: center;
  }}
  .footer-bar .fb-side {{
    font-weight: 800;
    font-size: 10.5px;
    line-height: 1.5;
    letter-spacing: 0.5px;
  }}
  .footer-bar .fb-mid {{
    font-family: 'Kalam', cursive;
    font-weight: 700;
    font-size: 14px;
  }}
  .footnotes {{
    font-size: 10.5px;
    color: var(--gray);
    text-align: center;
    line-height: 1.9;
    margin-top: 18px;
    padding: 0 30px 24px;
  }}

  /* ---------- Mobile ---------- */
  @media (max-width: 900px) {{
    .hero {{ min-height: 350px; border-radius: 0; margin: 0 0 16px; }}
    .catch {{ left: 15px; top: 14px; font-size: 13px; }}
    .stars {{ font-size: 9px; }}
    .avatar {{ width: 46px; height: 46px; top: 10px; right: 128px; border-width: 3px; }}
    .beef {{ right: 8px; top: 10px; padding: 6px 9px; font-size: 10px; border-width: 2px; }}
    .burger {{ left: 10px; top: 72px; bottom: auto; width: 40%; max-width: 170px; }}
    .title {{ top: 78px; right: 15px; font-size: 30px; letter-spacing: -2px; }}
    .burger-time {{ right: 15px; top: 126px; min-width: 0; width: 56%; padding: 8px 8px; font-size: 14px; border-width: 3px; }}
    .schedule {{ top: 292px; bottom: auto; left: 10px; right: 15px; justify-content: center; gap: 6px; }}
    .schedule-title {{ min-width: 0; padding: 10px 18px; font-size: 14px; }}
    .schedule button {{ width: 38px; height: 38px; font-size: 20px; }}
  }}
  @media (max-width: 480px) {{
    .panel {{ border-radius: 0; }}
    .body-pad {{ padding: 16px 8px 4px; }}
    .subnote {{ font-size: 12px; padding: 11px 12px; margin: 0 0 14px; }}
    .subnote .subnote-pin {{ width: 17px; height: 17px; }}

    .day-card {{ padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; }}
    .day-card-head {{ font-size: 13.5px; padding-bottom: 6px; margin-bottom: 6px; }}
    .day-card-body .event-row {{
      flex-wrap: wrap;
      column-gap: 8px;
      row-gap: 2px;
      padding: 6px 0;
    }}
    .event-row .time {{ min-width: 0; font-size: 10.5px; }}
    .place-link {{ font-size: 11.5px; }}

    .footer-bar {{ margin-top: 16px; padding: 12px 14px; flex-wrap: wrap; row-gap: 4px; }}
    .footer-bar .fb-side {{ font-size: 8.5px; }}
    .footer-bar .fb-mid {{ font-size: 12px; flex: 1 1 100%; order: -1; }}
    .footnotes {{ font-size: 8.5px; padding: 0 12px 12px; }}
  }}
</style>
</head>
<body>
  <section class="hero">
    <div class="catch">
      Always<br>
      Fresh &amp; Delicious!
      <div class="stars">★ ★ ★</div>
    </div>

    <div class="avatar"><img src="data:image/jpeg;base64,{TOP_LOGO_B64}" alt="あごぱっかーん"></div>

    <div class="beef">100% BEEF<br>100% SMILE.</div>

    <div class="burger"><img src="data:image/jpeg;base64,{PHOTO1_B64}" alt="あごぱっかーんバーガー"></div>

    <h1 class="title">あごぱっかーん</h1>

    <div class="burger-time">★ BURGER TIME! ★</div>

    <div class="schedule">
      <button type="button" id="prevMonthBtn" aria-label="前の月">‹</button>
      <div class="schedule-title" id="monthBanner">{YEAR}年{MONTH}月 出店スケジュール</div>
      <button type="button" id="nextMonthBtn" aria-label="次の月">›</button>
    </div>
  </section>

  <div class="panel">
    <div class="body-pad">
      <div class="subnote">
        {PIN_SVG.replace('class="pin"', 'class="subnote-pin"')}
        <span>
          場所名をタップ／クリックすると、Google マップで確認できます（別タブで開きます）。
        </span>
      </div>

      <div id="scheduleList">
        {schedule_html}
      </div>
    </div>

    <div class="footer-bar">
      <div class="fb-side">GOOD FOOD<br>GOOD MOOD</div>
      <div class="fb-mid">Have a good burger time.</div>
      <div class="fb-side">AGOPAKKAN BURGER<br>あごぱっかーん</div>
    </div>
    <div class="footnotes">
      天候や状況により、変更・中止となる場合がございます。最新情報はSNSをご確認ください。
    </div>
  </div>

  <script>
  // ---------------------------------------------------------------
  // Googleカレンダー自動連携設定
  // 1. Google Cloud Consoleで「Google Calendar API」を有効化したAPIキーを発行
  // 2. 下の apiKey に貼り付けて保存すれば、ページを開く・月を切り替えるたびに
  //    その月のGoogleカレンダーの予定を自動取得してこのカレンダーに反映します。
  // 3. APIキーが未設定の間は、8月のみ生成時点の予定（フォールバック）を表示し、
  //    他の月は空欄表示です。
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

  function buildScheduleHtml(year, month, byDay) {{
    var days = Object.keys(byDay)
      .map(Number)
      .filter(function(d) {{ return byDay[d] && byDay[d].length; }})
      .sort(function(a, b) {{ return a - b; }});

    if (!days.length) {{
      return '<div class="empty-state">この月の出店予定はまだありません。</div>';
    }}

    var html = "";
    days.forEach(function(day) {{
      var wdIdx = new Date(year, month - 1, day).getDay();
      var wd = WD_JP[wdIdx];
      var numCls = wdIdx === 0 ? "sun" : (wdIdx === 6 ? "sat" : "");
      var rows = "";
      byDay[day].forEach(function(e) {{
        var link = e.mapsQuery ? mapsUrl(e.mapsQuery) : null;
        var placeHtml = link
          ? '<a class="place-link" href="' + link + '" target="_blank" rel="noopener">' + pinSvg() + '<span>' + escapeHtml(e.name) + '</span></a>'
          : '<span class="place-link plain">' + escapeHtml(e.name) + '</span>';
        rows += '<div class="event-row"><span class="time">' + escapeHtml(e.time) + '</span>' + placeHtml + '</div>';
      }});
      html += '<div class="day-card">'
        + '<div class="day-card-head"><span class="daynum ' + numCls + '">' + pad2(day) + '</span><span class="wd">(' + wd + ')</span></div>'
        + '<div class="day-card-body">' + rows + '</div>'
        + '</div>';
    }});
    return html;
  }}

  function renderSchedule(year, month, byDay) {{
    document.getElementById("scheduleList").innerHTML = buildScheduleHtml(year, month, byDay);
  }}

  function loadMonth(year, month) {{
    currentYear = year;
    currentMonth = month;
    document.getElementById("monthBanner").textContent = year + "年" + month + "月 出店スケジュール";

    if (year === FALLBACK_YEAR && month === FALLBACK_MONTH) {{
      var byDay = {{}};
      Object.keys(FALLBACK_EVENTS).forEach(function(d) {{
        byDay[d] = FALLBACK_EVENTS[d].map(function(e) {{
          return {{ name: e.name, time: e.time, mapsQuery: e.maps || e.name }};
        }});
      }});
      renderSchedule(year, month, byDay);
    }} else {{
      document.getElementById("scheduleList").innerHTML = '<div class="empty-state">読み込み中…</div>';
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

  async function refreshForMonth(year, month) {{
    if (!CONFIG.apiKey || CONFIG.apiKey.indexOf("YOUR_") === 0) {{
      console.log("[あごぱっかーんカレンダー] Google Calendar APIキー未設定のため、" + year + "年" + month + "月はフォールバック／空欄表示です。");
      return;
    }}
    var today = todayJst();
    var cached = readCache(year, month);
    if (cached && cached.date === today) {{
      renderSchedule(year, month, cached.byDay);
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
      renderSchedule(year, month, byDay);
      console.log("[あごぱっかーんカレンダー] " + year + "年" + month + "月の最新の予定を取得し、本日分としてキャッシュしました。");
    }} catch (err) {{
      if (mySeq !== requestSeq) return;
      console.warn("[あごぱっかーんカレンダー] Googleカレンダーの取得に失敗しました。", err);
      if (cached) {{
        renderSchedule(year, month, cached.byDay); // 取得失敗時は古いキャッシュがあればそれで表示
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
