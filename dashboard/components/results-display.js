/**
 * Results Display Component
 * Handles real-time display of character analysis results
 */

class ResultsDisplay extends EventEmitter {
  constructor(selector) {
    super();
    this.container = document.querySelector(selector);
    this.results = new Map(); // character_id -> result data
    this.isDisplaying = false;

    this.init();
  }

  init() {
    if (!this.container) {
      console.error("Results display container not found");
      return;
    }

    this.render();
  }

  render() {
    this.container.innerHTML = `
            <div class="results-display-content">
                <!-- Results will be dynamically populated -->
            </div>
        `;
  }

  updateResult(data) {
    if (!data || !data.character_id) {
      console.warn("Invalid result data received:", data);
      return;
    }

    // Store or update result
    this.results.set(data.character_id, {
      ...data,
      timestamp: new Date().toISOString(),
    });

    // Update display
    this.renderResults();
  }

  renderResults() {
    if (this.results.size === 0) {
      this.showPlaceholder();
      return;
    }

    this.isDisplaying = true;
    const content = this.container.querySelector(".results-display-content");

    if (!content) return;

    content.innerHTML = Array.from(this.results.values())
      .map((result) => this.createResultCard(result))
      .join("");

    // Add event listeners for expandable content
    this.setupResultCardListeners();
  }

  createResultCard(result) {
    const engagementScore = result.engagement_score || 0;
    const decision = result.engagement_decision || "unknown";
    const reasoning = result.reasoning || "No reasoning provided";
    const characterName = result.character_name || result.character_id;

    const scoreColor = this.getScoreColor(engagementScore);
    const decisionClass = this.getDecisionClass(decision);
    const decisionIcon = this.getDecisionIcon(decision);

    return `
            <div class="result-card" data-character-id="${result.character_id}">
                <div class="result-card-header">
                    <div class="result-character-info">
                        <h3 class="result-character-name">${this.escapeHtml(
                          characterName
                        )}</h3>
                        <span class="result-character-id">ID: ${
                          result.character_id
                        }</span>
                    </div>
                    <div class="result-status">
                        <span class="result-timestamp">${this.formatTimestamp(
                          result.timestamp
                        )}</span>
                    </div>
                </div>
                
                <div class="result-card-body">
                    <!-- Engagement Score -->
                    <div class="result-score-section">
                        <h4>Engagement Score</h4>
                        <div class="score-display">
                            <div class="score-circle" style="--score-color: ${scoreColor}">
                                <span class="score-value">${Math.round(
                                  engagementScore * 100
                                )}%</span>
                            </div>
                            <div class="score-label">${this.getScoreLabel(
                              engagementScore
                            )}</div>
                        </div>
                    </div>
                    
                    <!-- Decision -->
                    <div class="result-decision-section">
                        <h4>Decision</h4>
                        <div class="decision-display ${decisionClass}">
                            <span class="decision-icon">${decisionIcon}</span>
                            <span class="decision-text">${this.formatDecision(
                              decision
                            )}</span>
                        </div>
                    </div>
                    
                    <!-- Reasoning -->
                    <div class="result-reasoning-section">
                        <h4>Reasoning</h4>
                        <div class="reasoning-content">
                            <p class="reasoning-text">${this.escapeHtml(
                              reasoning
                            )}</p>
                            ${
                              result.response_preview
                                ? `
                                <div class="response-preview">
                                    <h5>Response Preview</h5>
                                    <blockquote>${this.escapeHtml(
                                      result.response_preview
                                    )}</blockquote>
                                </div>
                            `
                                : ""
                            }
                        </div>
                    </div>
                    
                    <!-- Topic Analysis (if available) -->
                    ${
                      result.topic_analysis
                        ? this.renderTopicAnalysis(result.topic_analysis)
                        : ""
                    }
                    
                    <!-- Analysis Details (expandable) -->
                    <div class="result-details-section">
                        <button type="button" class="btn btn-secondary btn-sm details-toggle" data-character-id="${
                          result.character_id
                        }">
                            <span class="toggle-text">Show Details</span>
                            <span class="toggle-icon">▼</span>
                        </button>
                        <div class="result-details" id="details-${
                          result.character_id
                        }" style="display: none;">
                            <div class="details-content">
                                <h5>Analysis Details</h5>
                                <div class="detail-item">
                                    <strong>Processing Time:</strong> ${
                                      result.processing_time || "N/A"
                                    }
                                </div>
                                <div class="detail-item">
                                    <strong>Confidence:</strong> ${
                                      result.confidence || "N/A"
                                    }
                                </div>
                                <div class="detail-item">
                                    <strong>Model Version:</strong> ${
                                      result.model_version || "N/A"
                                    }
                                </div>
                                ${
                                  result.metadata
                                    ? `
                                    <div class="detail-item">
                                        <strong>Additional Data:</strong>
                                        <pre class="metadata-display">${JSON.stringify(
                                          result.metadata,
                                          null,
                                          2
                                        )}</pre>
                                    </div>
                                `
                                    : ""
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
  }

  renderTopicAnalysis(topicAnalysis) {
    const topics = Object.entries(topicAnalysis)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5); // Show top 5 topics

    return `
            <div class="result-topics-section">
                <h4>Topic Analysis</h4>
                <div class="topics-grid">
                    ${topics
                      .map(
                        ([topic, score]) => `
                        <div class="topic-item">
                            <span class="topic-name">${this.escapeHtml(
                              topic
                            )}</span>
                            <div class="topic-bar">
                                <div class="topic-bar-fill" style="width: ${
                                  score * 100
                                }%"></div>
                            </div>
                            <span class="topic-score">${Math.round(
                              score * 100
                            )}%</span>
                        </div>
                    `
                      )
                      .join("")}
                </div>
            </div>
        `;
  }

  setupResultCardListeners() {
    // Details toggle buttons
    const toggleButtons = document.querySelectorAll(".details-toggle");
    toggleButtons.forEach((button) => {
      button.addEventListener("click", (e) => {
        const characterId = e.target.dataset.characterId;
        this.toggleDetails(characterId);
      });
    });
  }

  toggleDetails(characterId) {
    const detailsElement = document.getElementById(`details-${characterId}`);
    const toggleButton = document.querySelector(
      `[data-character-id="${characterId}"] .details-toggle`
    );

    if (!detailsElement || !toggleButton) return;

    const isVisible = detailsElement.style.display !== "none";
    const toggleText = toggleButton.querySelector(".toggle-text");
    const toggleIcon = toggleButton.querySelector(".toggle-icon");

    if (isVisible) {
      detailsElement.style.display = "none";
      toggleText.textContent = "Show Details";
      toggleIcon.textContent = "▼";
    } else {
      detailsElement.style.display = "block";
      toggleText.textContent = "Hide Details";
      toggleIcon.textContent = "▲";
    }
  }

  showPlaceholder() {
    this.isDisplaying = false;
    const content = this.container.querySelector(".results-display-content");

    if (content) {
      content.innerHTML = `
                <div class="results-placeholder">
                    <div class="placeholder-content">
                        <div class="placeholder-icon">📊</div>
                        <h3>No Analysis Results Yet</h3>
                        <p>Select news content and characters, then click "Start Analysis" to see real-time results.</p>
                    </div>
                </div>
            `;
    }
  }

  clearResults() {
    this.results.clear();
    this.isDisplaying = false;
    this.showPlaceholder();
  }

  getResult(characterId) {
    return this.results.get(characterId);
  }

  getAllResults() {
    return Array.from(this.results.values());
  }

  hasResults() {
    return this.results.size > 0;
  }

  getScoreColor(score) {
    if (score >= 0.8) return "#27ae60"; // Green for high engagement
    if (score >= 0.6) return "#f39c12"; // Orange for medium engagement
    if (score >= 0.4) return "#e67e22"; // Dark orange for low-medium
    return "#e74c3c"; // Red for low engagement
  }

  getScoreLabel(score) {
    if (score >= 0.8) return "High Engagement";
    if (score >= 0.6) return "Medium Engagement";
    if (score >= 0.4) return "Low-Medium Engagement";
    return "Low Engagement";
  }

  getDecisionClass(decision) {
    switch (decision.toLowerCase()) {
      case "engage":
        return "decision-engage";
      case "ignore":
        return "decision-ignore";
      case "consider":
        return "decision-consider";
      default:
        return "decision-unknown";
    }
  }

  getDecisionIcon(decision) {
    switch (decision.toLowerCase()) {
      case "engage":
        return "✅";
      case "ignore":
        return "❌";
      case "consider":
        return "🤔";
      default:
        return "❓";
    }
  }

  formatDecision(decision) {
    return decision.charAt(0).toUpperCase() + decision.slice(1).toLowerCase();
  }

  formatTimestamp(timestamp) {
    if (!timestamp) return "Unknown";

    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (error) {
      return "Invalid timestamp";
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Animation methods for smooth updates
  animateResultUpdate(characterId) {
    const resultCard = document.querySelector(
      `[data-character-id="${characterId}"]`
    );
    if (resultCard) {
      resultCard.classList.add("updating");
      setTimeout(() => {
        resultCard.classList.remove("updating");
      }, 500);
    }
  }

  // Export results for download
  exportResults() {
    const results = this.getAllResults();
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(dataBlob);
    link.download = `character-analysis-${
      new Date().toISOString().split("T")[0]
    }.json`;
    link.click();
  }
}

// Export for testing
if (typeof module !== "undefined" && module.exports) {
  module.exports = { ResultsDisplay };
}
