import sqlite3
import os

DB_PATH = "workstation_advisor.db"
SCHEMA_PATH = "schema.sql"


ARCHETYPES = [
    {"name": "Executive / Road Warrior",            "is_mobile_primary": 1},
    {"name": "Analyst / Data Power User",            "is_mobile_primary": 0},
    {"name": "Software Developer / DevOps",          "is_mobile_primary": 0},
    {"name": "Designer (2D / Entry 3D)",             "is_mobile_primary": 0},
    {"name": "Media / Broadcast Professional",       "is_mobile_primary": 0},
    {"name": "Engineer / Creator (Advanced Compute)", "is_mobile_primary": 0},
    {"name": "AI / Data Scientist / ML Engineer",    "is_mobile_primary": 0},
    {"name": "Field / Edge Engineer",                "is_mobile_primary": 1},
]

INDUSTRIES = {
    "Executive / Road Warrior": [
        "Cross-Industry",
    ],
    "Analyst / Data Power User": [
        "Financial Services",
        "Healthcare",
        "Retail / CPG",
        "Energy",
        "Cross-Industry",
    ],
    "Software Developer / DevOps": [
        "Technology",
        "Technology / Enterprise",
        "Cross-Industry",
    ],
    "Designer (2D / Entry 3D)": [
        "Marketing / Advertising",
        "Technology",
        "Architecture",
        "Media & Entertainment",
        "Cross-Industry",
    ],
    "Media / Broadcast Professional": [
        "Media & Entertainment",
        "Sports",
        "Corporate",
    ],
    "Engineer / Creator (Advanced Compute)": [
        "Manufacturing",
        "Aerospace & Defense",
        "Architecture / AEC",
        "Media & Entertainment",
        "Gaming",
        "Energy",
        "Cross-Industry",
    ],
    "AI / Data Scientist / ML Engineer": [
        "Technology",
        "Healthcare",
        "Financial Services",
        "Retail / CPG",
        "Cross-Industry",
    ],
    "Field / Edge Engineer": [
        "Manufacturing",
        "Energy",
        "Defense",
        "Architecture / AEC",
        "Utilities",
    ],
}

# Structure: {(archetype_name, industry_name): [vertical_names]}
VERTICALS = {
    ("Executive / Road Warrior", "Cross-Industry"):                     ["Productivity"],
    ("Analyst / Data Power User", "Financial Services"):               ["Investment Banking", "Risk & Compliance"],
    ("Analyst / Data Power User", "Healthcare"):                       ["Health Economics"],
    ("Analyst / Data Power User", "Retail / CPG"):                     ["Demand Planning"],
    ("Analyst / Data Power User", "Energy"):                           ["Operations"],
    ("Analyst / Data Power User", "Cross-Industry"):                   ["Business Intelligence"],
    ("Software Developer / DevOps", "Technology"):                     ["Web / Mobile", "Backend / APIs", "Embedded / Systems"],
    ("Software Developer / DevOps", "Technology / Enterprise"):        ["DevOps / Platform"],
    ("Software Developer / DevOps", "Cross-Industry"):                 ["IT"],
    ("Designer (2D / Entry 3D)", "Marketing / Advertising"):           ["Brand & Identity"],
    ("Designer (2D / Entry 3D)", "Technology"):                        ["Product & UX"],
    ("Designer (2D / Entry 3D)", "Architecture"):                      ["Visualization"],
    ("Designer (2D / Entry 3D)", "Media & Entertainment"):             ["Publishing"],
    ("Designer (2D / Entry 3D)", "Cross-Industry"):                    ["Digital Content"],
    ("Media / Broadcast Professional", "Media & Entertainment"):       ["Broadcast / News", "Post-Production", "Virtual Production"],
    ("Media / Broadcast Professional", "Sports"):                      ["Production"],
    ("Media / Broadcast Professional", "Corporate"):                   ["Internal Media"],
    ("Engineer / Creator (Advanced Compute)", "Manufacturing"):        ["Mechanical Engineering", "Structural Engineering"],
    ("Engineer / Creator (Advanced Compute)", "Aerospace & Defense"):  ["Engineering"],
    ("Engineer / Creator (Advanced Compute)", "Architecture / AEC"):   ["Visualization"],
    ("Engineer / Creator (Advanced Compute)", "Media & Entertainment"): ["VFX / Animation"],
    ("Engineer / Creator (Advanced Compute)", "Gaming"):               ["Game Development"],
    ("Engineer / Creator (Advanced Compute)", "Energy"):               ["Oil & Gas"],
    ("Engineer / Creator (Advanced Compute)", "Cross-Industry"):       ["Rendering"],
    ("AI / Data Scientist / ML Engineer", "Technology"):               ["AI Research", "ML Engineering"],
    ("AI / Data Scientist / ML Engineer", "Healthcare"):               ["Clinical AI"],
    ("AI / Data Scientist / ML Engineer", "Financial Services"):       ["Quant / Risk"],
    ("AI / Data Scientist / ML Engineer", "Retail / CPG"):             ["Data Science"],
    ("AI / Data Scientist / ML Engineer", "Cross-Industry"):           ["Data Engineering"],
    ("Field / Edge Engineer", "Manufacturing"):                        ["Field Service"],
    ("Field / Edge Engineer", "Energy"):                               ["Oil & Gas / Utilities"],
    ("Field / Edge Engineer", "Defense"):                              ["Field Operations"],
    ("Field / Edge Engineer", "Architecture / AEC"):                   ["Construction"],
    ("Field / Edge Engineer", "Utilities"):                            ["Infrastructure"],
}

# Structure: {(archetype_name, vertical_name): [workload_names]}
WORKLOADS = {
    ("Executive / Road Warrior", "Productivity"): [
        "Productivity & Collaboration",
        "Executive Presentation",
    ],
    ("Analyst / Data Power User", "Investment Banking"): [
        "Financial Modeling & Forecasting",
    ],
    ("Analyst / Data Power User", "Risk & Compliance"): [
        "Scenario Analysis & Stress Testing",
    ],
    ("Analyst / Data Power User", "Health Economics"): [
        "Outcomes Modeling & Statistical Analysis",
    ],
    ("Analyst / Data Power User", "Demand Planning"): [
        "Sales & Inventory Forecasting",
    ],
    ("Analyst / Data Power User", "Operations"): [
        "Energy Data Analysis & Reporting",
    ],
    ("Analyst / Data Power User", "Business Intelligence"): [
        "BI Reporting & Dashboarding",
    ],
    ("Software Developer / DevOps", "Web / Mobile"): [
        "Full-Stack Development",
    ],
    ("Software Developer / DevOps", "Backend / APIs"): [
        "Microservices & API Development",
    ],
    ("Software Developer / DevOps", "DevOps / Platform"): [
        "CI/CD, IaC & Container Orchestration",
    ],
    ("Software Developer / DevOps", "Embedded / Systems"): [
        "Low-Level & Firmware Development",
    ],
    ("Software Developer / DevOps", "IT"): [
        "Internal Tools & Automation",
    ],
    ("Designer (2D / Entry 3D)", "Brand & Identity"): [
        "Graphic Design",
    ],
    ("Designer (2D / Entry 3D)", "Product & UX"): [
        "UI/UX Design",
    ],
    ("Designer (2D / Entry 3D)", "Visualization"): [
        "2D Drafting & Presentation",
    ],
    ("Designer (2D / Entry 3D)", "Publishing"): [
        "Image Editing & Compositing",
    ],
    ("Designer (2D / Entry 3D)", "Digital Content"): [
        "Web & Digital Content Creation",
    ],
    ("Media / Broadcast Professional", "Broadcast / News"): [
        "Live Video Production & Switching",
    ],
    ("Media / Broadcast Professional", "Post-Production"): [
        "Real-Time Editing & Color Grading",
    ],
    ("Media / Broadcast Professional", "Virtual Production"): [
        "Real-Time Rendering (LED Volume / VP)",
    ],
    ("Media / Broadcast Professional", "Production"): [
        "Live Sports Broadcasting",
    ],
    ("Media / Broadcast Professional", "Internal Media"): [
        "Event Streaming & Recording",
    ],
    ("Engineer / Creator (Advanced Compute)", "Mechanical Engineering"): [
        "3D CAD & Assembly Design",
    ],
    ("Engineer / Creator (Advanced Compute)", "Structural Engineering"): [
        "FEA / Structural Simulation",
    ],
    ("Engineer / Creator (Advanced Compute)", "Engineering"): [
        "CFD / Aerodynamic Simulation",
    ],
    ("Engineer / Creator (Advanced Compute)", "Visualization"): [
        "Architectural Rendering & BIM",
    ],
    ("Engineer / Creator (Advanced Compute)", "VFX / Animation"): [
        "3D Animation & Rendering",
    ],
    ("Engineer / Creator (Advanced Compute)", "Game Development"): [
        "Game Engine Development",
    ],
    ("Engineer / Creator (Advanced Compute)", "Oil & Gas"): [
        "Seismic Data Processing",
    ],
    ("Engineer / Creator (Advanced Compute)", "Rendering"): [
        "GPU / CPU Hybrid Rendering",
    ],
    ("AI / Data Scientist / ML Engineer", "AI Research"): [
        "Model Training & Fine-Tuning",
    ],
    ("AI / Data Scientist / ML Engineer", "ML Engineering"): [
        "Model Deployment & Local Inference",
    ],
    ("AI / Data Scientist / ML Engineer", "Clinical AI"): [
        "Medical Image Analysis",
    ],
    ("AI / Data Scientist / ML Engineer", "Quant / Risk"): [
        "Quantitative Modeling & Backtesting",
    ],
    ("AI / Data Scientist / ML Engineer", "Data Science"): [
        "Recommender Systems & Forecasting",
    ],
    ("AI / Data Scientist / ML Engineer", "Data Engineering"): [
        "Dataset Preparation & Feature Engineering",
    ],
    ("Field / Edge Engineer", "Field Service"): [
        "On-Site Diagnostics & Repair",
    ],
    ("Field / Edge Engineer", "Oil & Gas / Utilities"): [
        "Field Data Capture & Processing",
    ],
    ("Field / Edge Engineer", "Field Operations"): [
        "Disconnected / Offline Compute",
    ],
    ("Field / Edge Engineer", "Construction"): [
        "On-Site BIM & Project Review",
    ],
    ("Field / Edge Engineer", "Infrastructure"): [
        "Remote Monitoring & Edge Analytics",
    ],
}

# Structure: {workload_name: [(scale_level, scale_label, threshold_unit, threshold_min, threshold_max, description)]}
SCALE_TIERS = {
    "Productivity & Collaboration": [
        (1, "Light",    "apps", 1,  3,    "1-3 SaaS apps, light email and calendar use"),
        (2, "Standard", "apps", 4,  7,    "4-7 concurrent apps, video calls, CRM"),
        (3, "Heavy",    "apps", 8,  None, "8+ concurrent apps, heavy multitasking"),
    ],
    "Executive Presentation": [
        (1, "Light",    "apps", 1,  2,    "Single display, basic slide decks"),
        (2, "Standard", "apps", 2,  3,    "Dual display, video-heavy presentations"),
        (3, "Heavy",    "apps", 3,  None, "Multi-display, live demo + conferencing simultaneously"),
    ],
    "Financial Modeling & Forecasting": [
        (1, "Light",    "MB",  0,    50,   "Excel models up to 50MB, basic formulas"),
        (2, "Standard", "MB",  50,   500,  "Models 50-500MB, Power Query, live data connections"),
        (3, "Heavy",    "MB",  500,  None, "Models over 500MB, Python-based analysis, multi-app concurrent"),
    ],
    "Scenario Analysis & Stress Testing": [
        (1, "Light",    "scenarios", 1,   10,   "Up to 10 scenarios, single model"),
        (2, "Standard", "scenarios", 10,  100,  "10-100 scenarios, multi-variable stress tests"),
        (3, "Heavy",    "scenarios", 100, None, "100+ scenarios, Monte Carlo simulations, large datasets"),
    ],
    "Outcomes Modeling & Statistical Analysis": [
        (1, "Light",    "MB",  0,    100,  "Datasets up to 100MB, basic regression in R/Python"),
        (2, "Standard", "MB",  100,  1000, "100MB-1GB datasets, complex statistical models"),
        (3, "Heavy",    "GB",  1,    None, "Datasets over 1GB, survival analysis, large cohort studies"),
    ],
    "Sales & Inventory Forecasting": [
        (1, "Light",    "MB",  0,    100,  "Single region, up to 100MB data extract"),
        (2, "Standard", "MB",  100,  500,  "Multi-region, 100-500MB, BI tool integration"),
        (3, "Heavy",    "MB",  500,  None, "Global datasets over 500MB, real-time feed integration"),
    ],
    "Energy Data Analysis & Reporting": [
        (1, "Light",    "MB",  0,    200,  "Single asset, up to 200MB time-series data"),
        (2, "Standard", "MB",  200,  1000, "Multi-asset, 200MB-1GB, operational dashboards"),
        (3, "Heavy",    "GB",  1,    None, "Fleet-wide datasets over 1GB, predictive analytics"),
    ],
    "BI Reporting & Dashboarding": [
        (1, "Light",    "MB",  0,    500,  "Static reports, datasets up to 500MB, Power BI / Tableau basics"),
        (2, "Standard", "GB",  0.5,  5,    "Live connections, 500MB-5GB, complex calculated fields"),
        (3, "Heavy",    "GB",  5,    None, "Enterprise BI, datasets over 5GB, warehouse queries, DirectQuery"),
    ],
    "Full-Stack Development": [
        (1, "Light",    "containers", 0, 2,    "Single app, 1-2 services, lightweight local dev"),
        (2, "Standard", "containers", 2, 5,    "2-5 services, local DB + API + frontend concurrently"),
        (3, "Heavy",    "containers", 5, None, "5+ services, microservices locally, heavy browser dev tools"),
    ],
    "Microservices & API Development": [
        (1, "Light",    "containers", 0, 3,    "1-3 services, basic REST API development"),
        (2, "Standard", "containers", 3, 8,    "3-8 services, local service mesh, API gateway"),
        (3, "Heavy",    "containers", 8, None, "8+ services, event-driven architecture, local Kafka/RabbitMQ"),
    ],
    "CI/CD, IaC & Container Orchestration": [
        (1, "Light",    "containers", 0,  5,    "Basic CI pipeline, up to 5 containers locally"),
        (2, "Standard", "containers", 5,  15,   "5-15 containers, local k8s (minikube), Terraform runs"),
        (3, "Heavy",    "containers", 15, None, "15+ containers, local cluster simulation, large IaC state"),
    ],
    "Low-Level & Firmware Development": [
        (1, "Light",    "targets", 1, 2,    "Single target, basic cross-compilation"),
        (2, "Standard", "targets", 2, 5,    "2-5 targets, emulation, kernel builds"),
        (3, "Heavy",    "targets", 5, None, "5+ targets, FPGA toolchains, large embedded OS builds"),
    ],
    "Internal Tools & Automation": [
        (1, "Light",    "apps", 1, 3,    "Simple scripts, 1-3 internal tools"),
        (2, "Standard", "apps", 3, 8,    "3-8 tools, scheduled jobs, basic pipelines"),
        (3, "Heavy",    "apps", 8, None, "8+ tools, heavy automation, orchestration frameworks"),
    ],
    "Graphic Design": [
        (1, "Light",    "MB",  0,    200,  "Files up to 200MB, single artboard, Illustrator / Photoshop basics"),
        (2, "Standard", "MB",  200,  1000, "200MB-1GB, multi-artboard, high-res print assets"),
        (3, "Heavy",    "GB",  1,    None, "Files over 1GB, complex multi-layer compositions, large format"),
    ],
    "UI/UX Design": [
        (1, "Light",    "MB",  0,    100,  "Simple Figma files, up to 100MB, few components"),
        (2, "Standard", "MB",  100,  500,  "100-500MB, large design systems, prototyping"),
        (3, "Heavy",    "MB",  500,  None, "500MB+ files, enterprise design systems, heavy prototyping"),
    ],
    "2D Drafting & Presentation": [
        (1, "Light",    "MB",  0,    100,  "Simple floor plans, up to 100MB DWG files"),
        (2, "Standard", "MB",  100,  500,  "100-500MB, multi-sheet drawings, xrefs"),
        (3, "Heavy",    "MB",  500,  None, "500MB+ complex drawing sets, large xref structures"),
    ],
    "Image Editing & Compositing": [
        (1, "Light",    "MB",  0,    500,  "Single images up to 500MB, basic compositing"),
        (2, "Standard", "MB",  500,  2000, "500MB-2GB, multi-layer composites, RAW processing"),
        (3, "Heavy",    "GB",  2,    None, "Files over 2GB, high-res multi-layer composites, batch processing"),
    ],
    "Web & Digital Content Creation": [
        (1, "Light",    "apps", 1, 3,    "1-3 tools, lightweight web assets"),
        (2, "Standard", "apps", 3, 6,    "3-6 tools, video-rich content, motion graphics"),
        (3, "Heavy",    "apps", 6, None, "6+ tools, 4K video exports, complex motion graphics"),
    ],
    "Live Video Production & Switching": [
        (1, "Light",    "streams", 1, 2,    "1-2 input streams, 1080p, basic switching"),
        (2, "Standard", "streams", 2, 4,    "2-4 streams, 1080p/4K mix, live graphics overlay"),
        (3, "Heavy",    "streams", 4, None, "4+ streams, 4K/8K, real-time compositing, NDI"),
    ],
    "Real-Time Editing & Color Grading": [
        (1, "Light",    "resolution_px", 0,       2073600,  "Up to 1080p (1920x1080), basic cut and colour"),
        (2, "Standard", "resolution_px", 2073600, 8294400,  "1080p to 4K, multi-cam edit, node-based grading"),
        (3, "Heavy",    "resolution_px", 8294400, None,     "4K+ / 8K, HDR grading, multi-stream real-time"),
    ],
    "Real-Time Rendering (LED Volume / VP)": [
        (1, "Light",    "resolution_px", 0,       2073600,  "Simple LED walls, up to 1080p output"),
        (2, "Standard", "resolution_px", 2073600, 8294400,  "Multi-panel 4K LED, Unreal Engine VP"),
        (3, "Heavy",    "resolution_px", 8294400, None,     "Large-format 8K VP stages, real-time ray tracing"),
    ],
    "Live Sports Broadcasting": [
        (1, "Light",    "streams", 1, 2,    "Single camera feed, 1080p broadcast"),
        (2, "Standard", "streams", 2, 6,    "2-6 camera feeds, 4K, replay system"),
        (3, "Heavy",    "streams", 6, None, "6+ feeds, 4K/8K, real-time analytics overlay, AR graphics"),
    ],
    "Event Streaming & Recording": [
        (1, "Light",    "streams", 1, 1,    "Single stream, 1080p recording"),
        (2, "Standard", "streams", 1, 3,    "1-3 streams, 4K recording, live encoding"),
        (3, "Heavy",    "streams", 3, None, "3+ streams, multi-platform simultaneous streaming, 4K+"),
    ],
    "3D CAD & Assembly Design": [
        (1, "Light",    "parts", 0,    500,   "Assemblies up to 500 parts, SolidWorks / CATIA basics"),
        (2, "Standard", "parts", 500,  5000,  "500-5,000 parts, complex assemblies, drawing packages"),
        (3, "Heavy",    "parts", 5000, None,  "5,000+ parts, large digital mockups, DMU workflows"),
    ],
    "FEA / Structural Simulation": [
        (1, "Light",    "nodes", 0,        100000,   "Up to 100K mesh nodes, linear static analysis"),
        (2, "Standard", "nodes", 100000,   1000000,  "100K-1M nodes, non-linear analysis, modal"),
        (3, "Heavy",    "nodes", 1000000,  None,     "1M+ nodes, transient dynamic, large contact problems"),
    ],
    "CFD / Aerodynamic Simulation": [
        (1, "Light",    "cells", 0,         1000000,   "Up to 1M cells, steady-state, simple geometry"),
        (2, "Standard", "cells", 1000000,   10000000,  "1M-10M cells, transient, complex geometry"),
        (3, "Heavy",    "cells", 10000000,  None,      "10M+ cells, full aircraft/vehicle, LES turbulence"),
    ],
    "Architectural Rendering & BIM": [
        (1, "Light",    "MB",  0,    500,   "BIM models up to 500MB, basic Revit / ArchiCAD"),
        (2, "Standard", "MB",  500,  2000,  "500MB-2GB, full building models, coordinated MEP"),
        (3, "Heavy",    "GB",  2,    None,  "2GB+ models, campus-scale BIM, photorealistic rendering"),
    ],
    "3D Animation & Rendering": [
        (1, "Light",    "MB",  0,    500,   "Scenes up to 500MB, basic rigged characters"),
        (2, "Standard", "MB",  500,  3000,  "500MB-3GB, complex scenes, particle systems"),
        (3, "Heavy",    "GB",  3,    None,  "3GB+ scenes, VFX-heavy, high-poly environments, GPU rendering"),
    ],
    "Game Engine Development": [
        (1, "Light",    "GB",  0,  5,    "Projects up to 5GB, indie scale, basic lighting"),
        (2, "Standard", "GB",  5,  20,   "5-20GB, mid-size game, Lumen / Nanite, shader compilation"),
        (3, "Heavy",    "GB",  20, None, "20GB+ projects, AAA-scale, full engine compilation, large asset streaming"),
    ],
    "Seismic Data Processing": [
        (1, "Light",    "GB",  0,   50,   "Datasets up to 50GB, 2D seismic interpretation"),
        (2, "Standard", "GB",  50,  500,  "50-500GB, 3D seismic, attribute analysis"),
        (3, "Heavy",    "GB",  500, None, "500GB+ full-field 3D surveys, pre-stack depth migration"),
    ],
    "GPU / CPU Hybrid Rendering": [
        (1, "Light",    "MB",  0,    500,   "Scenes up to 500MB, low sample count, preview renders"),
        (2, "Standard", "MB",  500,  3000,  "500MB-3GB, production renders, moderate ray tracing"),
        (3, "Heavy",    "GB",  3,    None,  "3GB+ scenes, path tracing, high sample counts, batch rendering"),
    ],
    "Model Training & Fine-Tuning": [
        (1, "Light",    "params_billions", 0,  1,    "Models up to 1B parameters, experimentation, prototyping"),
        (2, "Standard", "params_billions", 1,  7,    "1B-7B parameters, fine-tuning runs, LoRA / QLoRA"),
        (3, "Heavy",    "params_billions", 7,  None, "7B+ parameters, full training runs, multi-GPU required"),
    ],
    "Model Deployment & Local Inference": [
        (1, "Light",    "params_billions", 0,  1,    "Models up to 1B params, low-latency single-user inference"),
        (2, "Standard", "params_billions", 1,  7,    "1B-7B params, quantised models, multi-user local serving"),
        (3, "Heavy",    "params_billions", 7,  None, "7B+ params, full precision inference, real-time serving"),
    ],
    "Medical Image Analysis": [
        (1, "Light",    "GB",  0,   10,   "Datasets up to 10GB, 2D image classification"),
        (2, "Standard", "GB",  10,  100,  "10-100GB, 3D volumetric analysis, segmentation"),
        (3, "Heavy",    "GB",  100, None, "100GB+ multi-modal imaging datasets, foundation model fine-tuning"),
    ],
    "Quantitative Modeling & Backtesting": [
        (1, "Light",    "GB",  0,  5,    "Datasets up to 5GB, single strategy backtesting"),
        (2, "Standard", "GB",  5,  50,   "5-50GB, multi-strategy, tick data, factor models"),
        (3, "Heavy",    "GB",  50, None, "50GB+ full market history, real-time signal generation"),
    ],
    "Recommender Systems & Forecasting": [
        (1, "Light",    "GB",  0,   10,   "Datasets up to 10GB, collaborative filtering basics"),
        (2, "Standard", "GB",  10,  100,  "10-100GB, deep learning recommenders, feature stores"),
        (3, "Heavy",    "GB",  100, None, "100GB+ interaction logs, real-time personalisation pipelines"),
    ],
    "Dataset Preparation & Feature Engineering": [
        (1, "Light",    "GB",  0,   10,   "Datasets up to 10GB, pandas / SQL transformations"),
        (2, "Standard", "GB",  10,  100,  "10-100GB, Spark / Dask, complex feature pipelines"),
        (3, "Heavy",    "GB",  100, None, "100GB+ distributed preprocessing, large embedding generation"),
    ],
    "On-Site Diagnostics & Repair": [
        (1, "Light",    "apps", 1, 2,    "Single diagnostic tool, basic field reporting"),
        (2, "Standard", "apps", 2, 4,    "2-4 tools, local data logging, offline operation"),
        (3, "Heavy",    "apps", 4, None, "4+ tools, real-time machine interface, edge compute"),
    ],
    "Field Data Capture & Processing": [
        (1, "Light",    "GB",  0,  5,    "Up to 5GB data capture, basic field forms"),
        (2, "Standard", "GB",  5,  50,   "5-50GB, sensor data logging, local processing"),
        (3, "Heavy",    "GB",  50, None, "50GB+ continuous capture, real-time edge analytics"),
    ],
    "Disconnected / Offline Compute": [
        (1, "Light",    "apps", 1, 3,    "1-3 offline apps, basic compute, no connectivity"),
        (2, "Standard", "apps", 3, 6,    "3-6 apps, local simulation, secure offline workflows"),
        (3, "Heavy",    "apps", 6, None, "6+ apps, classified environment, full offline AI inference"),
    ],
    "On-Site BIM & Project Review": [
        (1, "Light",    "MB",  0,    500,  "BIM viewer, models up to 500MB, markup only"),
        (2, "Standard", "MB",  500,  2000, "500MB-2GB, coordination review, clash detection"),
        (3, "Heavy",    "GB",  2,    None, "2GB+ full BIM editing on-site, federated models"),
    ],
    "Remote Monitoring & Edge Analytics": [
        (1, "Light",    "streams", 1,  3,    "1-3 sensor streams, basic threshold alerting"),
        (2, "Standard", "streams", 3,  10,   "3-10 streams, local time-series analytics"),
        (3, "Heavy",    "streams", 10, None, "10+ streams, real-time ML inference at edge"),
    ],
}

PRODUCTS = [
    {
        "name": "Dell Pro Max Micro",
        "brand": "Dell Pro Max",
        "form_factor": "Ultra-Compact Micro",
        "max_cpu_cores": 24,
        "max_cpu_tdp_watts": 85,
        "max_ram_gb": 64,
        "ram_slots": 2,
        "max_gpu_vram_gb": 20,
        "gpu_vram_range": "4 GB - 20 GB",
        "supports_dual_gpu": 0,
        "max_storage_nvme_tb": 2.0,
        "max_psu_watts": 280,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 11, Ubuntu 24.04, RHEL 9.4",
        "recommended_scale_min": 1,
        "recommended_scale_max": 2,
        "notes": "65W CPU thermally boosted to 85W. 2 PCIe Gen4 x8 slots. Space-constrained deployments.",
    },
    {
        "name": "Dell Pro Max Slim",
        "brand": "Dell Pro Max",
        "form_factor": "Small Form Factor",
        "max_cpu_cores": 24,
        "max_cpu_tdp_watts": 125,
        "max_ram_gb": 128,
        "ram_slots": 4,
        "max_gpu_vram_gb": 20,
        "gpu_vram_range": "4 GB - 20 GB",
        "supports_dual_gpu": 0,
        "max_storage_nvme_tb": 4.0,
        "max_psu_watts": 360,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 11, Ubuntu 24.04",
        "recommended_scale_min": 1,
        "recommended_scale_max": 2,
        "notes": "K-series 125W CPU option. HDD up to 8TB. 3 PCIe slots.",
    },
    {
        "name": "Dell Pro Max Tower T2",
        "brand": "Dell Pro Max",
        "form_factor": "Full Tower",
        "max_cpu_cores": 24,
        "max_cpu_tdp_watts": 250,
        "max_ram_gb": 128,
        "ram_slots": 4,
        "max_gpu_vram_gb": 48,
        "gpu_vram_range": "4 GB - 48 GB",
        "supports_dual_gpu": 0,
        "max_storage_nvme_tb": 4.0,
        "max_psu_watts": 1500,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 11, Ubuntu 24.04",
        "recommended_scale_min": 2,
        "recommended_scale_max": 3,
        "notes": "125W CPU with Unlimited Turbo to 250W. Gen5 NVMe available. RTX PRO 6000 Blackwell (48GB) max GPU.",
    },
    {
        "name": "Dell Precision 5860 Tower",
        "brand": "Dell Precision",
        "form_factor": "Mid-Size Tower",
        "max_cpu_cores": 24,
        "max_cpu_tdp_watts": 225,
        "max_ram_gb": 2048,
        "ram_slots": 8,
        "max_gpu_vram_gb": 48,
        "gpu_vram_range": "4 GB - 48 GB",
        "supports_dual_gpu": 1,
        "max_storage_nvme_tb": 4.0,
        "max_psu_watts": 1350,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 11, Ubuntu 22.04, RHEL 8.6",
        "recommended_scale_min": 2,
        "recommended_scale_max": 3,
        "notes": "Intel Xeon W-2400. Dual GPU support up to 2x 300W. 5 PCIe slots. Max 2TB RAM.",
    },
    {
        "name": "Dell Precision 7875 Tower",
        "brand": "Dell Precision",
        "form_factor": "Full Tower",
        "max_cpu_cores": 96,
        "max_cpu_tdp_watts": 350,
        "max_ram_gb": 2048,
        "ram_slots": 8,
        "max_gpu_vram_gb": 96,
        "gpu_vram_range": "4 GB - 96 GB",
        "supports_dual_gpu": 1,
        "max_storage_nvme_tb": 4.0,
        "max_psu_watts": 1350,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 10, Windows 11, Ubuntu 22.04, Ubuntu 24.04, RHEL 9.3",
        "recommended_scale_min": 3,
        "recommended_scale_max": 3,
        "notes": "AMD Threadripper Pro 9000WX/7000WX. Up to 96 cores. Dual 300W or single 500W triple-wide GPU. RTX 6000 Blackwell 96GB GDDR7.",
    },
    {
        "name": "Dell Precision 7960 Tower",
        "brand": "Dell Precision",
        "form_factor": "Full Tower",
        "max_cpu_cores": 60,
        "max_cpu_tdp_watts": 385,
        "max_ram_gb": 4096,
        "ram_slots": 16,
        "max_gpu_vram_gb": 96,
        "gpu_vram_range": "2 GB - 96 GB",
        "supports_dual_gpu": 1,
        "max_storage_nvme_tb": 8.0,
        "max_psu_watts": 2200,
        "isv_certified": 1,
        "ecc_memory": 1,
        "os_support": "Windows 11 for Workstations, Ubuntu 24.04, RHEL 9.3",
        "recommended_scale_min": 3,
        "recommended_scale_max": 3,
        "notes": "Intel Xeon W-3400. Up to 60 cores. 16 DIMM slots, max 4TB RAM. 8x M.2 NVMe via FlexBays. 8 PCIe slots. Rack-mountable (5U kit).",
    },
]


def run_schema(conn):
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    print("Schema applied.")


def seed_archetypes(cur):
    archetype_ids = {}
    for a in ARCHETYPES:
        cur.execute(
            "INSERT INTO archetypes (name, is_mobile_primary) VALUES (?, ?)",
            (a["name"], a["is_mobile_primary"]),
        )
        archetype_ids[a["name"]] = cur.lastrowid
    print(f"  archetypes: {len(archetype_ids)} rows inserted")
    return archetype_ids


def seed_industries(cur, archetype_ids):
    industry_ids = {}
    total = 0
    for archetype_name, names in INDUSTRIES.items():
        archetype_id = archetype_ids[archetype_name]
        for name in names:
            cur.execute(
                "INSERT INTO industries (archetype_id, name) VALUES (?, ?)",
                (archetype_id, name),
            )
            industry_ids[(archetype_name, name)] = cur.lastrowid
            total += 1
    print(f"  industries: {total} rows inserted")
    return industry_ids


def seed_verticals(cur, industry_ids):
    vertical_ids = {}
    total = 0
    for (archetype_name, industry_name), names in VERTICALS.items():
        industry_id = industry_ids[(archetype_name, industry_name)]
        for name in names:
            cur.execute(
                "INSERT INTO verticals (industry_id, name) VALUES (?, ?)",
                (industry_id, name),
            )
            vertical_ids[(archetype_name, name)] = cur.lastrowid
            total += 1
    print(f"  verticals: {total} rows inserted")
    return vertical_ids


def seed_workloads(cur, vertical_ids):
    workload_ids = {}
    total = 0
    for (archetype_name, vertical_name), names in WORKLOADS.items():
        vertical_id = vertical_ids[(archetype_name, vertical_name)]
        for name in names:
            cur.execute(
                "INSERT INTO workloads (vertical_id, name) VALUES (?, ?)",
                (vertical_id, name),
            )
            workload_ids[name] = cur.lastrowid
            total += 1
    print(f"  workloads: {total} rows inserted")
    return workload_ids


def seed_scale_tiers(cur, workload_ids):
    total = 0
    for workload_name, tiers in SCALE_TIERS.items():
        workload_id = workload_ids[workload_name]
        for (scale_level, scale_label, threshold_unit, threshold_min, threshold_max, description) in tiers:
            cur.execute(
                """INSERT INTO scale_tiers
                   (workload_id, scale_level, scale_label, threshold_unit, threshold_min, threshold_max, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (workload_id, scale_level, scale_label, threshold_unit, threshold_min, threshold_max, description),
            )
            total += 1
    print(f"  scale_tiers: {total} rows inserted")


SCALE_TIER_PRODUCTS = [
    # Archetype 2 — Analyst / Data Power User
    ("Financial Modeling & Forecasting", 1, 1, "Dell Pro Max Micro"),
    ("Financial Modeling & Forecasting", 1, 2, "Dell Pro Max Slim"),
    ("Financial Modeling & Forecasting", 2, 1, "Dell Pro Max Slim"),
    ("Financial Modeling & Forecasting", 2, 2, "Dell Pro Max Tower T2"),
    ("Financial Modeling & Forecasting", 3, 1, "Dell Pro Max Tower T2"),
    ("Financial Modeling & Forecasting", 3, 2, "Dell Precision 5860 Tower"),
    ("Scenario Analysis & Stress Testing", 1, 1, "Dell Pro Max Micro"),
    ("Scenario Analysis & Stress Testing", 1, 2, "Dell Pro Max Slim"),
    ("Scenario Analysis & Stress Testing", 2, 1, "Dell Pro Max Slim"),
    ("Scenario Analysis & Stress Testing", 2, 2, "Dell Pro Max Tower T2"),
    ("Scenario Analysis & Stress Testing", 3, 1, "Dell Pro Max Tower T2"),
    ("Scenario Analysis & Stress Testing", 3, 2, "Dell Precision 5860 Tower"),
    ("Outcomes Modeling & Statistical Analysis", 1, 1, "Dell Pro Max Micro"),
    ("Outcomes Modeling & Statistical Analysis", 1, 2, "Dell Pro Max Slim"),
    ("Outcomes Modeling & Statistical Analysis", 2, 1, "Dell Pro Max Slim"),
    ("Outcomes Modeling & Statistical Analysis", 2, 2, "Dell Pro Max Tower T2"),
    ("Outcomes Modeling & Statistical Analysis", 3, 1, "Dell Pro Max Tower T2"),
    ("Outcomes Modeling & Statistical Analysis", 3, 2, "Dell Precision 5860 Tower"),
    ("Sales & Inventory Forecasting", 1, 1, "Dell Pro Max Micro"),
    ("Sales & Inventory Forecasting", 1, 2, "Dell Pro Max Slim"),
    ("Sales & Inventory Forecasting", 2, 1, "Dell Pro Max Slim"),
    ("Sales & Inventory Forecasting", 2, 2, "Dell Pro Max Tower T2"),
    ("Sales & Inventory Forecasting", 3, 1, "Dell Pro Max Tower T2"),
    ("Sales & Inventory Forecasting", 3, 2, "Dell Precision 5860 Tower"),
    ("Energy Data Analysis & Reporting", 1, 1, "Dell Pro Max Micro"),
    ("Energy Data Analysis & Reporting", 1, 2, "Dell Pro Max Slim"),
    ("Energy Data Analysis & Reporting", 2, 1, "Dell Pro Max Slim"),
    ("Energy Data Analysis & Reporting", 2, 2, "Dell Pro Max Tower T2"),
    ("Energy Data Analysis & Reporting", 3, 1, "Dell Pro Max Tower T2"),
    ("Energy Data Analysis & Reporting", 3, 2, "Dell Precision 5860 Tower"),
    ("BI Reporting & Dashboarding", 1, 1, "Dell Pro Max Micro"),
    ("BI Reporting & Dashboarding", 1, 2, "Dell Pro Max Slim"),
    ("BI Reporting & Dashboarding", 2, 1, "Dell Pro Max Slim"),
    ("BI Reporting & Dashboarding", 2, 2, "Dell Pro Max Tower T2"),
    ("BI Reporting & Dashboarding", 3, 1, "Dell Pro Max Tower T2"),
    ("BI Reporting & Dashboarding", 3, 2, "Dell Precision 5860 Tower"),
    # Archetype 3 — Software Developer / DevOps
    ("Full-Stack Development", 1, 1, "Dell Pro Max Micro"),
    ("Full-Stack Development", 1, 2, "Dell Pro Max Slim"),
    ("Full-Stack Development", 2, 1, "Dell Pro Max Slim"),
    ("Full-Stack Development", 2, 2, "Dell Pro Max Tower T2"),
    ("Full-Stack Development", 3, 1, "Dell Pro Max Tower T2"),
    ("Full-Stack Development", 3, 2, "Dell Precision 5860 Tower"),
    ("Microservices & API Development", 1, 1, "Dell Pro Max Micro"),
    ("Microservices & API Development", 1, 2, "Dell Pro Max Slim"),
    ("Microservices & API Development", 2, 1, "Dell Pro Max Slim"),
    ("Microservices & API Development", 2, 2, "Dell Pro Max Tower T2"),
    ("Microservices & API Development", 3, 1, "Dell Pro Max Tower T2"),
    ("Microservices & API Development", 3, 2, "Dell Precision 5860 Tower"),
    ("CI/CD, IaC & Container Orchestration", 1, 1, "Dell Pro Max Slim"),
    ("CI/CD, IaC & Container Orchestration", 1, 2, "Dell Pro Max Tower T2"),
    ("CI/CD, IaC & Container Orchestration", 2, 1, "Dell Pro Max Tower T2"),
    ("CI/CD, IaC & Container Orchestration", 2, 2, "Dell Precision 5860 Tower"),
    ("CI/CD, IaC & Container Orchestration", 3, 1, "Dell Precision 5860 Tower"),
    ("CI/CD, IaC & Container Orchestration", 3, 2, "Dell Precision 7875 Tower"),
    ("Low-Level & Firmware Development", 1, 1, "Dell Pro Max Micro"),
    ("Low-Level & Firmware Development", 1, 2, "Dell Pro Max Slim"),
    ("Low-Level & Firmware Development", 2, 1, "Dell Pro Max Slim"),
    ("Low-Level & Firmware Development", 2, 2, "Dell Pro Max Tower T2"),
    ("Low-Level & Firmware Development", 3, 1, "Dell Pro Max Tower T2"),
    ("Low-Level & Firmware Development", 3, 2, "Dell Precision 5860 Tower"),
    ("Internal Tools & Automation", 1, 1, "Dell Pro Max Micro"),
    ("Internal Tools & Automation", 1, 2, "Dell Pro Max Slim"),
    ("Internal Tools & Automation", 2, 1, "Dell Pro Max Slim"),
    ("Internal Tools & Automation", 2, 2, "Dell Pro Max Tower T2"),
    ("Internal Tools & Automation", 3, 1, "Dell Pro Max Tower T2"),
    ("Internal Tools & Automation", 3, 2, "Dell Precision 5860 Tower"),
    # Archetype 4 — Designer (2D / Entry 3D)
    ("Graphic Design", 1, 1, "Dell Pro Max Micro"),
    ("Graphic Design", 1, 2, "Dell Pro Max Slim"),
    ("Graphic Design", 2, 1, "Dell Pro Max Slim"),
    ("Graphic Design", 2, 2, "Dell Pro Max Tower T2"),
    ("Graphic Design", 3, 1, "Dell Pro Max Tower T2"),
    ("Graphic Design", 3, 2, "Dell Precision 5860 Tower"),
    ("UI/UX Design", 1, 1, "Dell Pro Max Micro"),
    ("UI/UX Design", 1, 2, "Dell Pro Max Slim"),
    ("UI/UX Design", 2, 1, "Dell Pro Max Slim"),
    ("UI/UX Design", 2, 2, "Dell Pro Max Tower T2"),
    ("UI/UX Design", 3, 1, "Dell Pro Max Tower T2"),
    ("UI/UX Design", 3, 2, "Dell Precision 5860 Tower"),
    ("2D Drafting & Presentation", 1, 1, "Dell Pro Max Micro"),
    ("2D Drafting & Presentation", 1, 2, "Dell Pro Max Slim"),
    ("2D Drafting & Presentation", 2, 1, "Dell Pro Max Slim"),
    ("2D Drafting & Presentation", 2, 2, "Dell Pro Max Tower T2"),
    ("2D Drafting & Presentation", 3, 1, "Dell Pro Max Tower T2"),
    ("2D Drafting & Presentation", 3, 2, "Dell Precision 5860 Tower"),
    ("Image Editing & Compositing", 1, 1, "Dell Pro Max Slim"),
    ("Image Editing & Compositing", 1, 2, "Dell Pro Max Tower T2"),
    ("Image Editing & Compositing", 2, 1, "Dell Pro Max Tower T2"),
    ("Image Editing & Compositing", 2, 2, "Dell Precision 5860 Tower"),
    ("Image Editing & Compositing", 3, 1, "Dell Precision 5860 Tower"),
    ("Image Editing & Compositing", 3, 2, "Dell Precision 7875 Tower"),
    ("Web & Digital Content Creation", 1, 1, "Dell Pro Max Micro"),
    ("Web & Digital Content Creation", 1, 2, "Dell Pro Max Slim"),
    ("Web & Digital Content Creation", 2, 1, "Dell Pro Max Slim"),
    ("Web & Digital Content Creation", 2, 2, "Dell Pro Max Tower T2"),
    ("Web & Digital Content Creation", 3, 1, "Dell Pro Max Tower T2"),
    ("Web & Digital Content Creation", 3, 2, "Dell Precision 5860 Tower"),
    # Archetype 5 — Media / Broadcast Professional
    ("Live Video Production & Switching", 1, 1, "Dell Pro Max Tower T2"),
    ("Live Video Production & Switching", 1, 2, "Dell Precision 5860 Tower"),
    ("Live Video Production & Switching", 2, 1, "Dell Pro Max Tower T2"),
    ("Live Video Production & Switching", 2, 2, "Dell Precision 5860 Tower"),
    ("Live Video Production & Switching", 3, 1, "Dell Precision 5860 Tower"),
    ("Live Video Production & Switching", 3, 2, "Dell Precision 7875 Tower"),
    ("Real-Time Editing & Color Grading", 1, 1, "Dell Pro Max Tower T2"),
    ("Real-Time Editing & Color Grading", 1, 2, "Dell Precision 5860 Tower"),
    ("Real-Time Editing & Color Grading", 2, 1, "Dell Precision 5860 Tower"),
    ("Real-Time Editing & Color Grading", 2, 2, "Dell Precision 7875 Tower"),
    ("Real-Time Editing & Color Grading", 3, 1, "Dell Precision 7875 Tower"),
    ("Real-Time Editing & Color Grading", 3, 2, "Dell Precision 7960 Tower"),
    ("Real-Time Rendering (LED Volume / VP)", 1, 1, "Dell Pro Max Tower T2"),
    ("Real-Time Rendering (LED Volume / VP)", 1, 2, "Dell Precision 5860 Tower"),
    ("Real-Time Rendering (LED Volume / VP)", 2, 1, "Dell Precision 5860 Tower"),
    ("Real-Time Rendering (LED Volume / VP)", 2, 2, "Dell Precision 7875 Tower"),
    ("Real-Time Rendering (LED Volume / VP)", 3, 1, "Dell Precision 7875 Tower"),
    ("Real-Time Rendering (LED Volume / VP)", 3, 2, "Dell Precision 7960 Tower"),
    ("Live Sports Broadcasting", 1, 1, "Dell Pro Max Tower T2"),
    ("Live Sports Broadcasting", 1, 2, "Dell Precision 5860 Tower"),
    ("Live Sports Broadcasting", 2, 1, "Dell Precision 5860 Tower"),
    ("Live Sports Broadcasting", 2, 2, "Dell Precision 7875 Tower"),
    ("Live Sports Broadcasting", 3, 1, "Dell Precision 7875 Tower"),
    ("Live Sports Broadcasting", 3, 2, "Dell Precision 7960 Tower"),
    ("Event Streaming & Recording", 1, 1, "Dell Pro Max Tower T2"),
    ("Event Streaming & Recording", 1, 2, "Dell Precision 5860 Tower"),
    ("Event Streaming & Recording", 2, 1, "Dell Pro Max Tower T2"),
    ("Event Streaming & Recording", 2, 2, "Dell Precision 5860 Tower"),
    ("Event Streaming & Recording", 3, 1, "Dell Precision 5860 Tower"),
    ("Event Streaming & Recording", 3, 2, "Dell Precision 7875 Tower"),
    # Archetype 6 — Engineer / Creator (Advanced Compute)
    ("3D CAD & Assembly Design", 1, 1, "Dell Pro Max Tower T2"),
    ("3D CAD & Assembly Design", 1, 2, "Dell Precision 5860 Tower"),
    ("3D CAD & Assembly Design", 2, 1, "Dell Precision 5860 Tower"),
    ("3D CAD & Assembly Design", 2, 2, "Dell Precision 7875 Tower"),
    ("3D CAD & Assembly Design", 3, 1, "Dell Precision 7875 Tower"),
    ("3D CAD & Assembly Design", 3, 2, "Dell Precision 7960 Tower"),
    ("FEA / Structural Simulation", 1, 1, "Dell Precision 5860 Tower"),
    ("FEA / Structural Simulation", 1, 2, "Dell Precision 7875 Tower"),
    ("FEA / Structural Simulation", 2, 1, "Dell Precision 7875 Tower"),
    ("FEA / Structural Simulation", 2, 2, "Dell Precision 7960 Tower"),
    ("FEA / Structural Simulation", 3, 1, "Dell Precision 7875 Tower"),
    ("FEA / Structural Simulation", 3, 2, "Dell Precision 7960 Tower"),
    ("CFD / Aerodynamic Simulation", 1, 1, "Dell Precision 5860 Tower"),
    ("CFD / Aerodynamic Simulation", 1, 2, "Dell Precision 7875 Tower"),
    ("CFD / Aerodynamic Simulation", 2, 1, "Dell Precision 7875 Tower"),
    ("CFD / Aerodynamic Simulation", 2, 2, "Dell Precision 7960 Tower"),
    ("CFD / Aerodynamic Simulation", 3, 1, "Dell Precision 7875 Tower"),
    ("CFD / Aerodynamic Simulation", 3, 2, "Dell Precision 7960 Tower"),
    ("Architectural Rendering & BIM", 1, 1, "Dell Pro Max Tower T2"),
    ("Architectural Rendering & BIM", 1, 2, "Dell Precision 5860 Tower"),
    ("Architectural Rendering & BIM", 2, 1, "Dell Precision 5860 Tower"),
    ("Architectural Rendering & BIM", 2, 2, "Dell Precision 7875 Tower"),
    ("Architectural Rendering & BIM", 3, 1, "Dell Precision 7875 Tower"),
    ("Architectural Rendering & BIM", 3, 2, "Dell Precision 7960 Tower"),
    ("3D Animation & Rendering", 1, 1, "Dell Pro Max Tower T2"),
    ("3D Animation & Rendering", 1, 2, "Dell Precision 5860 Tower"),
    ("3D Animation & Rendering", 2, 1, "Dell Precision 5860 Tower"),
    ("3D Animation & Rendering", 2, 2, "Dell Precision 7875 Tower"),
    ("3D Animation & Rendering", 3, 1, "Dell Precision 7875 Tower"),
    ("3D Animation & Rendering", 3, 2, "Dell Precision 7960 Tower"),
    ("Game Engine Development", 1, 1, "Dell Pro Max Tower T2"),
    ("Game Engine Development", 1, 2, "Dell Precision 5860 Tower"),
    ("Game Engine Development", 2, 1, "Dell Precision 5860 Tower"),
    ("Game Engine Development", 2, 2, "Dell Precision 7875 Tower"),
    ("Game Engine Development", 3, 1, "Dell Precision 7875 Tower"),
    ("Game Engine Development", 3, 2, "Dell Precision 7960 Tower"),
    ("Seismic Data Processing", 1, 1, "Dell Precision 5860 Tower"),
    ("Seismic Data Processing", 1, 2, "Dell Precision 7875 Tower"),
    ("Seismic Data Processing", 2, 1, "Dell Precision 7875 Tower"),
    ("Seismic Data Processing", 2, 2, "Dell Precision 7960 Tower"),
    ("Seismic Data Processing", 3, 1, "Dell Precision 7960 Tower"),
    ("Seismic Data Processing", 3, 2, "Dell Precision 7875 Tower"),
    ("GPU / CPU Hybrid Rendering", 1, 1, "Dell Precision 5860 Tower"),
    ("GPU / CPU Hybrid Rendering", 1, 2, "Dell Precision 7875 Tower"),
    ("GPU / CPU Hybrid Rendering", 2, 1, "Dell Precision 7875 Tower"),
    ("GPU / CPU Hybrid Rendering", 2, 2, "Dell Precision 7960 Tower"),
    ("GPU / CPU Hybrid Rendering", 3, 1, "Dell Precision 7875 Tower"),
    ("GPU / CPU Hybrid Rendering", 3, 2, "Dell Precision 7960 Tower"),
    # Archetype 7 — AI / Data Scientist / ML Engineer
    ("Model Training & Fine-Tuning", 1, 1, "Dell Precision 7875 Tower"),
    ("Model Training & Fine-Tuning", 1, 2, "Dell Precision 5860 Tower"),
    ("Model Training & Fine-Tuning", 2, 1, "Dell Precision 7875 Tower"),
    ("Model Training & Fine-Tuning", 2, 2, "Dell Precision 7960 Tower"),
    ("Model Training & Fine-Tuning", 3, 1, "Dell Precision 7875 Tower"),
    ("Model Training & Fine-Tuning", 3, 2, "Dell Precision 7960 Tower"),
    ("Model Deployment & Local Inference", 1, 1, "Dell Precision 7875 Tower"),
    ("Model Deployment & Local Inference", 1, 2, "Dell Precision 5860 Tower"),
    ("Model Deployment & Local Inference", 2, 1, "Dell Precision 7875 Tower"),
    ("Model Deployment & Local Inference", 2, 2, "Dell Precision 7960 Tower"),
    ("Model Deployment & Local Inference", 3, 1, "Dell Precision 7960 Tower"),
    ("Model Deployment & Local Inference", 3, 2, "Dell Precision 7875 Tower"),
    ("Medical Image Analysis", 1, 1, "Dell Precision 5860 Tower"),
    ("Medical Image Analysis", 1, 2, "Dell Precision 7875 Tower"),
    ("Medical Image Analysis", 2, 1, "Dell Precision 7875 Tower"),
    ("Medical Image Analysis", 2, 2, "Dell Precision 7960 Tower"),
    ("Medical Image Analysis", 3, 1, "Dell Precision 7875 Tower"),
    ("Medical Image Analysis", 3, 2, "Dell Precision 7960 Tower"),
    ("Quantitative Modeling & Backtesting", 1, 1, "Dell Pro Max Slim"),
    ("Quantitative Modeling & Backtesting", 1, 2, "Dell Pro Max Tower T2"),
    ("Quantitative Modeling & Backtesting", 2, 1, "Dell Pro Max Tower T2"),
    ("Quantitative Modeling & Backtesting", 2, 2, "Dell Precision 5860 Tower"),
    ("Quantitative Modeling & Backtesting", 3, 1, "Dell Precision 7960 Tower"),
    ("Quantitative Modeling & Backtesting", 3, 2, "Dell Precision 7875 Tower"),
    ("Recommender Systems & Forecasting", 1, 1, "Dell Precision 5860 Tower"),
    ("Recommender Systems & Forecasting", 1, 2, "Dell Precision 7875 Tower"),
    ("Recommender Systems & Forecasting", 2, 1, "Dell Precision 7875 Tower"),
    ("Recommender Systems & Forecasting", 2, 2, "Dell Precision 7960 Tower"),
    ("Recommender Systems & Forecasting", 3, 1, "Dell Precision 7875 Tower"),
    ("Recommender Systems & Forecasting", 3, 2, "Dell Precision 7960 Tower"),
    ("Dataset Preparation & Feature Engineering", 1, 1, "Dell Pro Max Slim"),
    ("Dataset Preparation & Feature Engineering", 1, 2, "Dell Pro Max Tower T2"),
    ("Dataset Preparation & Feature Engineering", 2, 1, "Dell Pro Max Tower T2"),
    ("Dataset Preparation & Feature Engineering", 2, 2, "Dell Precision 5860 Tower"),
    ("Dataset Preparation & Feature Engineering", 3, 1, "Dell Precision 7960 Tower"),
    ("Dataset Preparation & Feature Engineering", 3, 2, "Dell Precision 7875 Tower"),
]


def seed_products(cur):
    for p in PRODUCTS:
        cur.execute(
            """INSERT INTO products
               (name, brand, form_factor, max_cpu_cores, max_cpu_tdp_watts, max_ram_gb, ram_slots,
                max_gpu_vram_gb, gpu_vram_range, supports_dual_gpu, max_storage_nvme_tb, max_psu_watts,
                isv_certified, ecc_memory, os_support, recommended_scale_min, recommended_scale_max, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p["name"], p["brand"], p["form_factor"], p["max_cpu_cores"], p["max_cpu_tdp_watts"],
                p["max_ram_gb"], p["ram_slots"], p["max_gpu_vram_gb"], p["gpu_vram_range"],
                p["supports_dual_gpu"], p["max_storage_nvme_tb"], p["max_psu_watts"],
                p["isv_certified"], p["ecc_memory"], p["os_support"],
                p["recommended_scale_min"], p["recommended_scale_max"], p["notes"],
            ),
        )
    print(f"  products: {len(PRODUCTS)} rows inserted")


def seed_scale_tier_products(cur):
    total = 0
    for (workload_name, scale_level, rank, product_name) in SCALE_TIER_PRODUCTS:
        row = cur.execute(
            """
            SELECT st.id
            FROM scale_tiers st
            JOIN workloads w ON w.id = st.workload_id
            WHERE w.name = ? AND st.scale_level = ?
            """,
            (workload_name, scale_level),
        ).fetchone()
        if row is None:
            raise ValueError(f"No scale_tier found for workload={workload_name!r}, scale_level={scale_level}")
        scale_tier_id = row[0]

        product_row = cur.execute(
            "SELECT id FROM products WHERE name = ?", (product_name,)
        ).fetchone()
        if product_row is None:
            raise ValueError(f"No product found with name={product_name!r}")
        product_id = product_row[0]

        cur.execute(
            """
            INSERT OR IGNORE INTO scale_tier_products (scale_tier_id, product_id, rank)
            VALUES (?, ?, ?)
            """,
            (scale_tier_id, product_id, rank),
        )
        total += cur.rowcount
    print(f"  scale_tier_products: {total} rows inserted")


def print_row_counts(conn):
    tables = ["archetypes", "industries", "verticals", "workloads", "scale_tiers", "products", "scale_tier_products", "users"]
    print("\nRow counts:")
    for table in tables:
        (count,) = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        print(f"  {table:<24} {count}")


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print("Running schema...")
    run_schema(conn)

    print("\nSeeding tables...")
    archetype_ids = seed_archetypes(cur)
    industry_ids  = seed_industries(cur, archetype_ids)
    vertical_ids  = seed_verticals(cur, industry_ids)
    workload_ids  = seed_workloads(cur, vertical_ids)
    seed_scale_tiers(cur, workload_ids)
    seed_products(cur)
    seed_scale_tier_products(cur)
    # users: stub only, no inserts   <- Stage 3

    conn.commit()
    print_row_counts(conn)
    conn.close()
    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
