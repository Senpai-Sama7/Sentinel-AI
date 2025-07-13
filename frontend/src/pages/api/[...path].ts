import { NextApiRequest, NextApiResponse } from 'next';
import httpProxy from 'http-proxy';

// Read the backend URL from environment variables.
// This allows us to easily point to different environments (local, staging, prod).
const ORCHESTRATOR_API_URL = process.env.ORCHESTRATOR_API_URL || 'http://localhost:8000';

const proxy = httpProxy.createProxyServer();

// Disable Next.js's default body parser so we can stream the request body untouched.
export const config = {
  api: {
    bodyParser: false,
  },
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  return new Promise<void>((resolve, reject) => {
    // Rewrite the request URL to remove the `/api` prefix.
    // e.g., a request to `/api/v1/analyze` becomes `/v1/analyze` for the backend.
    req.url = req.url?.replace(/^\/api/, '');

    // Add error handling for the proxy itself.
    proxy.once('error', (err) => {
      console.error('Proxy error:', err);
      res.status(502).send('Bad Gateway'); // 502 is appropriate for a proxy failure
      reject(err);
    });

    // Forward the request to the backend orchestrator service.
    proxy.web(req, res, {
      target: ORCHESTRATOR_API_URL,
      autoRewrite: true, // Rewrites the Host header.
      changeOrigin: true, // Important for proper proxying.
    }, (err) => {
      if (err) {
        // This callback handles errors post-response, but the 'error' event is primary.
        return reject(err);
      }
      resolve();
    });
  });
}