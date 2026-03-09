#!/usr/bin/env python3
# ============================================
# YOUTUBE DOWNLOADER - Auto Best Quality
# Shows available formats, picks best without FFmpeg
# ============================================

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

try:
    import yt_dlp as youtube_dl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp as youtube_dl


class YouTubeDownloader:
    def __init__(self):
        self.download_path = Path.home() / "Downloads" / "YouTube"
        self.download_path.mkdir(parents=True, exist_ok=True)
    
    def check_available_formats(self, url):
        """Check what qualities are available without FFmpeg"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Find pre-merged formats (video+audio together, no FFmpeg needed)
            premerged = []
            for f in formats:
                # Has both video and audio codec
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height', 0)
                    if height > 0:
                        premerged.append({
                            'height': height,
                            'format_id': f['format_id'],
                            'ext': f.get('ext', 'mp4')
                        })
            
            # Sort by height descending
            premerged.sort(key=lambda x: x['height'], reverse=True)
            
            # Get unique heights
            seen = set()
            unique = []
            for f in premerged:
                if f['height'] not in seen:
                    seen.add(f['height'])
                    unique.append(f)
            
            return unique, info.get('title', 'Unknown')
    
    def get_best_format(self, url, preferred_height):
        """Get best available format at or below preferred height"""
        available, title = self.check_available_formats(url)
        
        if not available:
            return 'best', "360p (only option)"
        
        # Find best format at or below preferred height
        for fmt in available:
            if fmt['height'] <= preferred_height:
                # Use format_id for exact match
                return fmt['format_id'], f"{fmt['height']}p"
        
        # If nothing matches, return lowest available
        lowest = available[-1]
        return lowest['format_id'], f"{lowest['height']}p (best available)"
    
    def download(self, url, format_type, preferred_quality, progress_hook):
        output = str(self.download_path / "%(title)s.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'extractaudio': True,
            })
            actual_quality = "MP3 192kbps"
        else:
            # Get best available format at preferred quality
            format_id, actual_quality = self.get_best_format(url, preferred_quality)
            ydl_opts['format'] = format_id
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {
                'title': info.get('title', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'quality': actual_quality,
            }


class GUI:
    def __init__(self):
        self.downloader = YouTubeDownloader()
        
        self.root = tk.Tk()
        self.root.title("YouTube Downloader - Abban Ali")
        self.root.geometry("550x700")
        self.root.configure(bg="#1e1e2e")
        
        self.colors = {
            'bg': '#1e1e2e',
            'surface': '#313244',
            'text': '#cdd6f4',
            'blue': '#89b4fa',
            'green': '#a6e3a1',
            'red': '#f38ba8',
            'yellow': '#f9e2af'
        }
        
        self.available_formats = []
        self.current_url = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header
        header = tk.Frame(main, bg=self.colors['surface'], height=50)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🎬 YouTube Downloader",
            font=('JetBrains Mono', 16, 'bold'),
            bg=self.colors['surface'],
            fg=self.colors['blue']
        ).pack(side='left', padx=15, pady=10)
        
        # URL
        url_frame = tk.Frame(main, bg=self.colors['bg'])
        url_frame.pack(fill='x', pady=8)
        
        tk.Label(
            url_frame,
            text="YouTube URL:",
            font=('JetBrains Mono', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        self.url_entry = tk.Entry(
            url_frame,
            font=('JetBrains Mono', 10),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat'
        )
        self.url_entry.pack(fill='x', pady=5, ipady=6)
        
        # Buttons row
        btn_row = tk.Frame(url_frame, bg=self.colors['bg'])
        btn_row.pack(fill='x', pady=5)
        
        tk.Button(
            btn_row,
            text="📋 Paste",
            command=self.paste_url,
            bg=self.colors['surface'],
            fg=self.colors['text'],
            activebackground=self.colors['blue'],
            relief='flat',
            cursor='hand2',
            font=('JetBrains Mono', 9)
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_row,
            text="🔍 Check Available",
            command=self.check_formats,
            bg=self.colors['surface'],
            fg=self.colors['yellow'],
            activebackground=self.colors['yellow'],
            activeforeground='#1e1e2e',
            relief='flat',
            cursor='hand2',
            font=('JetBrains Mono', 9)
        ).pack(side='left', padx=5)
        
        # Available formats display
        self.formats_frame = tk.Frame(main, bg=self.colors['surface'], padx=10, pady=10)
        self.formats_label = tk.Label(
            self.formats_frame,
            text="Click 'Check Available' to see what qualities this video offers",
            font=('JetBrains Mono', 9),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            wraplength=450,
            justify='left'
        )
        self.formats_label.pack(anchor='w')
        
        # Format selection
        fmt_frame = tk.Frame(main, bg=self.colors['bg'])
        fmt_frame.pack(fill='x', pady=8)
        
        tk.Label(
            fmt_frame,
            text="Format:",
            font=('JetBrains Mono', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        self.format_var = tk.StringVar(value='mp4')
        
        fmt_inner = tk.Frame(fmt_frame, bg=self.colors['bg'])
        fmt_inner.pack(fill='x', pady=5)
        
        tk.Radiobutton(
            fmt_inner,
            text="🎬 Video (MP4)",
            variable=self.format_var,
            value='mp4',
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['surface'],
            font=('JetBrains Mono', 10),
            command=self.toggle_quality
        ).pack(side='left', padx=5)
        
        tk.Radiobutton(
            fmt_inner,
            text="🎵 Audio (MP3)",
            variable=self.format_var,
            value='mp3',
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['surface'],
            font=('JetBrains Mono', 10),
            command=self.toggle_quality
        ).pack(side='left', padx=20)
        
        # Quality selection
        self.quality_frame = tk.Frame(main, bg=self.colors['bg'])
        self.quality_frame.pack(fill='x', pady=8)
        
        tk.Label(
            self.quality_frame,
            text="Preferred Quality:",
            font=('JetBrains Mono', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        self.quality_var = tk.StringVar(value='1080')
        
        self.quality_combo = ttk.Combobox(
            self.quality_frame,
            textvariable=self.quality_var,
            values=['1080', '720', '480', '360'],
            state='readonly',
            font=('JetBrains Mono', 10)
        )
        self.quality_combo.pack(fill='x', pady=5)
        
        tk.Label(
            self.quality_frame,
            text="⚡ Will auto-pick best available at or below this quality",
            font=('JetBrains Mono', 9),
            bg=self.colors['bg'],
            fg=self.colors['yellow']
        ).pack(anchor='w')
        
        # Location
        loc_frame = tk.Frame(main, bg=self.colors['bg'])
        loc_frame.pack(fill='x', pady=8)
        
        tk.Label(
            loc_frame,
            text="Save to:",
            font=('JetBrains Mono', 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        loc_inner = tk.Frame(loc_frame, bg=self.colors['surface'])
        loc_inner.pack(fill='x', pady=5)
        
        self.loc_label = tk.Label(
            loc_inner,
            text=str(self.downloader.download_path),
            font=('JetBrains Mono', 9),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            anchor='w',
            padx=10,
            pady=6
        )
        self.loc_label.pack(side='left', fill='x', expand=True)
        
        tk.Button(
            loc_inner,
            text="Change",
            command=self.change_location,
            bg=self.colors['surface'],
            fg=self.colors['text'],
            activebackground=self.colors['blue'],
            relief='flat',
            cursor='hand2',
            font=('JetBrains Mono', 9)
        ).pack(side='right', padx=5)
        
        # Progress
        self.progress_frame = tk.Frame(main, bg=self.colors['bg'])
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(
            self.progress_frame,
            text="Ready",
            font=('JetBrains Mono', 10),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.status_label.pack(anchor='w')
        
        # Spacer
        spacer = tk.Frame(main, bg=self.colors['bg'])
        spacer.pack(fill='both', expand=True)
        
        # Download button
        self.download_btn = tk.Button(
            main,
            text="⬇️  START DOWNLOAD",
            command=self.start_download,
            bg=self.colors['blue'],
            fg='#1e1e2e',
            activebackground=self.colors['green'],
            font=('JetBrains Mono', 14, 'bold'),
            relief='flat',
            cursor='hand2',
            height=2
        )
        self.download_btn.pack(fill='x', pady=15)
        
        # Footer
        tk.Label(
            main,
            text="by Abban Ali • github.com/AbbanAli",
            font=('JetBrains Mono', 9),
            bg=self.colors['bg'],
            fg='#6c7086'
        ).pack(side='bottom', pady=5)
    
    def check_formats(self):
        """Check what formats are available for this URL"""
        url = self.url_entry.get().strip()
        
        if not url or ('youtube' not in url and 'youtu.be' not in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL first")
            return
        
        self.formats_frame.pack(fill='x', pady=10, before=self.root.winfo_children()[0].winfo_children()[3])
        self.formats_label.config(text="🔍 Checking available formats...", fg=self.colors['blue'])
        self.root.update()
        
        try:
            formats, title = self.downloader.check_available_formats(url)
            
            if not formats:
                text = f"📹 {title[:50]}...\n\n❌ No pre-merged formats found!\nThis video may require FFmpeg to download in higher quality.\n\nTry: MP3 audio (always works)"
                self.formats_label.config(text=text, fg=self.colors['red'])
            else:
                heights = [str(f['height']) for f in formats]
                text = f"📹 {title[:50]}...\n\n✅ Available qualities (no FFmpeg needed):\n   " + "p, ".join(heights) + "p\n\n💡 Best available: {0}p".format(formats[0]['height'])
                self.formats_label.config(text=text, fg=self.colors['green'])
                
                # Auto-select best quality
                best = formats[0]['height']
                if best >= 1080:
                    self.quality_var.set('1080')
                elif best >= 720:
                    self.quality_var.set('720')
                elif best >= 480:
                    self.quality_var.set('480')
                else:
                    self.quality_var.set('360')
                
        except Exception as e:
            self.formats_label.config(text=f"❌ Error checking: {str(e)[:100]}", fg=self.colors['red'])
    
    def toggle_quality(self):
        if self.format_var.get() == 'mp3':
            self.quality_frame.pack_forget()
            self.formats_frame.pack_forget()
        else:
            self.quality_frame.pack(fill='x', pady=8, after=self.root.winfo_children()[0].winfo_children()[2])
            # Don't auto-show formats frame, let user click check
    
    def paste_url(self):
        try:
            url = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        except:
            pass
    
    def change_location(self):
        folder = filedialog.askdirectory(initialdir=self.downloader.download_path)
        if folder:
            self.downloader.download_path = Path(folder)
            self.loc_label.config(text=str(folder))
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(percent)
                self.status_label.config(text=f"Downloading... {percent:.1f}%")
        elif d['status'] == 'finished':
            self.status_label.config(text="Processing...")
        self.root.update_idletasks()
    
    def start_download(self):
        url = self.url_entry.get().strip()
        
        if not url or ('youtube' not in url and 'youtu.be' not in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        self.progress_frame.pack(fill='x', pady=10, before=self.download_btn)
        self.download_btn.config(state='disabled', text="⏳ DOWNLOADING...")
        self.progress_var.set(0)
        self.status_label.config(text="Starting...", fg=self.colors['text'])
        
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url):
        error_msg = None
        result = None
        
        try:
            fmt = self.format_var.get()
            preferred = int(self.quality_var.get())
            result = self.downloader.download(url, fmt, preferred, self.progress_hook)
        except Exception as e:
            error_msg = str(e)
        
        if error_msg:
            self.root.after(0, lambda msg=error_msg: self.show_error(msg))
        else:
            self.root.after(0, lambda res=result: self.show_success(res))
    
    def show_success(self, result):
        self.progress_var.set(100)
        self.status_label.config(text="Complete!", fg=self.colors['green'])
        self.download_btn.config(state='normal', text="⬇️  START DOWNLOAD")
        
        messagebox.showinfo("Success", 
            f"Downloaded: {result['title']}\n"
            f"By: {result['uploader']}\n"
            f"Quality: {result['quality']}\n"
            f"Saved to: {self.downloader.download_path}"
        )
        
        self.progress_frame.pack_forget()
        self.status_label.config(text="Ready", fg=self.colors['text'])
    
    def show_error(self, msg):
        self.download_btn.config(state='normal', text="⬇️  START DOWNLOAD")
        
        if "unavailable" in msg.lower():
            msg = "Video is unavailable or private"
        
        self.status_label.config(text=f"Error: {msg[:40]}", fg=self.colors['red'])
        messagebox.showerror("Error", f"Download failed:\n{msg}")
        self.progress_frame.pack_forget()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    GUI().run()