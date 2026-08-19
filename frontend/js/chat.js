// Chat Interface & Graph Logic

let network = null;

$(document).ready(function() {
    // Chat Form Submission
    $('#chat-form').submit(function(e) {
        e.preventDefault();
        const input = $('#chat-input');
        const message = input.val().trim();
        
        if (message) {
            // 1. Add User Message
            appendUserMessage(message);
            input.val('');
            
            // 2. Similar Search Toast Detection
            if (message.toLowerCase().includes('login') || message.toLowerCase().includes('auth')) {
                setTimeout(() => {
                    $('#similar-search-text').text(`"Where is authentication implemented?"`);
                    $('#similar-search-toast').removeClass('d-none');
                    setTimeout(() => $('#similar-search-toast').addClass('d-none'), 5000);
                }, 500);
            }

            // 3. Clear Evidence Pane and Add Skeleton
            $('#evidence-content').html(`
                <div class="mb-3" style="width: 75%; height: 20px; background-color: var(--border); border-radius: var(--radius-sm);"></div>
                <div class="mb-4" style="width: 100%; height: 80px; background-color: var(--border); border-radius: var(--radius-sm);"></div>
                <div class="mb-3" style="width: 50%; height: 20px; background-color: var(--border); border-radius: var(--radius-sm);"></div>
                <div style="width: 100%; height: 80px; background-color: var(--border); border-radius: var(--radius-sm);"></div>
            `);

            // 4. Simulate SSE Streaming AI Response with blinking cursor
            simulateSSEStream(message);
        }
    });

    // Delegate click for chunk chips
    $(document).on('click', '.chunk-chip', function() {
        const targetId = $(this).data('target');
        $('#tab-evidence').click(); // switch to evidence tab
        
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Flash effect
            $(targetElement).css('background-color', 'rgba(88, 166, 255, 0.1)');
            setTimeout(() => {
                $(targetElement).css('background-color', 'transparent');
            }, 1000);
        }
    });
});

function appendUserMessage(text) {
    const html = `
        <div class="chat-message d-flex gap-3">
            <div class="chat-avatar avatar-user"><i class="fa-solid fa-user"></i></div>
            <div class="flex-grow-1">
                <div class="fw-semibold text-primary mb-1 font-prose small">You</div>
                <p class="mb-0 text-primary font-prose lh-base">${escapeHtml(text)}</p>
            </div>
        </div>
    `;
    $('#chat-messages').append(html);
    scrollToBottom();
}

function simulateSSEStream(query) {
    // Append AI Avatar container
    const msgId = 'ai-msg-' + Date.now();
    const html = `
        <div class="chat-message d-flex gap-3">
            <div class="chat-avatar avatar-ai"><i class="fa-solid fa-terminal"></i></div>
            <div class="flex-grow-1">
                <div class="fw-semibold text-primary mb-1 font-prose small d-flex justify-content-between align-items-center">
                    <span>CodeMind <span class="ide-badge badge-success ms-2">GROUNDED</span></span>
                </div>
                <p class="mb-0 text-primary font-prose lh-base" style="min-height: 20px;">
                    <span id="${msgId}"></span><span class="cursor-blink"></span>
                </p>
                <div class="mt-2">
                    <span class="text-secondary font-code" style="font-size: 0.65rem;">Confidence Score: 0.92</span>
                    <div class="confidence-bar-container">
                        <div class="confidence-bar-fill bg-success" style="width: 92%;"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    $('#chat-messages').append(html);
    scrollToBottom();

    // Stream text chunks (simulated)
    const fullText = `Authentication is handled in \`authController.js\`. Routes are defined in \`authRoutes.js\`. The \`User\` schema verifies passwords via bcrypt.<br><br><span class="chunk-chip mt-2" data-target="chunk-auth-12"><i class="fa-solid fa-file-code me-1"></i>authController.js:42-65</span>`;
    
    let currentIdx = 0;
    const targetElement = $(`#${msgId}`);
    const blinkCursor = targetElement.next('.cursor-blink');
    
    // Simulate streaming
    const interval = setInterval(() => {
        if (currentIdx < fullText.length) {
            let chunk = fullText[currentIdx];
            if (chunk === '<') {
                let tag = '';
                while (fullText[currentIdx] !== '>' && currentIdx < fullText.length) {
                    tag += fullText[currentIdx];
                    currentIdx++;
                }
                tag += '>';
                chunk = tag;
            }
            
            targetElement.append(chunk);
            scrollToBottom();
            currentIdx++;
        } else {
            clearInterval(interval);
            // Remove blinking cursor when done
            blinkCursor.remove();
            populateEvidence();
        }
    }, 15); // simulate typewriter effect
}

function scrollToBottom() {
    const container = $('#chat-messages');
    container.animate({ scrollTop: container[0].scrollHeight }, 50);
}

function populateEvidence() {
    const evidenceHtml = `
        <div class="mb-4 p-3 border-bottom-subtle" id="chunk-auth-12" style="transition: background-color 0.3s;">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="text-primary mb-0 font-code small"><i class="fa-brands fa-node-js me-2 text-accent"></i>authController.js</h6>
                <span class="text-secondary font-code" style="font-size: 0.65rem;">Lines 42-65</span>
            </div>
            <pre class="m-0"><code class="language-javascript">
const loginUser = async (req, res) => {
    const { email, password } = req.body;
    
    try {
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ msg: 'Invalid credentials' });
        }
        
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ msg: 'Invalid credentials' });
        }
        
        const payload = { user: { id: user.id } };
        jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' },
            (err, token) => {
                if (err) throw err;
                res.json({ token });
            }
        );
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
};
            </code></pre>
            <div class="mt-2 text-end">
                <span class="ide-badge">CONTROLLER</span>
            </div>
        </div>
    `;
    
    $('#evidence-content').html(evidenceHtml);
    document.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
}

function newChat() {
    $('#chat-messages').html(`
        <div class="text-center my-5 text-secondary">
            <i class="fa-solid fa-terminal fs-1 mb-3 text-accent"></i>
            <h5 class="text-primary fw-semibold">Ask CodeMind</h5>
            <p class="text-secondary small font-code mt-2">Context Engine Active</p>
        </div>
    `);
    $('#evidence-content').html(`
        <div class="text-center text-secondary mt-5 pt-5">
            <i class="fa-solid fa-magnifying-glass fs-2 mb-3"></i>
            <p class="text-secondary small font-code mt-2">Retrieved chunks will appear here.</p>
        </div>
    `);
}

window.newChat = newChat;

// vis-network Graph Rendering
window.renderGraph = function() {
    const container = document.getElementById('network-graph');
    if (!container) return;

    // Terminal Dark Colors
    const nodeColor = { background: '#1c2128', border: '#30363d' };
    const fontObj = { color: '#e6edf3', face: 'JetBrains Mono', size: 12 };
    const edgeColor = { color: '#8b949e' };

    const nodes = new vis.DataSet([
        { id: 1, label: 'Login.jsx', shape: 'box', color: nodeColor, font: fontObj },
        { id: 2, label: 'authRoutes.js', shape: 'box', color: nodeColor, font: fontObj },
        { id: 3, label: 'authController.js', shape: 'box', color: { background: '#1c2128', border: '#58a6ff' }, font: fontObj, borderWidth: 2 },
        { id: 4, label: 'User.js', shape: 'box', color: nodeColor, font: fontObj }
    ]);

    const edges = new vis.DataSet([
        { id: 'e1', from: 1, to: 2, label: 'fetch() POST', arrows: 'to', font: { color: '#8b949e', size: 10, align: 'top', face: 'JetBrains Mono' }, color: edgeColor },
        { id: 'e2', from: 2, to: 3, label: 'calls', arrows: 'to', font: { color: '#8b949e', size: 10, align: 'top', face: 'JetBrains Mono' }, color: edgeColor },
        { id: 'e3', from: 3, to: 4, label: 'imports', arrows: 'to', font: { color: '#8b949e', size: 10, align: 'top', face: 'JetBrains Mono' }, color: edgeColor }
    ]);

    const data = { nodes: nodes, edges: edges };
    const options = {
        interaction: { hover: true },
        physics: { stabilization: false, barnesHut: { springLength: 150 } }
    };

    if (network) {
        network.destroy();
    }
    network = new vis.Network(container, data, options);
};

// Helper to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}
