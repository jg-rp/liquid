import React from "react";
import Layout from "@theme/Layout";
import ErrorBoundary from "@docusaurus/ErrorBoundary";
import Playground from "../components/Playground";

export default function PlaygroundPage() {
  return (
    <Layout title="Playground" description="Liquid playground">
      <ErrorBoundary
        fallback={({ error, tryAgain }) => (
          <div>
            <p>This component crashed because of error: {error.message}.</p>
            <button onClick={tryAgain}>Try Again!</button>
          </div>
        )}
      >
        <Playground />
      </ErrorBoundary>
    </Layout>
  );
}
