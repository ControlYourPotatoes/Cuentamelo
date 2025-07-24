/**
 * Server-Sent Events Handler
 * Manages real-time streaming connections for analysis updates
 */

class SSEHandler extends EventEmitter {
  constructor() {
    super();
    this.eventSource = null;
    this.sessionId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.reconnectDelay = 1000; // Start with 1 second
    this.isConnected = false;
    this.connectionTimeout = null;
  }

  connect(sessionId) {
    if (this.isConnected) {
      this.disconnect();
    }

    this.sessionId = sessionId;
    this.reconnectAttempts = 0;

    try {
      this.establishConnection();
    } catch (error) {
      console.error("Failed to establish SSE connection:", error);
      this.emit("connection-error", error);
    }
  }

  establishConnection() {
    const url = `/api/analyze-stream/${this.sessionId}`;

    // Create EventSource
    this.eventSource = new EventSource(url);

    // Set connection timeout
    this.connectionTimeout = setTimeout(() => {
      if (!this.isConnected) {
        this.handleConnectionError(new Error("Connection timeout"));
      }
    }, 10000); // 10 second timeout

    // Connection opened
    this.eventSource.onopen = (event) => {
      console.log("SSE connection opened");
      this.isConnected = true;
      this.reconnectAttempts = 0;
      clearTimeout(this.connectionTimeout);
    };

    // Message received
    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error("Failed to parse SSE message:", error);
      }
    };

    // Analysis update event
    this.eventSource.addEventListener("analysis-update", (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit("analysis-update", data);
      } catch (error) {
        console.error("Failed to parse analysis update:", error);
      }
    });

    // Analysis complete event
    this.eventSource.addEventListener("analysis-complete", (event) => {
      try {
        const data = JSON.parse(event.data);
        this.isConnected = false;
        this.emit("analysis-complete", data);
      } catch (error) {
        console.error("Failed to parse analysis complete:", error);
      }
    });

    // Error handling
    this.eventSource.onerror = (event) => {
      console.error("SSE connection error:", event);
      this.handleConnectionError(new Error("SSE connection failed"));
    };
  }

  handleMessage(data) {
    // Handle different message types
    switch (data.type) {
      case "analysis-update":
        this.emit("analysis-update", data);
        break;
      case "analysis-complete":
        this.isConnected = false;
        this.emit("analysis-complete", data);
        break;
      case "error":
        this.emit("connection-error", new Error(data.message));
        break;
      default:
        console.log("Unknown SSE message type:", data.type);
    }
  }

  handleConnectionError(error) {
    this.isConnected = false;
    clearTimeout(this.connectionTimeout);

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
      );

      setTimeout(() => {
        this.establishConnection();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error("Max reconnection attempts reached");
      this.emit("connection-error", error);
    }
  }

  disconnect() {
    this.isConnected = false;
    clearTimeout(this.connectionTimeout);

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    console.log("SSE connection closed");
  }

  isConnectionActive() {
    return (
      this.isConnected &&
      this.eventSource &&
      this.eventSource.readyState === EventSource.OPEN
    );
  }

  getConnectionStatus() {
    if (!this.eventSource) {
      return "disconnected";
    }

    switch (this.eventSource.readyState) {
      case EventSource.CONNECTING:
        return "connecting";
      case EventSource.OPEN:
        return "connected";
      case EventSource.CLOSED:
        return "closed";
      default:
        return "unknown";
    }
  }
}

// Export for testing
if (typeof module !== "undefined" && module.exports) {
  module.exports = { SSEHandler };
}
