"""
Starlight Cinema Classics - Companion Application
Manage live broadcast schedule seeds, inspect upcoming procedural lineups,
insert custom embeddable streams (bstr.video, Archive.org, self-hosted),
and export save slots for local testing.
"""

import sys
import os
import json
import math
from datetime import datetime, timezone, timedelta
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Curated Film & Preroll Canon matching index.html
CURATED_FEATURE_FILMS = [
    {"id": 'his_girl_friday', "title": 'His Girl Friday (1940)', "length": 5504},
    {"id": 'TheStranger_0', "title": 'The Stranger (1946)', "length": 5472},
    {"id": 'the-lady-vanishes-1938', "title": 'The Lady Vanishes (1938)', "length": 5760},
    {"id": 'my_favorite_brunette', "title": 'My Favorite Brunette (1947)', "length": 5212},
    {"id": 'house_on_haunted_hill_ipod', "title": 'House on Haunted Hill (1959)', "length": 4483},
    {"id": 'suddenly', "title": 'Suddenly (1954)', "length": 4620},
    {"id": 'ScarletStreet', "title": 'Scarlet Street (1945)', "length": 6120},
    {"id": 'Detour', "title": 'Detour (1945)', "length": 4080},
    {"id": 'doa_ipod', "title": 'D.O.A. (1949)', "length": 4980},
    {"id": 'Hitch_Hiker', "title": 'The Hitch-Hiker (1953)', "length": 4260},
    {"id": 'kansascityconfidencial', "title": 'Kansas City Confidential (1952)', "length": 5940},
    {"id": 'He_Walked_By_Night.avi', "title": 'He Walked by Night (1948)', "length": 4740},
    {"id": 'Charade_1953', "title": 'Charade (1963)', "length": 6780},
    {"id": 'Night.Of.The.Living.Dead_1080p', "title": 'Night of the Living Dead (1968)', "length": 5760},
    {"id": 'CarnivalofSouls', "title": 'Carnival of Souls (1962)', "length": 4980},
    {"id": 'The_Little_Shop_of_Horrors.mpeg', "title": 'The Little Shop of Horrors (1960)', "length": 4320},
    {"id": 'Mclintock.avi', "title": 'McLintock! (1963)', "length": 7595},
    {"id": 'Cyrano_DeBergerac', "title": 'Cyrano de Bergerac (1950)', "length": 6720},
    {"id": 'dressed_to_kill', "title": 'Dressed to Kill (1946)', "length": 4320},
    {"id": 'gullivers_travels1939', "title": "Gulliver's Travels (1939)", "length": 4560},
    {"id": 'white_zombie', "title": 'White Zombie (1932)', "length": 4020},
    {"id": 'PennySerenade', "title": 'Penny Serenade (1941)', "length": 7140},
    {"id": 'royal_wedding', "title": 'Royal Wedding (1951)', "length": 5580}
]

VINTAGE_POLICY_CONCESSION_REELS = [
    {"id": 'SnackBarArtDeco', "title": 'Art Deco Concessions & Snack Bar', "length": 35},
    {"id": 'Intermission2', "title": 'Drive-In Intermission: Refreshment Time', "length": 35},
    {"id": 'Intermission4bCircus', "title": 'Circus Intermission & Refreshment Reel', "length": 53},
    {"id": 'Intermission4aCircus', "title": 'Circus Snack Stand Intermission', "length": 30},
    {"id": 'Intermission3CokePainter', "title": 'Theater Courtesy & Intermission Clock', "length": 56},
    {"id": 'SnackBarCircus', "title": 'Circus Concessions & Popcorn Special', "length": 30},
    {"id": 'SnackBarRicos', "title": 'Snack Bar: Fresh Nachos & Refreshments', "length": 44},
    {"id": 'SnackBarCastleberryBarbeque', "title": 'Lobby Concessions: Sandwiches & Soda', "length": 36},
    {"id": 'SnackBarCartoonSpace', "title": 'Retro Animated Concessions In Space', "length": 36},
    {"id": 'Intermission1', "title": 'Vintage Intermission Countdown Clock', "length": 38},
    {"id": 'Drive-inSnackBarAd', "title": 'Theater Refreshment Stand Announcement', "length": 63},
    {"id": 'DriveInPopcornItalian', "title": 'Hot Buttered Popcorn Concessions Reel', "length": 27},
    {"id": 'Drive-inWelcomeBw', "title": 'Welcome to the Theater: House Policy & Courtesy', "length": 114},
    {"id": 'Drive-inWelcomeToTheDrive-in', "title": 'Welcome To The Cinema Presentation', "length": 63},
    {"id": 'DriveIn-Showtime-Sparkle', "title": 'Showtime Curtain Call & Policy Announcement', "length": 32},
    {"id": 'AnnoucForYoungLovers', "title": 'Theater Policy & Intermission Courtesy', "length": 26},
    {"id": 'Three-Musketeers-Commercial-1', "title": 'Vintage Lobby Concession: Chocolate Bar Special', "length": 63},
    {"id": 'ShastaSodaCommercial-Frankenstein', "title": 'Thirst Quencher: Classic Refreshment Bumper', "length": 56},
    {"id": 'Intermission6bw', "title": 'Classic Black & White Intermission Clock', "length": 53}
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHED_FILE = os.path.join(SCRIPT_DIR, "live-sched.json")


class Mulberry32:
    """Deterministic PRNG matching JavaScript mulberry32 implementation."""
    def __init__(self, seed: int):
        self.s = seed & 0xFFFFFFFF

    def next(self) -> float:
        self.s = (self.s + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.s
        t = int(math.imul_poly(t ^ (t >> 15), t | 1))
        t ^= t + int(math.imul_poly(t ^ (t >> 7), t | 61))
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0


def imul(a, b):
    return (a * b) & 0xFFFFFFFF

math.imul_poly = imul


def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m:02d}m {s:02d}s"


def compute_schedule(seed, epoch_dt, target_dt, hours=12):
    """
    Computes deterministic schedule window around target_dt.
    """
    rng = Mulberry32(seed)
    recent_movies = []
    
    current_time = epoch_dt
    window_start = target_dt - timedelta(minutes=15)
    window_end = target_dt + timedelta(hours=hours)

    items = []
    step = 0

    while current_time < window_end:
        is_movie = (step % 2 == 0)
        step += 1

        if is_movie:
            candidates = [m for m in CURATED_FEATURE_FILMS if m['id'] not in recent_movies]
            if not candidates:
                candidates = CURATED_FEATURE_FILMS
            idx = int(rng.next() * len(candidates))
            chosen = candidates[idx]
            
            recent_movies.append(chosen['id'])
            if len(recent_movies) > 6:
                recent_movies.pop(0)

            duration = chosen['length']
            item_end = current_time + timedelta(seconds=duration)
            if item_end >= window_start:
                items.append({
                    "type": "movie",
                    "title": chosen['title'],
                    "id": chosen['id'],
                    "start": current_time,
                    "end": item_end,
                    "duration": duration
                })
            current_time = item_end
        else:
            idx = int(rng.next() * len(VINTAGE_POLICY_CONCESSION_REELS))
            chosen = VINTAGE_POLICY_CONCESSION_REELS[idx]
            duration = chosen['length']
            item_end = current_time + timedelta(seconds=duration)
            if item_end >= window_start:
                items.append({
                    "type": "preroll",
                    "title": chosen['title'],
                    "id": chosen['id'],
                    "start": current_time,
                    "end": item_end,
                    "duration": duration
                })
            current_time = item_end

    return items


class StarlightCompanionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Starlight Cinema Classics — Schedule & Broadcast Planner")
        self.geometry("960x680")
        self.configure(bg="#120a06")

        self.sched_data = self.load_sched_file()

        self.setup_styles()
        self.create_widgets()
        self.refresh_schedule_view()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(".", background="#120a06", foreground="#f2ece4", font=('Segoe UI', 9))
        style.configure("TLabel", background="#120a06", foreground="#cfa862", font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 14, 'bold'), foreground="#cfa862")
        style.configure("TButton", background="#2a160d", foreground="#f2ece4", borderwidth=1, focuscolor="#cfa862")
        style.map("TButton", background=[('active', '#780d16'), ('pressed', '#a81c25')])
        style.configure("Treeview", background="#1a0e08", foreground="#f2ece4", fieldbackground="#1a0e08", rowheight=24)
        style.map("Treeview", background=[('selected', '#780d16')])

    def load_sched_file(self):
        if os.path.exists(SCHED_FILE):
            try:
                with open(SCHED_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print("Error loading sched file:", e)
        return {
            "seed": 19401225,
            "epoch": "2026-01-01T00:00:00Z",
            "inserts": []
        }

    def save_sched_file(self):
        try:
            with open(SCHED_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.sched_data, f, indent=2)
            messagebox.showinfo("Saved", f"Schedule configuration saved to:\n{SCHED_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving schedule: {e}")

    def create_widgets(self):
        # Top Header Bar
        top_frame = tk.Frame(self, bg="#1a0e09", pady=10, padx=15)
        top_frame.pack(fill=tk.X)

        title = ttk.Label(top_frame, text="★ STARLIGHT CINEMA BROADCAST PLANNER", style="Header.TLabel")
        title.pack(side=tk.LEFT)

        # Seed & Epoch Controls
        ctrl_frame = tk.Frame(self, bg="#120a06", pady=10, padx=15)
        ctrl_frame.pack(fill=tk.X)

        ttk.Label(ctrl_frame, text="Schedule Seed:").pack(side=tk.LEFT, padx=(0, 5))
        self.seed_var = tk.StringVar(value=str(self.sched_data.get('seed', 19401225)))
        self.seed_entry = tk.Entry(ctrl_frame, textvariable=self.seed_var, width=12, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.seed_entry.pack(side=tk.LEFT, padx=(0, 15))

        btn_new_seed = ttk.Button(ctrl_frame, text="Generate New Seed", command=self.generate_new_seed)
        btn_new_seed.pack(side=tk.LEFT, padx=(0, 10))

        btn_save_sched = ttk.Button(ctrl_frame, text="Save live-sched.json", command=self.save_schedule_settings)
        btn_save_sched.pack(side=tk.LEFT, padx=(0, 15))

        btn_pull_live = ttk.Button(ctrl_frame, text="Pull Published (GitHub)", command=self.pull_published_schedule)
        btn_pull_live.pack(side=tk.RIGHT)

        # Tabbed notebook: 1. Live Schedule Viewer, 2. Manual Schedule Inserts, 3. Local Test Save Exporter
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # TAB 1: Live Timeline View
        tab_timeline = tk.Frame(notebook, bg="#120a06")
        notebook.add(tab_timeline, text="  12-Hour Broadcast Timeline  ")
        self.setup_timeline_tab(tab_timeline)

        # TAB 2: Custom Inserts Manager
        tab_inserts = tk.Frame(notebook, bg="#120a06")
        notebook.add(tab_inserts, text="  Manual Schedule Inserts  ")
        self.setup_inserts_tab(tab_inserts)

        # TAB 3: Local Test Save Exporter
        tab_export = tk.Frame(notebook, bg="#120a06")
        notebook.add(tab_export, text="  Export Slot Save for Testing  ")
        self.setup_export_tab(tab_export)

    def setup_timeline_tab(self, parent):
        top = tk.Frame(parent, bg="#120a06", pady=6)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Inspect schedule for upcoming broadcast times (UTC):").pack(side=tk.LEFT)
        btn_refresh = ttk.Button(top, text="Refresh Timeline", command=self.refresh_schedule_view)
        btn_refresh.pack(side=tk.RIGHT)

        cols = ("time", "type", "title", "duration")
        self.tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode='browse')
        self.tree.heading("time", text="Scheduled Start (UTC)")
        self.tree.heading("type", text="Cadence Type")
        self.tree.heading("title", text="Title")
        self.tree.heading("duration", text="Duration")

        self.tree.column("time", width=180)
        self.tree.column("type", width=110)
        self.tree.column("title", width=460)
        self.tree.column("duration", width=100)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_inserts_tab(self, parent):
        frame = tk.Frame(parent, bg="#120a06", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Schedule Custom Streams (bstr.video, Archive.org, or self-hosted assets):", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        form = tk.Frame(frame, bg="#1a0e08", padx=10, pady=10, borderwidth=1, relief="ridge")
        form.pack(fill=tk.X, pady=(0, 10))

        # Title
        tk.Label(form, text="Title:", bg="#1a0e08", fg="#cfa862").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.insert_title = tk.Entry(form, width=45, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.insert_title.grid(row=0, column=1, columnspan=3, sticky=tk.W, pady=3)

        # Video Stream URL
        tk.Label(form, text="Direct MP4 URL:", bg="#1a0e08", fg="#cfa862").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.insert_url = tk.Entry(form, width=55, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.insert_url.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=3)

        # Start Time (ISO UTC)
        tk.Label(form, text="Start Time (UTC):", bg="#1a0e08", fg="#cfa862").grid(row=2, column=0, sticky=tk.W, pady=3)
        now_str = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00Z")
        self.insert_time = tk.Entry(form, width=25, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.insert_time.insert(0, now_str)
        self.insert_time.grid(row=2, column=1, sticky=tk.W, pady=3)

        # Duration seconds
        tk.Label(form, text="Duration (sec):", bg="#1a0e08", fg="#cfa862").grid(row=2, column=2, sticky=tk.W, padx=(10, 5), pady=3)
        self.insert_dur = tk.Entry(form, width=10, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.insert_dur.insert(0, "3600")
        self.insert_dur.grid(row=2, column=3, sticky=tk.W, pady=3)

        # Cut mode
        tk.Label(form, text="Cut Mode:", bg="#1a0e08", fg="#cfa862").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.insert_mode = tk.StringVar(value="graceful")
        tk.Radiobutton(form, text="Graceful (Waits for film to end)", variable=self.insert_mode, value="graceful", bg="#1a0e08", fg="#fff", selectcolor="#780d16").grid(row=3, column=1, sticky=tk.W)
        tk.Radiobutton(form, text="Hard (Strict cut at start time)", variable=self.insert_mode, value="hard", bg="#1a0e08", fg="#fff", selectcolor="#780d16").grid(row=3, column=2, sticky=tk.W)

        btn_add = ttk.Button(form, text="+ Add Insert to Schedule", command=self.add_insert)
        btn_add.grid(row=4, column=1, sticky=tk.W, pady=(8, 0))

        # Treeview of existing inserts
        ttk.Label(frame, text="Active Scheduled Inserts:").pack(anchor=tk.W, pady=(10, 4))
        cols = ("time", "title", "mode", "dur")
        self.insert_tree = ttk.Treeview(frame, columns=cols, show='headings', height=6)
        self.insert_tree.heading("time", text="Start Time (UTC)")
        self.insert_tree.heading("title", text="Title")
        self.insert_tree.heading("mode", text="Mode")
        self.insert_tree.heading("dur", text="Duration")
        self.insert_tree.column("time", width=180)
        self.insert_tree.column("title", width=380)
        self.insert_tree.column("mode", width=100)
        self.insert_tree.column("dur", width=100)
        self.insert_tree.pack(fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(frame, bg="#120a06")
        btn_row.pack(fill=tk.X, pady=6)
        ttk.Button(btn_row, text="Remove Selected Insert", command=self.remove_insert).pack(side=tk.LEFT)

        self.refresh_inserts_list()

    def setup_export_tab(self, parent):
        frame = tk.Frame(parent, bg="#120a06", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Generate Local Test Save File (.json)", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        p = tk.Label(frame, text="Export a customized session containing any tested video URL (e.g. bstr.video or new archive titles).\nYou can import this directly into Slot 1, 2, or 3 via the custom pause menu in the app.",
                     bg="#120a06", fg="#ccc", justify=tk.LEFT)
        p.pack(anchor=tk.W, pady=(0, 15))

        f = tk.Frame(frame, bg="#1a0e08", padx=15, pady=15, relief="ridge", borderwidth=1)
        f.pack(fill=tk.X, pady=(0, 15))

        tk.Label(f, text="Test Film Title:", bg="#1a0e08", fg="#cfa862").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.test_title = tk.Entry(f, width=45, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.test_title.insert(0, "Custom Embed Test Presentation")
        self.test_title.grid(row=0, column=1, sticky=tk.W, pady=4)

        tk.Label(f, text="Direct MP4 URL:", bg="#1a0e08", fg="#cfa862").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.test_url = tk.Entry(f, width=55, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.test_url.insert(0, "https://archive.org/download/his_girl_friday/his_girl_friday.mp4")
        self.test_url.grid(row=1, column=1, sticky=tk.W, pady=4)

        tk.Label(f, text="Duration (sec):", bg="#1a0e08", fg="#cfa862").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.test_dur = tk.Entry(f, width=12, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.test_dur.insert(0, "5500")
        self.test_dur.grid(row=2, column=1, sticky=tk.W, pady=4)

        tk.Label(f, text="Seek Offset (sec):", bg="#1a0e08", fg="#cfa862").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.test_offset = tk.Entry(f, width=12, bg="#25160d", fg="#fff", insertbackground="#fff")
        self.test_offset.insert(0, "120")
        self.test_offset.grid(row=3, column=1, sticky=tk.W, pady=4)

        ttk.Button(frame, text="Save & Export Starlight Test Save (.json)", command=self.export_test_save).pack(anchor=tk.W)

    def generate_new_seed(self):
        new_seed = int(datetime.now().timestamp()) % 100000000
        self.seed_var.set(str(new_seed))
        self.refresh_schedule_view()

    def save_schedule_settings(self):
        try:
            seed_val = int(self.seed_var.get())
        except ValueError:
            messagebox.showerror("Invalid Seed", "Please enter a valid integer for the seed.")
            return

        self.sched_data['seed'] = seed_val
        self.save_sched_file()

    def pull_published_schedule(self):
        url = "https://blainekyle.github.io/AO-Movies/live-sched.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read().decode('utf-8'))
            self.sched_data = data
            self.seed_var.set(str(data.get('seed', 19401225)))
            self.refresh_inserts_list()
            self.refresh_schedule_view()
            messagebox.showinfo("Success", f"Successfully pulled published schedule from {url}")
        except Exception as e:
            messagebox.showwarning("Notice", f"Could not fetch online live-sched.json ({e}). Using local file.")

    def refresh_schedule_view(self):
        try:
            seed = int(self.seed_var.get())
        except ValueError:
            seed = 19401225

        epoch_str = self.sched_data.get('epoch', '2026-01-01T00:00:00Z')
        epoch_dt = datetime.fromisoformat(epoch_str.replace('Z', '+00:00'))
        now_dt = datetime.now(timezone.utc)

        schedule_items = compute_schedule(seed, epoch_dt, now_dt, hours=12)

        self.tree.delete(*self.tree.get_children())
        for it in schedule_items:
            t_str = it['start'].strftime("%Y-%m-%d %H:%M:%S")
            kind = "Feature Film" if it['type'] == 'movie' else "Vintage Bumper"
            self.tree.insert("", tk.END, values=(t_str, kind, it['title'], format_duration(it['duration'])))

    def refresh_inserts_list(self):
        self.insert_tree.delete(*self.insert_tree.get_children())
        for ins in self.sched_data.get('inserts', []):
            self.insert_tree.insert("", tk.END, values=(
                ins.get('startTime', ''),
                ins.get('title', ''),
                ins.get('mode', 'graceful'),
                format_duration(ins.get('duration', 0))
            ))

    def add_insert(self):
        title = self.insert_title.get().strip()
        url = self.insert_url.get().strip()
        st = self.insert_time.get().strip()
        mode = self.insert_mode.get()

        try:
            dur = int(self.insert_dur.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Duration must be an integer (seconds).")
            return

        if not title or not url or not st:
            messagebox.showerror("Error", "Please fill in title, MP4 URL, and start time.")
            return

        new_insert = {
            "id": f"insert_{int(datetime.now().timestamp())}",
            "title": title,
            "url": url,
            "startTime": st,
            "duration": dur,
            "mode": mode
        }

        if 'inserts' not in self.sched_data:
            self.sched_data['inserts'] = []
        self.sched_data['inserts'].append(new_insert)
        self.save_sched_file()
        self.refresh_inserts_list()

    def remove_insert(self):
        sel = self.insert_tree.selection()
        if not sel:
            return
        idx = self.insert_tree.index(sel[0])
        inserts = self.sched_data.get('inserts', [])
        if 0 <= idx < len(inserts):
            del inserts[idx]
            self.save_sched_file()
            self.refresh_inserts_list()

    def export_test_save(self):
        title = self.test_title.get().strip()
        url = self.test_url.get().strip()
        try:
            dur = int(self.test_dur.get().strip())
            offset = int(self.test_offset.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Duration and seek offset must be numbers.")
            return

        item = {
            "type": "movie",
            "identifier": "custom_test",
            "title": title,
            "description": "Custom embed presentation created in Starlight Companion.",
            "url": url,
            "sourceUrl": url,
            "duration": dur,
            "startTime": offset
        }

        payload = {
            "app": "Starlight Cinema Classics",
            "version": "2.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "currentIndex": 0,
            "playbackPosition": offset,
            "currentMovieTitle": title,
            "queue": [item]
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"starlight_test_slot_{Date_token()}.json"
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            messagebox.showinfo("Exported", f"Saved test save file:\n{filepath}\n\nImport it into any slot in the app pause menu!")


def Date_token():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


if __name__ == "__main__":
    app = StarlightCompanionApp()
    app.mainloop()
