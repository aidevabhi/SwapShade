# SwapShade

A Django application for image colorization.

## Deployment on Render

This project is configured for easy deployment on Render's free tier using Docker.

### Prerequisites

1. A [Render](https://render.com/) account
2. Git repository with your project code

### Deployment Steps

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Log in to your Render account
3. Click on the "New +" button and select "Blueprint"
4. Connect your Git repository
5. Render will automatically detect the `render.yaml` file and configure the service
6. Click "Apply" to start the deployment

### Manual Deployment (Alternative)

If you prefer to deploy manually:

1. Log in to your Render account
2. Click on the "New +" button and select "Web Service"
3. Connect your Git repository
4. Select "Docker" as the runtime
5. Choose the "Free" plan
6. Set the following environment variables:
   - `DJANGO_SECRET_KEY`: Generate a secure random key
   - `DJANGO_ALLOWED_HOSTS`: `.onrender.com,localhost,127.0.0.1`
   - `DEBUG`: `False`
7. Click "Create Web Service"

## Local Development with Docker

To run the application locally using Docker:

```bash
# Build the Docker image
docker build -t swapshade .

# Run the container
docker run -p 8000:8000 swapshade
```

Then visit http://localhost:8000 in your browser.

## Project Structure

- `colorizer_app/`: Main Django application
- `image_colorizer/`: Django project settings
- `media/`: User uploaded and processed images
- `Dockerfile`: Docker configuration
- `render.yaml`: Render deployment configuration