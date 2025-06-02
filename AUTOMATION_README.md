# 🎵 Weekly Spotify Playlist Automation

This automation system creates a new Spotify playlist every week and automatically adds "OWA OWA" by Lil Tecca to it. It leverages your existing Spotify MCP server to interact with the Spotify API.

## 🚀 Quick Start

### Option 1: Simple Shell Script (Recommended)
```bash
./create_weekly_playlist.sh
```

### Option 2: Python Script Directly
```bash
# Install dependencies first
pip install mcp

# Run the script
python3 weekly_playlist_automation.py
```

## 📋 What It Does

1. **Creates a Weekly Playlist**: Generates a playlist named like "Weekly Mix - Dec 09 to Dec 15, 2024"
2. **Adds OWA OWA**: Automatically searches for and adds "OWA OWA" by Lil Tecca
3. **Ready for More**: You can manually add more tracks or extend the script

## ⚙️ Setup Requirements

### Prerequisites
- ✅ **Spotify MCP Server** (already set up in this directory)
- ✅ **Node.js & npm** (for running the MCP server)
- ✅ **Python 3** (for the automation script)
- ✅ **MCP Python library** (auto-installed by the shell script)

### First Time Setup
1. **Ensure your MCP server is built**:
   ```bash
   npm run build
   ```

2. **Test the automation**:
   ```bash
   ./create_weekly_playlist.sh
   ```

## 🔄 Weekly Automation Options

### Option 1: Manual Execution
Run the script whenever you want a new playlist:
```bash
./create_weekly_playlist.sh
```

### Option 2: Cron Job (Automatic)
Set up a weekly cron job to run automatically:

1. Open crontab:
   ```bash
   crontab -e
   ```

2. Add this line for every Monday at 9 AM:
   ```bash
   0 9 * * 1 cd /Users/cdhu/Desktop/personal_github/spotify-mcp-server && ./create_weekly_playlist.sh
   ```

3. Save and exit

### Option 3: macOS Automator
Create an Automator app to run the script with a double-click.

### Option 4: Custom Schedule
Modify the cron schedule for different frequencies:
- **Daily**: `0 9 * * *` (every day at 9 AM)
- **Bi-weekly**: `0 9 * * 1/2` (every other Monday)
- **Monthly**: `0 9 1 * *` (first day of each month)

## 🛠️ Customization

### Adding More Tracks
Edit `weekly_playlist_automation.py` and add more searches after the OWA OWA section:

```python
# Search for more tracks
additional_searches = [
    "NEVER LAST Lil Tecca",
    "BAD TIME Lil Tecca",
    "TASTE Lil Tecca"
]

for search_query in additional_searches:
    search_response = await client.search_spotify(search_query, "track", 1)
    track_ids = extract_track_ids(search_response)
    if track_ids:
        await client.add_tracks_to_playlist(playlist_id, [track_ids[0]])
```

### Changing Playlist Names
Modify the `generate_playlist_name()` function:

```python
def generate_playlist_name():
    return f"🎵 Weekly Vibes - {datetime.now().strftime('%B %Y')}"
```

### Making Playlists Public
Change the `public` parameter in the script:

```python
create_response = await client.create_playlist(
    name=playlist_name,
    description=playlist_description,
    public=True  # Make playlists public
)
```

## 🔧 Troubleshooting

### "MCP server not found"
```bash
npm run build
```

### "mcp module not found"
```bash
pip install mcp
```

### "No active device found"
Make sure Spotify is open and playing on one of your devices before running the script.

### Authentication Issues
Your Spotify MCP server handles authentication. If there are auth issues:
1. Check your `spotify-config.json`
2. Re-run the auth process: `npm run auth`

## 📂 Files Created

- `weekly_playlist_automation.py` - Main automation script
- `create_weekly_playlist.sh` - Convenient shell wrapper
- `requirements.txt` - Python dependencies
- `AUTOMATION_README.md` - This documentation

## 🎯 Example Output

```
🎵 Starting Weekly Spotify Playlist Automation
==================================================
✅ Connected to Spotify MCP server
📝 Creating playlist: Weekly Mix - Dec 09 to Dec 15, 2024
✅ Created playlist with ID: 3cEYpjA9oz9GiPac4AsH4n
🔍 Searching for 'OWA OWA' by Lil Tecca...
🎶 Found OWA OWA with ID: 5E3XPRJVgYnxhMAFI7nZ7N
✅ Successfully added 'OWA OWA' to the playlist!
📱 Playlist 'Weekly Mix - Dec 09 to Dec 15, 2024' is ready in your Spotify!
```

## 🔮 Future Enhancements

- **Smart Track Selection**: Add tracks based on your recent listening history
- **Genre Mixing**: Automatically add tracks from different genres
- **Collaborative Playlists**: Create playlists that friends can edit
- **Mood-Based Selection**: Add tracks based on weather, time of day, etc.
- **Integration with Last.fm**: Add your most-played tracks from the week

---

🎵 **Enjoy your automated weekly playlists!** 🎵 