import os
import sys
from waitress import serve
from config.wsgi import application

# This script starts the Library System for the whole college network
if __name__ == '__main__':
    print("--------------------------------------------------")
    print("📚 GECDahod Library System - Production Server")
    print("--------------------------------------------------")
    print("Starting server on port 80...")
    print("Your colleagues can now visit the library at:")
    print("http://[YOUR_SERVER_IP]/")
    print("Press Ctrl+C to stop the server.")
    print("--------------------------------------------------")
    
    try:
        # host='0.0.0.0' makes it accessible to the local network
        # port=80 is the standard web port (no need to type :8000)
        serve(application, host='0.0.0.0', port=80, threads=8)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "Permission denied" in str(e):
            print("\n💡 Tip: Port 80 requires 'Administrator' privileges.")
            print("Try running your terminal as Administrator, or change port to 8080.")
        sys.exit(1)
