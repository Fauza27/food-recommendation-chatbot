# Food Finder - Frontend

Frontend aplikasi Food Finder menggunakan Next.js 15, TypeScript, Tailwind CSS, dan shadcn/ui.

## 🚀 Features

- ✅ **Chat dengan AI** - Chatbot untuk rekomendasi tempat makan
- ✅ **Explore Restoran** - Browse 709+ restoran dengan search & filter
- ✅ **Responsive Design** - Mobile-first dengan breakpoints custom
- ✅ **Dark Mode Ready** - Support dark mode
- ✅ **Smooth Animations** - Framer Motion animations
- ✅ **Type-Safe** - Full TypeScript support

## 📱 Responsive Breakpoints

```typescript
Mobile: default (< 640px)
Tablet: 640px (sm)
Desktop: 768px (md)
Large: 1024px (lg)
Extra Large: 1280px (xl)
```

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **State Management**: TanStack Query (React Query)
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Markdown**: React Markdown

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Chat page (home)
│   │   ├── explore/
│   │   │   └── page.tsx          # Explore page
│   │   ├── layout.tsx            # Root layout
│   │   ├── providers.tsx         # React Query provider
│   │   └── globals.css           # Global styles
│   │
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── badge.tsx
│   │   │   └── skeleton.tsx
│   │   ├── ChatHeader.tsx        # Navigation header
│   │   ├── ChatBubble.tsx        # Chat message bubble
│   │   ├── RestaurantCard.tsx    # Restaurant card
│   │   └── TypingIndicator.tsx   # Loading indicator
│   │
│   └── lib/
│       ├── api.ts                # API client & types
│       └── utils.ts              # Utility functions
│
├── .env.local                    # Environment variables
├── tailwind.config.ts            # Tailwind configuration
├── next.config.js                # Next.js configuration
└── package.json                  # Dependencies
```

## 🎨 Pages

### 1. Chat Page (`/`)
- AI chatbot untuk rekomendasi
- Conversation history
- Restaurant cards hasil rekomendasi
- Suggestion chips
- Real-time typing indicator

### 2. Explore Page (`/explore`)
- Browse semua restoran (709+)
- Search functionality
- Category filter
- Pagination
- Responsive grid layout

## 🔌 API Integration

### Chat API
```typescript
POST /chat
Body: {
  message: string;
  conversation_history: ConversationMessage[];
}
```

### Posts API
```typescript
GET /api/posts?page=1&limit=20&search=japanese&category=Japanese%20Food
```

### Categories API
```typescript
GET /api/categories
```

See `src/lib/api.ts` for full API client implementation.

## 🎯 Components

### ChatHeader
Navigation header dengan logo dan menu.

### ChatBubble
Message bubble untuk user dan AI dengan support markdown.

### RestaurantCard
Card untuk menampilkan informasi restoran:
- Nama & status operasional
- Kategori & harga
- Jam buka
- Menu andalan
- Fasilitas
- Link lokasi & Instagram

### TypingIndicator
Animated loading indicator saat AI mengetik.

## 🎨 Styling

### Tailwind Classes
```css
.glass - Background blur effect
.glass-strong - Stronger blur effect
.scrollbar-none - Hide scrollbar
```

### Color Scheme
- Primary: Blue (#3B82F6)
- Secondary: Gray
- Accent: Orange (🍊)
- Destructive: Red

### Dark Mode
Automatic dark mode support dengan CSS variables.

## 📱 Responsive Design

### Mobile (< 640px)
- Single column layout
- Full-width components
- Touch-optimized buttons
- Horizontal scroll for categories

### Tablet (640px - 768px)
- 2-column grid for cards
- Larger touch targets
- Optimized spacing

### Desktop (768px+)
- 3-column grid for cards
- Hover effects
- Larger content area
- Better typography

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables
Set `NEXT_PUBLIC_API_URL` in your deployment platform.

## 🧪 Testing

```bash
# Run tests (if configured)
npm test

# Type check
npm run type-check

# Lint
npm run lint
```

## 📊 Performance

- **First Load**: ~200KB
- **Lighthouse Score**: 90+
- **Core Web Vitals**: Good
- **Image Optimization**: Next.js automatic
- **Code Splitting**: Automatic per route

## 🔍 SEO

- Metadata configured in `layout.tsx`
- Semantic HTML
- Proper heading hierarchy
- Alt text for images (when added)

## 🐛 Troubleshooting

### API Connection Error
```bash
# Check backend is running
curl http://localhost:8000/health

# Check environment variable
echo $NEXT_PUBLIC_API_URL
```

### Build Errors
```bash
# Clear cache
rm -rf .next
npm run build
```

### Type Errors
```bash
# Regenerate types
npm run type-check
```

## 📝 Development Tips

### Adding New Components
```bash
# Use shadcn/ui CLI
npx shadcn-ui@latest add [component-name]
```

### API Client
All API calls go through `src/lib/api.ts`. Add new endpoints there.

### Styling
Use Tailwind classes. Custom styles in `globals.css`.

### State Management
Use React Query for server state, useState for local state.

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

## 📄 License

MIT License

## 🙏 Credits

- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Backend**: FastAPI + Python

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Production Ready ✅
