/**
 * News Selector Component
 * Handles news content selection via dropdown scenarios and custom input
 */

class NewsSelector extends EventEmitter {
  constructor(selector) {
    super();
    this.container = document.querySelector(selector);
    this.scenarios = [];
    this.selectedNews = null;
    this.maxCustomLength = 2000;

    this.init();
  }

  init() {
    if (!this.container) {
      console.error("News selector container not found");
      return;
    }

    this.render();
    this.setupEventListeners();
  }

  render() {
    this.container.innerHTML = `
            <div class="news-selector-content">
                <!-- Scenario Dropdown -->
                <div class="news-option">
                    <label for="scenario-select">Select News Scenario</label>
                    <select id="scenario-select" class="form-select">
                        <option value="">Choose a scenario...</option>
                    </select>
                </div>
                
                <!-- Custom News Input -->
                <div class="news-option">
                    <label for="custom-news">Or Enter Custom News</label>
                    <textarea 
                        id="custom-news" 
                        class="form-textarea" 
                        placeholder="Enter your news content here..."
                        maxlength="${this.maxCustomLength}"
                        rows="4"
                    ></textarea>
                    <div class="input-counter">
                        <span id="char-count">0</span> / ${this.maxCustomLength} characters
                    </div>
                    <div class="input-error" id="custom-news-error" style="display: none;"></div>
                </div>
                
                <!-- Selected News Display -->
                <div class="selected-news" id="selected-news-display" style="display: none;">
                    <h4>Selected Content</h4>
                    <div class="news-preview" id="news-preview"></div>
                    <button type="button" class="btn btn-secondary btn-sm" id="clear-selection">
                        Clear Selection
                    </button>
                </div>
            </div>
        `;
  }

  setupEventListeners() {
    // Scenario dropdown change
    const scenarioSelect = document.getElementById("scenario-select");
    if (scenarioSelect) {
      scenarioSelect.addEventListener("change", (e) => {
        this.handleScenarioSelection(e.target.value);
      });
    }

    // Custom news input
    const customNews = document.getElementById("custom-news");
    if (customNews) {
      customNews.addEventListener("input", (e) => {
        this.handleCustomNewsInput(e.target.value);
      });

      customNews.addEventListener("blur", (e) => {
        this.validateCustomNews(e.target.value);
      });
    }

    // Clear selection button
    const clearBtn = document.getElementById("clear-selection");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this.clearSelection();
      });
    }
  }

  setScenarios(scenarios) {
    this.scenarios = scenarios;
    this.populateScenarioDropdown();
  }

  populateScenarioDropdown() {
    const select = document.getElementById("scenario-select");
    if (!select) return;

    // Clear existing options except the first placeholder
    select.innerHTML = '<option value="">Choose a scenario...</option>';

    // Add scenario options
    this.scenarios.forEach((scenario) => {
      const option = document.createElement("option");
      option.value = scenario.id;
      option.textContent = scenario.title;
      option.dataset.content = scenario.content;
      select.appendChild(option);
    });
  }

  handleScenarioSelection(scenarioId) {
    // Clear custom news input
    const customNews = document.getElementById("custom-news");
    if (customNews) {
      customNews.value = "";
      this.updateCharCount(0);
    }

    if (!scenarioId) {
      this.clearSelection();
      return;
    }

    const scenario = this.scenarios.find((s) => s.id === scenarioId);
    if (scenario) {
      this.selectedNews = {
        id: scenario.id,
        title: scenario.title,
        content: scenario.content,
        isCustom: false,
      };

      this.displaySelectedNews();
      this.emit("news-selected", this.selectedNews);
    }
  }

  handleCustomNewsInput(value) {
    this.updateCharCount(value.length);
    this.validateCustomNews(value);

    if (value.trim()) {
      // Clear scenario selection
      const scenarioSelect = document.getElementById("scenario-select");
      if (scenarioSelect) {
        scenarioSelect.value = "";
      }

      this.selectedNews = {
        id: "custom",
        title: "Custom News",
        content: value.trim(),
        isCustom: true,
      };

      this.displaySelectedNews();
      this.emit("news-selected", this.selectedNews);
    } else {
      this.clearSelection();
    }
  }

  validateCustomNews(value) {
    const errorElement = document.getElementById("custom-news-error");
    const textarea = document.getElementById("custom-news");

    if (!errorElement || !textarea) return;

    let errorMessage = "";

    if (value.length > this.maxCustomLength) {
      errorMessage = `Content exceeds maximum length of ${this.maxCustomLength} characters`;
    } else if (value.trim().length < 10) {
      errorMessage = "Please enter at least 10 characters of news content";
    }

    if (errorMessage) {
      errorElement.textContent = errorMessage;
      errorElement.style.display = "block";
      textarea.classList.add("error");
    } else {
      errorElement.style.display = "none";
      textarea.classList.remove("error");
    }
  }

  updateCharCount(count) {
    const counter = document.getElementById("char-count");
    if (counter) {
      counter.textContent = count;

      // Update color based on usage
      const percentage = (count / this.maxCustomLength) * 100;
      if (percentage > 90) {
        counter.style.color = "#e74c3c";
      } else if (percentage > 75) {
        counter.style.color = "#f39c12";
      } else {
        counter.style.color = "#7f8c8d";
      }
    }
  }

  displaySelectedNews() {
    const display = document.getElementById("selected-news-display");
    const preview = document.getElementById("news-preview");

    if (!display || !preview) return;

    if (this.selectedNews) {
      const previewText =
        this.selectedNews.content.length > 150
          ? this.selectedNews.content.substring(0, 150) + "..."
          : this.selectedNews.content;

      preview.innerHTML = `
                <div class="news-preview-header">
                    <strong>${this.selectedNews.title}</strong>
                    ${
                      this.selectedNews.isCustom
                        ? '<span class="badge custom">Custom</span>'
                        : '<span class="badge scenario">Scenario</span>'
                    }
                </div>
                <div class="news-preview-content">${this.escapeHtml(
                  previewText
                )}</div>
            `;

      display.style.display = "block";
    } else {
      display.style.display = "none";
    }
  }

  clearSelection() {
    this.selectedNews = null;

    // Clear form inputs
    const scenarioSelect = document.getElementById("scenario-select");
    const customNews = document.getElementById("custom-news");

    if (scenarioSelect) scenarioSelect.value = "";
    if (customNews) {
      customNews.value = "";
      this.updateCharCount(0);
      this.validateCustomNews("");
    }

    // Hide display
    const display = document.getElementById("selected-news-display");
    if (display) display.style.display = "none";

    this.emit("news-selected", null);
  }

  getSelectedNews() {
    return this.selectedNews;
  }

  reset() {
    this.clearSelection();
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  isValid() {
    if (!this.selectedNews) return false;

    if (this.selectedNews.isCustom) {
      const content = this.selectedNews.content.trim();
      return content.length >= 10 && content.length <= this.maxCustomLength;
    }

    return true;
  }
}

// Export for testing
if (typeof module !== "undefined" && module.exports) {
  module.exports = { NewsSelector };
}
