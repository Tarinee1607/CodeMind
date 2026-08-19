// CodeMind UI Orchestrator (IDE Theme)

$(document).ready(function() {
    console.log("CodeMind UI initialized (IDE Architecture Theme).");

    // Interactive Mouse Spotlight
    $(document).mousemove(function(e) {
        $('.mouse-glow').get(0).style.setProperty('--mouse-x', `${e.clientX}px`);
        $('.mouse-glow').get(0).style.setProperty('--mouse-y', `${e.clientY}px`);
    });

    // Toggle Login/Register
    $('#show-register').click(function(e) {
        e.preventDefault();
        $('#login-form').addClass('d-none');
        $('#register-form').removeClass('d-none');
    });

    $('#show-login').click(function(e) {
        e.preventDefault();
        $('#register-form').addClass('d-none');
        $('#login-form').removeClass('d-none');
    });

    // Mock Login Action
    $('#login-form').submit(function(e) {
        e.preventDefault();
        const btn = $(this).find('button');
        const originalHtml = btn.html();
        btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...');
        setTimeout(() => {
            showDashboard();
            btn.html(originalHtml);
        }, 800);
    });

    // Mock Register Action
    $('#register-form').submit(function(e) {
        e.preventDefault();
        const btn = $(this).find('button');
        const originalHtml = btn.html();
        btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Initializing...');
        setTimeout(() => {
            showDashboard();
            btn.html(originalHtml);
        }, 800);
    });

    // Logout
    $('#btn-logout').click(function(e) {
        e.preventDefault();
        showScreen('auth-screen');
    });

    // Add Repo / Indexing Flow (Pipeline A Simulation)
    $('#add-repo-form').submit(function(e) {
        e.preventDefault();
        const btn = $(this).find('button');
        btn.prop('disabled', true);
        
        // Show progress UI
        $('#indexing-progress').removeClass('d-none');
        
        // Simulate Pipeline A: Cloning -> Parsing -> Embedding
        setTimeout(() => completeStage('clone', 'parse', '2. Code Parser (tree-sitter) [Running...]'), 1500);
        setTimeout(() => completeStage('parse', 'embed', '3. Embedding Generator [Running...]'), 3500);
        setTimeout(() => {
            completeStage('embed', null, null);
            $('#addRepoModal').modal('hide');
            // Reset for next time
            btn.prop('disabled', false);
            $('#indexing-progress').addClass('d-none');
            resetStages();
        }, 5500);
    });

    // Ctrl+K / Cmd+K shortcut
    $(document).keydown(function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if ($('#chat-screen').hasClass('active')) {
                $('#chat-input').focus();
            } else if ($('#dashboard-screen').hasClass('active')) {
                openChat('CodeMind');
                setTimeout(() => $('#chat-input').focus(), 100);
            }
        }
    });

    // Split Pane Tabs
    $('#tab-evidence').click(function() {
        $(this).addClass('active').removeClass('text-secondary');
        $('#tab-relationships').removeClass('active').addClass('text-secondary');
        $('#evidence-content').removeClass('d-none');
        $('#relationships-content').addClass('d-none');
    });

    $('#tab-relationships').click(function() {
        $(this).addClass('active').removeClass('text-secondary');
        $('#tab-evidence').removeClass('active').addClass('text-secondary');
        $('#relationships-content').removeClass('d-none');
        $('#evidence-content').addClass('d-none');
        
        // Render graph if visNetwork exists
        if (window.renderGraph) {
            window.renderGraph();
        }
    });
});

// Screen Management
function showScreen(screenId) {
    $('.screen-section').removeClass('active');
    $('#' + screenId).addClass('active');
}

function showDashboard() {
    showScreen('dashboard-screen');
}
window.showDashboard = showDashboard;

function openChat(repoName) {
    $('#current-repo-badge').text(repoName);
    showScreen('chat-screen');
    $('#chat-input').focus();
}
window.openChat = openChat;

// Pipeline A Simulation Helpers
function completeStage(current, next, nextText) {
    // Complete current
    $(`#icon-${current}`).removeClass('fa-circle-notch fa-spin text-pipeline-a').addClass('fa-check text-success');
    $(`#text-${current}`).text($(`#text-${current}`).text().replace('[Running...]', '[Done]'));
    
    // Start next
    if (next) {
        $(`#icon-${next}`).removeClass('fa-circle text-secondary').addClass('fa-circle-notch fa-spin text-pipeline-a');
        $(`#text-${next}`).removeClass('text-secondary').addClass('text-primary fw-bold').text(nextText);
    }
}

function resetStages() {
    ['clone', 'parse', 'embed'].forEach(stage => {
        $(`#icon-${stage}`).removeClass('fa-check text-success fa-circle-notch fa-spin text-pipeline-a').addClass('fa-circle text-secondary');
    });
    $(`#icon-clone`).removeClass('fa-circle text-secondary').addClass('fa-circle-notch fa-spin text-pipeline-a');
    
    $('#text-clone').addClass('text-primary fw-bold').removeClass('text-secondary').text('1. Repository Manager [Running...]');
    $('#text-parse').addClass('text-secondary').removeClass('text-primary fw-bold').text('2. Code Parser (tree-sitter)');
    $('#text-embed').addClass('text-secondary').removeClass('text-primary fw-bold').text('3. Embedding Generator');
}
