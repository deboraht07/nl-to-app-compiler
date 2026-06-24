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
    <html><head><title>NL-to-App Compiler</title>
    <style>
      body { font-family: -apple-system, sans-serif; background:#0B0B0D; color:#F2F2F3;
             max-width:700px; margin:60px auto; padding:0 20px; }
      h1 { color:#9B6BFF; }
      textarea { width:100%; height:100px; padding:12px; border:1px solid #333;
                 border-radius:8px; font-size:14px; background:#18181B; color:#fff; }
      button { background:#9B6BFF; color:white; border:none; padding:12px 20px;
               border-radius:8px; font-weight:600; cursor:pointer; margin-top:10px; }
      pre { background:#18181B; border:1px solid #333; border-radius:8px; padding:16px;
            overflow:auto; max-height:500px; font-size:12px; color:#ccc; }
      a.btn { display:inline-block; margin-top:10px; color:#9B6BFF; text-decoration:none; font-weight:600; }
    </style></head>
    <body>
      <h1>⚡ NL-to-App Compiler</h1>
      <p>Describe an app in plain English. The system extracts intent, designs the architecture,
      generates UI/API/DB/Auth schemas, validates them, and auto-repairs any inconsistencies.</p>
      <textarea id="prompt" placeholder="Build a CRM with login, contacts, dashboard...">Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.</textarea><br>
      <button onclick="generate()">Generate</button>
      <a class="btn" id="previewLink" href="#" target="_blank" style="display:none;">→ Open rendered app preview</a>
      <pre id="output">Output JSON will appear here...</pre>
      <script>
        async function generate() {
          const prompt = document.getElementById('prompt').value;
          document.getElementById('output').textContent = 'Generating... (multiple LLM calls, may take 10-20s)';
          const res = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({prompt})
          });
          const data = await res.json();
          document.getElementById('output').textContent = JSON.stringify(data, null, 2);

          const link = document.getElementById('previewLink');
          link.href = '#';
          link.style.display = 'inline-block';
          link.onclick = async (e) => {
            e.preventDefault();
            const r = await fetch('/preview', {
              method: 'POST',
              headers: {'Content-Type':'application/json'},
              body: JSON.stringify({prompt})
            });
            const html = await r.text();
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.location.href = url;
          };
        }
      </script>
    </body></html>
    """