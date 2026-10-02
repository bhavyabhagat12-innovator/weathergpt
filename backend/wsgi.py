import os  
import uvicorn  
port = int(os.environ.get("PORT", 8080))  
uvicorn.run("app.api.main:app", host="0.0.0.0", port=port) 
