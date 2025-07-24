/**
 * Character Selector Component
 * Handles character selection with visual cards and multi-select functionality
 */

class CharacterSelector extends EventEmitter {
  constructor(selector) {
    super();
    this.container = document.querySelector(selector);
    this.characters = [];
    this.selectedCharacters = [];

    this.init();
  }

  init() {
    if (!this.container) {
      console.error("Character selector container not found");
      return;
    }

    this.render();
    this.setupEventListeners();
  }

  render() {
    this.container.innerHTML = `
            <div class="character-selector-content">
                <!-- Character Grid -->
                <div class="character-grid" id="character-grid">
                    <div class="character-loading">
                        <div class="loading-spinner"></div>
                        <p>Loading characters...</p>
                    </div>
                </div>
                
                <!-- Selection Summary -->
                <div class="selection-summary" id="selection-summary" style="display: none;">
                    <div class="summary-header">
                        <h4>Selected Characters</h4>
                        <button type="button" class="btn btn-secondary btn-sm" id="clear-characters">
                            Clear All
                        </button>
                    </div>
                    <div class="selected-list" id="selected-list"></div>
                </div>
                
                <!-- No Characters Message -->
                <div class="no-characters" id="no-characters" style="display: none;">
                    <div class="no-characters-content">
                        <div class="no-characters-icon">👥</div>
                        <h4>No Characters Available</h4>
                        <p>No characters are currently available for analysis.</p>
                    </div>
                </div>
            </div>
        `;
  }

  setupEventListeners() {
    // Clear all characters button
    const clearBtn = document.getElementById("clear-characters");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this.clearAllSelections();
      });
    }
  }

  setCharacters(characters) {
    this.characters = characters;
    this.renderCharacterGrid();
  }

  renderCharacterGrid() {
    const grid = document.getElementById("character-grid");
    const noCharacters = document.getElementById("no-characters");

    if (!grid) return;

    if (!this.characters || this.characters.length === 0) {
      grid.style.display = "none";
      if (noCharacters) noCharacters.style.display = "block";
      return;
    }

    if (noCharacters) noCharacters.style.display = "none";
    grid.style.display = "grid";

    grid.innerHTML = this.characters
      .map(
        (character) => `
            <div class="character-card" data-character-id="${character.id}">
                <div class="character-card-header">
                    <div class="character-avatar">
                        ${this.getCharacterAvatar(character)}
                    </div>
                    <div class="character-checkbox">
                        <input 
                            type="checkbox" 
                            id="char-${character.id}" 
                            value="${character.id}"
                            class="character-checkbox-input"
                        >
                        <label for="char-${
                          character.id
                        }" class="character-checkbox-label"></label>
                    </div>
                </div>
                <div class="character-card-body">
                    <h4 class="character-name">${this.escapeHtml(
                      character.name
                    )}</h4>
                    <p class="character-description">${this.escapeHtml(
                      character.description || "No description available"
                    )}</p>
                </div>
                <div class="character-card-footer">
                    <span class="character-id">ID: ${character.id}</span>
                </div>
            </div>
        `
      )
      .join("");

    // Add event listeners to checkboxes
    this.setupCharacterCheckboxListeners();
  }

  setupCharacterCheckboxListeners() {
    const checkboxes = document.querySelectorAll(".character-checkbox-input");

    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", (e) => {
        this.handleCharacterSelection(e.target.value, e.target.checked);
      });
    });
  }

  handleCharacterSelection(characterId, isSelected) {
    const character = this.characters.find((c) => c.id === characterId);
    if (!character) return;

    if (isSelected) {
      if (!this.selectedCharacters.find((c) => c.id === characterId)) {
        this.selectedCharacters.push(character);
      }
    } else {
      this.selectedCharacters = this.selectedCharacters.filter(
        (c) => c.id !== characterId
      );
    }

    this.updateSelectionSummary();
    this.updateCharacterCardStates();
    this.emit("characters-selected", {
      selectedCharacters: [...this.selectedCharacters],
    });
  }

  updateSelectionSummary() {
    const summary = document.getElementById("selection-summary");
    const selectedList = document.getElementById("selected-list");

    if (!summary || !selectedList) return;

    if (this.selectedCharacters.length > 0) {
      selectedList.innerHTML = this.selectedCharacters
        .map(
          (character) => `
                <div class="selected-character-item">
                    <span class="selected-character-name">${this.escapeHtml(
                      character.name
                    )}</span>
                    <button 
                        type="button" 
                        class="remove-character" 
                        data-character-id="${character.id}"
                        title="Remove ${character.name}"
                    >
                        ×
                    </button>
                </div>
            `
        )
        .join("");

      summary.style.display = "block";

      // Add event listeners to remove buttons
      const removeButtons = selectedList.querySelectorAll(".remove-character");
      removeButtons.forEach((button) => {
        button.addEventListener("click", (e) => {
          const characterId = e.target.dataset.characterId;
          this.removeCharacter(characterId);
        });
      });
    } else {
      summary.style.display = "none";
    }
  }

  updateCharacterCardStates() {
    const cards = document.querySelectorAll(".character-card");

    cards.forEach((card) => {
      const characterId = card.dataset.characterId;
      const checkbox = card.querySelector(".character-checkbox-input");
      const isSelected = this.selectedCharacters.find(
        (c) => c.id === characterId
      );

      if (isSelected) {
        card.classList.add("selected");
        if (checkbox) checkbox.checked = true;
      } else {
        card.classList.remove("selected");
        if (checkbox) checkbox.checked = false;
      }
    });
  }

  removeCharacter(characterId) {
    const checkbox = document.getElementById(`char-${characterId}`);
    if (checkbox) {
      checkbox.checked = false;
      this.handleCharacterSelection(characterId, false);
    }
  }

  clearAllSelections() {
    this.selectedCharacters = [];

    // Uncheck all checkboxes
    const checkboxes = document.querySelectorAll(".character-checkbox-input");
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    // Update UI
    this.updateSelectionSummary();
    this.updateCharacterCardStates();

    this.emit("characters-selected", {
      selectedCharacters: [],
    });
  }

  getSelectedCharacters() {
    return [...this.selectedCharacters];
  }

  reset() {
    this.clearAllSelections();
  }

  getCharacterAvatar(character) {
    // Use character avatar if available, otherwise create initials
    if (character.avatar) {
      return `<img src="${character.avatar}" alt="${character.name}" class="character-avatar-img">`;
    } else {
      const initials = character.name
        .split(" ")
        .map((word) => word.charAt(0))
        .join("")
        .toUpperCase()
        .substring(0, 2);

      return `<div class="character-avatar-initials">${initials}</div>`;
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  selectCharacter(characterId) {
    const checkbox = document.getElementById(`char-${characterId}`);
    if (checkbox && !checkbox.checked) {
      checkbox.checked = true;
      this.handleCharacterSelection(characterId, true);
    }
  }

  deselectCharacter(characterId) {
    const checkbox = document.getElementById(`char-${characterId}`);
    if (checkbox && checkbox.checked) {
      checkbox.checked = false;
      this.handleCharacterSelection(characterId, false);
    }
  }

  selectAllCharacters() {
    this.characters.forEach((character) => {
      this.selectCharacter(character.id);
    });
  }

  getSelectionCount() {
    return this.selectedCharacters.length;
  }

  hasSelection() {
    return this.selectedCharacters.length > 0;
  }
}

// Export for testing
if (typeof module !== "undefined" && module.exports) {
  module.exports = { CharacterSelector };
}
