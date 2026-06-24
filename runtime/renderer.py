# Rotating accent colors for cards — flat, vector-style, bold (inspired by dark CRM dashboard UIs)
ACCENT_COLORS = ["#E94BB2", "#7FE05E", "#4D8DFF", "#F5D94B", "#9B6BFF"]


def render_app(schemas: dict, mock_data: dict) -> str:
    ui = schemas["ui_schema"]

    nav_links = "".join(
        f'<a href="#{page.route.strip("/")}" class="nav-link">{page.name}</a>'
        for page in ui.pages
    )

    sections = ""
    color_index = 0

    for page in ui.pages:
        sections += f'<section id="{page.route.strip("/")}" class="page-section">'
        sections += f'<div class="page-header"><h2>{page.name}</h2>'
        sections += f'<span class="roles-badge">{", ".join(page.allowed_roles)}</span></div>'
        sections += '<div class="card-grid">'

        for comp in page.components:
            color = ACCENT_COLORS[color_index % len(ACCENT_COLORS)]
            color_index += 1

            if comp.type == "table":
                rows = mock_data.get(comp.entity, [])
                row_items = ""
                for row in rows[:4]:
                    primary = next(iter(row.values()), "—")
                    secondary_parts = [f"{k}: {v}" for k, v in list(row.items())[1:3]]
                    row_items += f"""
                    <div class="list-row">
                      <div class="avatar" style="background:{color}"></div>
                      <div class="row-text">
                        <div class="row-title">{primary}</div>
                        <div class="row-sub">{' · '.join(secondary_parts)}</div>
                      </div>
                    </div>"""
                sections += f"""
                <div class="dcard" style="background:{color}">
                  <div class="dcard-label">{comp.entity or 'Records'}</div>
                  {row_items or '<div class="row-sub">No records yet</div>'}
                </div>"""

            elif comp.type == "form":
                fields_html = "".join(
                    f'<input class="dinput" type="text" placeholder="{f}" />'
                    for f in comp.fields
                )
                sections += f"""
                <div class="dcard form-dcard" style="background:{color}">
                  <div class="dcard-label">{page.name}</div>
                  {fields_html}
                  <button class="dbutton" onclick="alert('Static preview — wire to /api endpoints for a real submit.')">Continue</button>
                </div>"""

            elif comp.type == "chart":
                heights = [38, 58, 48, 72, 60, 85, 70]
                width_step = 100 / (len(heights) - 1)
                points = " ".join(f"{round(i*width_step,1)},{round(100-h,1)}" for i, h in enumerate(heights))
                sections += f"""
                <div class="dcard chart-dcard" style="background:{color}">
                  <div class="dcard-label">Trend</div>
                  <svg class="trend-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <polyline points="{points}" fill="none" stroke="rgba(0,0,0,0.55)" stroke-width="3" vector-effect="non-scaling-stroke" />
                  </svg>
                </div>"""
            elif comp.type == "card":
                # Card components with no entity (e.g. dashboard summary cards) get
                # placeholder stat content instead of an empty box.
                stat_value = "1,284" if "dashboard" in page.name.lower() else "$4,920"
                stat_label = "Active this month" if "dashboard" in page.name.lower() else "Total this month"
                sections += f"""
                <div class="dcard stat-dcard" style="background:{color}">
                  <div class="dcard-label">{page.name} Summary</div>
                  <div class="stat-value">{stat_value}</div>
                  <div class="stat-sub">{stat_label}</div>
                </div>"""

            else:
                sections += f'<div class="dcard" style="background:{color}"><div class="dcard-label">{comp.type}</div></div>'

        sections += '</div></section>'

    first_page = ui.pages[0].name if ui.pages else "App"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{first_page} — Preview</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap');
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background:
      radial-gradient(circle at 15% 0%, rgba(155,107,255,0.10), transparent 45%),
      radial-gradient(circle at 85% 20%, rgba(233,75,178,0.08), transparent 40%),
      #0B0B0D;
    color: #F2F2F3;
    min-height: 100vh;
  }}
  .topbar {{
    background: rgba(20,20,23,0.7);
    backdrop-filter: blur(14px) saturate(140%);
    padding: 18px 32px;
    display: flex; align-items: center; gap: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: sticky; top: 0; z-index: 10;
  }}
  .logo {{
    font-family: 'Manrope', sans-serif;
    font-weight: 800; font-size: 17px; letter-spacing: -0.3px;
    margin-right: 28px; display:flex; align-items:center; gap:8px;
  }}
  .logo-dot {{ width:8px; height:8px; border-radius:50%; background:#9B6BFF; box-shadow:0 0 12px #9B6BFF; }}
  .nav-link {{
    color: #8B8B92; text-decoration: none; font-size: 13.5px; font-weight: 600;
    padding: 7px 14px; border-radius: 20px; transition: all .2s ease;
  }}
  .nav-link:hover {{ background: rgba(255,255,255,0.07); color: #fff; }}
  .page-section {{ padding: 48px 32px; max-width: 1140px; margin: 0 auto; animation: fadeIn .5s ease; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}
  .page-header {{ display:flex; align-items:baseline; justify-content:space-between; margin-bottom:26px; }}
  .page-header h2 {{
    font-family: 'Manrope', sans-serif; font-size: 27px; font-weight: 800; letter-spacing:-0.5px;
  }}
  .roles-badge {{
    font-size: 10.5px; font-weight: 700; color: #0B0B0D;
    background: linear-gradient(135deg, #F5D94B, #F0C419);
    padding: 5px 13px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.4px;
  }}
  .card-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 18px;
  }}
  .dcard {{
    border-radius: 24px; padding: 22px; color: #0B0B0D; min-height: 168px;
    display: flex; flex-direction: column; gap: 12px;
    box-shadow: 0 16px 32px -12px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.25);
    transition: transform .25s ease, box-shadow .25s ease;
    position: relative; overflow: hidden;
  }}
  .dcard::before {{
    content:""; position:absolute; inset:0; border-radius:24px;
    background: linear-gradient(135deg, rgba(255,255,255,0.18), transparent 55%);
    pointer-events:none;
  }}
  .dcard:hover {{ transform: translateY(-3px); box-shadow: 0 22px 38px -10px rgba(0,0,0,0.55); }}
  .dcard-label {{
    font-family:'Manrope', sans-serif; font-weight: 800; font-size: 14.5px;
    opacity: 0.8; text-transform: uppercase; letter-spacing: 0.3px;
  }}
  .list-row {{ display:flex; align-items:center; gap:11px; }}
  .avatar {{
    width:34px; height:34px; border-radius:50%; background:rgba(0,0,0,0.22); flex-shrink:0;
    border: 1.5px solid rgba(0,0,0,0.15);
  }}
  .row-title {{ font-weight:700; font-size:14px; }}
  .row-sub {{ font-size:12px; opacity:0.65; }}
  .form-dcard {{ align-items: stretch; }}
  .dinput {{
    border: none; border-radius: 13px; padding: 13px 15px; font-size: 13.5px;
    background: rgba(0,0,0,0.13); color: #0B0B0D; font-weight:600; font-family:'Inter',sans-serif;
  }}
  .dinput::placeholder {{ color: rgba(0,0,0,0.45); }}
  .dbutton {{
    background: #0B0B0D; color: #fff; border: none; padding: 13px;
    border-radius: 13px; font-weight: 700; cursor: pointer; margin-top: 4px;
    font-size: 13.5px; transition: opacity .2s;
  }}
  .dbutton:hover {{ opacity: 0.82; }}
  .chart-dcard {{ justify-content: flex-end; }}
  .stat-dcard {{ justify-content: center; }}
  .stat-value {{ font-family:'Manrope', sans-serif; font-size: 36px; font-weight: 800; letter-spacing: -0.5px; }}
  .stat-sub {{ font-size: 13px; opacity: 0.7; font-weight: 600; }}
</style>
</head>
<body>
  <div class="topbar">
    <span class="logo"><span class="logo-dot"></span>{first_page}</span>
    {nav_links}
  </div>
  {sections}
</body>
</html>"""
