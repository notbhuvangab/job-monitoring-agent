# Job Monitoring Frontend

Modern React/Next.js frontend for the Job Monitoring & Resume Fit Agent.

## 🎨 Features

- **Three-Column Layout**: Visual separation by job fit (Best/Mid/Least)
- **Real-Time Updates**: WebSocket integration for live job notifications
- **Advanced Filtering**: Search, remote toggle, company filter
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Built with Tailwind CSS
- **TypeScript**: Type-safe development

## 🏗️ Structure

```
app/
├── page.tsx           # Main dashboard page
├── layout.tsx         # Root layout
└── globals.css        # Global styles

components/
├── JobCard.tsx        # Individual job card
├── JobColumn.tsx      # Column container for jobs
└── Header.tsx         # Header with filters and controls

lib/
├── api.ts             # API client functions
└── websocket.ts       # WebSocket client class
```

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Configure environment
cp env_example.txt .env.local
# Edit .env.local with backend URLs

# Development
npm run dev

# Production build
npm run build
npm start
```

## 📦 Dependencies

- **next**: React framework (v14)
- **react**: UI library
- **axios**: HTTP client
- **tailwindcss**: Utility-first CSS
- **typescript**: Type safety

## 🎯 Components

### JobCard
Displays individual job with:
- Title, company, location
- Work type badge (remote/hybrid/onsite)
- Score percentage with color coding
- Matched skills tags
- Apply button

Props:
```typescript
interface JobCardProps {
  job: Job;
}
```

### JobColumn
Container for job cards in each category:
- Header with icon and count
- Scrollable job list
- Empty state

Props:
```typescript
interface JobColumnProps {
  title: string;
  jobs: Job[];
  color: 'green' | 'blue' | 'gray';
  icon: React.ReactNode;
}
```

### Header
Top navigation and controls:
- Search bar
- Remote-only toggle
- Resume upload button
- Manual fetch trigger
- Statistics display

Props:
```typescript
interface HeaderProps {
  stats: Stats | null;
  onSearch: (query: string) => void;
  onRemoteToggle: (enabled: boolean) => void;
  onUploadResume: (file: File) => void;
  onTriggerFetch: () => void;
}
```

## 🔌 API Integration

The `lib/api.ts` file provides typed API functions:

```typescript
// Get jobs with filters
const jobs = await api.getJobs({
  label: 'best',
  remote_only: true,
  search: 'python',
});

// Upload resume
await api.uploadResume(file);

// Get statistics
const stats = await api.getStats();

// Trigger manual fetch
await api.triggerFetch();
```

## 🔄 WebSocket Integration

Real-time updates via WebSocket:

```typescript
const wsClient = new WebSocketClient();

wsClient.connect((message) => {
  if (message.type === 'new_job') {
    console.log('New job:', message.data);
    // Refresh job list
  }
});

// Cleanup
wsClient.disconnect();
```

## 🎨 Styling

### Tailwind Configuration

Custom colors defined in `tailwind.config.js`:
- primary: Blue
- secondary: Purple
- success: Green
- warning: Orange
- danger: Red

### Color Scheme

- **Best Fit**: Green (`bg-green-50`, `text-green-600`)
- **Mid Fit**: Blue (`bg-blue-50`, `text-blue-600`)
- **Least Fit**: Gray (`bg-gray-50`, `text-gray-600`)

### Responsive Design

Breakpoints:
- Mobile: < 768px (1 column)
- Tablet: 768px - 1024px (2 columns)
- Desktop: > 1024px (3 columns)

## 🔧 Configuration

### Environment Variables

`.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Next.js Config

`next.config.js`:
```javascript
module.exports = {
  reactStrictMode: true,
  // Add custom config here
}
```

## 🧪 Development

### Run Development Server
```bash
npm run dev
# Open http://localhost:3000
```

### Build for Production
```bash
npm run build
npm start
```

### Lint Code
```bash
npm run lint
```

## 📱 Features Detail

### Search
- Searches job title, company, and description
- Debounced input (instant search)
- Case-insensitive matching

### Remote Toggle
- Shows only remote jobs when enabled
- Toggle switch UI component
- Filters applied immediately

### Resume Upload
- Accepts PDF and TXT files
- Drag-and-drop support
- Progress indication
- Success/error feedback

### Job Cards
- Truncated descriptions (200 chars)
- Top 8 matched skills shown
- Score color coding:
  - Green: >85%
  - Blue: 65-85%
  - Gray: <65%

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy

# Production deployment
vercel --prod
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t job-monitor-frontend .
docker run -p 3000:3000 job-monitor-frontend
```

### Static Export

```bash
# Add to next.config.js
module.exports = {
  output: 'export',
}

# Build
npm run build
# Output in 'out/' directory
```

## 🐛 Troubleshooting

### WebSocket connection fails
- Check backend is running
- Verify WS_URL in `.env.local`
- Check browser console for errors

### API requests fail
- Verify backend is running at API_URL
- Check CORS configuration
- Review network tab in DevTools

### Styles not loading
- Clear `.next` cache: `rm -rf .next`
- Reinstall dependencies: `npm install`
- Check Tailwind configuration

### Build errors
- Delete `node_modules` and `.next`
- Run `npm install`
- Check TypeScript errors: `npm run build`

## 📚 References

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🎯 Best Practices

- Use TypeScript for type safety
- Keep components small and focused
- Use React hooks for state management
- Implement proper error handling
- Add loading states for async operations
- Optimize images and assets
- Use semantic HTML
- Ensure accessibility (ARIA labels)

## 🔐 Security

- API URLs configured via environment variables
- No sensitive data in client code
- CORS handled by backend
- File upload validation
- XSS protection via React
- CSP headers (configure in production)

