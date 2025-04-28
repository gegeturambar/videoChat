# Gmail Flow

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An intelligent Gmail account manager built with the Motia framework. This workflow monitors incoming emails, analyzes them using Hugging Face's AI models, and automatically responds based on the content analysis.

<p align="center">
  <img src="https://img.shields.io/badge/Motia-Framework-blue" alt="Motia Framework"/>
  <img src="https://img.shields.io/badge/Gmail-API-red" alt="Gmail API"/>
  <img src="https://img.shields.io/badge/HuggingFace-AI-yellow" alt="HuggingFace AI"/>
  <img src="https://img.shields.io/badge/Discord-API-7289DA" alt="Discord API"/>
</p>

## ✨ Features

- 📊 Smart email classification by category (work, personal, social, promotion, spam, update)
- 🚨 Urgency detection (high, medium, low) with prioritization
- 💬 Intelligent automated responses based on email context
- 🏷️ Automatic email organization (labeling, archiving)
- 📈 Daily summary reports via Discord
- 🔒 Secure Gmail API integration with OAuth2 authentication flow
- ⚡ Real-time email monitoring with webhook notifications

## 📋 Prerequisites

- **Node.js** (v18+)
- **Python** (v3.8+)
- **Gmail API credentials** (client_id and client_secret)
- **Google Cloud project** with Pub/Sub API enabled
- **Hugging Face API token**
- **Discord webhook URL** (for daily summaries)

## 🚀 Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/gmail-flow.git
   cd gmail-flow
   ```

2. **Run the installation script**
   ```bash
   ./setup.sh
   ```
   This script will:
   - Check and install prerequisites (Python 3, pnpm)
   - Create and configure Python virtual environment
   - Install Python dependencies
   - Install Node.js dependencies
   - Set up the .env file from .env.example

3. **Start the development server**
   ```bash
   source python_modules/bin/activate  # Activate Python virtual environment
   pnpm run dev
   ```

4. **Open the Motia Workbench**
   
   Navigate to [http://localhost:3000](http://localhost:3000) to access the workflow UI.

## 🔧 Detailed Setup

### Setting up Google Cloud Project and Gmail API

Before you can use the Gmail Account Manager, you need to set up a Google Cloud project with the Gmail API and Pub/Sub:

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click on "New Project" and follow the steps to create a new project
   - Note your project ID for later use

2. **Enable the Gmail API**:
   - In your project, go to "APIs & Services" > "Library"
   - Search for "Gmail API" and click on it
   - Click "Enable"

3. **Enable the Pub/Sub API**:
   - In your project, go to "APIs & Services" > "Library"
   - Search for "Cloud Pub/Sub API" and click on it
   - Click "Enable"

4. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Set the application type to "Desktop app"
   - Click "Create"
   - Note your Client ID and Client Secret for your `.env` file:
     ```
     GOOGLE_CLIENT_ID=your_client_id
     GOOGLE_CLIENT_SECRET=your_client_secret
     ```

### Setting up Google Pub/Sub for Gmail Notifications

To enable real-time email notifications, you need to set up a Google Cloud Pub/Sub topic and subscription:

1. **Create a Pub/Sub Topic**:
   - In your Google Cloud Console, go to "Pub/Sub" > "Topics"
   - Click "Create Topic"
   - Name your topic (e.g., `gmail-notifications`)
   - Add the service account `gmail-api-push@system.gserviceaccount.com` as a Topic Publisher to allow Gmail to publish notifications
   - Click "Create"
   - Note the full topic name (usually `projects/your-project-id/topics/gmail-notifications`) for your `.env` file:
     ```
     GOOGLE_PUBSUB_TOPIC=projects/your-project-id/topics/gmail-notifications
     ```

2. **Create a Pub/Sub Subscription**:
   - Once your topic is created, click "Create Subscription"
   - Name your subscription (e.g., `gmail-notifications-push`)
   - Set the Delivery Type to "Push"
   - Set the Endpoint URL to your webhook URL (e.g., `https://your-domain.com/api/gmail-webhook`)
     - For local development, you'll need to use a tool like ngrok to expose your local server
   - Click "Create"

3. **Set up Domain Verification** (if needed):
   - If you're using a custom domain for your webhook endpoint, you may need to verify domain ownership
   - Follow the instructions in Google Cloud Console for domain verification

### Gmail API Authentication

This project includes a complete OAuth2 authentication flow for the Gmail API:

1. Start the development server: `pnpm dev`
2. Navigate to the authentication workflow in the Motia Workbench
3. The workflow will generate an authorization URL
4. Open the URL in your browser and authorize the application
5. The application will receive and store your authentication tokens

### Discord Webhook Configuration

To receive daily email summaries in Discord, follow these steps to set up a webhook:

1. **Create a Discord Server** (skip if you already have one):
   - Open Discord and click the "+" icon on the left sidebar
   - Select "Create My Own" and follow the setup wizard

2. **Create a Channel for Notifications**:
   - Right-click on your server name and select "Server Settings"
   - Go to "Channels" and click "Create Channel"
   - Name it (e.g., "email-summaries") and click "Create"

3. **Create a Webhook**:
   - Right-click on your new channel and select "Edit Channel"
   - Go to "Integrations" tab
   - Click "Create Webhook"
   - Give it a name (e.g., "Gmail Summary Bot")
   - Optionally, customize the avatar
   - Click "Copy Webhook URL"

4. **Add Webhook URL to Environment Variables**:
   - Open your `.env` file
   - Add or update the Discord webhook URL:
     ```
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
     ```

5. **Test the Webhook**:
   - You can test if your webhook is working correctly with this curl command:
     ```bash
     curl -X POST -H "Content-Type: application/json" \
     -d '{"content": "Testing Gmail Account Manager webhook"}' \
     https://discord.com/api/webhooks/your-webhook-url
     ```
   - You should see the message appear in your Discord channel

### Hugging Face Setup

1. **Create a Hugging Face Account**:
   - Sign up at [Hugging Face](https://huggingface.co/join)

2. **Generate an API Token**:
   - Go to your [Hugging Face account settings](https://huggingface.co/settings/tokens)
   - Create a new API token
   - Copy the token to your `.env` file:
     ```
     HUGGINGFACE_API_TOKEN=your_api_token
     ```

## 🌊 Workflow Architecture

The Gmail Account Manager workflow consists of the following steps:

### 1. Gmail Authentication (Multi-Step Flow)
- **Files**: 
  - `steps/gmail-get-auth-url.step.ts`: Generates OAuth2 authorization URL
  - `steps/gmail-auth.step.ts`: Handles authorization code exchange
  - `steps/gmail-token-status.step.ts`: Checks token validity and refreshes if needed

### 2. Gmail Webhook (API Step)
- **File**: `steps/gmail-webhook.step.ts`
- **Purpose**: Receives notifications from Gmail when new emails arrive
- **Emits**: `gmail.new_email` event with message details
- **Endpoint**: `POST /api/gmail-webhook`

### 3. Gmail Watch (API Step)
- **File**: `steps/gmail-watch.step.ts`
- **Purpose**: Sets up push notifications for the Gmail account
- **Endpoint**: `GET /api/watch`

### 4. Fetch Email (Event Step)
- **File**: `steps/fetch-email.step.ts`
- **Purpose**: Retrieves the full email content from Gmail API
- **Subscribes to**: `gmail.email.received`
- **Emits**: `gmail.email.fetched` with complete email data
- **Key Functions**: Authenticates with Gmail API, fetches message content, parses attachments

### 5. Analyze Email (Event Step)
- **File**: `steps/analyze-email.step.py`
- **Purpose**: Uses Hugging Face models to analyze email content
- **Subscribes to**: `gmail.email.fetched`
- **Emits**: `gmail.email.analyzed` with analysis results
- **Analysis Performed**: 
  - Category classification
  - Urgency detection
  - Sentiment analysis
  - Key information extraction

### 6. Organize Email (Event Step)
- **File**: `steps/organize-email.step.ts`
- **Purpose**: Applies labels and organization based on analysis
- **Subscribes to**: `gmail.email.analyzed`
- **Emits**: `[gmail.email.organized, gmail.email.archived]`
- **Actions**: Creates/applies labels, archives certain emails, marks importance

### 7. Auto-Respond to Email (Event Step)
- **File**: `steps/auto-responder.step.ts`
- **Purpose**: Generates and sends appropriate responses for certain emails
- **Subscribes to**: `gmail.email.analyzed`
- **Emits**: `gmail.email.responded`
- **Features**: 
  - Template selection based on email context
  - Personalization of responses
  - Auto-reply for urgent messages
  - Follow-up scheduling

### 8. Daily Summary (Cron Step)
- **File**: `steps/daily-summary.step.ts`
- **Purpose**: Compiles and sends daily email activity summary
- **Schedule**: Runs daily at 6:00 PM
- **Emits**: `gmail.summary.sent`
- **Delivery**: Sends report to Discord via webhook

## 🧪 Testing

### Simulating Gmail Webhook

You can simulate a Gmail webhook event with this curl command:

```bash
curl -X POST http://localhost:3000/api/gmail-webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"data":"eyJlbWFpbEFkZHJlc3MiOiJhbmRlcnNvbm9mbEBnbWFpbC5jb20iLCJoaXN0b3J5SWQiOjI4NTUyNjgyfQ==","messageId":"13594882889976308","publishTime":"2025-03-10T23:30:09.266Z"},"subscription":"projects/xxxx/subscriptions/xxxxx"}'
```

### Testing the Workflow

1. **Manual Email Testing**:
   - Send an email to your Gmail account while the workflow is running
   - Check the Motia Workbench logs to see the workflow in action

2. **Testing Individual Steps**:
   - Use the Motia Workbench to test individual steps
   - For example, to test the auto-responder:
     ```bash
     npx motia emit --topic gmail.email.analyzed --message '{"subject": "Urgent Request", "text": "This is an urgent matter that needs your attention", "analysis": {"category": "work", "urgency": "high", "sentiment": "neutral"}}'
     ```

## 📁 Project Structure

- `steps/` - Contains all workflow steps
  - `gmail-get-auth-url.step.ts` - Generates OAuth2 URL
  - `gmail-auth.step.ts` - Handles OAuth2 flow
  - `gmail-token-status.step.ts` - Manages token refresh
  - `gmail-webhook.step.ts` - Webhook endpoint for Gmail notifications
  - `gmail-watch.step.ts` - Sets up Gmail push notifications
  - `fetch-email.step.ts` - Fetches email content from Gmail API
  - `analyze-email.step.py` - Python step for email analysis using Hugging Face
  - `organize-email.step.ts` - Organizes emails (labels, archives)
  - `auto-responder.step.ts` - Generates appropriate responses
  - `daily-summary.step.ts` - Sends daily summary to Discord
- `services/` - Shared service modules
- `config/` - Configuration files
- `.motia/` - Motia framework configuration

## 📦 Dependencies

### Node.js Dependencies
- **@motiadev/core**, **@motiadev/workbench**, **motia**: Motia framework
- **googleapis**, **google-auth-library**: Google API integration
- **gmail-api-parse-message-ts**: Gmail message parsing
- **axios**: HTTP client
- **zod**: Schema validation
- **react**: UI components

### Python Dependencies
- **transformers**, **torch**: Machine learning models
- **scikit-learn**, **numpy**, **pandas**: Data processing
- **huggingface_hub**: Access to Hugging Face models
- **python-dotenv**: Environment variable loading

## 🛠️ Troubleshooting

- **Python Module Errors**: Ensure you've installed all required Python packages with `pip install -r requirements.txt`
- **Authentication Errors**: Verify your API credentials and follow the authentication flow
- **Webhook Issues**: Make sure the webhook endpoint is publicly accessible or properly configured for testing
- **Token Refresh Errors**: Check that your OAuth tokens are valid and that the refresh flow is working properly
- **Pub/Sub Not Working**: Verify that your Pub/Sub topic and subscription are properly configured and that your service account has the necessary permissions

## 📝 Environment Variables

Create a `.env` file with the following variables:

```
# Google API Configuration
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_PUBSUB_TOPIC=projects/your-project-id/topics/gmail-notifications

# HuggingFace Configuration
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Discord Integration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url

# Auto-Responder Configuration
AUTO_RESPONDER_NAME=Your Name
AUTO_RESPONDER_EMAIL=your-email@example.com
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [Motia Framework Documentation](https://motiadev.com)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Hugging Face Documentation](https://huggingface.co/docs)
- [Discord Webhook Documentation](https://discord.com/developers/docs/resources/webhook)

## 🐳 Docker

The application can be run using Docker for a consistent development and production environment.

### Development with Docker

1. **Build the development image**
   ```bash
   docker build -t gmail-flow:dev -f Dockerfile.dev .
   ```

2. **Run the development container**
   ```bash
   docker run -it --rm \
     -p 3000:3000 \
     -v $(pwd):/app \
     -v /app/node_modules \
     -v /app/python_modules \
     --env-file .env \
     gmail-flow:dev
   ```

### Production with Docker

1. **Build the production image**
   ```bash
   docker build -t gmail-flow:prod .
   ```

2. **Run the production container**
   ```bash
   docker run -d \
     -p 3000:3000 \
     --env-file .env \
     gmail-flow:prod
   ```

### Docker Compose

For easier development, you can use Docker Compose:

1. **Start the services**
   ```bash
   docker-compose up
   ```

2. **Stop the services**
   ```bash
   docker-compose down
   ```

The application will be available at [http://localhost:3000](http://localhost:3000). 