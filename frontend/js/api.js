// API Service Mock
// This file will handle real backend calls once the FastAPI backend is ready.

const API = {
    // Auth
    login: async (email, password) => {
        console.log("Mock API: login", email);
        return { token: "mock_jwt_token", user: { name: "Developer" } };
    },
    
    register: async (name, email, password) => {
        console.log("Mock API: register", email);
        return { success: true };
    },

    // Repositories
    getRepositories: async () => {
        return [
            { id: 1, name: "CodeMind", status: "Indexed", lastUpdated: "2h ago", fileCount: 124 }
        ];
    },
    
    addRepository: async (url) => {
        return { success: true, message: "Indexing started" };
    },

    // Chat / Query
    askQuestion: async (repoId, question) => {
        console.log("Mock API: asking question", question);
        return {
            answer: "This is a mock answer from the API service.",
            hasEvidence: true,
            evidence: {}
        };
    }
};

window.API = API;
