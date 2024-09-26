from fastapi import FastAPI, HTTPException
import json
from collections import defaultdict

app = FastAPI()

# Load the JSON data at startup
with open('servers.json', 'r') as f:
    servers = json.load(f)

# Route 1: Retrieve all servers
@app.get("/servers")
def get_servers():
    return servers

# Route 2: Retrieve a server by name (e.g., "W17975")
@app.get("/servers/{server_name}")
def get_server_by_name(server_name: str):
    server = next((s for s in servers if s["name"].lower() == server_name.lower()), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

# Route 3: Retrieve servers by tag name (e.g., servers with "Workgroup 2" tag)
@app.get("/servers/tags/{tag_name}")
def get_servers_by_tag(tag_name: str):
    filtered_servers = [s for s in servers if any(tag["name"] == tag_name for tag in s.get("tags", []))]
    if not filtered_servers:
        raise HTTPException(status_code=404, detail="No servers found with this tag")
    return filtered_servers

# Route 4: Add a tag to a server
@app.put("/servers/{server_name}/tags")
def add_tag_to_server(server_name: str, tag_id: int, tag_name: str, tag_color: str):
    server = next((s for s in servers if s["name"].lower() == server_name.lower()), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Check if the tag already exists
    if any(tag["name"] == tag_name for tag in server.get("tags", [])):
        return {"message": f"Tag '{tag_name}' already exists on {server_name}"}
    
    # Add the new tag
    new_tag = {
        "id": tag_id,
        "url": f"/vmanage-server/rest/rest-api/tags/{tag_id}",
        "name": tag_name,
        "tagColor": tag_color
    }
    server["tags"].append(new_tag)
    return {"message": f"Tag '{tag_name}' added successfully to {server_name}"}

# Route 5: Get server statistics (Optional)
@app.get("/servers/stats")
def get_server_stats():
    tag_count = defaultdict(int)
    for server in servers:
        for tag in server.get("tags", []):
            tag_count[tag["name"]] += 1
        if not server.get("tags"):
            tag_count["untagged"] += 1
    return tag_count
