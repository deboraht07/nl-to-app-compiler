from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.repair import validate_and_repair
from runtime.mock_data import generate_mock_data
from runtime.renderer import render_app

app = FastAPI(title="NL-to-App Compiler")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate(req: PromptRequest):
    start = time.time()
    log = []

    try:
        intent = extract_intent(req.prompt)
        design = design_system(intent.model_dump())
        schemas = generate_schemas(design.model_dump())
        schemas = validate_and_repair(schemas, log)

        elapsed = round(time.time() - start, 2)

        return JSONResponse({
            "success": True,
            "latency_seconds": elapsed,
            "intent": intent.model_dump(),
            "app_design": design.model_dump(),
            "ui_schema": schemas["ui_schema"].model_dump(),
            "api_schema": schemas["api_schema"].model_dump(),
            "db_schema": schemas["db_schema"].model_dump(),
            "auth_schema": schemas["auth_schema"].model_dump(),
            "repair_log": log,
        })
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return JSONResponse({
            "success": False,
            "latency_seconds": elapsed,
            "error": str(e),
            "repair_log": log,
        }, status_code=500)


@app.post("/preview", response_class=HTMLResponse)
def preview(req: PromptRequest):
    intent = extract_intent(req.prompt)
    design = design_system(intent.model_dump())
    schemas = generate_schemas(design.model_dump())
    log = []
    schemas = validate_and_repair(schemas, log)
    mock_data = generate_mock_data(schemas["db_schema"])
    return render_app(schemas, mock_data)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html><head>
    <meta charset="UTF-8">
    <title>NL-to-App Compiler</title>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
      * { box-sizing: border-box; margin:0; padding:0; }
      body {
        font-family: 'Inter', -apple-system, sans-serif;
        background:
          radial-gradient(circle at 10% -5%, rgba(155,107,255,0.22), transparent 42%),
          radial-gradient(circle at 90% 10%, rgba(233,75,178,0.14), transparent 38%),
          radial-gradient(circle at 50% 100%, rgba(79,141,255,0.08), transparent 50%),
          #08080A;
        color: #F2F2F3;
        min-height: 100vh;
      }
      .wrap { max-width: 980px; margin: 0 auto; padding: 56px 24px 64px; }
      .hero { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 40px; align-items: center; margin-bottom: 44px; }
      @media (max-width: 760px) { .hero { grid-template-columns: 1fr; } }
      .eyebrow {
        font-size: 11.5px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase;
        color: #B89BFF; margin-bottom: 16px; display:flex; align-items:center; gap:8px;
      }
      .eyebrow .dot { width:6px; height:6px; border-radius:50%; background:#9B6BFF; box-shadow:0 0 12px #9B6BFF; }
      h1 {
        font-family: 'Manrope', sans-serif; font-size: 38px; font-weight: 800;
        letter-spacing: -0.8px; line-height:1.12; margin-bottom: 16px;
      }
      h1 .accent { color: #B89BFF; }
      .sub { color: #9A9AA0; font-size: 14.5px; line-height: 1.65; max-width: 480px; }

      .terminal {
        background: #0E0E12; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;
        padding: 18px; font-family: 'JetBrains Mono', monospace; font-size: 12px;
        box-shadow: 0 24px 60px -20px rgba(155,107,255,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
        height: 230px; overflow: hidden;
      }
      .terminal-dots { display:flex; gap:6px; margin-bottom:14px; }
      .terminal-dots span { width:9px; height:9px; border-radius:50%; }
      .terminal-dots span:nth-child(1){ background:#E94BB2; }
      .terminal-dots span:nth-child(2){ background:#F5D94B; }
      .terminal-dots span:nth-child(3){ background:#7FE05E; }
      #typed { color: #8B8B92; white-space: pre-wrap; line-height:1.7; }
      #typed .key { color: #B89BFF; }
      #typed .str { color: #7FE05E; }
      #typed .cursor { display:inline-block; width:6px; height:13px; background:#B89BFF; animation: blink 1s step-end infinite; vertical-align:-2px; }
      @keyframes blink { 50% { opacity: 0; } }

      .panel {
        background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px; padding: 22px;
      }
      textarea {
        width:100%; min-height:104px; padding:14px; border:1px solid rgba(255,255,255,0.08);
        border-radius:12px; font-size:14px; background:rgba(0,0,0,0.3); color:#F2F2F3;
        font-family:'Inter',sans-serif; resize: vertical;
      }
      textarea:focus { outline: none; border-color: #9B6BFF; }
      .row { display:flex; align-items:center; justify-content:space-between; margin-top:14px; gap: 16px; }
      button.generate {
        background: linear-gradient(135deg, #A879FF, #7A4DFF); color:white; border:none;
        padding:13px 26px; border-radius:12px; font-weight:700; cursor:pointer; font-size:14px;
        box-shadow: 0 10px 26px -8px rgba(155,107,255,0.55); transition: transform .15s ease;
        white-space: nowrap;
      }
      button.generate:hover { transform: translateY(-1px); }
      button.generate:disabled { opacity:0.5; cursor:not-allowed; transform:none; }
      a.preview-link {
        color:#B89BFF; text-decoration:none; font-weight:700; font-size:13.5px;
        display:none; align-items:center; gap:6px; white-space:nowrap;
      }
      .output-label {
        font-size: 11px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase;
        color: #6B6B72; margin: 28px 0 10px;
      }
      pre {
        background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 18px; overflow:auto; max-height:440px;
        font-size: 12px; color: #C8C8CC; line-height:1.55; font-family:'JetBrains Mono', monospace;
      }
    </style></head>
    <body>
      <div class="wrap">
        <div class="hero">
          <div>
            <div class="eyebrow"><span class="dot"></span>NL-to-App Compiler</div>
           <h1>Describe your app.<br><span class="accent">Get a real schema.</span></h1>
            <p class="sub">
              This compiler turns a plain English description into a validated UI, API,
              database, and auth schema. It checks consistency across every layer and
              repairs anything that breaks.
            </p>
          </div>
          <div class="terminal">
            <div class="terminal-dots"><span></span><span></span><span></span></div>
            <div id="typed"></div>
          </div>
        </div>

        <div class="panel">
          <textarea id="prompt" placeholder="e.g. Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.">Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.</textarea>
          <div class="row">
            <button class="generate" id="genBtn" onclick="generate()">Generate schema</button>
            <a class="preview-link" id="previewLink" href="#">Open rendered preview →</a>
          </div>
        </div>

        <div class="output-label">Output</div>
        <pre id="output">Run a prompt to see the generated schema here.</pre>
      </div>
      <script>
        // Signature element: types out a tiny mock compile sequence on load
        const lines = [
          '> "Build a CRM with contacts..."',
          '',
          '{',
          '  "<span class=\\'key\\'>entities</span>": [<span class=\\'str\\'>"Contact"</span>],',
          '  "<span class=\\'key\\'>roles</span>": [<span class=\\'str\\'>"Admin"</span>],',
          '  "<span class=\\'key\\'>has_payments</span>": true',
          '}',
          '',
          '✓ validated · 0 errors'
        ];
        let li = 0, ci = 0;
        const el = document.getElementById('typed');
        function typeStep() {
          if (li >= lines.length) { el.innerHTML += '<span class="cursor"></span>'; return; }
          const line = lines[li];
          if (ci <= line.length) {
            const rendered = lines.slice(0, li).join('\\n') + (li>0?'\\n':'') + line.slice(0, ci);
            el.innerHTML = rendered.replace(/\\n/g, '<br>') + '<span class="cursor"></span>';
            ci += 2;
            setTimeout(typeStep, 18);
          } else {
            li++; ci = 0;
            setTimeout(typeStep, 120);
          }
        }
        typeStep();

        let lastPrompt = "";
        async function generate() {
          const prompt = document.getElementById('prompt').value;
          lastPrompt = prompt;
          const btn = document.getElementById('genBtn');
          btn.disabled = true;
          btn.textContent = "Generating...";
          document.getElementById('output').textContent = 'Running pipeline (multiple LLM calls, ~10-40s)...';
          document.getElementById('previewLink').style.display = 'none';

          try {
            const res = await fetch('/generate', {
              method: 'POST',
              headers: {'Content-Type':'application/json'},
              body: JSON.stringify({prompt})
            });
            const data = await res.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);

            if (data.success) {
              const link = document.getElementById('previewLink');
              link.style.display = 'inline-flex';
              link.onclick = async (e) => {
                e.preventDefault();
                const r = await fetch('/preview', {
                  method: 'POST',
                  headers: {'Content-Type':'application/json'},
                  body: JSON.stringify({prompt: lastPrompt})
                });
                const html = await r.text();
                const blob = new Blob([html], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                window.location.href = url;
              };
            }
          } finally {
            btn.disabled = false;
            btn.textContent = "Generate schema";
          }
        }
      </script>
    </body></html>
    """