<h1 align="center">Resume JD Analyzer</h1>

<p align="center">
  AI-powered candidate evaluation using resume relevance, repository intelligence, semantic scoring, and LLM reasoning.
</p>

<p align="center">
  <a href="#overview">Overview</a> &bull;
  <a href="#strengths">Strengths</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#setup">Setup</a> &bull;
  <a href="#docker">Docker</a> &bull;
  <a href="#extensions">Extensions</a>
</p>

<hr />

<h2 id="overview">Overview</h2>

<p>
  <strong>Resume JD Analyzer</strong> is a Streamlit application that evaluates how well a candidate matches a job description by combining four signals:
</p>

<ul>
  <li>Resume-to-job-description relevance</li>
  <li>Repository code similarity</li>
  <li>Documentation and configuration relevance</li>
  <li>LLM-based hiring reasoning</li>
</ul>

<p>
  Instead of relying only on keyword matching or sending everything directly to an LLM, this project builds an evidence-driven evaluation pipeline.
  It analyzes the candidate's resume, inspects a GitHub repository, extracts meaningful code and non-code chunks, ranks them semantically, and then
  asks an LLM to produce strengths, gaps, reasoning, and a final score.
</p>

<h2 id="why-it-matters">Why It Matters</h2>

<p>Most hiring tools fail in one of these ways:</p>

<ul>
  <li>They are too shallow and only match resume keywords.</li>
  <li>They are too expensive and too ungrounded because they depend entirely on LLM prompts.</li>
</ul>

<p>
  This project takes a stronger middle path: retrieval, static analysis, embeddings, and LLM judgment are combined so the final output is more explainable,
  more grounded, and closer to how an experienced engineering manager evaluates candidates.
</p>

<h2 id="strengths">Core Strengths</h2>

<ul>
  <li><strong>Multi-signal scoring</strong>: blends resume match, code similarity, documentation similarity, and LLM evaluation.</li>
  <li><strong>Repository-aware analysis</strong>: inspects what the candidate has actually built, not just what they claim.</li>
  <li><strong>Grounded LLM reasoning</strong>: the model sees top-ranked evidence instead of the entire repository dump.</li>
  <li><strong>Code + non-code coverage</strong>: documentation, config, infra, and notebooks all participate in the analysis.</li>
  <li><strong>Explainable output</strong>: the UI shows weighted score breakdowns, strengths, gaps, and reasoning.</li>
  <li><strong>Modular design</strong>: ingestion, chunking, embedding, scoring, and reasoning are separated into focused modules.</li>
  <li><strong>Container-ready</strong>: ships with Docker support for repeatable deployment.</li>
</ul>

<h2 id="what-it-does">What It Does</h2>

<ol>
  <li>Accepts a PDF resume, a job description, and a GitHub repository URL.</li>
  <li>Extracts text from the resume PDF.</li>
  <li>Clones the repository to temporary storage.</li>
  <li>Separates repository content into code, docs, config, and infra.</li>
  <li>Builds a lightweight dependency graph from discovered definitions and calls.</li>
  <li>Chunks code and non-code content into analyzable units.</li>
  <li>Embeds repository chunks and job-description text using <code>SentenceTransformer</code>.</li>
  <li>Ranks code and docs via cosine similarity.</li>
  <li>Scores the resume with a BM25 + cosine hybrid.</li>
  <li>Calls Groq-hosted <code>llama-3.3-70b-versatile</code> for qualitative evaluation.</li>
  <li>Returns a final weighted score, breakdown, strengths, gaps, and reasoning.</li>
</ol>

<h2 id="scoring">Scoring Model</h2>

<p>The current weighting in <a href="./app.py">app.py</a> is:</p>

<table>
  <thead>
    <tr>
      <th>Signal</th>
      <th>Weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Resume Match</td>
      <td>20%</td>
    </tr>
    <tr>
      <td>Code Similarity</td>
      <td>30%</td>
    </tr>
    <tr>
      <td>Documentation Similarity</td>
      <td>10%</td>
    </tr>
    <tr>
      <td>LLM Evaluation</td>
      <td>40%</td>
    </tr>
  </tbody>
</table>

<p>
  This gives the system a strong reasoning layer while keeping semantic retrieval and visible evidence at the center of the decision.
</p>

<h2 id="architecture">Architecture</h2>

<pre><code>Resume PDF + JD + GitHub Repo
          |
          v
   PDF text extraction
          |
          v
    Repository cloning
          |
          v
 File classification + reading
          |
          v
  Code chunking / doc chunking
          |
          v
 Dependency graph generation
          |
          v
 Embedding generation
          |
          v
 Cosine + BM25 scoring
          |
          v
   Evidence selection
          |
          v
 LLM reasoning on top evidence
          |
          v
 Final weighted evaluation UI</code></pre>

<h3>Main Modules</h3>

<ul>
  <li><a href="./frontend.py">frontend.py</a>: Streamlit UI and result rendering.</li>
  <li><a href="./app.py">app.py</a>: end-to-end pipeline orchestration.</li>
  <li><a href="./clone.py">clone.py</a>: repository cloning, file reading, categorization, cleanup.</li>
  <li><a href="./code_chunck.py">code_chunck.py</a>: regex-based function chunking for code files.</li>
  <li><a href="./otherchunking.py">otherchunking.py</a>: chunking for docs, config, and infra content.</li>
  <li><a href="./graph.py">graph.py</a>: dependency graph creation and summarization.</li>
  <li><a href="./embeding.py">embeding.py</a>: chunk embedding generation.</li>
  <li><a href="./final.py">final.py</a>: semantic ranking and top-k evidence selection.</li>
  <li><a href="./text_embedding.py">text_embedding.py</a>: embeddings for job description and resume text.</li>
  <li><a href="./BM.py">BM.py</a>: lexical scoring for resume matching.</li>
  <li><a href="./llmreason.py">llmreason.py</a>: Groq LLM call and fallback handling.</li>
  <li><a href="./parser.py">parser.py</a>: PDF parsing with PyMuPDF.</li>
  <li><a href="./mode_loader.py">mode_loader.py</a>: shared sentence-transformer loading.</li>
</ul>

<h2 id="tech-stack">Tech Stack</h2>

<ul>
  <li>Python 3.11</li>
  <li>Streamlit</li>
  <li>SentenceTransformers</li>
  <li>NumPy / scikit-learn</li>
  <li>PyMuPDF</li>
  <li>Groq API</li>
  <li>System git</li>
  <li>Docker</li>
</ul>

<h2 id="setup">Local Setup</h2>

<h3>Prerequisites</h3>

<ul>
  <li>Python 3.11</li>
  <li>git</li>
  <li>Internet access for repository cloning, model download, and Groq inference</li>
</ul>

<h3>Environment Variables</h3>

<p>Create a <code>.env</code> file in the project root:</p>

<pre><code>GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token_optional</code></pre>

<ul>
  <li><code>GROQ_API_KEY</code> is required for LLM evaluation.</li>
  <li><code>HF_TOKEN</code> is optional, but useful in some Hugging Face environments.</li>
</ul>

<h3>Run Locally</h3>

<p>Create the environment:</p>

<pre><code>python -m venv .venv</code></pre>

<p>Windows:</p>

<pre><code>.venv\Scripts\activate</code></pre>

<p>macOS / Linux:</p>

<pre><code>source .venv/bin/activate</code></pre>

<p>Install dependencies and start the app:</p>

<pre><code>pip install -r requirements.txt
streamlit run frontend.py</code></pre>

<p>Open <code>http://localhost:8501</code>.</p>

<h2 id="docker">Docker</h2>

<p>This repository includes <a href="./Dockerfile">Dockerfile</a> and <a href="./.dockerignore">.dockerignore</a>.</p>

<h3>Build</h3>

<pre><code>docker build -t resume-jd-analyzer .</code></pre>

<h3>Run</h3>

<pre><code>docker run --rm -p 8501:8501 -e GROQ_API_KEY=your_groq_api_key -e HF_TOKEN=your_huggingface_token resume-jd-analyzer</code></pre>

<p>Then open <code>http://localhost:8501</code>.</p>

<h2 id="operations">Operational Notes</h2>

<ul>
  <li>Logs are written to <code>app.log</code>.</li>
  <li>Repositories are cloned into temporary directories and deleted after processing.</li>
  <li>The sentence-transformer model is loaded once and reused in-process.</li>
  <li>The UI is server-rendered through Streamlit.</li>
</ul>

<h2 id="production">Production Readiness</h2>

<ul>
  <li><strong>Explainable scoring</strong>: users can see where the final score comes from.</li>
  <li><strong>Evidence-first reasoning</strong>: LLM evaluation is scoped to ranked evidence.</li>
  <li><strong>Modular pipeline</strong>: easier to test, replace, or scale individual stages.</li>
  <li><strong>Containerized delivery</strong>: simpler deployment across environments.</li>
  <li><strong>Low-friction interface</strong>: accessible to recruiters, hiring managers, and evaluators.</li>
</ul>

<h2 id="extensions">Where We Can Extend</h2>

<h3>Retrieval and Ranking</h3>

<ul>
  <li>Add vector-store caching for repeated repository evaluations.</li>
  <li>Use stronger ranking strategies such as weighted top-k or fusion methods.</li>
  <li>Introduce repo-size-aware sampling for large repositories.</li>
</ul>

<h3>Static Analysis</h3>

<ul>
  <li>Replace regex chunking with AST-based parsing for higher precision.</li>
  <li>Enrich the dependency graph with imports, inheritance, modules, and service boundaries.</li>
  <li>Add quality signals from tests, project structure, and architecture patterns.</li>
</ul>

<h3>Resume Intelligence</h3>

<ul>
  <li>Extract structured skills, tenure, role level, and domain expertise.</li>
  <li>Add support for DOCX and plain-text resumes.</li>
  <li>Normalize skill taxonomies across equivalent technologies.</li>
</ul>

<h3>LLM Evaluation</h3>

<ul>
  <li>Add role-specific prompts for backend, frontend, ML, DevOps, and data roles.</li>
  <li>Support multiple model backends for comparison and calibration.</li>
  <li>Add stricter schema validation and retry handling for malformed responses.</li>
</ul>

<h3>Platform and Product</h3>

<ul>
  <li>Persist historical analyses for side-by-side candidate comparisons.</li>
  <li>Add authentication, audit trails, and role-based access.</li>
  <li>Expose the pipeline through an API in addition to the Streamlit app.</li>
  <li>Add async execution for large repos and concurrent workloads.</li>
</ul>

<h3>Reliability and MLOps</h3>

<ul>
  <li>Add automated tests for parsing, chunking, scoring, and response validation.</li>
  <li>Add CI for linting, tests, and Docker builds.</li>
  <li>Add metrics, tracing, and structured observability.</li>
  <li>Introduce model/version pinning and calibration datasets.</li>
</ul>

<h2 id="limitations">Current Limitations</h2>

<ul>
  <li><strong>Regex-based parsing</strong>: lightweight and flexible, but less precise than AST-based parsing.</li>
  <li><strong>Simplified BM25</strong>: useful for local scoring, but not a full retrieval engine.</li>
  <li><strong>No persistent storage</strong>: results are not yet saved for later review.</li>
  <li><strong>No auth layer</strong>: current UI is best suited for demos, internal tools, or controlled environments.</li>
  <li><strong>External dependencies</strong>: runtime depends on GitHub access, model availability, and Groq connectivity.</li>
  <li><strong>No automated test suite yet</strong>: this should be added before serious scale-up.</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li>Recruiter screening for engineering roles</li>
  <li>Technical pre-screening before interview loops</li>
  <li>Internal talent mobility matching</li>
  <li>Engineering manager review support</li>
  <li>Hackathon or demo candidate analysis</li>
</ul>

<h2 id="status">Project Status</h2>

<p>
  The project is already strong as a practical intelligent screening tool because it does not stop at resume keywords. It inspects candidate code,
  ranks relevant evidence, and uses that evidence to drive reasoning.
</p>

<p>
  The clearest next step is to harden precision, scale, and reliability around the solid pipeline that already exists.
</p>
