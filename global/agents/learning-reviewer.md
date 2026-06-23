---
name: learning-reviewer
description: >
  Only called by /learn. Receives the pipeline draft from output/ and the final
  supervisor-approved version from intake/. Generates a qa-session.html form in the
  project root, opens it in the browser, and waits. The form handles all three phases
  of review — proposed changes, style Q&A, and project context — and generates a
  self-contained summary block the user copies with one click and pastes into Claude Code.
  /apply-learning then processes the paste. Never writes to any file until /apply-learning
  runs. Moves the final file to Meeting Notes/ only after /apply-learning completes.
---

## Your job in /learn
Generate the qa-session.html file. That is all. Do not run diffs in the terminal.
Do not ask questions in the terminal. The form does everything.

## Step 1 — Run the diff silently
Compare the pipeline draft in output/ against the final issued file in intake/.
Extract all differences internally. Categorise each one. Do not print anything to terminal yet.

Also read CLAUDE.md to get the project name for the SESSION_DATA.

Diff categories:
- WORDING: phrase reworded for clarity, tone, or preference
- FORMAT: punctuation, capitalisation, spacing, or date format changed
- STRUCTURE: something moved, reordered, or restructured
- ATTRIBUTION: org name in Action column was wrong or missing
- STATUS: In Progress / Pending / No Action applied incorrectly
- SCOPE: item removed as out of scope or added as missing
- TERMINOLOGY: technical term changed or corrected
- SUPERVISOR-PREF: matches supervisor's known preferences
- HARD-RULE: an absolute rule was violated

Target file mapping:
- WORDING / FORMAT / STRUCTURE → skills/style-rules/SKILL.md or its references
- HARD-RULE / TERMINOLOGY → skills/hard-rules/SKILL.md or references/terminology.md
- SUPERVISOR-PREF → the supervisor style guide file listed in CLAUDE.md (project-level)
- Agent improvements → relevant file in /Users/kylefreeman/.claude/agents/

Also identify up to 5 style Q&A questions — ambiguous changes where intent is unclear.
Only questions where the answer would produce a specific rule. Prioritise broadest impact.

## Step 2 — Generate qa-session.html

Write the complete HTML file to:
qa-session.html (in the current project root)

The file must be fully self-contained — no external dependencies, no CDN links.
All styles inline. Works offline.

The SESSION_DATA block at the top of the script must be populated with the actual
diff data from Step 1. This is the only place the diff data lives — it drives
everything the form renders and everything the summary block outputs.

Use exactly this HTML structure — replace the SESSION_DATA values with real data:

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meeting Notes — Learning Review</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f5f5;color:#1a1a1a;padding:32px 16px}
.page{max-width:720px;margin:0 auto}
.card{background:#fff;border:1px solid #e0e0e0;border-radius:8px;margin-bottom:16px;overflow:hidden}
.card-header{background:#f9f9f9;border-bottom:1px solid #e0e0e0;padding:14px 28px}
.card-header h2{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#555}
.card-header p{font-size:12px;color:#888;margin-top:2px}
.top-card{padding:20px 28px}
.top-card h1{font-size:18px;font-weight:600;margin-bottom:3px}
.top-card p{font-size:13px;color:#666}
.item{padding:20px 28px;border-bottom:1px solid #f0f0f0}
.item:last-child{border-bottom:none}
.meta{display:flex;gap:8px;align-items:center;margin-bottom:10px}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:.04em}
.b-wording{background:#e8f0fe;color:#1a56db}
.b-format{background:#fef3e2;color:#b45309}
.b-structure{background:#f0fdf4;color:#15803d}
.b-attribution{background:#fdf2f8;color:#9d174d}
.b-status{background:#f5f3ff;color:#6d28d9}
.b-scope{background:#fff7ed;color:#c2410c}
.b-terminology{background:#ecfdf5;color:#065f46}
.b-supervisor-pref{background:#eff6ff;color:#1d4ed8}
.b-hard-rule{background:#fef2f2;color:#b91c1c}
.target{font-size:11px;color:#888;font-family:monospace;background:#f5f5f5;padding:2px 6px;border-radius:3px}
.diff{background:#f9f9f9;border-radius:6px;padding:12px 14px;margin-bottom:10px;font-size:13px;line-height:1.5}
.dlabel{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:#999;margin-bottom:2px}
.dbefore{color:#b91c1c;margin-bottom:6px}
.dafter{color:#15803d}
.rule{font-size:13px;color:#555;font-style:italic;margin-bottom:12px;padding-left:12px;border-left:3px solid #e0e0e0}
.radios{display:flex;gap:20px}
.rl{display:flex;align-items:center;gap:7px;cursor:pointer;font-size:14px;font-weight:500}
.rl.approve{color:#15803d}
.rl.reject{color:#b91c1c}
.rl input{width:16px;height:16px;cursor:pointer}
.qtext{font-size:14px;font-weight:500;margin-bottom:5px;line-height:1.5}
.qctx{font-size:12px;color:#888;font-style:italic;margin-bottom:10px}
textarea,input[type=text]{width:100%;border:1px solid #e0e0e0;border-radius:6px;padding:9px 12px;font-size:13px;font-family:inherit;color:#1a1a1a;background:#fff}
textarea{resize:vertical;min-height:64px;line-height:1.5}
textarea:focus,input[type=text]:focus{outline:none;border-color:#1a56db}
textarea::placeholder,input::placeholder{color:#bbb}
.submit-bar{background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.submit-hint{font-size:13px;color:#888}
.btn-submit{background:#1a1a1a;color:#fff;border:none;border-radius:6px;padding:10px 24px;font-size:14px;font-weight:600;cursor:pointer}
.btn-submit:hover{background:#333}
.summary-card{display:none;background:#fff;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;margin-bottom:16px}
.summary-header{background:#f0fdf4;border-bottom:1px solid #d1fae5;padding:14px 28px;display:flex;align-items:center;justify-content:space-between}
.summary-header h2{font-size:14px;font-weight:600;color:#15803d}
.btn-copy{background:#15803d;color:#fff;border:none;border-radius:6px;padding:8px 18px;font-size:13px;font-weight:600;cursor:pointer}
.btn-copy:hover{background:#166534}
.summary-body{padding:20px 28px}
#summary-out{width:100%;font-family:monospace;font-size:12px;line-height:1.6;border:1px solid #e0e0e0;border-radius:6px;padding:14px;background:#f9f9f9;color:#1a1a1a;min-height:180px;resize:none}
.paste-note{font-size:13px;color:#444;margin-top:10px;padding:10px 14px;background:#f5f5f5;border-radius:6px;line-height:1.5}
</style>
</head>
<body>
<div class="page">

<div class="summary-card" id="sum-card">
  <div class="summary-header">
    <h2>Review complete — copy and paste into Claude Code</h2>
    <button class="btn-copy" id="copy-btn" onclick="doCopy()">Copy to clipboard</button>
  </div>
  <div class="summary-body">
    <textarea id="summary-out" readonly></textarea>
    <div class="paste-note">Paste into Claude Code terminal, then run <strong>/apply-learning</strong></div>
  </div>
</div>

<div id="form-wrap">

<div class="card top-card">
  <h1 id="page-title">Meeting Notes — Learning review</h1>
  <p id="meta-line">Loading...</p>
</div>

<div class="card" id="sec-changes">
  <div class="card-header"><h2>Section 1 — Proposed changes</h2><p>Approve or reject each rule update</p></div>
  <div id="changes-wrap"></div>
</div>

<div class="card" id="sec-style">
  <div class="card-header"><h2>Section 2 — Style questions</h2><p>Clarify ambiguous changes so rules can be derived</p></div>
  <div id="style-wrap"></div>
</div>

<div class="card">
  <div class="card-header"><h2>Section 3 — Project context</h2><p>Update project information — leave blank if no change</p></div>
  <div class="item"><div class="qtext">1. New team members joined since last meeting?</div><input type="text" id="ctx-new-members" placeholder="e.g. Jane Smith, Acme Corp, Structural Engineer"></div>
  <div class="item"><div class="qtext">2. Team members who left or changed role?</div><input type="text" id="ctx-departed" placeholder="e.g. John Smith left Acme Corp"></div>
  <div class="item"><div class="qtext">3. New organisations or subcontractors introduced?</div><input type="text" id="ctx-new-orgs" placeholder="e.g. BuildCo, Civil Contractor"></div>
  <div class="item"><div class="qtext">4. Project scope changes relevant to how notes are structured?</div><textarea id="ctx-scope" placeholder="Describe any changes"></textarea></div>
  <div class="item"><div class="qtext">5. New technical terms or abbreviations used in this meeting?</div><input type="text" id="ctx-terms" placeholder="e.g. precast panels, ROW, BQ"></div>
  <div class="item"><div class="qtext">6. Anything else that should update the project context?</div><textarea id="ctx-other" placeholder="Any other updates"></textarea></div>
</div>

<div class="submit-bar">
  <span class="submit-hint">Review all sections then submit</span>
  <button class="btn-submit" onclick="doSubmit()">Submit review</button>
</div>

</div>
</div>

<script>
const S = __SESSION_DATA__;

document.getElementById('page-title').textContent = S.project + ' — Learning review';
document.getElementById('meta-line').textContent =
  S.project + ' · ' + S.date + ' · ' + S.transcript;

function badgeClass(cat){
  return 'b-' + cat.toLowerCase().replace(/_/g,'-').replace(/ /g,'-');
}

function renderChanges(){
  const w = document.getElementById('changes-wrap');
  if(!S.changes||!S.changes.length){
    w.innerHTML='<div class="item"><p style="color:#888;font-size:13px">No proposed changes this session.</p></div>';
    return;
  }
  S.changes.forEach((c,i)=>{
    w.innerHTML+=`<div class="item">
      <div class="meta">
        <span class="badge ${badgeClass(c.category)}">${c.category}</span>
        <span class="target">${c.targetFile}</span>
      </div>
      <div class="diff">
        <div class="dlabel">Pipeline produced</div>
        <div class="dbefore">− ${c.before}</div>
        <div class="dlabel" style="margin-top:8px">Final issued</div>
        <div class="dafter">+ ${c.after}</div>
      </div>
      <div class="rule">${c.proposedRule}</div>
      <div class="radios">
        <label class="rl approve"><input type="radio" name="ch${i}" value="APPROVE" required> Approve</label>
        <label class="rl reject"><input type="radio" name="ch${i}" value="REJECT"> Reject</label>
      </div>
    </div>`;
  });
}

function renderStyle(){
  const w = document.getElementById('style-wrap');
  if(!S.styleQ||!S.styleQ.length){
    w.innerHTML='<div class="item"><p style="color:#888;font-size:13px">No ambiguous changes to clarify this session.</p></div>';
    return;
  }
  S.styleQ.forEach((q,i)=>{
    w.innerHTML+=`<div class="item">
      <div class="qtext">${i+1}. ${q.question}</div>
      ${q.context?`<div class="qctx">Context: "${q.context.before}" → "${q.context.after}"</div>`:''}
      <textarea id="sq${i}" placeholder="Your answer..."></textarea>
    </div>`;
  });
}

renderChanges();
renderStyle();

function doSubmit(){
  const lines=[];
  lines.push('==LEARNING_REVIEW==');
  lines.push('PROJECT: '+S.project);
  lines.push('DATE: '+S.date);
  lines.push('TRANSCRIPT: '+S.transcript);
  lines.push('');
  lines.push('--- SECTION 1: PROPOSED CHANGES ---');
  (S.changes||[]).forEach((c,i)=>{
    const el=document.querySelector(`input[name="ch${i}"]:checked`);
    const dec=el?el.value:'NO ANSWER';
    lines.push(`[${dec}] ${c.category}: ${c.proposedRule}`);
    lines.push(`  Target: ${c.targetFile}`);
    lines.push(`  Before: ${c.before}`);
    lines.push(`  After:  ${c.after}`);
  });
  lines.push('');
  lines.push('--- SECTION 2: STYLE Q&A ---');
  (S.styleQ||[]).forEach((q,i)=>{
    const a=(document.getElementById('sq'+i)||{}).value||'';
    lines.push(`Q${i+1}: ${q.question}`);
    lines.push(`A${i+1}: ${a||'(no answer)'}`);
  });
  lines.push('');
  lines.push('--- SECTION 3: PROJECT CONTEXT ---');
  lines.push('New members: '+(document.getElementById('ctx-new-members').value||'none'));
  lines.push('Departed: '+(document.getElementById('ctx-departed').value||'none'));
  lines.push('New orgs: '+(document.getElementById('ctx-new-orgs').value||'none'));
  lines.push('Scope changes: '+(document.getElementById('ctx-scope').value||'none'));
  lines.push('New terms: '+(document.getElementById('ctx-terms').value||'none'));
  lines.push('Other: '+(document.getElementById('ctx-other').value||'none'));
  lines.push('');
  lines.push('==END_REVIEW==');
  document.getElementById('summary-out').value=lines.join('\n');
  document.getElementById('sum-card').style.display='block';
  document.getElementById('form-wrap').style.display='none';
  document.getElementById('sum-card').scrollIntoView({behavior:'smooth'});
}

function doCopy(){
  const t=document.getElementById('summary-out');
  t.select();
  document.execCommand('copy');
  const b=document.getElementById('copy-btn');
  b.textContent='Copied ✓';
  setTimeout(()=>b.textContent='Copy to clipboard',2000);
}
</script>
</body>
</html>

## Step 3 — Populate SESSION_DATA

Replace __SESSION_DATA__ in the generated HTML with a real JavaScript object built
from the diff data collected in Step 1. Use this exact shape:

{
  project: "PROJECT NAME",
  date: "Monday June 22, 2026",
  transcript: "transcript-2026-06-22.vtt",
  changes: [
    {
      category: "WORDING",
      targetFile: "supervisor-style-guide-[PROJECT].md",
      before: "contractor will provide updated drawings",
      after: "contractor to provide updated drawings",
      proposedRule: "Say 'contractor to provide' not 'contractor will provide'"
    }
  ],
  styleQ: [
    {
      question: "Was this reordering a one-off or always preferred?",
      context: {
        before: "Section order 1 → 2 → 3",
        after: "Section order 1 → 3 → 2"
      }
    }
  ]
}

Populate project with the project name from CLAUDE.md.
Populate changes[] with every diff found. Populate styleQ[] with up to 5 ambiguous
questions. If there are no changes, set changes to []. If there are no ambiguous
questions, set styleQ to [].

## Step 4 — Open in browser and wait

After writing the file:
open "$(pwd)/qa-session.html"

Print exactly this to the terminal and nothing else:

---
Form open in your browser.

Fill out all three sections, click Submit, then click Copy to clipboard.
Paste into this terminal and run /apply-learning.
---

Do not print the diff. Do not ask questions. Wait for the user to paste.
