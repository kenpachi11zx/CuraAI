# CuraAI - Virtual Health Assistant

A production-ready Flask-based AI health assistant that provides medical guidance using Google's Gemini AI.

## 🚀 Production Ready Features

- ✅ **Security**: Environment variables, secure headers, input validation
- ✅ **Error Handling**: Comprehensive logging and graceful error recovery
- ✅ **Monitoring**: Health check endpoint and production logging
- ✅ **Performance**: Gunicorn WSGI server and optimized static files
- ✅ **Deployment**: Ready for Heroku, Railway, DigitalOcean, AWS
- ✅ **API Management**: Message limits and usage control for cost management

## Features

- AI-powered health consultation with medical safety protocols
- Symptom analysis and evidence-based recommendations
- Safe OTC medication suggestions with dosage information
- Professional medical tone and comprehensive disclaimers
- Session-based conversation tracking with context preservation
- Age and gender-specific medical advice
- Comprehensive medication database integration
- **Interactive 3D Background**: Powered by Spline for immersive user experience
- **Message Limit System**: Session-based message counting to manage API costs
- **Real-time Counter**: Visual feedback showing remaining messages per session

## Prerequisites

- Python 3.11+
- Google Gemini API key
- Flask and production dependencies

## Quick Setup

1. **Clone and install**
   ```bash
   git clone <your-repo-url>
   cd CuraAI
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

3. **Run locally**
   ```bash
   python app.py
   ```

## Production Deployment

### Heroku (Recommended)
```bash
# Set environment variables
heroku config:set GEMINI_API_KEY=your_actual_api_key
heroku config:set SECRET_KEY=your_secure_secret_key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main
```

### Other Platforms
- **Railway**: Connect GitHub repo and set environment variables
- **DigitalOcean**: Use App Platform with automatic deployments
- **AWS**: Deploy with Elastic Beanstalk

## Environment Variables

### Required
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Flask secret key for sessions (use strong random key)

### Optional
- `FLASK_ENV`: Set to "production" for deployment
- `PORT`: Port number (auto-set by deployment platforms)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Usage Management

### Message Limits
- **Session Limit**: 7 messages per user session to manage API costs
- **Smart Counting**: Only counts actual consultations, not age/gender questions
- **Visual Feedback**: Real-time counter showing remaining messages
- **Session Reset**: Users can refresh the page to start a new session

### Cost Control Features
- Automatic message counting and limit enforcement
- User-friendly limit reached messages
- Session-based tracking to prevent abuse
- Graceful degradation when limits are reached

## Security & Compliance

- 🔒 **Medical Disclaimers**: Comprehensive legal disclaimers included
- 🔒 **Data Privacy**: No sensitive data stored permanently
- 🔒 **Input Validation**: All user inputs sanitized and validated
- 🔒 **Session Security**: Secure session management with HTTP-only cookies
- 🔒 **HTTPS Enforcement**: Security headers and HTTPS redirects
- 🔒 **API Protection**: Rate limiting and usage controls

## Monitoring & Health Checks

- **Health Endpoint**: `GET /health` for monitoring
- **Logging**: Comprehensive application logging
- **Error Tracking**: Graceful error handling and reporting
- **Performance**: Optimized for production workloads
- **Debug Endpoints**: `/debug-messages` for message count inspection

## Medical Safety Features

- Age and gender validation before medical advice
- Comprehensive medication database with dosages
- Clear disclaimers about AI limitations
- Recommendations for professional medical consultation
- Safety protocols for different age groups

## UI/UX Features

- **Modern Design**: Clean, professional interface with gradient backgrounds
- **3D Interactive Background**: Powered by Spline for immersive experience
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile
- **Chat History**: Persistent conversation management with local storage
- **Quick Actions**: Pre-defined health queries for common symptoms
- **Real-time Typing Indicators**: Visual feedback during AI responses
- **Error Recovery**: Graceful error handling with retry functionality
- **Message Counter**: Visual indicator showing remaining messages per session
- **Testing Mode Notice**: Clear indication when running in testing mode

### Spline 3D Background

The application features an interactive 3D background powered by Spline, creating an immersive and modern user experience:

- **Interactive Orb**: Floating 3D element that responds to user interaction
- **Smooth Animations**: Fluid motion and transitions
- **Performance Optimized**: Lightweight implementation that doesn't impact app performance
- **Cross-platform**: Works on all modern browsers and devices

The 3D background is embedded via iframe from Spline's hosting service, providing a professional and engaging visual element that enhances the medical consultation experience.

## Architecture

```
CuraAI/
├── app.py              # Main Flask application with message limits
├── medicine.py         # Medication database
├── requirements.txt    # Dependencies
├── Procfile           # Heroku deployment
├── runtime.txt        # Python version
├── static/            # CSS, JS, images
├── templates/         # HTML templates
└── logs/             # Production logs (auto-created)
```

## Development

### Local Development
```bash
export FLASK_ENV=development
python app.py
```

### Testing
- Health check: `curl http://localhost:5000/health`
- Chat endpoint: `POST /chat` with JSON body
- Message count: `GET /message-count`
- Debug messages: `GET /debug-messages`

### API Endpoints

- `POST /chat` - Main chat endpoint with message limit enforcement
- `GET /message-count` - Get current message count for user session
- `POST /reset-messages` - Reset message count for testing
- `GET /health` - Health check endpoint
- `GET /debug-messages` - Debug endpoint for message count inspection

## Support

For issues related to:
- **API Limits**: Check message counter and refresh page for new session
- **Deployment**: Ensure all environment variables are set correctly
- **Performance**: Monitor logs and health endpoint
- **Medical Advice**: Always consult healthcare professionals for serious concerns
