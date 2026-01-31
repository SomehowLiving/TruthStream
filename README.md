# TruthStream

**Real-time decentralized verification for the internet — anchored to 0G’s 50 Gbps Data Availability layer.**

TruthStream delivers AI-powered fact-checking in seconds and permanently records the results on-chain, ensuring that truth can move as fast as misinformation.

---

## 1. Project Title

**TruthStream**
*Verify before virality.*

---

## 2. Overview / Description

### What it does

TruthStream is a decentralized AI verification layer that analyzes images, videos, and text in real time, generates a structured investigation report, and permanently anchors the results to 0G’s Data Availability network. Each verification produces a cryptographically verifiable **Truth Certificate** that can be publicly audited and shared.

### Who it’s for

* Journalists and fact-checkers verifying viral content
* Social media users validating forwarded images or videos
* Newsrooms and platforms seeking transparent verification workflows
* Developers building DeFAI and Web3 applications that require verifiable data

### Why it exists

Misinformation spreads in minutes, but verification takes hours or days. Existing fact-checking systems are slow, centralized, and opaque. TruthStream closes this gap by combining fast AI investigation with blockchain-backed permanence, creating an immutable record of *when*, *how*, and *why* a piece of content was verified.

---

## 3. Demo / Screenshots

* Live web demo showcasing the end-to-end verification flow
* Visual Truth Certificate linked to a 0G explorer entry
* UI showing upload → investigation → DA confirmation

This project is highly visual and user-facing; the demo demonstrates how verification completes in seconds rather than hours.

---

## 4. Features

* ⚡ **Sub-5-Second Verification** — parallel AI analysis plus high-throughput DA anchoring
* 🔗 **0G-Native Design** — built specifically for 0G’s modular DA + EVM architecture
* 🧠 **Multi-AI Redundancy** — automatic fallback across multiple LLM providers
* 🔍 **Transparent Investigations** — open, auditable evidence chain for every verdict
* 🛡️ **TOMA Scoring Framework** — Transparency, Ownership, Monetization, Alignment
* 💰 **Stake-to-Verify Economics** — verifications are backed by economic commitment
* 🌐 **Censorship Resistance** — records persist even if original content is deleted
* 🎭 **Multi-Modal Support** — images, videos, and text
* 🧩 **Browser Extension Support** — verify content without leaving social platforms
* 📱 **Responsive Interface** — usable across mobile, tablet, and desktop

---

## 5. Installation

TruthStream is designed to be developer-friendly and runnable locally.

### Requirements

* Modern Node.js runtime
* Python 3.11 or newer
* 0G testnet wallet for DA publishing and contract interactions
* Optional caching layer for improved performance

### Local Setup

The project includes a frontend interface, backend AI investigation service, and smart contract integration. After installing dependencies and configuring environment variables, the system can be run locally with the frontend and backend operating together.

---

## 6. Usage

### Basic Verification Flow

1. Upload an image, video, or text snippet
2. TruthStream extracts claims and investigates using AI
3. Evidence is cross-referenced against live web sources
4. A TOMA score and investigation summary are generated
5. Results are anchored to 0G’s Data Availability layer
6. A shareable Truth Certificate is produced

### Advanced Usage

* Staking tokens to economically back a verification
* Challenging an existing verification with counter-evidence
* Consuming verification data via API for external applications

---

## 7. Configuration

TruthStream is configured via environment variables.

### Key Configuration Areas

* AI provider credentials (at least one required)
* 0G RPC endpoint and wallet key
* Deployed smart contract address
* Optional caching and environment flags

Defaults are provided where possible, with safe fallbacks for missing paid APIs.

---

## 8. Project Structure

The repository is organized as a modular monorepo:

* Frontend web application
* Optional browser extension
* Backend API for AI investigations
* Smart contracts for verification and staking
* Shared tooling, documentation, and CI

This structure allows independent iteration on UI, AI logic, and on-chain components.

---

## 9. Contributing

Contributions are welcome from the 0G and Web3 community.

### Guidelines

* Fork the repository and create a feature or fix branch
* Follow existing naming conventions and code style
* Include tests where applicable
* Open a pull request with a clear description of changes

Even small improvements—docs, UI polish, or new AI providers—are encouraged.

---

## 10. Tests

The project includes:

* Backend tests for verification logic and AI fallbacks
* Smart contract tests for staking and dispute flows
* Frontend tests for core UI components

Tests ensure correctness across AI analysis, DA anchoring, and on-chain recording.

---

## 11. Roadmap / TODO

**Near Term**

* WhatsApp and messaging platform verification bots
* Expanded deepfake detection for video frames
* Browser extension public release

**Mid Term**

* DAO-based dispute resolution
* Verifier reputation system
* Cross-chain verification exports

**Long Term**

* Zero-knowledge proofs for AI integrity
* Decentralized AI oracle network
* Mainnet deployment on 0G

---

## 12. License

MIT License
© 2025 TruthStream Contributors

---

## 13. Credits / Acknowledgments

Built during the **0G Bangalore Hackathon**.

Powered by:

* **0G Labs** — high-throughput Data Availability infrastructure
* **Anthropic (Claude 3.5)** — claim extraction and synthesis
* **Groq & Tavily** — fast inference and real-time search
* Open-source communities across Web3, AI, and frontend tooling

TruthStream is built with the belief that **verification should be public, fast, and permanent**—not centralized, slow, or opaque.

---
