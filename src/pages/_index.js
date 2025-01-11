import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import HomepageFeatures from "@site/src/components/HomepageFeatures";

import styles from "./index.module.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroInner}>
          <h1 className={clsx("margin-bottom--lg", styles.heroProjectTagline)}>
            <span className={styles.heroTitleTextHtml}>
              A <b>flexible</b>, non-evaluating template engine for end users.
            </span>
          </h1>
          <div className={styles.indexCtas}>
            <Link
              className="button button--secondary button--lg"
              to="/introduction/getting-started"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
