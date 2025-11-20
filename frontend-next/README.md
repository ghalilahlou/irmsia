# IRMSIA Medical AI - Frontend

Next.js 15 frontend for the IRMSIA Medical Imaging AI platform.

## 🚀 Features

- **Next.js 15** with App Router
- **TailwindCSS** for styling
- **React Query (TanStack)** for API caching
- **Axios** for HTTP requests
- **JWT Authentication** with secure cookie storage
- **DICOM Upload** with drag & drop
- **AI Analysis** visualization
- **Blockchain Audit Logs** display

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## 🛠️ Installation

1. **Install dependencies:**

```bash
cd frontend-next
npm install
```

2. **Configure environment:**

The `.env.local` file has been created automatically. If you need to recreate it, copy `env.example`:

```bash
# On Windows PowerShell
Copy-Item env.example .env.local

# On Linux/Mac
cp env.example .env.local
```

Edit `.env.local` and set your API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend-next/
├── app/                    # Next.js App Router pages
│   ├── login/             # Login page
│   ├── dashboard/         # Dashboard page
│   ├── upload/            # DICOM upload page
│   ├── analysis/          # AI analysis page
│   └── logs/              # Audit logs page
├── components/            # React components
│   ├── ui/               # ShadCN UI components
│   ├── Navbar.tsx        # Navigation bar
│   ├── Dropzone.tsx      # File upload component
│   ├── DicomPreview.tsx  # DICOM image preview
│   ├── AnalysisCard.tsx  # AI analysis display
│   └── BlockchainLogTable.tsx  # Audit logs table
├── lib/                  # Utilities
│   ├── api.ts           # API client (Axios)
│   ├── auth.ts          # Authentication helpers
│   └── utils.ts          # Utility functions
└── public/              # Static assets
```

## 🔐 Authentication

The frontend uses JWT tokens stored in HTTP-only cookies for security:

- Login: `POST /api/v1/auth/login`
- Token is automatically included in all API requests
- Token refresh handled automatically
- Automatic redirect to login on 401 errors

## 📡 API Integration

All API calls go through the centralized client in `lib/api.ts`:

- **Auth API**: `authAPI.login()`, `authAPI.register()`, `authAPI.me()`
- **DICOM API**: `dicomAPI.upload()`, `dicomAPI.getMetadata()`
- **AI API**: `aiAPI.analyze()`, `aiAPI.getModels()`
- **Blockchain API**: `blockchainAPI.getHash()`, `blockchainAPI.getAccessLogs()`

## 🎨 UI Components

The project uses a custom UI component library based on ShadCN/UI:

- `Button` - Styled button component
- `Card` - Card container with header/content/footer
- `Input` - Form input field
- All components are fully typed with TypeScript

## 🔒 Security

- JWT tokens stored in secure HTTP-only cookies
- No PHI stored in localStorage
- Content-Security-Policy headers configured
- Automatic token refresh on expiration
- Protected routes with authentication checks

## 🧪 Development

### Adding a New Page

1. Create a new folder in `app/`
2. Add a `page.tsx` file
3. Use the `Navbar` component for navigation
4. Check authentication with `auth.isAuthenticated()`

### Adding a New API Endpoint

1. Add the endpoint function in `lib/api.ts`
2. Use React Query hooks in your component:

```tsx
const { data, isLoading } = useQuery({
  queryKey: ['my-data'],
  queryFn: () => myAPI.getData(),
});
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_COOKIE_NAME` | JWT cookie name | `irmsia_token` |
| `NEXT_PUBLIC_COOKIE_MAX_AGE` | Cookie expiration (seconds) | `86400` |

## 🐛 Troubleshooting

### API Connection Issues

- Verify backend is running on the correct port
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

### Authentication Issues

- Clear cookies and try logging in again
- Verify JWT token is being set correctly
- Check backend authentication endpoint

### Build Errors

- Delete `.next` folder and rebuild
- Clear `node_modules` and reinstall dependencies
- Check TypeScript errors in console

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

## 📄 License

This project is part of the IRMSIA Medical AI platform.

