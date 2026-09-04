const API_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:" || window.location.hostname === "") ? "http://127.0.0.1:8000" : "/api";
let currentRepoId = null;

$(document).ready(function() {
    
    // Setup AJAX to include Authorization header globally
    const token = localStorage.getItem("token");
    if (token) {
        $.ajaxSetup({
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } else {
        // Redirect to login if token is missing
        if (!window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("index.html")) {
            window.location.href = "login.html";
        }
    }
    
    // Handle Repository Clone
    $("#cloneBtn").click(function() {
        const repoUrl = $("#repoUrl").val().trim();
        if (!repoUrl) return;
        
        $("#repoStatus").text("Cloning and indexing...");
        $("#cloneBtn").prop("disabled", true);
        
        $.ajax({
            url: `${API_URL}/repos`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ github_url: repoUrl }),
            success: function(res) {
                $("#repoStatus").text("Repository successfully ingested! " + res.chunks_processed + " chunks processed.");
                $("#chatInput, #sendBtn").prop("disabled", false);
                currentRepoId = res.repo_id;
                $("#welcomeMsg").hide();
            },
            error: function(err) {
                $("#repoStatus").text("Error cloning repository: " + (err.responseJSON ? err.responseJSON.detail : err.statusText));
                $("#cloneBtn").prop("disabled", false);
            }
        });
    });

    // Handle Chat Submit
    $("#chatForm").submit(function(e) {
        e.preventDefault();
        
        const question = $("#chatInput").val().trim();
        if (!question) return;
        
        if (!currentRepoId) {
            appendMessage("bot", "Please clone a repository first.");
            return;
        }
        
        // Append user message
        appendMessage("user", question);
        $("#chatInput").val("");
        
        // Disable input while waiting
        $("#chatInput, #sendBtn").prop("disabled", true);
        
        $.ajax({
            url: `${API_URL}/ask`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                question: question,
                repo_id: String(currentRepoId)
            }),
            success: function(res) {
                appendMessage("bot", res.answer, res.sources);
            },
            error: function(err) {
                appendMessage("bot", "Sorry, an error occurred while generating the answer: " + (err.responseJSON ? err.responseJSON.detail : err.statusText));
            },
            complete: function() {
                $("#chatInput, #sendBtn").prop("disabled", false);
                $("#chatInput").focus();
            }
        });
    });
    
    function appendMessage(sender, text, sources = []) {
        let html = `<div class="chat-bubble ${sender}">`;
        
        html += `<div>${text}</div>`;
        
        if (sources && sources.length > 0) {
            html += `<div class="mt-2" style="font-size: 0.85em; color: #a1a1aa;"><strong>Sources:</strong><ul>`;
            sources.forEach(src => {
                html += `<li><code>${src}</code></li>`;
            });
            html += `</ul></div>`;
        }
        
        html += `</div>`;
        $("#chatBox").append(html);
        
        // Auto scroll to bottom
        $("#chatBox").scrollTop($("#chatBox")[0].scrollHeight);
    }
});
