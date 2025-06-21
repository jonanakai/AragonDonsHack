import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
import os
from config import UI_CONFIG, GAME_CONFIG
from game_manager import GameManager
import logging

logger = logging.getLogger(__name__)

class PromptChainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG['window_title'])
        self.root.geometry(UI_CONFIG['window_size'])
        self.root.configure(bg=UI_CONFIG['theme']['bg_color'])
        
        self.game_manager = GameManager()
        self.current_images = {'original': None, 'target': None}
        self.timer_running = False
        self.timer_thread = None
        
        self._setup_ui()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background=UI_CONFIG['theme']['bg_color'],
                       foreground=UI_CONFIG['theme']['fg_color'],
                       font=(UI_CONFIG['font_family'], 16, 'bold'))
        
        style.configure('Info.TLabel',
                       background=UI_CONFIG['theme']['bg_color'],
                       foreground=UI_CONFIG['theme']['fg_color'],
                       font=(UI_CONFIG['font_family'], UI_CONFIG['font_size']))
        
        style.configure('Success.TLabel',
                       background=UI_CONFIG['theme']['bg_color'],
                       foreground=UI_CONFIG['theme']['success_color'],
                       font=(UI_CONFIG['font_family'], UI_CONFIG['font_size'], 'bold'))
        
        style.configure('Error.TLabel',
                       background=UI_CONFIG['theme']['bg_color'],
                       foreground=UI_CONFIG['theme']['error_color'],
                       font=(UI_CONFIG['font_family'], UI_CONFIG['font_size']))
    
    def _setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=UI_CONFIG['theme']['bg_color'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎮 Prompt Chain", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Game setup frame
        self.setup_frame = tk.Frame(main_frame, bg=UI_CONFIG['theme']['bg_color'])
        self.setup_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Setup controls
        setup_label = ttk.Label(self.setup_frame, text="Game Setup", style='Title.TLabel')
        setup_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Rounds selection
        rounds_frame = tk.Frame(self.setup_frame, bg=UI_CONFIG['theme']['bg_color'])
        rounds_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rounds_frame, text="Number of Rounds:", style='Info.TLabel').pack(side=tk.LEFT)
        self.rounds_var = tk.IntVar(value=GAME_CONFIG['default_rounds'])
        rounds_spinbox = ttk.Spinbox(rounds_frame, from_=GAME_CONFIG['min_rounds'], 
                                   to=GAME_CONFIG['max_rounds'], textvariable=self.rounds_var, width=10)
        rounds_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Primary image selection
        image_frame = tk.Frame(self.setup_frame, bg=UI_CONFIG['theme']['bg_color'])
        image_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(image_frame, text="Primary Image:", style='Info.TLabel').pack(side=tk.LEFT)
        self.image_path_var = tk.StringVar()
        image_entry = ttk.Entry(image_frame, textvariable=self.image_path_var, width=40)
        image_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        browse_btn = ttk.Button(image_frame, text="Browse", command=self._browse_image)
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(image_frame, text="(Leave empty to generate AI image)", 
                 style='Info.TLabel').pack(side=tk.LEFT)
        
        # Start game button
        self.start_btn = ttk.Button(self.setup_frame, text="Start New Game", 
                                   command=self._start_game)
        self.start_btn.pack(pady=(10, 0))
        
        # Game area (initially hidden)
        self.game_frame = tk.Frame(main_frame, bg=UI_CONFIG['theme']['bg_color'])
        
        # Progress bar
        self.progress_frame = tk.Frame(self.game_frame, bg=UI_CONFIG['theme']['bg_color'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_label = ttk.Label(self.progress_frame, text="", style='Info.TLabel')
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=(5, 0))
        
        # Timer
        self.timer_frame = tk.Frame(self.game_frame, bg=UI_CONFIG['theme']['bg_color'])
        self.timer_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.timer_label = ttk.Label(self.timer_frame, text="Time remaining: 02:00", style='Info.TLabel')
        self.timer_label.pack(anchor=tk.W)
        
        # Images frame
        images_frame = tk.Frame(self.game_frame, bg=UI_CONFIG['theme']['bg_color'])
        images_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Original image
        original_frame = tk.Frame(images_frame, bg=UI_CONFIG['theme']['bg_color'])
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(original_frame, text="Original Image", style='Info.TLabel').pack()
        self.original_canvas = tk.Canvas(original_frame, bg='white', 
                                       width=UI_CONFIG['image_display_size'][0],
                                       height=UI_CONFIG['image_display_size'][1])
        self.original_canvas.pack(pady=(5, 0))
        
        # Target image
        target_frame = tk.Frame(images_frame, bg=UI_CONFIG['theme']['bg_color'])
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(target_frame, text="Target Image (Guess the prompt!)", style='Info.TLabel').pack()
        self.target_canvas = tk.Canvas(target_frame, bg='white',
                                     width=UI_CONFIG['image_display_size'][0],
                                     height=UI_CONFIG['image_display_size'][1])
        self.target_canvas.pack(pady=(5, 0))
        
        # Prompt input frame
        prompt_frame = tk.Frame(self.game_frame, bg=UI_CONFIG['theme']['bg_color'])
        prompt_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(prompt_frame, text="Your Prompt:", style='Info.TLabel').pack(anchor=tk.W)
        
        self.prompt_text = tk.Text(prompt_frame, height=4, width=60, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, pady=(5, 0))
        
        # Submit button
        self.submit_btn = ttk.Button(prompt_frame, text="Submit Prompt", 
                                    command=self._submit_prompt, state=tk.DISABLED)
        self.submit_btn.pack(pady=(10, 0))
        
        # Results frame (initially hidden)
        self.results_frame = tk.Frame(main_frame, bg=UI_CONFIG['theme']['bg_color'])
        
        # Results title
        results_title = ttk.Label(self.results_frame, text="🎉 Game Complete! 🎉", style='Title.TLabel')
        results_title.pack(pady=(0, 20))
        
        # Results text
        self.results_text = tk.Text(self.results_frame, height=20, width=80, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # New game button
        new_game_btn = ttk.Button(self.results_frame, text="Start New Game", 
                                 command=self._show_setup)
        new_game_btn.pack(pady=(20, 0))
    
    def _browse_image(self):
        """Open file dialog to select primary image"""
        file_path = filedialog.askopenfilename(
            title="Select Primary Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.image_path_var.set(file_path)
    
    def _start_game(self):
        """Start a new game"""
        try:
            # Validate inputs
            rounds = self.rounds_var.get()
            if not (GAME_CONFIG['min_rounds'] <= rounds <= GAME_CONFIG['max_rounds']):
                messagebox.showerror("Error", f"Rounds must be between {GAME_CONFIG['min_rounds']} and {GAME_CONFIG['max_rounds']}")
                return
            
            # Get image path
            image_path = self.image_path_var.get().strip()
            if image_path and not os.path.exists(image_path):
                messagebox.showerror("Error", "Selected image file does not exist")
                return
            
            # Start game in background thread
            def start_game_thread():
                try:
                    self.game_manager.initialize_game(
                        primary_image_path=image_path if image_path else None,
                        total_rounds=rounds
                    )
                    
                    # Update UI on main thread
                    self.root.after(0, self._show_game)
                    self.root.after(0, self._update_round_display)
                    
                except Exception as e:
                    logger.error(f"Failed to start game: {e}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start game: {str(e)}"))
            
            threading.Thread(target=start_game_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            messagebox.showerror("Error", f"Error starting game: {str(e)}")
    
    def _show_game(self):
        """Show the game interface"""
        self.setup_frame.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self._start_timer()
    
    def _show_setup(self):
        """Show the setup interface"""
        self.game_frame.pack_forget()
        self.results_frame.pack_forget()
        self.setup_frame.pack(fill=tk.X, pady=(0, 20))
        self.game_manager.reset_game()
    
    def _update_round_display(self):
        """Update the round display with current images"""
        round_info = self.game_manager.get_current_round_info()
        if not round_info:
            return
        
        # Update progress
        progress = self.game_manager.get_game_progress()
        self.progress_label.config(text=f"Round {progress['current_round']} of {progress['total_rounds']}")
        self.progress_bar['value'] = progress['progress_percentage']
        
        # Load and display images
        self._load_image(round_info['original_image'], self.original_canvas, 'original')
        self._load_image(round_info['target_image'], self.target_canvas, 'target')
        
        # Enable submit button
        self.submit_btn.config(state=tk.NORMAL)
        
        # Clear prompt text
        self.prompt_text.delete(1.0, tk.END)
    
    def _load_image(self, image_path, canvas, image_type):
        """Load and display an image on a canvas"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image not found: {image_path}")
                return
            
            # Load and resize image
            image = Image.open(image_path)
            image.thumbnail(UI_CONFIG['image_display_size'], Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Store reference to prevent garbage collection
            self.current_images[image_type] = photo
            
            # Clear canvas and display image
            canvas.delete("all")
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # Center the image
            x = (canvas_width - photo.width()) // 2
            y = (canvas_height - photo.height()) // 2
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
    
    def _start_timer(self):
        """Start the turn timer"""
        self.timer_running = True
        self.time_remaining = GAME_CONFIG['turn_time_limit']
        
        def update_timer():
            if not self.timer_running:
                return
            
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_label.config(text=f"Time remaining: {minutes:02d}:{seconds:02d}")
            
            if self.time_remaining <= 0:
                self.timer_running = False
                messagebox.showwarning("Time's Up!", "Time limit reached! Submitting current prompt...")
                self._submit_prompt()
                return
            
            self.time_remaining -= 1
            self.root.after(1000, update_timer)
        
        update_timer()
    
    def _stop_timer(self):
        """Stop the turn timer"""
        self.timer_running = False
    
    def _submit_prompt(self):
        """Submit the player's prompt"""
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt!")
            return
        
        # Disable submit button during processing
        self.submit_btn.config(state=tk.DISABLED)
        self._stop_timer()
        
        # Submit in background thread
        def submit_thread():
            try:
                self.game_manager.submit_player_prompt(prompt)
                
                # Check if game is finished
                if self.game_manager.game_state['game_finished']:
                    self.root.after(0, self._show_results)
                else:
                    self.root.after(0, self._update_round_display)
                    self.root.after(0, self._start_timer)
                
            except Exception as e:
                logger.error(f"Failed to submit prompt: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to submit prompt: {str(e)}"))
                self.root.after(0, lambda: self.submit_btn.config(state=tk.NORMAL))
        
        threading.Thread(target=submit_thread, daemon=True).start()
    
    def _show_results(self):
        """Show the game results"""
        self.game_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get full chain
        chain = self.game_manager.get_full_chain()
        if not chain:
            return
        
        # Build results text
        results = "🎮 PROMPT CHAIN RESULTS 🎮\n\n"
        results += f"Game completed with {len(chain['rounds'])} rounds!\n\n"
        
        results += "📋 FULL PROMPT CHAIN:\n"
        results += "=" * 50 + "\n\n"
        
        for i, round_data in enumerate(chain['rounds']):
            results += f"Round {round_data['round']} ({round_data['player_name']}):\n"
            results += f"Prompt: \"{round_data['prompt']}\"\n"
            results += f"Image: {round_data['image_path']}\n"
            results += "-" * 30 + "\n\n"
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PromptChainGUI()
    app.run() 