"""
Comprehensive skills taxonomy + recruiter intelligence database.
Used for ATS scoring, gap analysis, and top-1% suggestions.
"""

# ── Programming Languages ─────────────────────────────────────────────────────
LANGUAGES = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "julia",
    "haskell", "elixir", "erlang", "clojure", "f#", "dart", "lua", "perl",
    "shell", "bash", "powershell", "groovy", "cobol", "fortran", "assembly",
    "objective-c", "vba", "sql", "plsql", "tsql",
]

# ── Frontend ──────────────────────────────────────────────────────────────────
FRONTEND = [
    "react", "react.js", "vue", "vue.js", "angular", "svelte", "next.js",
    "nuxt.js", "gatsby", "remix", "html", "css", "sass", "scss", "less",
    "tailwind", "tailwindcss", "bootstrap", "material-ui", "chakra-ui",
    "styled-components", "emotion", "webpack", "vite", "rollup", "esbuild",
    "babel", "eslint", "prettier", "jest", "vitest", "cypress", "playwright",
    "storybook", "webgl", "webassembly", "wasm", "webrtc", "websockets",
    "graphql", "apollo", "relay", "redux", "zustand", "mobx", "recoil",
    "rxjs", "react native", "expo", "flutter", "ionic",
]

# ── Backend / APIs ────────────────────────────────────────────────────────────
BACKEND = [
    "node.js", "express", "fastapi", "django", "flask", "rails",
    "spring", "spring boot", "gin", "echo", "fiber", "actix", "axum",
    "fastify", "nestjs", "laravel", "symfony", "asp.net", ".net core",
    "grpc", "graphql", "rest", "restful", "openapi", "swagger",
    "oauth", "jwt", "websockets", "microservices", "event-driven",
    "cqrs", "domain-driven design", "ddd", "hexagonal architecture",
    "clean architecture", "solid", "tdd", "bdd",
]

# ── Databases ─────────────────────────────────────────────────────────────────
DATABASES = [
    "postgresql", "postgres", "mysql", "mariadb", "sqlite", "oracle",
    "sql server", "mssql", "mongodb", "cassandra", "dynamodb", "cosmosdb",
    "redis", "memcached", "elasticsearch", "opensearch", "neo4j", "dgraph",
    "influxdb", "timescaledb", "cockroachdb", "planetscale", "vitess",
    "snowflake", "bigquery", "redshift", "databricks", "dbt",
    "prisma", "sqlalchemy", "hibernate", "sequelize", "typeorm",
]

# ── Cloud / Infrastructure ────────────────────────────────────────────────────
CLOUD = [
    "aws", "amazon web services", "gcp", "google cloud", "azure",
    "ec2", "s3", "lambda", "rds", "dynamodb", "cloudfront", "route53",
    "eks", "ecs", "fargate", "sqs", "sns", "kinesis", "glue", "athena",
    "cloud run", "cloud functions", "gke", "bigquery", "pubsub",
    "azure devops", "aks", "azure functions", "blob storage",
    "terraform", "pulumi", "cloudformation", "cdk", "ansible", "chef",
    "puppet", "packer",
]

# ── DevOps / Platform ─────────────────────────────────────────────────────────
DEVOPS = [
    "kubernetes", "k8s", "docker", "helm", "istio", "envoy", "linkerd",
    "prometheus", "grafana", "datadog", "new relic", "splunk", "elk",
    "elasticsearch", "logstash", "kibana", "jaeger", "zipkin", "opentelemetry",
    "ci/cd", "github actions", "gitlab ci", "jenkins", "circleci", "argocd",
    "flux", "gitops", "terraform", "ansible", "linux", "nginx", "apache",
    "haproxy", "vault", "consul", "nomad", "kafka", "rabbitmq", "nats",
    "celery", "airflow", "dagster", "prefect",
]

# ── ML / AI / Data ────────────────────────────────────────────────────────────
ML_AI = [
    "machine learning", "deep learning", "neural networks", "nlp",
    "natural language processing", "computer vision", "llm", "large language models",
    "transformers", "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "pandas", "numpy", "scipy", "matplotlib",
    "seaborn", "plotly", "hugging face", "langchain", "llamaindex", "openai",
    "fine-tuning", "rag", "retrieval augmented generation", "embeddings",
    "vector database", "pinecone", "weaviate", "chromadb", "faiss",
    "mlops", "mlflow", "weights & biases", "wandb", "dvc", "feature engineering",
    "a/b testing", "statistical analysis", "bayesian", "reinforcement learning",
    "spark", "pyspark", "hadoop", "hive", "flink", "kafka streams",
]

# ── Security ──────────────────────────────────────────────────────────────────
SECURITY = [
    "appsec", "devsecops", "soc 2", "iso 27001", "owasp", "penetration testing",
    "pen testing", "threat modeling", "security audit", "vulnerability assessment",
    "siem", "iam", "zero trust", "cryptography", "ssl/tls", "pki",
    "oauth", "saml", "mfa", "rbac", "abac", "compliance", "gdpr", "hipaa",
    "pci dss", "cve", "cwe", "burp suite", "metasploit", "nmap", "wireshark",
]

# ── Product / Design ──────────────────────────────────────────────────────────
PRODUCT_DESIGN = [
    "product management", "product strategy", "roadmap", "okrs", "kpis",
    "user research", "user interviews", "usability testing", "a/b testing",
    "ux", "ui", "figma", "sketch", "adobe xd", "invision", "principle",
    "prototyping", "wireframing", "design systems", "accessibility", "wcag",
    "data analysis", "sql", "amplitude", "mixpanel", "segment", "looker",
    "tableau", "power bi", "growth hacking", "funnel optimization",
    "product-led growth", "plg", "go-to-market", "gtm",
]

# ── Leadership / Management ───────────────────────────────────────────────────
LEADERSHIP = [
    "engineering management", "team leadership", "mentoring", "coaching",
    "hiring", "performance reviews", "1:1s", "roadmap planning",
    "cross-functional", "stakeholder management", "executive communication",
    "p&l", "budget management", "vendor management", "agile", "scrum",
    "kanban", "sprint planning", "retrospectives", "incident management",
    "on-call", "sla", "slo", "sre", "post-mortem",
]

# ── All skills flat (for matching) ────────────────────────────────────────────
ALL_SKILLS = sorted(set(
    LANGUAGES + FRONTEND + BACKEND + DATABASES +
    CLOUD + DEVOPS + ML_AI + SECURITY + PRODUCT_DESIGN + LEADERSHIP
))

SKILL_CATEGORIES = {
    "Programming Languages": LANGUAGES,
    "Frontend": FRONTEND,
    "Backend & APIs": BACKEND,
    "Databases": DATABASES,
    "Cloud": CLOUD,
    "DevOps & Platform": DEVOPS,
    "ML / AI / Data": ML_AI,
    "Security": SECURITY,
    "Product & Design": PRODUCT_DESIGN,
    "Leadership & Management": LEADERSHIP,
}

# ── Strong vs Weak Action Verbs ───────────────────────────────────────────────
STRONG_VERBS = {
    "architected", "engineered", "designed", "built", "launched", "shipped",
    "led", "managed", "directed", "orchestrated", "spearheaded", "pioneered",
    "scaled", "optimized", "reduced", "increased", "grew", "drove", "boosted",
    "accelerated", "cut", "saved", "generated", "delivered", "established",
    "transformed", "migrated", "modernized", "refactored", "automated",
    "implemented", "deployed", "integrated", "developed", "created",
    "designed", "built", "owned", "defined", "shaped", "influenced",
    "mentored", "hired", "recruited", "onboarded", "trained",
    "collaborated", "partnered", "aligned", "negotiated",
}

WEAK_VERBS = {
    "helped", "assisted", "worked on", "worked with", "participated",
    "involved in", "responsible for", "duties included", "tasked with",
    "supported", "contributed to", "part of", "member of",
    "handled", "dealt with", "did", "made",
}

WEAK_TO_STRONG_MAP = {
    "helped": "led",
    "assisted": "engineered",
    "worked on": "built",
    "worked with": "collaborated on",
    "participated": "drove",
    "involved in": "owned",
    "responsible for": "managed",
    "duties included": "delivered",
    "supported": "enabled",
    "contributed to": "developed",
    "handled": "directed",
}

# ── Role-specific bullet point templates (Top 1% signals) ────────────────────
ROLE_BULLET_TEMPLATES = {
    "software engineer": [
        "Architected and shipped [feature/system] used by [X]M+ users, reducing latency by [X]%",
        "Led migration from [old tech] to [new tech], cutting infrastructure costs by $[X]K/year",
        "Built CI/CD pipeline that reduced deployment time from [X] hours to [X] minutes",
        "Identified and fixed [N] critical performance bottlenecks, improving p99 latency by [X]%",
        "Mentored [N] junior engineers through code reviews, design docs, and pair programming",
        "Designed and implemented [system] handling [X]K+ requests/second with 99.9% uptime",
        "Reduced test suite runtime by [X]% through parallelization and intelligent test selection",
        "Drove adoption of [technology/practice] across [N] teams, improving developer velocity by [X]%",
    ],
    "backend engineer": [
        "Designed RESTful/GraphQL APIs serving [X]M requests/day with [X]ms average latency",
        "Optimised [database] queries reducing page load time by [X]% for [X]K daily users",
        "Built event-driven microservice architecture handling [X]K events/second via Kafka",
        "Implemented distributed caching layer reducing database load by [X]%",
        "Led backend rewrite from [monolith/old tech] to microservices, enabling [X]x scale",
        "Achieved [X]% reduction in API error rate by implementing circuit breakers and retry logic",
    ],
    "frontend engineer": [
        "Rebuilt [product] UI with [framework], improving Lighthouse performance score from [X] to [X]",
        "Implemented code-splitting and lazy loading, reducing initial bundle size by [X]%",
        "Built reusable component library used by [N] product teams, eliminating [X]% of duplicated code",
        "Improved Core Web Vitals (LCP/FID/CLS) meeting Google's 'Good' threshold, lifting SEO ranking",
        "Led accessibility audit and remediation achieving WCAG 2.1 AA compliance across [product]",
        "Reduced frontend bug rate by [X]% by introducing TypeScript and comprehensive unit testing",
    ],
    "devops engineer": [
        "Reduced deployment frequency from weekly to [X]x daily with zero-downtime CI/CD pipeline",
        "Cut cloud infrastructure costs by $[X]K/month ([X]%) through right-sizing and reserved instances",
        "Improved system reliability from [X]% to [X]% uptime, reducing incidents by [X]%",
        "Built Kubernetes platform supporting [N] microservices across [N] teams with full GitOps workflow",
        "Implemented observability stack (metrics, logs, traces) reducing MTTR from [X] hours to [X] min",
        "Automated infrastructure provisioning with Terraform, cutting environment setup from days to hours",
    ],
    "data engineer": [
        "Built real-time data pipeline processing [X]GB/day with sub-[X]-second latency using [tech]",
        "Designed star-schema data warehouse reducing analyst query time from minutes to seconds",
        "Migrated [X]TB of data from [source] to [destination] with zero data loss or downtime",
        "Created self-service analytics platform reducing data team requests by [X]%",
        "Improved data quality by [X]% by implementing automated validation and anomaly detection",
    ],
    "machine learning engineer": [
        "Trained and deployed [model type] achieving [X]% accuracy, [X]% improvement over baseline",
        "Reduced model inference latency by [X]% through quantization, pruning, and batching",
        "Built end-to-end ML pipeline from feature engineering to production serving [X]K predictions/day",
        "Implemented A/B testing framework enabling [N] concurrent model experiments",
        "Reduced model training costs by [X]% via distributed training optimisation",
        "Deployed RAG-based system reducing customer support tickets by [X]%",
    ],
    "product manager": [
        "Owned [product/feature] from 0→1, growing to [X]K MAU in [N] months",
        "Led cross-functional team of [N] to launch [feature], driving [X]% increase in [metric]",
        "Defined and shipped roadmap delivering $[X]M in incremental ARR",
        "Reduced customer churn by [X]% through [initiative], validated via [X]-week experiment",
        "Increased activation rate from [X]% to [X]% by redesigning onboarding with [N] experiments",
        "Built 0→1 [product line] achieving product-market fit in [N] months based on NPS of [X]",
    ],
    "security engineer": [
        "Reduced attack surface by [X]% by implementing zero-trust network architecture",
        "Led SOC 2 Type II compliance effort, achieving certification in [N] months",
        "Built automated vulnerability scanning pipeline identifying [X]K issues before production",
        "Reduced mean time to detect (MTTD) from [X] days to [X] hours with enhanced SIEM rules",
        "Implemented secrets management with Vault, eliminating [N] hardcoded credentials incidents",
    ],
    "engineering manager": [
        "Grew engineering team from [N] to [N] through strategic hiring across [N] countries",
        "Improved team velocity by [X]% by introducing [process/practice] and removing blockers",
        "Reduced P1 incident rate by [X]% through improved on-call processes and runbooks",
        "Delivered [project] on-time and [X]% under budget, serving [X]M users at launch",
        "Improved team retention to [X]%, [X]% above company average, through career development programmes",
        "Built engineering culture of ownership; reduced review cycle time by [X]% via async-first norms",
    ],
}

# ── Top 1% differentiation signals by role ───────────────────────────────────
TOP_1_PERCENT_SIGNALS = {
    "software engineer": [
        "Open source contributions with measurable community impact (stars, downloads, contributors)",
        "Conference talks, technical blog posts, or patents demonstrating thought leadership",
        "Specific scale numbers: QPS handled, users served, data volume, uptime SLA met",
        "Cost savings with dollar amounts — recruiters love seeing direct business impact",
        "Cross-team influence: drove adoption of your solution beyond your immediate team",
        "Mentorship: specific junior engineers you've grown into senior/staff roles",
    ],
    "backend engineer": [
        "Distributed systems design experience with real scale (millions of users, TB of data)",
        "Ownership of critical paths — auth, payments, search — not just feature work",
        "On-call experience and incident command — shows production maturity",
        "Database expertise: schema design, query optimisation, migrations at scale",
        "API design authority: versioning strategy, breaking vs non-breaking changes, SDKs",
    ],
    "frontend engineer": [
        "Performance obsession: Core Web Vitals, bundle size, rendering strategies",
        "Accessibility track record: WCAG compliance, screen reader testing, inclusive design",
        "Design system authorship — not just consuming a DS, but building and governing one",
        "State management at scale: complex data flow, real-time sync, offline support",
        "Cross-browser/device expertise with documented testing methodology",
    ],
    "devops engineer": [
        "Platform engineering mindset — you build for other engineers, not just ops",
        "Cost engineering: actual dollar savings achieved with specific initiatives",
        "Reliability track record: uptime numbers, incident reduction, chaos engineering",
        "Self-service infrastructure: developers deploy without opening tickets",
        "Security-as-code: policy enforcement in pipelines, not just documentation",
    ],
    "data engineer": [
        "Data contracts and data quality ownership — not just pipelines, but trust in data",
        "Real-time vs batch trade-off decision-making with measurable outcomes",
        "Cost optimisation of data infrastructure (storage, compute, egress)",
        "Platform adoption: data platform used by N+ analysts/scientists",
        "Data governance: lineage, cataloguing, PII handling at scale",
    ],
    "machine learning engineer": [
        "Models shipped to production with measurable business impact — not just notebooks",
        "ML system design: feature stores, model registries, monitoring, drift detection",
        "Inference optimisation: latency, throughput, cost per prediction",
        "LLM/foundation model experience: fine-tuning, RAG, prompt engineering, evals",
        "Research-to-production track record: translating papers into production systems",
    ],
    "product manager": [
        "Metrics ownership: you define, instrument, and move the metrics, not just track them",
        "Discovery rigor: user interviews → insight → hypothesis → experiment → learning",
        "Technical depth: can write specs that need zero clarification from engineering",
        "Revenue or growth impact with specific dollar or percentage figures",
        "0→1 experience: greenfield product with validated PMF, not just feature work",
    ],
    "security engineer": [
        "Threat models authored for complex systems with documented risk decisions",
        "Red team / offensive security experience to complement defensive work",
        "Security champion programme: spreading security culture beyond the security team",
        "Compliance ownership end-to-end (SOC 2, ISO 27001, PCI DSS)",
        "Bug bounty findings or responsible disclosure track record",
    ],
}

# ── ATS red flags (things that hurt your score) ───────────────────────────────
ATS_RED_FLAGS = [
    "tables in resume (ATS cannot parse)",
    "headers/footers with key info",
    "images or graphics",
    "non-standard section names",
    "multiple columns (some ATS fail)",
    "missing contact information",
    "no skills section",
    "dates missing on experience",
    "functional resume format (hides gaps but ATS dislikes)",
    "pdf with text as image",
]

# ── Certifications that add top-1% signal ────────────────────────────────────
HIGH_VALUE_CERTS = {
    "cloud": ["aws certified solutions architect", "aws certified developer", "gcp professional cloud architect",
              "azure solutions architect", "cka", "ckad", "certified kubernetes administrator",
              "terraform associate", "google cloud professional data engineer"],
    "security": ["cissp", "ceh", "oscp", "aws security specialty", "comptia security+"],
    "data": ["databricks certified", "dbt certified", "google professional data engineer"],
    "ml": ["aws ml specialty", "google professional ml engineer", "tensorflow developer certificate"],
}
