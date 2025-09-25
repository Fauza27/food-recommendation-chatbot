# JalanJalan MakanEnak

A modern restaurant recommendation app built with Next.js 14+, featuring Apple-inspired design aesthetics and real-time chat functionality for food recommendations.

## Features

- **Modern Glassmorphism Design**: Apple-inspired UI with backdrop blur effects, rounded corners, and semi-transparent backgrounds
- **Responsive Layout**: Mobile-first design with collapsible sidebar navigation
- **Real-time Chatbot**: WhatsApp-style chat interface for restaurant recommendations
- **Restaurant Discovery**: Browse and filter restaurant posts with search functionality
- **Dark Mode Support**: Toggle between light and dark themes
- **Performance Optimized**: Built with Next.js App Router for optimal performance

## Tech Stack

- **Frontend**: Next.js 14+, React 18, TypeScript
- **Styling**: Tailwind CSS with custom glassmorphism utilities
- **UI Components**: Radix UI primitives, Lucide React icons
- **Forms**: React Hook Form with validation
- **API**: Axios for HTTP requests
- **State Management**: React hooks with localStorage persistence
- **Notifications**: React Hot Toast

## Getting Started

1. **Clone the repository**
```bash
git clone <repository-url>
cd jalanjalan-makanenak
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env.local
```
Edit `.env.local` and add your backend API URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run the development server**
```bash
npm run dev
```

5. **Open your browser**
Navigate to [http://localhost:3000](http://localhost:3000)

## API Integration

The app integrates with your RAG-powered FastAPI backend running on `http://localhost:8000` with the following endpoint:

### POST /api/chat
**Request:**
```json
{
  "query": "string"
}
```

**Response:**
```json
{
  "answer": "string",
  "cards": [
    {
      "nama_tempat": "string",
      "link": "string",
      "harga": "string",
      "lokasi": "string",
      "jam_operasional": "string",
      "deskripsi": "string",
      "menu_andalan": "string",
      "kategori": "string",
      "cocok_untuk": "string"
    }
  ]
}
```

## Backend Setup

Make sure your RAG backend is running before using the chatbot:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend requires:
- AWS Bedrock access for embeddings and LLM
- Qdrant vector database connection
- Environment variables for QDRANT_API_KEY and AWS credentials

## Project Structure

```
├── app/                    # Next.js App Router pages
│   ├── chatbot/           # Chatbot page
│   ├── posts/             # Restaurant posts page
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page (redirects to chatbot)
├── components/            # Reusable React components
│   ├── Header.tsx         # App header with theme toggle
│   ├── Sidebar.tsx        # Navigation sidebar
│   ├── RestaurantCard.tsx # Restaurant card for chat
│   └── RestaurantPostCard.tsx # Restaurant card for posts
├── data/                  # Static data
│   └── posts.ts          # Restaurant posts data
├── lib/                   # Utility functions
└── styles/               # Global styles
```

## Features

### Chatbot Page (`/chatbot`)
- WhatsApp-style chat interface
- Real-time message exchange with AI assistant
- Horizontal scrollable restaurant recommendations
- Chat history persistence in localStorage
- Markdown support for AI responses
- Loading states and error handling

### Posts Page (`/posts`)
- Instagram feed-style restaurant grid
- Search functionality across multiple fields
- Category filtering with chips/pills interface
- Client-side filtering and sorting
- Responsive card layout

### Design System
- **Colors**: Neutral palette with blue accents
- **Typography**: Inter font family for clean readability
- **Effects**: Glassmorphism with backdrop-blur and transparency
- **Animations**: Subtle hover effects and smooth transitions
- **Responsive**: Mobile-first approach with Tailwind breakpoints

## Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on every push

### Manual Build
```bash
npm run build
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.