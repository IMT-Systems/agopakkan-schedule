# -*- coding: utf-8 -*-
import datetime
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

def day_card_html(day, wd_label, events):
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
        f'<div class="day-card-head">{day:02d}<span class="wd">({wd_label})</span></div>'
        f'<div class="day-card-body">{rows}</div>'
        f'</div>'
    )

schedule_html = ""
for day in sorted(EVENTS.keys()):
    real_events = [e for e in EVENTS[day] if not e.get("deco_only")]
    if not real_events:
        continue
    wd_label = WEEKDAY_JP[(datetime.date(YEAR, MONTH, day).weekday() + 1) % 7]
    schedule_html += day_card_html(day, wd_label, real_events)

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
    max-width: 640px;
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

  /* ---------- Schedule list (1 card per day) ---------- */
  .day-card {{
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--card);
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
  .place-link .pin {{ flex: 0 0 auto; margin-top: 3px; color: var(--accent); }}
  a.place-link:hover span {{ color: var(--accent); text-decoration: underline; }}
  .place-link.plain {{ color: var(--gray); font-weight: 400; }}
  .empty-state {{
    text-align: center;
    color: var(--gray);
    font-size: 13px;
    padding: 40px 0;
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

  /* ---------- Mobile ---------- */
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
        場所名をタップ／クリックすると、Google マップで確認できます（別タブで開きます）。<br>
        ※ ‹ › ボタンで表示する月を切り替えられます。Googleカレンダー連携時は、切り替えた月の最新の予定を自動取得します。
      </div>

      <div id="scheduleList">
        {schedule_html}
      </div>

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
      var wd = WD_JP[new Date(year, month - 1, day).getDay()];
      var rows = "";
      byDay[day].forEach(function(e) {{
        var link = e.mapsQuery ? mapsUrl(e.mapsQuery) : null;
        var placeHtml = link
          ? '<a class="place-link" href="' + link + '" target="_blank" rel="noopener">' + pinSvg() + '<span>' + escapeHtml(e.name) + '</span></a>'
          : '<span class="place-link plain">' + escapeHtml(e.name) + '</span>';
        rows += '<div class="event-row"><span class="time">' + escapeHtml(e.time) + '</span>' + placeHtml + '</div>';
      }});
      html += '<div class="day-card">'
        + '<div class="day-card-head">' + pad2(day) + '<span class="wd">(' + wd + ')</span></div>'
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
