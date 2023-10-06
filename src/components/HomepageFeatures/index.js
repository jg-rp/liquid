import React from "react";
import clsx from "clsx";
import styles from "./styles.module.css";
import Link from "@docusaurus/Link";

const FeatureList = [
  {
    title: "Compatible",
    Svg: require("@site/static/img/undraw_code_typing_re_p8b9.svg").default,
    description: (
      <>
        Python Liquid strives to be 100% compatible with the reference
        implementation of Liquid, written in Ruby. See the{" "}
        <Link to="./known_issues"> known issues page</Link> for a description of
        differences between Python Liquid and Ruby Liquid.
      </>
    ),
  },
  {
    title: "Safe",
    Svg: require("@site/static/img/undraw_security_re_a2rk.svg").default,
    description: (
      <>
        Designed for situations where template authors are untrusted, Python
        Liquid is non{" "}
        <Link to="https://docs.python.org/3/library/functions.html#eval">
          evaluating
        </Link>
        , it guards against mutation of{" "}
        <Link to="/introduction/render-context#environment-globals">
          shared template data
        </Link>
        , and will never expose arbitrary properties or methods of{" "}
        <Link to="/introduction/render-context"> render context</Link> objects.
      </>
    ),
  },
  {
    title: "Flexible",
    Svg: require("@site/static/img/undraw_code_review_re_woeb.svg").default,
    description: (
      <>
        Add to, remove or replace built-in <Link to="/language/tags">tags</Link>{" "}
        and <Link to="/language/filters">filters</Link> to suit your needs.
        Define custom template <Link to="/guides/custom-loaders">loaders</Link>{" "}
        to read template source text from a database, a remote file system, or
        parse front matter data.
      </>
    ),
  },
  {
    title: "Django and Flask",
    Svg: require("@site/static/img/undraw_web_development_0l6v.svg").default,
    description: (
      <>
        Integrate with <Link to="https://www.djangoproject.com/">Django</Link>{" "}
        or <Link to="https://flask.palletsprojects.com/">Flask</Link> using the{" "}
        <Link to="/guides/django-liquid">Django template backend</Link> for
        Python Liquid or the{" "}
        <Link to="/guides/flask-liquid">Flask extension</Link> for Python
        Liquid.
      </>
    ),
  },
  {
    title: "Asynchronous",
    Svg: require("@site/static/img/undraw_speed_test_re_pe1f.svg").default,
    description: (
      <>
        Optionally load templates and render context data asynchronously with
        Python Liquid's <Link to="/introduction/async-support">async API</Link>,
        built with{" "}
        <Link to="https://docs.python.org/3/library/asyncio.html">asyncio</Link>
        .
      </>
    ),
  },
];

function Feature({ feature, className }) {
  return (
    <div className={clsx("col", className)}>
      <div className="text--center">
        <feature.Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{feature.title}</h3>
        <p>{feature.description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  const firstRow = FeatureList.slice(0, 3);
  const secondRow = FeatureList.slice(3);

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row margin-bottom--lg">
          {firstRow.map((feature, idx) => (
            <Feature key={idx} feature={feature} />
          ))}
        </div>
        <div className="row">
          {secondRow.map((feature, idx) => (
            <Feature
              key={idx}
              feature={feature}
              className={clsx("col--4", idx === 0 && "col--offset-2")}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
