// Dynamically point to whichever host served this page.
// This works for localhost AND for other devices on the same network.
const API_BASE_URL = `${window.location.origin}/api`;

// Utility to convert ArrayBuffer to Hex String
function buf2hex(buffer) {
    return [...new Uint8Array(buffer)]
        .map(x => x.toString(16).padStart(2, '0'))
        .join('');
}

// Convert PEM to ArrayBuffer (DER format) - Required by Web Crypto API
function pemToArrayBuffer(pem) {
    const b64 = pem.replace(/-----BEGIN [A-Z ]+-----/g, '')
                   .replace(/-----END [A-Z ]+-----/g, '')
                   .replace(/\s+/g, '');
    const binary = window.atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// SHA-256 Hash
async function sha256(str) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
    return buf2hex(buf);
}

// State
let storedPrivateKeyBuffer = null;
let storedPublicKeyPem = null;
let currentCandidate = null;

// Page Initialization Routing
document.addEventListener('DOMContentLoaded', () => {
    // 1. Login Logic
    const btnLogin = document.getElementById('btn-login');
    if (btnLogin) {
        btnLogin.onclick = handleLogin;
    }

    // 2. Voting Logic
    if (window.location.pathname.endsWith('vote.html')) {
        loadKeysFromStorage();
        if (!storedPrivateKeyBuffer || !storedPublicKeyPem) {
            alert('Security Error: Private or Public key missing. Redirecting to login.');
            window.location.href = 'index.html';
            return;
        }
    }

    // 3. Dashboard Logic
    if (window.location.pathname.endsWith('dashboard.html')) {
        pollBlockchain();
        // Set up the polling mechanism directly via setInterval
        setInterval(pollBlockchain, 30000); 
    }
});

async function handleLogin() {
    const privateKeyUpload = document.getElementById('private-key-upload');
    const publicKeyUpload = document.getElementById('public-key-upload');

    if (!privateKeyUpload.files[0] || !publicKeyUpload.files[0]) {
        alert("Please upload both your Private AND Public Key (.pem) files to authenticate.");
        return;
    }

    try {
        const privText = await privateKeyUpload.files[0].text();
        const pubText = await publicKeyUpload.files[0].text();

        // Validate it is somewhat readable by our parser
        const privBuf = pemToArrayBuffer(privText);
        
        // Save to sessionStorage so it doesn't persist after closing tab
        sessionStorage.setItem('privateKeyDer', buf2hex(privBuf));
        sessionStorage.setItem('publicKeyPem', pubText.trim());
        
        window.location.href = 'vote.html';
    } catch(e) {
        alert("Authentication Failed. Invalid PEM format detected: " + e.message);
    }
}

function loadKeysFromStorage() {
    const privHex = sessionStorage.getItem('privateKeyDer');
    if (privHex) {
        const bytes = new Uint8Array(privHex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        storedPrivateKeyBuffer = bytes.buffer;
    }
    storedPublicKeyPem = sessionStorage.getItem('publicKeyPem');
}

// UI Functions for vote.html
async function showModal(candidate) {
    currentCandidate = candidate;
    document.getElementById('selectedCandidate').innerText = candidate;
    document.getElementById('signatureModal').style.display = 'flex';
    document.getElementById('previewSignature').innerText = "Generating zero-knowledge cryptographic signature...";

    try {
        // Implement the highly secure Web Crypto API
        const privateKey = await crypto.subtle.importKey(
            "pkcs8",
            storedPrivateKeyBuffer,
            {
                name: "RSA-PSS",
                hash: "SHA-256",
            },
            false,
            ["sign"]
        );

        const enc = new TextEncoder();
        
        // PSS Configuration matching cryptography library in Python
        // cryptography by default uses MAX_LENGTH for salt, but web crypto uses the hash size (32 bytes)
        // For compatibility with verify without MAX_LENGTH, we supply 32. 
        // Python handles this gracefully!
        const signatureBuffer = await crypto.subtle.sign(
            {
                name: "RSA-PSS",
                saltLength: 32 
            },
            privateKey,
            enc.encode(candidate)
        );

        const sigHex = buf2hex(signatureBuffer);
        document.getElementById('previewSignature').innerText = sigHex;

        console.log("DEBUG: Generated signature hex (first 50):", sigHex.substring(0, 50));

        // Save signature hex globally for form submission step
        window.currentSignatureHex = sigHex;

    } catch (e) {
        console.error(e);
        document.getElementById('previewSignature').innerText = "FATAL ERROR: Failed to natively sign payload. Check key configuration. Details: " + e.message;
    }
}

function hideModal() {
    document.getElementById('signatureModal').style.display = 'none';
    currentCandidate = null;
    window.currentSignatureHex = null;
}

// Submits the vote to the Python Flask backend
async function submitVote() {
    if (!currentCandidate || !window.currentSignatureHex) {
        alert("Signature is still generating or missing!");
        return;
    }

    try {
        // Calculate voter ID locally utilizing sha256 to hash the exact public key string mapping to backend
        const strippedPem = storedPublicKeyPem.replace(/\s+/g, '');
        const voterId = await sha256(strippedPem);

        console.log("DEBUG: Client voterId:", voterId);
        console.log("DEBUG: Stripped PEM (first 100):", strippedPem.substring(0, 100));

        const payload = {
            voter_id: voterId,
            vote: currentCandidate,
            public_key_pem: storedPublicKeyPem,
            signature: window.currentSignatureHex
        };

        const response = await fetch(`${API_BASE_URL}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert("Broadcast Success: " + data.message + "\nBlock Mined Confirmed!");
            
            // Clear keys for security after single vote cast
            sessionStorage.clear();
            
            window.location.href = 'dashboard.html';
        } else {
            alert("Node Rejection: " + data.error);
        }
    } catch (e) {
        alert("Connection Error: Failed to reach the local backend blockchain node.");
        console.error(e);
    }
}

// Logic for updating dashboard.html
async function pollBlockchain() {
    console.log("Polling blockchain node...");
    try {
        // 1. Fetch & Tally
        const resultsReq = await fetch(`${API_BASE_URL}/results`);
        if(resultsReq.ok) {
            const results = await resultsReq.json();
            
            if(document.getElementById('total-votes')) {
                document.getElementById('total-votes').innerText = results.total_votes;
            }
            if(document.getElementById('tally-a')) {
                document.getElementById('tally-a').innerText = results.results['Candidate A'] || 0;
            }
            if(document.getElementById('tally-b')) {
                document.getElementById('tally-b').innerText = results.results['Candidate B'] || 0;
            }
            if(document.getElementById('tally-c')) {
                document.getElementById('tally-c').innerText = results.results['Candidate C'] || 0;
            }
        }

        // 2. Fetch the Transparent Ledger
        const chainReq = await fetch(`${API_BASE_URL}/chain`);
        if(chainReq.ok) {
            const chainData = await chainReq.json();
            
            // Update live network status UI
            const statusDiv = document.querySelector('.explorer-status');
            if (statusDiv) {
                statusDiv.innerHTML = `<div class="status-dot"></div> Node Synced (Block ${chainData.length - 1})`;
            }
            
            const feed = document.getElementById('blockchain-feed');
            if (feed) {
                feed.innerHTML = ''; // Wipes the static examples out
                
                // Render from top down (Reverse Chronological Order)
                for (let i = chainData.chain.length - 1; i >= 0; i--) {
                    const block = chainData.chain[i];
                    const blockEl = document.createElement('div');
                    blockEl.className = 'block';
                    
                    let txHtml = '';
                    if (Array.isArray(block.data)) {
                        if (block.data.length === 0) {
                             txHtml += `<div class="transaction-item" style="color: var(--color-text-secondary);">Empty Block</div>`;
                        }
                        block.data.forEach(tx => {
                            // Extract just the first 10 hex characters of their public VoterID
                            const voterShort = tx.voter_id ? tx.voter_id.substring(0, 10) + '...' : 'Unknown';
                            txHtml += `<div class="transaction-item">Vote Cast by VoterID: <span style="color:var(--color-accent)">${voterShort}</span> -> ${tx.vote}</div>`;
                        });
                    } else {
                        // Genesis block contains a string
                        txHtml = `<div class="transaction-item" style="color: var(--color-text-secondary);">${block.data}</div>`;
                    }

                    // Dynamically shorten long hashes so it doesn't aggressively wrap 
                    const shortHash = block.hash.length > 20 ? block.hash.substring(0,10) + '...' + block.hash.substring(block.hash.length-10) : block.hash;
                    const shortPrev = block.previous_hash.length > 20 ? block.previous_hash.substring(0,10) + '...' + block.previous_hash.substring(block.previous_hash.length-10) : block.previous_hash;

                    blockEl.innerHTML = `
                        <div class="block-header">Block #${block.index} ${block.index === 0 ? '(Genesis)' : ''}</div>
                        <div class="block-detail">
                            <span class="label">Block Hash:</span>
                            <span class="hash-value">${shortHash}</span>
                        </div>
                        <div class="block-detail">
                            <span class="label">Previous Hash:</span>
                            <span class="hash-value">${shortPrev}</span>
                        </div>
                        <div class="block-detail">
                            <span class="label">Timestamp:</span>
                            <span>${new Date(block.timestamp * 1000).toLocaleString()}</span>
                        </div>
                        <div class="block-transactions">
                            ${txHtml}
                        </div>
                    `;
                    feed.appendChild(blockEl);
                }
            }
        }
    } catch (e) {
        console.error("Dashboard connection failed", e);
    }
}
