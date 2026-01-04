# 02 - TECHNOLOGY STACK

## Stack Overview

Kiosk POS menggunakan modern tech stack dengan fokus pada **performance**, **developer experience**, dan **scalability**.

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND STACK                           │
├─────────────────────────────────────────────────────────────┤
│  SvelteKit 2.0  │  TailwindCSS 3.x  │  Vite 5.x           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     BACKEND STACK                            │
├─────────────────────────────────────────────────────────────┤
│  Django 4.2  │  DRF 3.14  │  Python 3.11  │  PostgreSQL 15 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE STACK                        │
├─────────────────────────────────────────────────────────────┤
│  Docker  │  Docker Compose  │  Nginx  │  Node.js (Kitchen) │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Technologies

### Core Framework

#### SvelteKit 2.0
**Website**: https://kit.svelte.dev  
**Version**: `^2.0.0`

**Why Chosen**:
- ✅ **Smallest Bundle**: ~10KB compared to React (~40KB) or Vue (~30KB)
- ✅ **Reactive by Default**: No useState/useEffect complexity
- ✅ **Compile-Time Optimization**: Converts to vanilla JS
- ✅ **SSR Built-in**: Server-side rendering out of the box
- ✅ **File-Based Routing**: Intuitive project structure

**Key Features Used**:
```javascript
// Reactive declarations
$: totalPrice = items.reduce((sum, item) => sum + item.price, 0);

// Stores for global state
import { writable } from 'svelte/store';
export const cart = writable([]);

// Server-side data loading
export async function load({ params, fetch }) {
    const response = await fetch(`/api/products/${params.id}`);
    return { product: await response.json() };
}
```

**Use Cases in Project**:
- Cashier terminal UI
- Admin panel
- Real-time cart updates
- Product catalog browsing

---

#### Vite 5.x
**Website**: https://vitejs.dev  
**Version**: `^5.0.0`

**Why Chosen**:
- ⚡ **Lightning Fast**: HMR (Hot Module Replacement) in milliseconds
- 📦 **Optimized Build**: Tree-shaking and code-splitting
- 🔧 **Plugin Ecosystem**: Rich plugin support
- 🎯 **Native ESM**: No bundling during dev

**Configuration**:
```javascript
// vite.config.js
export default defineConfig({
    plugins: [sveltekit()],
    server: {
        port: 5173,
        host: '0.0.0.0',
        proxy: {
            '/api': {
                target: 'http://backend:8000',
                changeOrigin: true
            }
        }
    }
});
```

---

### Styling

#### TailwindCSS 3.x
**Website**: https://tailwindcss.com  
**Version**: `^3.4.0`

**Why Chosen**:
- 🎨 **Utility-First**: Fast development with utility classes
- 📱 **Responsive**: Built-in breakpoints
- 🌗 **Dark Mode**: Easy theme switching
- 🔧 **Customizable**: Extend with custom colors/spacing
- 📦 **Small Bundle**: Unused classes purged automatically

**Custom Configuration**:
```javascript
// tailwind.config.js
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
        extend: {
            colors: {
                primary: '#FF6B35',
                secondary: '#F7931E',
                accent: '#00B4D8',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        }
    },
    plugins: []
};
```

**Usage Examples**:
```svelte
<button class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 
               transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
    Add to Cart
</button>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Product cards -->
</div>
```

---

### State Management

#### Svelte Stores
**Built-in**: Part of Svelte core

**Types Used**:
1. **Writable Store**: Mutable state
```javascript
import { writable } from 'svelte/store';
export const cart = writable([]);
cart.update(items => [...items, newItem]);
```

2. **Derived Store**: Computed values
```javascript
import { derived } from 'svelte/store';
export const cartTotal = derived(cart, $cart => 
    $cart.reduce((sum, item) => sum + item.price, 0)
);
```

3. **Readable Store**: Read-only state
```javascript
import { readable } from 'svelte/store';
export const time = readable(new Date(), set => {
    const interval = setInterval(() => set(new Date()), 1000);
    return () => clearInterval(interval);
});
```

**Stores in Project**:
- `auth.js`: User authentication state
- `cart.js`: Shopping cart
- `tenant.js`: Current tenant context
- `outlet.js`: Current outlet context

---

### API Communication

#### Native Fetch API
**Why**: Built-in, no extra dependencies

**Wrapper Functions**:
```javascript
// lib/api/client.js
const API_BASE = 'http://localhost:8000/api';

export async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
            ...options.headers
        }
    });
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
}
```

---

## Backend Technologies

### Core Framework

#### Django 4.2 LTS
**Website**: https://www.djangoproject.com  
**Version**: `4.2.x`

**Why Chosen**:
- 🏗️ **Batteries Included**: ORM, Admin, Authentication built-in
- 🔒 **Security**: CSRF, XSS, SQL injection protection by default
- 📚 **Mature Ecosystem**: Thousands of packages
- 🎯 **LTS Support**: Long-term support (until April 2026)
- 🐍 **Python**: Easy to read, write, and maintain

**Key Features Used**:
```python
# ORM with relationships
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='OrderItem')
    
    class Meta:
        ordering = ['-created_at']

# Admin interface (auto-generated)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']

# Middleware for tenant isolation
class TenantMiddleware:
    def __call__(self, request):
        # Extract and set tenant
        pass
```

---

#### Django REST Framework 3.14
**Website**: https://www.django-rest-framework.org  
**Version**: `3.14.x`

**Why Chosen**:
- 🌐 **RESTful API**: Best practices out of the box
- 📄 **Serialization**: Easy model-to-JSON conversion
- 🔐 **Authentication**: JWT, Token, Session support
- 📖 **Browsable API**: Interactive API documentation
- 🔍 **Filtering & Pagination**: Built-in support

**Core Components**:

**1. Serializers**:
```python
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name', 'image']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
```

**2. ViewSets**:
```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description']
```

**3. Routers**:
```python
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'promotions', PromotionViewSet)
```

---

#### SimpleJWT
**Package**: `djangorestframework-simplejwt`  
**Version**: `^5.3.0`

**Why Chosen**:
- 🎫 **Token-Based**: Stateless authentication
- 🔄 **Refresh Tokens**: Long-lived sessions
- ⚡ **Fast**: No database lookup per request
- 📱 **Mobile-Friendly**: Easy to implement in mobile apps

**Configuration**:
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

**Usage**:
```python
# views.py
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Add custom claims
        response.data['role'] = request.user.role
        response.data['tenant_id'] = request.user.tenant_id
        return response
```

---

### Database

#### PostgreSQL 15
**Website**: https://www.postgresql.org  
**Version**: `15.x`

**Why Chosen**:
- 🔒 **ACID Compliant**: Data integrity guaranteed
- 📊 **Advanced Features**: JSON support, full-text search, window functions
- ⚡ **Performance**: Fast queries, excellent indexing
- 🔧 **Extensible**: PostGIS, pg_trgm, and more
- 🆓 **Open Source**: No licensing costs

**Configuration**:
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='kiosk_pos'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}
```

**Indexes Used**:
```python
class Product(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['tenant', 'is_available']),
            models.Index(fields=['name']),  # For search
        ]
```

**JSON Field Usage**:
```python
class Order(models.Model):
    metadata = models.JSONField(default=dict, blank=True)
    # Store: {"notes": "Extra spicy", "special_requests": [...]}
```

---

### Python Packages

#### Core Dependencies
```txt
# requirements.txt
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.0
django-filter==23.3
drf-spectacular==0.27.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
django-environ==0.11.2
Pillow==10.1.0
celery==5.3.4
django-celery-beat==2.5.0
redis==5.0.1
```

#### django-cors-headers
**Purpose**: Handle CORS for frontend-backend communication
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Cashier
    "http://localhost:5175",  # Admin
]
CORS_ALLOW_CREDENTIALS = True
```

#### django-filter
**Purpose**: Advanced filtering for API endpoints
```python
class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['category', 'is_available']
```

#### drf-spectacular
**Purpose**: OpenAPI 3.0 documentation
```python
# Generates: /api/schema/swagger-ui/
SPECTACULAR_SETTINGS = {
    'TITLE': 'Kiosk POS API',
    'DESCRIPTION': 'Multi-Tenant F&B POS System API',
    'VERSION': '2.0.0',
}
```

#### Pillow
**Purpose**: Image processing (product images, logos)
```python
from PIL import Image

def resize_product_image(image_path):
    img = Image.open(image_path)
    img.thumbnail((800, 800))
    img.save(image_path, optimize=True, quality=85)
```

---

## Infrastructure Technologies

### Containerization

#### Docker
**Website**: https://www.docker.com  
**Version**: `24.x`

**Why Chosen**:
- 📦 **Consistency**: Same environment everywhere
- 🚀 **Fast Deployment**: Build once, run anywhere
- 🔧 **Easy Setup**: One command to start all services
- 🎯 **Isolation**: Services don't interfere with each other

**Dockerfile Example (Backend)**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

#### Docker Compose
**Version**: `2.x`

**Purpose**: Orchestrate multiple containers

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: kiosk_pos
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/kiosk_pos

  frontend:
    build: ./frontend
    command: npm run dev -- --host 0.0.0.0
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend

  admin:
    build: ./admin
    command: npm run dev -- --host 0.0.0.0
    volumes:
      - ./admin:/app
      - /app/node_modules
    ports:
      - "5175:5175"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
      - admin

volumes:
  postgres_data:
```

**Commands**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart specific service
docker-compose restart backend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

---

### Web Server

#### Nginx
**Website**: https://nginx.org  
**Version**: `alpine` (lightweight)

**Why Chosen**:
- ⚡ **Fast**: High performance reverse proxy
- 📁 **Static Files**: Efficient static file serving
- 🔄 **Load Balancing**: Built-in load balancer
- 🔒 **SSL**: HTTPS termination

**Configuration**:
```nginx
# nginx/nginx.conf
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:5173;
}

upstream admin {
    server admin:5175;
}

server {
    listen 80;
    
    # API requests
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Admin panel
    location /admin-panel/ {
        proxy_pass http://admin/;
        proxy_set_header Host $host;
    }
    
    # Cashier terminal (default)
    location / {
        proxy_pass http://frontend/;
        proxy_set_header Host $host;
    }
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

---

### Real-Time Communication

#### Node.js Kitchen Sync Server
**Version**: Node.js 18.x  
**Purpose**: WebSocket server for real-time kitchen updates

**Technology**: Socket.IO
```javascript
// kitchen-sync-server/server.js
const io = require('socket.io')(3001, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Handle kitchen display connections
io.on('connection', (socket) => {
    console.log('Kitchen display connected:', socket.id);
    
    // Subscribe to outlet-specific orders
    socket.on('subscribe_outlet', (outletId) => {
        socket.join(`outlet_${outletId}`);
    });
    
    // Broadcast new order to outlet
    socket.on('new_order', (order) => {
        io.to(`outlet_${order.outlet_id}`).emit('order_created', order);
    });
    
    // Update order status
    socket.on('update_status', (update) => {
        io.to(`outlet_${update.outlet_id}`).emit('order_updated', update);
    });
});
```

**Client (Kitchen Display)**:
```javascript
import io from 'socket.io-client';

const socket = io('ws://localhost:3001');

socket.on('connect', () => {
    socket.emit('subscribe_outlet', currentOutletId);
});

socket.on('order_created', (order) => {
    addOrderToDisplay(order);
    playNotificationSound();
});
```

---

## Development Tools

### Code Quality

#### Linters & Formatters
```json
// package.json (Frontend)
{
  "devDependencies": {
    "eslint": "^8.55.0",
    "eslint-plugin-svelte": "^2.35.1",
    "prettier": "^3.1.1",
    "prettier-plugin-svelte": "^3.1.2"
  }
}
```

```python
# Backend - requirements-dev.txt
black==23.12.0        # Code formatter
flake8==6.1.0         # Linter
isort==5.13.2         # Import sorter
pylint==3.0.3         # Code analyzer
pytest==7.4.3         # Testing
pytest-django==4.7.0  # Django testing
```

---

### Environment Management

#### Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Node Package Manager
```bash
npm install          # Install dependencies
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
```

---

## Version Compatibility Matrix

| Component | Version | Compatible With |
|-----------|---------|----------------|
| Python | 3.11+ | Django 4.2 |
| Django | 4.2.x LTS | DRF 3.14 |
| PostgreSQL | 15.x | Django 4.2 |
| Node.js | 18.x LTS | SvelteKit 2.0 |
| npm | 9.x+ | Node 18 |
| Docker | 24.x | Docker Compose 2.x |

---

## Performance Benchmarks

### Frontend Bundle Size
```
Cashier Terminal:
- JS Bundle: ~120 KB (gzipped)
- CSS: ~15 KB (gzipped)
- Total: ~135 KB

Admin Panel:
- JS Bundle: ~180 KB (gzipped)
- CSS: ~20 KB (gzipped)
- Total: ~200 KB
```

### API Response Times
```
GET /api/products/        →  ~50ms (100 products)
POST /api/orders/         →  ~120ms (create order)
GET /api/orders/?page=1   →  ~80ms (paginated)
WebSocket latency         →  ~30ms (kitchen sync)
```

---

## Monitoring & Logging (Planned)

### Application Monitoring
- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **Datadog**: Infrastructure monitoring

### Logging
```python
# Django logging configuration
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## Security Tools

### HTTPS/SSL (Production)
- Let's Encrypt certificates
- Auto-renewal with Certbot

### Secrets Management
```bash
# .env file (never commit!)
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-jwt-secret
```

### Security Headers (Nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

---

**Last Updated**: January 4, 2026  
**Version**: 2.0  
**Tech Stack Review**: Scheduled for Q2 2026
