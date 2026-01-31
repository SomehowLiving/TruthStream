**TruthStream: The Complete User Journey & Backend Architecture**
*A Millisecond-by-Millisecond Breakdown*

---

## 🎭 USER ENTRY POINTS

### Entry A: Web Dashboard (Primary)
**Persona:** Journalist, fact-checker, researcher  
**URL:** `truthstream.0g.ai/verify`

### Entry B: Browser Extension (The "Shield")
**Persona:** General internet user  
**Action:** Icon in toolbar showing "Verified" badges on Twitter/X, WhatsApp Web, News sites

### Entry C: WhatsApp Bot (The India Bet)
**Persona:** Tier-2/3 city users, viral forward recipients  
**Number:** Save +91-XXXX-TRUTH-0 (example)

---

## 🚀 FLOW 1: INSTANT VERIFICATION (The Hero Journey)

### **STEP 1: Content Ingestion** (0-500ms)

#### **User Side (UI)**
```
┌─────────────────────────────────────────────┐
│  🔍 TruthStream                        [Connect]│
├─────────────────────────────────────────────┤
│                                             │
│  [ Drop image/video here ]                  │
│       or                                    │
│  [ Paste URL _______________________ ]      │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 📎 election_video.mp4 (12MB)       │    │
│  │ Uploading... ████████████ 100%     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [ Analyze Truth ] ◄── Active after upload  │
└─────────────────────────────────────────────┘
```

**Interactions:**
- Drag-and-dropzone with glassmorphism effect (CSS: `backdrop-filter: blur(10px)`)
- Client-side hashing starts immediately (SHA-256 in browser using Web Crypto API)
- Progress bar is real file upload to temp S3/MinIO bucket (not blockchain yet)

#### **Backend Side**
```python
# Received at FastAPI endpoint
@app.post("/api/v1/ingest")
async def ingest_content(file: UploadFile = File(...), url: str = None):
    # 1. Generate content fingerprint immediately
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()
    
    # 2. Check cache (Redis) - "Have we seen this before?"
    cached = await redis.get(f"truth:{content_hash}")
    if cached:
        return json.loads(cached)  # Return in <10ms if known
    
    # 3. Store in temp hot storage (IPFS/0G temp)
    temp_uri = await store_temp(content)
    
    # 4. Trigger AI pipeline asynchronously
    task_id = await start_ai_analysis(content_hash, temp_uri)
    
    return {"task_id": task_id, "status": "analyzing", "hash": content_hash}
```

**0G Connection:** None yet (too expensive for temp storage). Using standard cloud for ingestion buffer.

---

### **STEP 2: The AI Analysis Pipeline** (500ms - 3000ms)

#### **User Side (UI)**
```
┌─────────────────────────────────────────────┐
│  🔍 Analyzing Content...               ⏱️ 2s │
├─────────────────────────────────────────────┤
│                                             │
│  [Spinning 0G Logo Animation]               │
│                                             │
│  Current Stage:                             │
│  ✓ Visual Analysis (Deepfake scan)         │
│  ✓ Metadata extraction                      │
│  ⟩ Cross-reference sources...    [Loading] │
│  ○ Bias detection                           │
│  ○ Blockchain anchoring                     │
│                                             │
│  💡 Did you know?                           │
│  This analysis will be permanent on 0G      │
│  in approximately 1.2 seconds               │
└─────────────────────────────────────────────┘
```

**UX Details:**
- Steps animate as completed (progressive disclosure)
- "Did you know" rotating tips educate about 0G DA layer
- Cancel button available (kills the API request)

#### **Backend Side (Parallel Processing)**

**Pipeline A: Visual Analysis (GPU-intensive)**
```python
# Running on 0G Compute Node (or Replicate API for hackathon)
async def visual_analysis(uri):
    # Deepfake detection using MesoNet or similar
    deepfake_score = await replicate.run(
        "operations-research-group/mesonet:latest",
        input={"image": uri}
    )
    
    # Image forensics (ELA - Error Level Analysis)
    manipulation_markers = await run_ela(uri)
    
    # C2PA metadata check (Content Authenticity Initiative)
    c2pa_manifest = extract_c2pa(uri)
    
    return {
        "deepfake_probability": deepfake_score,
        "ela_score": manipulation_markers,
        "c2pa_present": c2pa_manifest is not None,
        "c2pa_data": c2pa_manifest
    }
```

**Pipeline B: Semantic Analysis (LLM)**
```python
async def semantic_analysis(content_hash, text_content):
    # Extract text via OCR (if image) or transcript (if video)
    extracted_text = await extract_text(uri)
    
    # Claude 3.5 Sonnet analysis
    prompt = f"""
    Analyze this text for:
    1. Factual claims (bullet list)
    2. Stated vs implied meaning
    3. Emotional manipulation techniques
    4. Political leanings (left/center/right spectrum)
    5. Sensationalism score (0-100)
    
    Text: {extracted_text}
    """
    
    analysis = await anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_claude_response(analysis.content)
```

**Pipeline C: Source Verification (Real-time Web Search)**
```python
async def verify_sources(claims):
    # Perplexity API for real-time fact checking
    results = []
    for claim in claims:
        search = await perplexity.query(
            f"Fact check: {claim} recent news",
            recency_days=30
        )
        results.append({
            "claim": claim,
            "verified": search.answer,
            "sources": search.sources,
            "confidence": search.confidence
        })
    return results
```

**Aggregation & TOMA Score Calculation:**
```python
def calculate_toma_scores(visual, semantic, sources):
    # Transparency: Do we know the AI model details?
    transparency = 100 if c2pa_present else 85  # -15 if no source metadata
    
    # Ownership: Can we trace the original creator?
    ownership = 100 if c2pa_manifest else 40    # Low if anonymous
    
    # Monetization: Is there value at stake?
    # (Calculated later in staking step, default 0)
    
    # Alignment: Bias detection
    alignment_score = 100 - abs(semantic.political_leaning - 50)  # 50 = neutral
    
    return {
        "transparency": transparency,
        "ownership": ownership,
        "alignment": alignment_score,
        "overall": (transparency + ownership + alignment) / 3
    }
```

---

### **STEP 3: The 0G DA Publishing** (The Magic Moment) (3000ms - 4500ms)

#### **User Side (UI)**
```
┌─────────────────────────────────────────────┐
│  ✅ Analysis Complete!                   [🔍]│
├─────────────────────────────────────────────┤
│                                             │
│  🛡️ TOMA Score: 87/100                      │
│  Status: VERIFIED WITH CONTEXT              │
│                                             │
│  ┌─ TRUTH CERTIFICATE ─────────────────┐    │
│  │ 0x7f83...91a2                        │    │
│  │ Block: #4,291,883  │  Time: 2.1s    │    │
│  │ Hot Dog: 0.0001 0G                   │    │
│  └──────────────────────────────────────┘    │
│                                             │
│  ⚠️ Context Alert:                          │
│  Image is REAL but cropped to remove        │
│  timestamp showing it is from 2022, not     │
│  today's event.                             │
│                                             │
│  [View on 0G Explorer] [Challenge -50 0G]   │
└─────────────────────────────────────────────┘
```

**UX Details:**
- Certificate looks like a trading card (collectible aesthetic)
- "Hot Dog" = slang for gas fee (user-friendly)
- 3D tilt effect on mouse hover (CSS `transform: perspective(1000px) rotateX(...)`)
- One-click copy of certificate hash

#### **Backend Side (0G Integration)**

**Critical Path: Publishing to 0G DA Layer**
```javascript
// Node.js service using 0G SDK
const { DAClient } = require('@0g/sdk');

async function publishToZeroG(analysisData, contentHash) {
    const client = new DAClient({
        rpcEndpoint: 'https://rpc.0g.testnet',
        privateKey: process.env.DA_PUBLISHER_KEY
    });
    
    // Prepare the blob - 0G DA can handle up to 1MB per blob
    const certificate = {
        version: "truthstream-v1",
        content_hash: contentHash,
        timestamp: Date.now(),
        toma_scores: analysisData.toma,
        ai_analysis: {
            model: "claude-3-5-sonnet",
            version: "20241022",
            confidence: analysisData.confidence,
            deepfake_score: analysisData.visual.deepfake_probability
        },
        sources: analysisData.sources,
        // ZK Proof placeholder (for future)
        proof: null
    };
    
    // Compress for storage efficiency
    const blobData = Buffer.from(JSON.stringify(certificate));
    
    // Publish to 0G DA Namespace
    // This is where the 50 Gbps speed matters
    const startTime = performance.now();
    
    const receipt = await client.publishBlob({
        namespace: 'truthstream-news-v1',
        data: blobData,
        // 0G DA uses KZG commitments for data availability
        commitment: await generateKZG(blobData)
    });
    
    const finalityTime = performance.now() - startTime;
    console.log(`0G DA Finality: ${finalityTime}ms`); // Should be <500ms
    
    return {
        blobId: receipt.blobId,           // Permanent retrieval ID
        txHash: receipt.transactionHash,  // 0G Chain tx
        blockHeight: receipt.blockHeight,
        daGasCost: receipt.gasUsed,       // In 0G tokens
        finalityMs: finalityTime
    };
}
```

**Parallel: Permanent Storage on 0G Storage**
```javascript
// For the actual media file (larger than 1MB)
const { StorageClient } = require('@0g/sdk/storage');

async function archiveMedia(fileBuffer, contentHash) {
    const storage = new StorageClient({
        indexer: 'https://indexer.0g.testnet',
        // Erasure coding ensures 99.999% durability
        redundancy: 3
    });
    
    // Upload with content addressing
    const uploadTx = await storage.upload(fileBuffer, {
        tags: [
            `content-hash:${contentHash}`,
            'protocol:truthstream',
            'tier:permanent'
        ],
        // Storage duration: permanent (staked)
        duration: 'permanent'
    });
    
    return uploadTx.rootHash;
}
```

**Smart Contract Interaction (Staking Escrow)**
```solidity
// Immediately called after DA confirmation
function recordVerification(
    bytes32 _contentHash,
    bytes32 _daBlobId,
    bytes32 _storageHash,
    uint8 _tomaScore
) external {
    // Only trusted AI oracle (our backend) can call
    require(msg.sender == aiOracleAddress, "Unauthorized");
    
    certificates[_contentHash] = Certificate({
        contentHash: _contentHash,
        daBlobId: _daBlobId,
        storageHash: _storageHash,
        tomaScore: _tomaScore,
        timestamp: block.timestamp,
        staked: 0, // User hasn't staked yet
        status: Status.VERIFIED
    });
    
    emit ContentVerified(_contentHash, _daBlobId, _tomaScore);
}
```

---

### **STEP 4: The Staking Layer** (Optional - 4500ms+)

#### **User Side (UI)**
```
┌─────────────────────────────────────────────┐
│  Trust this verification?                   │
├─────────────────────────────────────────────┤
│                                             │
│  Current Community Confidence: 94%          │
│  Based on 23 stakers (avg 15 0G each)       │
│                                             │
│  [Stake 10 0G] [Stake 50 0G] [Custom]       │
│  │                                            │
│  └──► Potential reward: +2.3 0G/year        │
│       Risk: Lose stake if proven false      │
│                                             │
│  Or just [Share Results] without staking    │
└─────────────────────────────────────────────┘
```

**Backend:**
```javascript
// User initiates stake
async function stakeOnTruth(contentHash, amount) {
    const tx = await contract.stakeTruth(contentHash, {
        value: ethers.utils.parseEther(amount.toString())
    });
    
    // Update UI with staking position
    return {
        stakeId: tx.events.Staked.returnValues.id,
        unlockTime: Date.now() + (7 * 24 * 60 * 60 * 1000), // 7 days
        rewardAPR: calculateAPR(contentHash) // Dynamic based on disputes
    };
}
```

---

## 🔄 FLOW 2: BROWSER EXTENSION (Passive Verification)

### **User Experience**
1. User installs Chrome extension
2. Browsing Twitter/X, sees tweet with image
3. Extension icon pulses purple (0G brand color)
4. Hover over badge → Mini popup appears:

```
┌──────────────────┐
│ 🛡️ 87/100 VERIFIED│
├──────────────────┤
│ Source: 0G DA    │
│ Hash: 0x7f8...   │
│ [View Full Cert] │
└──────────────────┘
```

### **Backend (Content Script)**
```javascript
// content.js - Runs on every page
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        // Detect images in tweets
        const images = document.querySelectorAll('img[data-testid="tweetPhoto"]');
        images.forEach(async (img) => {
            const imageUrl = img.src;
            
            // Check cache first
            const cached = await chrome.storage.local.get(imageUrl);
            if (cached) {
                addBadge(img, cached.score);
                return;
            }
            
            // Hash the image (client-side)
            const hash = await hashImage(imageUrl);
            
            // Check 0G Registry (our API)
            const cert = await fetch(`https://api.truthstream.0g.ai/check/${hash}`);
            
            if (cert.exists) {
                addBadge(img, cert.tomaScore);
                // Cache locally
                chrome.storage.local.set({[imageUrl]: cert});
            }
        });
    });
});
```

---

## ⚔️ FLOW 3: THE CHALLENGE/DISPUTE (The Economic Game)

### **User Side (UI)**
User sees content marked "VERIFIED" but believes it's fake:

```
┌─────────────────────────────────────────────┐
│  ⚠️ Challenge This Verification?            │
├─────────────────────────────────────────────┤
│                                             │
│  You are challenging:                       │
│  "PM Speech Video"                          │
│  Current staked: 450 0G                     │
│                                             │
│  To challenge, you must stake: 900 0G       │
│  (2x current stake)                         │
│                                             │
│  Reason for challenge:                      │
│  [ ] Out of context                         │
│  [ ] Visually manipulated                   │
│  [ ] Different event/location               │
│  [Other: ________________]                  │
│                                             │
│  Evidence (Upload proof):                   │
│  [Drop original here]                       │
│                                             │
│  [Submit Challenge]                         │
│                                             │
│  ⏳ Resolution: 7 days or AI jury decides   │
└─────────────────────────────────────────────┘
```

### **Backend (Dispute Resolution)**

**Phase 1: Challenge Initiated**
```solidity
function challengeVerification(
    bytes32 _contentHash,
    string memory _reason,
    bytes32 _evidenceHash
) external payable {
    Certificate storage cert = certificates[_contentHash];
    require(msg.value >= cert.staked * 2, "2x stake required");
    require(!cert.challenged, "Already challenged");
    
    challenges[_contentHash] = Challenge({
        challenger: msg.sender,
        stake: msg.value,
        reason: _reason,
        evidenceHash: _evidenceHash,
        startTime: block.timestamp,
        votesForTruth: 0,
        votesForFalse: 0
    });
    
    cert.challenged = true;
    cert.status = Status.DISPUTED;
    
    emit ChallengeInitiated(_contentHash, msg.sender, msg.value);
}
```

**Phase 2: AI Jury (Automated)**
```python
# After 7 days or threshold reached
async def resolve_with_ai_jury(contentHash):
    cert = await get_certificate(contentHash)
    challenge = await get_challenge(contentHash)
    
    # Re-run analysis with higher scrutiny
    deep_analysis = await claude_analyze(
        cert.storageHash,
        focus="forensic_details",
        context=challenge.evidenceHash
    )
    
    # Determine winner
    if deep_analysis.overruled:
        # Challenger wins
        await contract.resolve(contentHash, False)  # False = original was wrong
        await send_reward(challenge.challenger, cert.staked * 3)
    else:
        # Original verifier wins
        await contract.resolve(contentHash, True)
        await slash_challenger(challenge.challenger)
```

---

## 📊 ADMIN/ARCHIVIST VIEW (Power Users)

### **Search Interface**
```
┌─────────────────────────────────────────────┐
│  TruthStream Archivist                      │
├─────────────────────────────────────────────┤
│                                             │
│  Search: [____________________] [🔍]        │
│  Filters: [Images ▼] [Verified ▼] [7 days ▼]│
│                                             │
│  Results:                                   │
│  ┌──────────────────────────────────────┐   │
│  │ 📰 Election News Batch #241          │   │
│  │ 1,234 items | 98.2% verified         │   │
│  │ DA Root: 0x9f82...11a3               │   │
│  │ [Download Dataset] [Verify Batch]    │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  Network Stats:                             │
│  • 50.2 Gbps throughput                     │
│  • 1.2M certificates issued                 │
│  • Avg finality: 1.8 seconds                │
└─────────────────────────────────────────────┘
```

---

## 🏗️ INFRASTRUCTURE ARCHITECTURE

### **System Diagram**
```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                           │
│  React/Next.js Frontend    │   Chrome Ext   │   WhatsApp Bot │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                   │
│  • Rate limiting (100 req/min free tier)                     │
│  • JWT Auth (Web2) / Wallet Auth (Web3)                      │
│  • Request routing                                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐  ┌─────────▼──────────┐
│   AI ORCHESTRATOR │  │   0G INTEGRATION     │
│  (Celery/Redis)   │  │  (Node.js service)   │
│                   │  │                      │
│  • Claude API     │  │  • DA Client         │
│  • Deepfake GPU   │  │  • Storage Client    │
│  • Perplexity     │  │  • Contract Admin    │
│  • OCR Service    │  │  • Gas Station       │
└────────┬──────────┘  └─────────┬──────────┘
         │                       │
         └───────────┬───────────┘
                     │
        ┌────────────▼────────────┐
        │    0G NETWORK LAYER      │
        │  ┌─────────┐ ┌────────┐ │
        │  │ 0G DA   │ │0G Chain│ │
        │  │ Layer   │ │ (EVM)  │ │
        │  └────┬────┘ └────┬───┘ │
        │       └──────┬────┘     │
        │       ┌──────▼────┐      │
        │       │ 0G Storage│      │
        │       │ (Archive) │      │
        │       └───────────┘      │
        └──────────────────────────┘
```

---

## ⚡ PERFORMANCE BUDGETS

| Operation | Target Time | Tech |
|-----------|-------------|------|
| **Image Upload** | <2s | Multipart/form-data → S3 |
| **AI Analysis** | <3s | Parallel GPU + LLM calls |
| **0G DA Finality** | <500ms | 50 Gbps direct inject |
| **Total to Certificate** | **<5s** | End-to-end |
| **Challenge Resolution** | 7 days or AI jury | Smart contract timelock |

---

## 🎯 THE "HOLY SHIT" MOMENT (For Judges)

**The Demo Sequence:**
1. **Upload deepfake video** (shows Modi saying something false)
2. **Screen splits:**
   - Left: AI scanning frame-by-frame
   - Right: 0G block explorer showing real-time blob creation
3. **At exactly 2.3 seconds:** Both sides flash green simultaneously
4. **Reveal:** "While traditional blockchains take 12 seconds per block, 0G DA confirmed this analysis in 2.3 seconds—**before the deepfake could go viral**."
5. **Stake moment:** "I'm so confident this is fake, I'm staking 50 real $0G tokens. If I'm wrong, I lose them. If I'm right, I earn yield."

**The Backend Secret:**
During the demo, you're actually pre-uploading to 0G DA while the AI runs (parallel, not sequential). The "2.3 seconds" includes both AI + blockchain, which is impossible on Ethereum (15s block time) or even Solana (400ms but often congested).

---