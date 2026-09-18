<div align="center"><a href="https://oasislocal.github.io/O.A.S.I.S./">
  <img src="assets/oasis-banner.png" alt="O.A.S.I.S. — Local AI Assistant" width="100%">
</a><br>O.A.S.I.S.

Offline AI System for Information Sovereignty

The AI assistant that lives on your PC.

Local AI · Private by design · Offline-first · No account · No subscription

<br><a href="https://github.com/OASISLocal/O.A.S.I.S./releases">
<img src="https://img.shields.io/badge/Download-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download for Windows">
</a>
<a href="https://oasislocal.github.io/O.A.S.I.S./">
<img src="https://img.shields.io/badge/Website-O.A.S.I.S.-00BFA6?style=for-the-badge" alt="Website">
</a>
<a href="https://discord.gg/88yfW5UwGC">
<img src="https://img.shields.io/badge/Community-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
</a><br><br>

<a href="https://github.com/OASISLocal/O.A.S.I.S./releases">
<img src="https://img.shields.io/badge/version-0.2.0_beta-00BFA6?style=flat-square" alt="Version 0.2.0 beta">
</a>
<img src="https://img.shields.io/badge/platform-Windows_10%2F11-0078D4?style=flat-square&logo=windows&logoColor=white" alt="Windows 10 and 11">
<img src="https://img.shields.io/badge/AI-local_models-00BFA6?style=flat-square" alt="Local AI models"><br><br>

«Type or talk. O.A.S.I.S. uses local AI, your files, your screen and your PC's tools to get things done.»

</div>---

Contents

<details>
<summary><strong>Navigate this README</strong></summary>- "What is O.A.S.I.S.?" (#what-is-oasis)
- "Why O.A.S.I.S.?" (#why-oasis)
- "How it works" (#how-it-works)
- "Capabilities" (#capabilities)
  - "PC control" (#pc-control)
  - "Files and documents" (#files-and-documents)
  - "Memory" (#memory)
  - "Voice" (#voice)
  - "Vision" (#vision)
  - "Coding" (#coding)
  - "Workflows" (#workflows)
- "Tools" (#tools)
- "Permissions and safety" (#permissions-and-safety)
- "Local AI and models" (#local-ai-and-models)
- "Privacy" (#privacy)
- "Hardware" (#hardware)
- "Installation" (#installation)
- "Plans" (#plans)
- "Comparison" (#comparison)
- "Architecture" (#architecture)
- "Roadmap" (#roadmap)
- "Beta status" (#beta-status)
- "FAQ" (#faq)
- "Community" (#community)
- "Contributing" (#contributing)
- "Resources" (#resources)

</details>---

What is O.A.S.I.S.?

O.A.S.I.S. — Offline AI System for Information Sovereignty is a local AI assistant for Windows designed to do more than generate text.

It runs AI models directly on your computer and provides an expanding set of tools that allow the assistant to work with your environment.

O.A.S.I.S. can:

- understand and search local files
- read and summarize documents
- maintain local memory
- analyze images and screenshots
- control supported applications and system functions
- manage timers and reminders
- work with calendars and notes
- assist with coding
- execute code inside an isolated sandbox
- create scheduled workflows
- use voice input and output
- operate without an Internet connection for supported local functionality

The central idea is simple:

«Give AI access to useful computer capabilities without making a cloud service a mandatory part of the architecture.»

<div align="center"><img src="assets/oasis-demo.gif" alt="O.A.S.I.S. in action" width="88%"></div>---

Why O.A.S.I.S.?

Most AI interfaces are primarily conversation interfaces.

O.A.S.I.S. is designed around conversation + tools + actions.

Instead of:

User
  ↓
Question
  ↓
AI
  ↓
Text answer

O.A.S.I.S. can work through:

User request
     ↓
Understand
     ↓
Select capability
     ↓
Check permissions
     ↓
Use tool
     ↓
Verify result
     ↓
Return result

For example:

«"Find the electricity bills I downloaded and calculate my Q2 total."»

A possible local workflow is:

Find files
    ↓
Read documents
    ↓
Extract amounts
    ↓
Calculate
    ↓
Reference source files
    ↓
Return result

The model generates the reasoning and tool requests.

The tool layer performs the actual computer operations.

---

How it works

O.A.S.I.S. combines a local model runtime with memory, documents, tools and a permission layer.

flowchart TD
    A[User] --> B[O.A.S.I.S. Interface]

    B --> C[Agent Core]

    C --> D[Local AI Model]
    C --> E[Memory]
    C --> F[Document Context]
    C --> G[Tool Selection]

    G --> H[Permission Layer]

    H --> I[PC Tools]
    H --> J[File Tools]
    H --> K[Code Sandbox]
    H --> L[System Tools]
    H --> M[Network Tools]

    I --> N[Your PC]
    J --> N
    K --> N
    L --> N

    M --> O[External Services]

This separation is important.

A model being capable of requesting an action does not automatically mean it should have unrestricted permission to perform that action.

---

Capabilities

PC control

O.A.S.I.S. can interact with supported parts of your Windows environment.

Examples include:

- opening applications
- controlling windows
- changing system volume
- controlling supported media applications
- managing clipboard content
- inspecting CPU, RAM, disk and network information
- inspecting processes
- managing temporary files
- checking Wi-Fi status
- locking the PC
- sleep
- restart
- shutdown

Higher-impact operations can require explicit approval.

---

Files and documents

O.A.S.I.S. can work with information stored on your computer.

Supported workflows include:

- finding files
- copying files
- moving files
- renaming files
- searching file content
- reading documents
- asking questions about documents
- extracting information
- calculating values from documents
- referencing source documents

Example:

"Find the three electricity bills from Q2
and calculate the total."

The assistant can turn a natural-language request into a sequence of local file and analysis operations.

---

Memory

O.A.S.I.S. includes local memory designed to preserve useful context between conversations.

Memory can include:

- facts
- notes
- conversation information
- personal context
- document-related information

Memory can be searched semantically and managed from the application.

Users can remove stored information by:

- individual item
- memory type
- source file

The goal is persistent context without giving up control over what is stored.

---

Voice

O.A.S.I.S. supports voice interaction designed around local processing.

Current product capabilities include:

- voice input
- spoken responses
- Spanish
- English
- wake-word interaction
- interruptible conversations
- spoken reminders
- spoken timers

Local speech processing is designed to keep supported voice workflows on the computer.

---

Vision

O.A.S.I.S. can analyze images and screen content.

Screen-related workflows include:

- screenshots
- screen analysis
- understanding visible content
- extracting information from the screen
- interacting with supported UI elements

Screen access is permission-controlled.

The intended model is:

«The assistant accesses your screen when you ask it to, rather than treating continuous screen access as the default.»

---

Coding

O.A.S.I.S. can assist with software development and code-related tasks.

Capabilities include:

- explaining code
- analyzing errors
- working with repositories
- Git status
- generating code
- testing code
- sandboxed execution
- reviewing proposed changes

The coding workflow can be structured around:

Request
  ↓
Generate change
  ↓
Run in sandbox
  ↓
Test
  ↓
Review diff
  ↓
Approve
  ↓
Apply

The isolated sandbox is intended to reduce the risk of executing generated code directly against the user's normal environment.

Expanded coding and sandbox capabilities are included in O.A.S.I.S. Max.

---

Workflows

O.A.S.I.S. can automate recurring tasks.

A workflow can combine multiple tools:

Schedule
   ↓
Read calendar
   ↓
Check information
   ↓
Process data
   ↓
Generate result
   ↓
Notify user

Example:

«"Every Monday morning, prepare my weekly briefing."»

The beta includes simple routines and scheduled workflows, while expanded conditional automation is part of Max.

---

Tools

O.A.S.I.S. currently advertises 80+ tools and counting.

Instead of treating tools as one large list, they can be understood as several functional groups.

Area| Examples
PC| Apps, windows, volume, processes
System| CPU, RAM, disk, network, Wi-Fi
Files| Search, copy, move, rename
Documents| PDFs, notes, document analysis
Coding| Git, sandbox, code workflows
Web| Search, pages, translation
Productivity| Calendar, reminders, timers, notes
Media| Spotify and supported controls
Vision| Screenshots and screen analysis
Memory| Facts, notes, conversations, documents
Integration| MCP and external tool servers

The toolset continues to evolve throughout the beta.

---

Permissions and safety

An AI assistant with access to your computer needs a clear permission model.

O.A.S.I.S. therefore provides per-tool permission switches and risk-aware controls.

Conceptually:

Risk| Example| Possible control
Low| Calculator| Automatic
Low| System information| Automatic
Medium| Open application| Permission configurable
Medium| Move files| Permission configurable
Medium| Clipboard modification| Permission configurable
High| Delete files| Explicit approval
High| Execute code| Sandbox / approval
High| Restart or shutdown| Explicit approval

The exact behavior depends on the individual tool and current application configuration.

The principle is:

«The assistant can request actions. The user controls the boundaries.»

---

Local AI and models

O.A.S.I.S. is designed to run AI models locally.

The current product page highlights:

- Llama 3.2
- Gemma 4
- Qwen 2.5
- GGUF-compatible models

GGUF compatibility allows users to work with a broad ecosystem of quantized local models.

Examples include models from families such as:

- Llama
- Gemma
- Qwen
- DeepSeek
- Phi
- Mistral

Model availability depends on the specific model, format and O.A.S.I.S. version.

---

Model selection

Different models make sense for different hardware.

A useful rule of thumb:

Hardware profile| Typical direction
CPU-only| Smaller quantized models
Modern laptop| Smaller / medium models
Dedicated GPU| Larger or faster models
More VRAM| Larger local models
More system RAM| Larger CPU / partially offloaded models

Performance depends on the model, quantization, context size, backend and hardware.

For that reason, individual benchmark figures should always be interpreted together with the hardware and model configuration that produced them.

---

Privacy

Privacy is a core design principle of O.A.S.I.S.

The application is designed around local-first processing.

Local workflows

When using local models and local tools:

- conversations can remain on your PC
- documents can remain on your PC
- memory can remain on your PC
- local model inference happens on your hardware
- local voice processing can happen on your hardware
- screen analysis can be performed locally

Network-dependent workflows

Some capabilities inherently require connectivity.

Examples include:

- web search
- online pages
- external services
- external tool servers
- optional cloud model integrations
- remote companion functionality

Therefore:

«O.A.S.I.S. is offline-first, not a claim that every possible feature is network-independent.»

No mandatory cloud backend is required for the core local experience.

---

Privacy controls

The product provides controls intended to make sensitive capabilities explicit.

Depending on the feature, users can control access to:

- microphone
- screen
- files
- tools
- higher-risk actions
- external integrations

The application also exposes local/engine status information so users can understand how the current session is operating.

---

Verification and reliability

Local execution does not make an AI model infallible.

O.A.S.I.S. instead provides mechanisms that can help users verify important operations.

These include:

- source references for document-derived information
- tool results
- calculations
- sandbox execution
- code diffs
- explicit permissions
- visible tool activity

These mechanisms can reduce certain classes of errors, but they should not be interpreted as a guarantee that every generated answer is factually correct.

---

Hardware requirements

O.A.S.I.S. currently targets:

- Windows 10
- Windows 11
- 64-bit systems

The product page describes the beta as capable of running on a modern CPU, with an NVIDIA GPU recommended but not required.

Docker is required only when using the code-execution sandbox.

General hardware guidance

Component| Guidance
CPU| Modern CPU
RAM| Depends on selected model
GPU| NVIDIA recommended for faster local inference
VRAM| More VRAM allows larger/faster model configurations
Storage| Required for the application and downloaded models
Docker| Required for code sandbox workflows

Local AI performance varies considerably with model size and quantization.

---

Installation

1. Download

Download the latest Windows release:

<a href="https://github.com/OASISLocal/O.A.S.I.S./releases">
<img src="https://img.shields.io/badge/Download_latest_release-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download latest release">
</a>---

2. Install

Run the Windows installer.

The normal installation process does not require command-line configuration.

---

3. Download a model

Open the Models section and select a model appropriate for your hardware.

The model is downloaded locally and can then be used without requiring a cloud inference service.

---

4. Start using O.A.S.I.S.

Type a request or activate voice mode.

Try:

Find the PDF I downloaded yesterday.

Summarize this document.

How much did I spend in Q2?

What's using the most RAM?

Turn the volume down.

Explain this code error.

Remind me tomorrow at 9.

Prepare my weekly briefing.

---

Plans

Personal

Free

The current Personal edition includes:

- unlimited chat and voice
- choice of AI models
- screen and image vision
- everyday PC control
- memory
- documents
- simple routines

No account is required.

<a href="https://github.com/OASISLocal/O.A.S.I.S./releases">
<img src="https://img.shields.io/badge/Download_Personal-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download Personal">
</a>---

Max

Early access

€15 one-time during early access → €25 at 1.0

Max is presented as a one-time purchase rather than a recurring subscription.

The current product page lists additional capabilities including:

- advanced coding and sandbox functionality
- unlimited persistent memory
- scheduled conditional routines
- Discord voice
- Telegram voice
- Android companion
- browser extension
- external tool servers
- voice cloning
- local backup

Max is currently presented as an early-access / waitlist product.

Check the website for current availability and terms.

---

O.A.S.I.S. vs cloud assistants

O.A.S.I.S. and cloud AI services use different architectural approaches.

Capability| O.A.S.I.S.| Cloud-first assistant
Local model inference| Yes| Usually no
Offline local operation| Yes| Usually no
Mandatory cloud backend| No for local workflows| Usually
Local model choice| Yes| Usually limited
Local PC tools| Yes| Varies
Local documents| Yes| Depends on service
Local memory| Yes| Depends on service
Online services| Optional| Usually core
Hardware responsibility| User's PC| Provider's infrastructure

The choice depends on whether a user prioritizes local control, hardware ownership, model flexibility, cloud capabilities or convenience.

---

Architecture

At a high level:

┌───────────────────────────────────────────────┐
│                    USER                       │
│             Text / Voice / UI                 │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│                O.A.S.I.S. CORE                │
│                                               │
│  Context · Planning · Memory · Tool routing   │
└───────────────┬───────────────┬───────────────┘
                │               │
                ▼               ▼
       ┌────────────────┐   ┌────────────────┐
       │   LOCAL AI     │   │ LOCAL MEMORY   │
       │    MODELS      │   │ & DOCUMENTS    │
       └────────────────┘   └────────────────┘
                │
                ▼
       ┌────────────────┐
       │  TOOL SYSTEM   │
       └───────┬────────┘
               │
               ▼
       ┌────────────────┐
       │   PERMISSIONS  │
       └───────┬────────┘
               │
       ┌───────┴───────────────────────┐
       ▼                               ▼
┌───────────────┐               ┌───────────────┐
│ YOUR WINDOWS  │               │ NETWORK /     │
│ ENVIRONMENT   │               │ EXTERNAL APIs │
└───────────────┘               └───────────────┘

The architecture intentionally distinguishes:

model → tool request → permission → execution

rather than treating the model itself as an unrestricted system administrator.

---

Security model

The security model is based around several principles:

Least privilege

A tool should only receive the access necessary for its function.

Explicit permissions

Sensitive capabilities can require user approval.

Isolation

Code execution can be separated from the normal user environment through the sandbox.

Visibility

Tool activity and important operations should be inspectable.

Local-first execution

Local tasks should not require unnecessary external processing.

---

Roadmap

O.A.S.I.S. is under active development.

Current product

- [x] Local chat
- [x] Local models
- [x] Voice
- [x] Memory
- [x] Documents
- [x] Vision
- [x] PC tools
- [x] Tool permissions
- [x] Simple routines
- [x] Model management

Expanded capabilities

- [x] Coding workflows
- [x] Sandbox workflows
- [x] Scheduled workflows
- [x] Proactive notifications
- [x] MCP / external tool servers
- [x] Discord / Telegram integrations
- [x] Android companion
- [x] Browser extension

Availability varies by edition and release.

Future development

- [ ] Linux support
- [ ] macOS support
- [ ] Expanded plugin ecosystem
- [ ] Multi-agent capabilities
- [ ] Additional integrations
- [ ] Expanded companion experiences

«The roadmap can change as development progresses.»

---

Beta status

Current release:

O.A.S.I.S. v0.2.0 beta

The beta is intended for users who want to test the local assistant while the product continues to evolve.

Expect changes to:

- interface
- tools
- model support
- permissions
- workflows
- integrations
- hardware compatibility

When reporting an issue, include enough information to reproduce it.

---

Bug reports

Please include:

O.A.S.I.S. version:
Windows version:
CPU:
GPU:
RAM:
Model:
Quantization:
What happened:
Expected behavior:
Steps to reproduce:
Logs:

Open an issue:

<a href="https://github.com/OASISLocal/O.A.S.I.S./issues">
<img src="https://img.shields.io/badge/Report_a_bug-GitHub_Issues-181717?style=for-the-badge&logo=github&logoColor=white" alt="Report a bug">
</a>---

Frequently asked questions

<details>
<summary><strong>Does O.A.S.I.S. work without Internet?</strong></summary>Yes, for supported local functionality.

After installing O.A.S.I.S. and downloading a local model, core local AI functionality can operate without an Internet connection.

Features such as web search, online pages and external services require connectivity.

</details><details>
<summary><strong>Does O.A.S.I.S. require an account?</strong></summary>No account is required for the Personal edition.

</details><details>
<summary><strong>Can I use my own model?</strong></summary>O.A.S.I.S. supports GGUF-compatible local models.

The product currently highlights Llama 3.2, Gemma 4 and Qwen 2.5.

</details><details>
<summary><strong>Can it run without a GPU?</strong></summary>Yes.

O.A.S.I.S. can run on modern CPU systems, although a dedicated NVIDIA GPU is recommended for a faster experience.

</details><details>
<summary><strong>Does it access my screen continuously?</strong></summary>Screen analysis is permission-controlled and intended to be used when requested.

</details><details>
<summary><strong>Can it control my PC?</strong></summary>Yes.

The tool system can interact with supported applications, windows, volume, media, clipboard and other system functions.

Higher-impact operations can require explicit approval.

</details><details>
<summary><strong>Can it remember information?</strong></summary>Yes.

O.A.S.I.S. provides local memory for facts, notes, conversations and other supported context.

Stored information can be managed and removed.

</details><details>
<summary><strong>Does O.A.S.I.S. guarantee correct answers?</strong></summary>No.

O.A.S.I.S. provides tools that can help verify certain operations, but no AI model should be assumed to be universally correct.

</details><details>
<summary><strong>Is Personal free?</strong></summary>Yes.

The Personal edition is currently offered free of charge.

</details><details>
<summary><strong>Is Max a subscription?</strong></summary>No.

The current product page presents Max as a one-time purchase:

€15 early access → €25 at 1.0.

</details><details>
<summary><strong>Does it support macOS or Linux?</strong></summary>Not currently.

The current beta targets Windows 10 and Windows 11.

</details><details>
<summary><strong>Where should I report bugs?</strong></summary>Use GitHub Issues for reproducible technical problems.

</details>---

Community

O.A.S.I.S. is being developed with an early community around the project.

<a href="https://discord.gg/88yfW5UwGC">
<img src="https://img.shields.io/badge/Join_the_Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join Discord">
</a>Community areas include:

Area| Purpose
Announcements| Releases and major updates
General| Discussion
Showcase| Projects and workflows
Suggestions| Feature ideas
Beta| Early testing
Bugs| Problem reports
Documentation| Guides and references
Development| Contributor discussion

---

Contributing

Before opening a large pull request:

1. Check existing issues.
2. Check current documentation.
3. Verify that the feature isn't already implemented.
4. Discuss major architectural changes first.
5. Keep changes focused.
6. Document user-facing behavior.
7. Test on supported Windows configurations.

During beta, documentation, testing, reproducible bug reports and hardware feedback are particularly valuable.

---

Project principles

O.A.S.I.S. is built around a small set of principles.

Principle| Meaning
Local first| Prefer local processing when practical
User control| The user controls capabilities and permissions
Explicit actions| Sensitive operations should be visible
Model freedom| Support a broad local-model ecosystem
Useful memory| Persistent context should remain manageable
Practical automation| AI should be able to perform multi-step tasks
Transparency| Users should understand what the system is doing

---

Download

<div align="center"><a href="https://github.com/OASISLocal/O.A.S.I.S./releases">
<img src="https://img.shields.io/badge/Download_O.A.S.I.S.-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download O.A.S.I.S.">
</a><br><br>

<strong>Windows 10 / 11</strong>

<br>Local models · Offline-first · No account required

</div>---

Resources

<div align="center">Resource| 
Product website| "O.A.S.I.S." (https://oasislocal.github.io/O.A.S.I.S./)
Releases| "GitHub Releases" (https://github.com/OASISLocal/O.A.S.I.S./releases)
Source| "GitHub Repository" (https://github.com/OASISLocal/O.A.S.I.S.)
Issues| "GitHub Issues" (https://github.com/OASISLocal/O.A.S.I.S./issues)
Community| "Discord" (https://discord.gg/88yfW5UwGC)

</div>---

<div align="center"><br><a href="https://oasislocal.github.io/O.A.S.I.S./">
  <img src="assets/oasis-banner.png" alt="O.A.S.I.S." width="75%">
</a><br><br>

O.A.S.I.S.

The AI assistant that lives on your PC.

Local AI · Private by design · Offline-first · Tool-enabled

<br><a href="https://github.com/OASISLocal/O.A.S.I.S./releases"><strong>Download</strong></a>
  ·  
<a href="https://oasislocal.github.io/O.A.S.I.S./"><strong>Website</strong></a>
  ·  
<a href="https://discord.gg/88yfW5UwGC"><strong>Community</strong></a>
  ·  
<a href="https://github.com/OASISLocal/O.A.S.I.S./issues"><strong>Issues</strong></a>

<br><br>

<sub>Your AI. Your PC. Your rules.</sub>

</div>