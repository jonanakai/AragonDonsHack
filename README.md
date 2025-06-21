# AI Image Telephone

A modern web application for playing AI Image Telephone - a fun game where players take turns modifying images with AI prompts using Replicate's Flux model.

## Features

- 🎮 **Modern Web Interface**: Beautiful, responsive UI built with React and Tailwind CSS
- 🖼️ **Drag & Drop Image Upload**: Easy image upload with drag and drop functionality
- 🤖 **AI Image Processing**: Powered by Replicate's Flux 1.1 Pro model
- 👥 **Multi-Player Support**: 2-6 players can participate in each game
- 📱 **Real-time Updates**: Live game status and progress tracking
- 🖼️ **Image Gallery**: View the complete chain of modified images
- 💾 **Download Images**: Save any image from the chain
- 🔄 **Game Management**: Reset games or start new ones easily

## How to Play

1. **Start a Game**: Choose the number of players (2-6)
2. **Upload Image**: Drag and drop or select a starting image
3. **Take Turns**: Each player writes a prompt describing how to modify the current image
4. **Watch the Magic**: AI processes each prompt and creates a new image
5. **See Results**: View the complete chain of transformations at the end

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Replicate API token

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   REPLICATE_API_TOKEN=your_replicate_api_token_here
   ```

3. **Start the Flask backend**:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the React development server**:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

### Getting a Replicate API Token

1. Go to [replicate.com](https://replicate.com)
2. Sign up or log in to your account
3. Navigate to your account settings
4. Copy your API token
5. Add it to your `.env` file

## Project Structure

```
aragondonshack/
├── app.py                 # Flask backend API
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── uploads/              # Uploaded images (auto-created)
├── images/               # Generated images (auto-created)
├── frontend/             # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.js        # Main app component
│   │   └── index.js      # Entry point
│   ├── package.json      # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS config
└── README.md
```

## API Endpoints

- `POST /api/game/create` - Create a new game
- `POST /api/game/<id>/upload-image` - Upload starting image
- `POST /api/game/<id>/submit-prompt` - Submit player prompt
- `GET /api/game/<id>/status` - Get game status
- `GET /api/game/<id>/image/<index>` - Get image by index
- `POST /api/game/<id>/reset` - Reset game

## Technologies Used

### Backend
- **Flask**: Python web framework
- **Replicate**: AI model API
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **React**: JavaScript library for building user interfaces
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **React Dropzone**: File upload component
- **Lucide React**: Icon library

## Development

### Running in Development Mode

1. Start the backend:
   ```bash
   python app.py
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. The built files will be in `frontend/build/`

## Contributing

This project was created for the Replicate Hackathon 2025 by:
- Jona Nakai
- Laurent Ludwig
- Rumi Loghmani
- Nathan Wu

## License

This project is open source and available under the MIT License.
