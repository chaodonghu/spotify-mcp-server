#!/usr/bin/env python3
"""
Complete Weekly Spotify Playlist Creator
Creates a weekly playlist and adds new songs by specified artists from the last week.
Uses actual Spotify release date filtering instead of text matching.
"""

import json
import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path


# Configure your favorite artists here
FAVORITE_ARTISTS = [
    "Lil Tecca",
    "Playboi Carti", 
    "Travis Scott",
    "Don Toliver",
    "Lil Uzi Vert",
    "Future",
    "Metro Boomin",
    "21 Savage",
    "PlaqueBoyMax",
    "4batz"
]


def get_week_dates():
    """Get the current week's start and end dates."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_cutoff_date():
    """Get the cutoff date for recent releases (7 days ago)."""
    return datetime.now() - timedelta(days=7)


def generate_playlist_name():
    """Generate a playlist name for the current week."""
    start_week, end_week = get_week_dates()
    return f"Weekly New Drops - {start_week.strftime('%b %d')} to {end_week.strftime('%b %d, %Y')}"


def send_mcp_request(process, request_id, method, params=None):
    """Send an MCP request to the server process."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    request_json = json.dumps(request)
    
    process.stdin.write(request_json + '\n')
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    
    try:
        return json.loads(response_line)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        return None


def extract_playlist_id(response_text):
    """Extract playlist ID from create playlist response."""
    match = re.search(r'Playlist ID: ([a-zA-Z0-9]+)', response_text)
    return match.group(1) if match else None


def extract_track_info_with_dates(search_text):
    """Extract track information including release dates from search response."""
    tracks = []
    for line in search_text.split('\n'):
        # Look for lines with track info including release date:
        # "Title" by Artist (duration) - Released: YYYY-MM-DD - ID: track_id
        match = re.search(
            r'^\d+\.\s*"([^"]+)"\s+by\s+([^(]+)\s*\([^)]+\)\s*-\s*Released:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9]{2}|[0-9]{4}|Unknown)\s*-\s*ID:\s*([a-zA-Z0-9]+)', 
            line
        )
        if match:
            title, artist, release_date, track_id = match.groups()
            tracks.append({
                'title': title.strip(),
                'artist': artist.strip(),
                'release_date': release_date.strip(),
                'id': track_id.strip()
            })
    return tracks


def parse_spotify_date(date_str):
    """Parse Spotify release date string to datetime object."""
    date_str = date_str.strip()
    
    if date_str == 'Unknown':
        return None
    
    try:
        # Spotify dates can be YYYY-MM-DD, YYYY-MM, or YYYY
        if len(date_str) == 10:  # YYYY-MM-DD
            return datetime.strptime(date_str, '%Y-%m-%d')
        elif len(date_str) == 7:  # YYYY-MM
            return datetime.strptime(date_str + '-01', '%Y-%m-%d')
        elif len(date_str) == 4:  # YYYY
            return datetime.strptime(date_str + '-01-01', '%Y-%m-%d')
    except ValueError:
        pass
    
    return None


def is_recent_release(release_date_str, cutoff_date):
    """Check if a release date is within the last 7 days."""
    release_date = parse_spotify_date(release_date_str)
    
    if not release_date:
        return False
    
    return release_date >= cutoff_date


def search_artist_tracks(process, request_id, artist):
    """Search for tracks by an artist and filter by release date."""
    print(f"  🔍 Searching for tracks by {artist}...")
    
    cutoff_date = get_cutoff_date()
    found_tracks = []
    
    # Search for tracks by this artist (simple search)
    search_queries = [
        f"artist:{artist}",
        f"{artist}",
        f"{artist} 2025"  # Include current year for recency
    ]
    
    for query in search_queries:
        search_response = send_mcp_request(process, request_id, "tools/call", {
            "name": "searchSpotify",
            "arguments": {
                "query": query,
                "type": "track",
                "limit": 50  # Get more results to find recent ones
            }
        })
        request_id += 1
        
        if search_response and "result" in search_response:
            search_text = search_response["result"]["content"][0]["text"]
            tracks = extract_track_info_with_dates(search_text)
            
            for track in tracks:
                # Check if this track is actually by the artist we're looking for
                if artist.lower() in track['artist'].lower():
                    # Check if it's a recent release
                    if is_recent_release(track['release_date'], cutoff_date):
                        # Avoid duplicates
                        if not any(t['id'] == track['id'] for t in found_tracks):
                            found_tracks.append(track)
                            print(f"    ✅ Found recent release: \"{track['title']}\" (Released: {track['release_date']})")
    
    return found_tracks[:3], request_id  # Max 3 per artist


def create_weekly_playlist():
    """Create a weekly playlist with songs released in the last 7 days."""
    print("🎵 Creating Weekly New Drops Playlist")
    print("=" * 50)
    print(f"🎤 Searching for tracks by {len(FAVORITE_ARTISTS)} artists:")
    for artist in FAVORITE_ARTISTS:
        print(f"   • {artist}")
    
    cutoff_date = get_cutoff_date()
    print(f"\n📅 Looking for tracks released after {cutoff_date.strftime('%Y-%m-%d')} (last 7 days)")
    print("🔍 Using actual Spotify release date filtering")
    print()
    
    # Path to the built MCP server
    script_dir = Path(__file__).parent
    server_path = script_dir / "build" / "index.js"
    
    if not server_path.exists():
        print(f"❌ MCP server not found at {server_path}")
        print("Please run 'npm run build' first to build the TypeScript server.")
        return False
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            ["node", str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✅ Started MCP server")
        
        request_id = 1
        
        # 1. Initialize connection
        init_response = send_mcp_request(process, request_id, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "weekly-new-drops-creator",
                "version": "2.0.0"
            }
        })
        request_id += 1
        
        if not init_response or "result" not in init_response:
            print("❌ Failed to initialize connection")
            return False
        
        print("✅ Connected to Spotify MCP server")
        
        # 2. Create playlist
        playlist_name = generate_playlist_name()
        print(f"📝 Creating playlist: {playlist_name}")
        
        create_response = send_mcp_request(process, request_id, "tools/call", {
            "name": "createPlaylist",
            "arguments": {
                "name": playlist_name,
                "description": f"Tracks released in the last 7 days - {datetime.now().strftime('%Y-%m-%d')}",
                "public": False
            }
        })
        request_id += 1
        
        if not create_response or "result" not in create_response:
            print("❌ Failed to create playlist")
            return False
        
        # Extract playlist ID
        response_text = create_response["result"]["content"][0]["text"]
        playlist_id = extract_playlist_id(response_text)
        
        if not playlist_id:
            print("❌ Failed to extract playlist ID")
            return False
        
        print(f"✅ Created playlist with ID: {playlist_id}")
        
        # 3. Search for recent releases by each artist
        all_tracks = []
        track_ids_to_add = []
        
        for artist in FAVORITE_ARTISTS:
            print(f"\n🎤 Checking {artist} for tracks released in the last 7 days...")
            
            tracks, request_id = search_artist_tracks(process, request_id, artist)
            
            if tracks:
                print(f"  ✅ Found {len(tracks)} recent track(s):")
                for track in tracks:
                    print(f"     📅 \"{track['title']}\" (Released: {track['release_date']})")
                    all_tracks.append(track)
                    track_ids_to_add.append(track['id'])
            else:
                print(f"  ❌ No tracks from the last 7 days found for {artist}")
        
        # 4. Add tracks to playlist
        if track_ids_to_add:
            print(f"\n➕ Adding {len(track_ids_to_add)} recent tracks to playlist...")
            
            add_response = send_mcp_request(process, request_id, "tools/call", {
                "name": "addTracksToPlaylist",
                "arguments": {
                    "playlistId": playlist_id,
                    "trackIds": track_ids_to_add
                }
            })
            request_id += 1
            
            if add_response and "result" in add_response:
                add_text = add_response["result"]["content"][0]["text"]
                if "Successfully added" in add_text:
                    print(f"  ✅ Added {len(track_ids_to_add)} tracks")
                    
                    print(f"\n🎉 Weekly playlist '{playlist_name}' is ready!")
                    print(f"📊 Added {len(track_ids_to_add)} tracks released in the last 7 days")
                    print("📱 Check your Spotify app to see the new playlist!")
                    
                    # Show summary of added tracks
                    print(f"\n🎵 Recent Releases Added:")
                    for track in all_tracks:
                        print(f"   📅 \"{track['title']}\" by {track['artist']} (Released: {track['release_date']})")
                else:
                    print(f"  ⚠️  Tracks might not have been added properly")
            else:
                print(f"  ❌ Failed to add tracks to playlist")
        else:
            print("\n😔 No tracks released in the last 7 days found")
            print("   This is normal - artists don't release new music every week!")
            print("   The empty playlist was created and will be ready for next week.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during playlist creation: {e}")
        return False
        
    finally:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()


def setup_automation_instructions():
    """Show instructions for setting up weekly automation."""
    script_path = Path(__file__).absolute()
    
    print("\n" + "=" * 60)
    print("⏰ WEEKLY AUTOMATION SETUP")
    print("=" * 60)
    print("\nTo run this script automatically every week:")
    print("\n1. Open terminal and run: crontab -e")
    print("2. Add this line to run every Monday at 9 AM:")
    print(f"   0 9 * * 1 cd {script_path.parent} && python3 {script_path.name}")
    print("\n3. Save and exit")
    print("\nHow it works:")
    print("• Uses actual Spotify release dates (not text matching)")
    print("• Searches for all tracks by your favorite artists")
    print("• Filters tracks released in the last 7 days")
    print("• Max 3 tracks per artist to keep playlist manageable")
    print(f"\nManual run: python3 {script_path.name}")


if __name__ == "__main__":
    print("🎵 Weekly New Drops Playlist Creator")
    print("🤖 Powered by MCP + Spotify")
    print("📅 Uses actual Spotify release dates")
    print("✨ Much more accurate than text matching!")
    print()
    
    try:
        success = create_weekly_playlist()
        
        if success:
            setup_automation_instructions()
        else:
            print("\n😞 Failed to create weekly playlist")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Playlist creation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 