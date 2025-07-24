#!/usr/bin/env python3
"""
Dashboard Server - Simple HTTP server for the HTML dashboard.

This script serves the HTML dashboard on a local HTTP server.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving the dashboard"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()


def main():
    """Main function to start the dashboard server"""
    # Check if dashboard directory exists
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        print("Please make sure the dashboard directory exists with index.html")
        sys.exit(1)
    
    # Check if index.html exists
    index_file = DASHBOARD_DIR / "index.html"
    if not index_file.exists():
        print(f"❌ Dashboard index.html not found: {index_file}")
        print("Please make sure index.html exists in the dashboard directory")
        sys.exit(1)
    
    # Change to dashboard directory
    os.chdir(DASHBOARD_DIR)
    
    # Create server
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print("🎭 Cuentamelo Dashboard Server")
        print("=" * 40)
        print(f"📁 Serving from: {DASHBOARD_DIR}")
        print(f"🌐 Dashboard URL: http://localhost:{PORT}")
        print(f"🔗 API Base URL: http://localhost:8000")
        print("=" * 40)
        print("Press Ctrl+C to stop the server")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Server error: {e}")


if __name__ == "__main__":
    main() 