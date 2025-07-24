/**
 * Interactive Dashboard Main Controller
 * Manages the overall dashboard functionality and component coordination
 */

class InteractiveDashboard {
  constructor() {
    this.components = {};
    this.currentSession = null;
    this.isAnalyzing = false;

    this.init();
  }

  init() {
    // Initialize components
    this.initializeComponents();

    // Set up event listeners
    this.setupEventListeners();

    // Load initial data
    this.loadInitialData();

    console.log("Interactive Dashboard initialized");
  }

  initializeComponents() {
    // Initialize SSE handler for real-time updates
    this.components.sseHandler = new SSEHandler();

    // Initialize news selector component
    this.components.newsSelector = new NewsSelector("#news-selector");

    // Initialize character selector component
    this.components.characterSelector = new CharacterSelector(
      "#character-selector"
    );

    // Initialize results display component
    this.components.resultsDisplay = new ResultsDisplay("#results-container");

    // Set up component communication
    this.setupComponentCommunication();
  }

  setupComponentCommunication() {
    // News selector events
    this.components.newsSelector.on("news-selected", (data) => {
      this.handleNewsSelection(data);
    });

    // Character selector events
    this.components.characterSelector.on("characters-selected", (data) => {
      this.handleCharacterSelection(data);
    });

    // SSE handler events
    this.components.sseHandler.on("analysis-update", (data) => {
      this.handleAnalysisUpdate(data);
    });

    this.components.sseHandler.on("analysis-complete", (data) => {
      this.handleAnalysisComplete(data);
    });

    this.components.sseHandler.on("connection-error", (error) => {
      this.handleConnectionError(error);
    });
  }

  setupEventListeners() {
    // Start analysis button
    const startBtn = document.getElementById("start-analysis");
    if (startBtn) {
      startBtn.addEventListener("click", () => this.startAnalysis());
    }

    // Reset analysis button
    const resetBtn = document.getElementById("reset-analysis");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => this.resetAnalysis());
    }

    // Error modal handlers
    const modalClose = document.getElementById("modal-close");
    if (modalClose) {
      modalClose.addEventListener("click", () => this.hideErrorModal());
    }

    const errorRetry = document.getElementById("error-retry");
    if (errorRetry) {
      errorRetry.addEventListener("click", () => this.retryAnalysis());
    }

    const errorClose = document.getElementById("error-close");
    if (errorClose) {
      errorClose.addEventListener("click", () => this.hideErrorModal());
    }

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.hideErrorModal();
      }
    });
  }

  async loadInitialData() {
    try {
      this.showLoading("Loading dashboard data...");

      // Load characters and scenarios in parallel
      const [characters, scenarios] = await Promise.all([
        this.fetchCharacters(),
        this.fetchScenarios(),
      ]);

      // Initialize components with data
      this.components.characterSelector.setCharacters(characters);
      this.components.newsSelector.setScenarios(scenarios);

      this.hideLoading();
      this.updateStatus("Ready to analyze");
    } catch (error) {
      console.error("Failed to load initial data:", error);
      this.showError("Failed to load dashboard data. Please refresh the page.");
      this.hideLoading();
    }
  }

  async fetchCharacters() {
    const response = await fetch("/api/characters");
    if (!response.ok) {
      throw new Error(`Failed to fetch characters: ${response.status}`);
    }
    return await response.json();
  }

  async fetchScenarios() {
    const response = await fetch("/api/scenarios");
    if (!response.ok) {
      throw new Error(`Failed to fetch scenarios: ${response.status}`);
    }
    return await response.json();
  }

  handleNewsSelection(data) {
    console.log("News selected:", data);
    this.updateStatus("News content selected");
  }

  handleCharacterSelection(data) {
    console.log("Characters selected:", data);
    this.updateStatus(`${data.selectedCharacters.length} characters selected`);
  }

  handleAnalysisUpdate(data) {
    console.log("Analysis update:", data);
    this.components.resultsDisplay.updateResult(data);
  }

  handleAnalysisComplete(data) {
    console.log("Analysis complete:", data);
    this.isAnalyzing = false;
    this.updateAnalysisButton(false);
    this.updateStatus("Analysis complete");
    this.components.sseHandler.disconnect();
  }

  handleConnectionError(error) {
    console.error("SSE connection error:", error);
    this.showError("Connection lost. Please try again.");
    this.isAnalyzing = false;
    this.updateAnalysisButton(false);
  }

  async startAnalysis() {
    if (this.isAnalyzing) {
      return;
    }

    const selectedNews = this.components.newsSelector.getSelectedNews();
    const selectedCharacters =
      this.components.characterSelector.getSelectedCharacters();

    if (!selectedNews || !selectedNews.content) {
      this.showError("Please select or enter news content to analyze.");
      return;
    }

    if (!selectedCharacters || selectedCharacters.length === 0) {
      this.showError("Please select at least one character to analyze.");
      return;
    }

    try {
      this.isAnalyzing = true;
      this.updateAnalysisButton(true);
      this.updateStatus("Starting analysis...");

      // Clear previous results
      this.components.resultsDisplay.clearResults();

      // Start SSE connection
      const sessionId = await this.initiateAnalysis(
        selectedNews,
        selectedCharacters
      );
      this.currentSession = sessionId;

      // Connect to SSE stream
      this.components.sseHandler.connect(sessionId);

      this.updateStatus("Analysis in progress...");
    } catch (error) {
      console.error("Failed to start analysis:", error);
      this.showError("Failed to start analysis. Please try again.");
      this.isAnalyzing = false;
      this.updateAnalysisButton(false);
    }
  }

  async initiateAnalysis(news, characters) {
    const response = await fetch("/api/analyze-engagement", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        news_content: news.content,
        character_ids: characters.map((c) => c.id),
        custom_news: news.isCustom || false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Analysis request failed: ${response.status}`);
    }

    const result = await response.json();
    return result.session_id;
  }

  resetAnalysis() {
    this.isAnalyzing = false;
    this.currentSession = null;

    // Reset components
    this.components.newsSelector.reset();
    this.components.characterSelector.reset();
    this.components.resultsDisplay.clearResults();

    // Disconnect SSE
    this.components.sseHandler.disconnect();

    // Reset UI
    this.updateAnalysisButton(false);
    this.updateStatus("Ready to analyze");

    console.log("Analysis reset");
  }

  retryAnalysis() {
    this.hideErrorModal();
    if (this.currentSession) {
      this.components.sseHandler.connect(this.currentSession);
    } else {
      this.startAnalysis();
    }
  }

  updateAnalysisButton(isAnalyzing) {
    const startBtn = document.getElementById("start-analysis");
    if (!startBtn) return;

    const btnText = startBtn.querySelector(".btn-text");
    const btnLoading = startBtn.querySelector(".btn-loading");

    if (isAnalyzing) {
      startBtn.disabled = true;
      btnText.style.display = "none";
      btnLoading.style.display = "inline-flex";
    } else {
      startBtn.disabled = false;
      btnText.style.display = "inline";
      btnLoading.style.display = "none";
    }
  }

  updateStatus(message) {
    const statusElement = document.querySelector(".status-text");
    if (statusElement) {
      statusElement.textContent = message;
    }
  }

  showLoading(message = "Loading...") {
    const overlay = document.getElementById("loading-overlay");
    const messageEl = document.getElementById("loading-message");

    if (overlay) {
      overlay.style.display = "flex";
    }

    if (messageEl) {
      messageEl.textContent = message;
    }
  }

  hideLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.style.display = "none";
    }
  }

  showError(message) {
    const modal = document.getElementById("error-modal");
    const messageEl = document.getElementById("error-message");

    if (modal) {
      modal.style.display = "flex";
    }

    if (messageEl) {
      messageEl.textContent = message;
    }
  }

  hideErrorModal() {
    const modal = document.getElementById("error-modal");
    if (modal) {
      modal.style.display = "none";
    }
  }
}

// Event emitter utility for component communication
class EventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }

  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach((callback) => callback(data));
    }
  }

  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter((cb) => cb !== callback);
    }
  }
}

// Initialize dashboard when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new InteractiveDashboard();
});

// Export for testing
if (typeof module !== "undefined" && module.exports) {
  module.exports = { InteractiveDashboard, EventEmitter };
}
