import { useState, FormEvent } from 'react';
import type { NextPage } from 'next';
import Head from 'next/head';
import styles from '@/styles/Home.module.css';

// Type definition for the API response, ensuring type safety.
interface AnalysisResponse {
  answer: string;
  graph_context: string;
  rag_context: string;
}

const Home: NextPage = () => {
  // State management using React Hooks
  const [query, setQuery] = useState<string>('Explain the purpose of the main function.');
  const [filePath, setFilePath] = useState<string>('orchestrator/main.py');
  const [commitHash, setCommitHash] = useState<string>('latest');
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResponse(null);

    try {
      // The API call goes to our own Next.js backend, which proxies the request.
      const res = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath, git_commit_hash: commitHash, query }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'An unknown error occurred on the server.');
      }

      setResponse(data as AnalysisResponse);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Sentinel AI Codec</title>
        <meta name="description" content="An AI-powered codebase analysis tool" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Sentinel AI Codec
        </h1>

        <p className={styles.description}>
          The intelligent interface for understanding complex codebases.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label htmlFor="filePath">File Path</label>
            <input id="filePath" type="text" value={filePath} onChange={(e) => setFilePath(e.target.value)} placeholder="e.g., orchestrator/main.py" required />
          </div>
          <div className={styles.inputGroup}>
            <label htmlFor="query">Your Query</label>
            <input id="query" type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g., What is the purpose of this file?" required />
          </div>
          <button type="submit" disabled={isLoading} className={styles.submitButton}>
            {isLoading ? 'Analyzing...' : 'Analyze Code'}
          </button>
        </form>

        {isLoading && <div className={styles.loader}></div>}
        {error && <p className={styles.error}>Error: {error}</p>}

        {response && (
          <div className={styles.results}>
            <div className={styles.answerSection}>
              <h3>AI Generated Answer</h3>
              <p>{response.answer}</p>
            </div>
            <div className={styles.contextGrid}>
              <div className={styles.contextBox}>
                <h4>Graph Context (from AST)</h4>
                <pre>{response.graph_context}</pre>
              </div>
              <div className={styles.contextBox}>
                <h4>Documentation Context (from RAG)</h4>
                <pre>{response.rag_context}</pre>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;