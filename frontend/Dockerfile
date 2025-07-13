# frontend/Dockerfile

# --- Stage 1: Build Stage ---
# Use a specific Node.js version for reproducible builds.
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and lock files
COPY package*.json ./

# Install all dependencies, including devDependencies for building
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the Next.js application for production
RUN npm run build

# --- Stage 2: Production Stage ---
# Use a lean Node.js image for the final container
FROM node:18-alpine

WORKDIR /app

# Create a non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy built assets from the builder stage
# The .next/standalone directory is optimized for production deployment
COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/public ./public

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# The command to run the application
# This uses the optimized Node.js server provided by Next.js
CMD ["node", "server.js"]