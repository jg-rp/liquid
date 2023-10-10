import React, { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { Allotment } from "allotment";
import "allotment/dist/style.css";
import { usePython } from "react-py";
import Editor from "@monaco-editor/react";
import { useColorMode } from "@docusaurus/theme-common";

import styles from "./styles.module.css";

const main = `\
import json
import sys
from liquid import Environment, CachingFileSystemLoader

try:
    with open("data.json") as fd:
        data = json.load(fd)
except (json.error, FileNotFoundError) as err:
    sys.stdout.write(str(err))
    data = {}

env = Environment(loader=CachingFileSystemLoader("."))

try:
    template = env.get_template("index.liquid")
    print(template.render(**data))
except Exception as err:
    sys.stdout.write(str(err))
    raise
`;

const initData = JSON.stringify(
  { foo: "bar", baz: [1, 2, 3] },
  undefined,
  "  "
);

const initLiquid = `\
{% assign n = 'bob,sue' | split: ',' -%}
{% for y in n %}Hello, {{ y }}!
{% endfor %}`;

function LiquidEditor({ defaultValue, theme, beforeMount, onMount, onChange }) {
  return (
    <Editor
      height="100%"
      language="liquid"
      theme={theme}
      defaultValue={defaultValue}
      beforeMount={beforeMount}
      onMount={onMount}
      onChange={onChange}
      options={{
        codeLens: false,
        minimap: { enabled: false },
        tabSize: 2,
        renderLineHighlight: "none",
        scrollBeyondLastLine: false,
        scrollbar: { alwaysConsumeMouseWheel: false },
        padding: { bottom: 10, top: 10 },
      }}
    />
  );
}

function DataEditor({ defaultValue, theme, onChange }) {
  return (
    <Editor
      height="100%"
      language="json"
      theme={theme}
      defaultValue={defaultValue}
      onChange={onChange}
      options={{
        codeLens: false,
        minimap: { enabled: false },
        tabSize: 2,
        renderLineHighlight: "none",
        scrollBeyondLastLine: false,
        scrollbar: { alwaysConsumeMouseWheel: false },
        padding: { bottom: 10, top: 10 },
      }}
    />
  );
}

function ResultEditor({ result, theme }) {
  return (
    <Editor
      height="100%"
      language="plain"
      theme={theme}
      value={result}
      options={{
        codeLens: false,
        minimap: { enabled: false },
        tabSize: 2,
        renderLineHighlight: "none",
        scrollBeyondLastLine: false,
        scrollbar: { alwaysConsumeMouseWheel: false },
        padding: { bottom: 10, top: 10 },
        wordWrap: "on",
        lineNumbers: "off",
        readOnly: true,
      }}
    />
  );
}

export default function Playground() {
  const { colorMode } = useColorMode();
  const initTheme = colorMode === "light" ? "light" : "vs-dark";

  const {
    runPython,
    stdout,
    stderr,
    isLoading,
    isReady,
    isRunning,
    interruptExecution,
    writeFile,
  } = usePython();

  useEffect(async () => {
    if (!isLoading) {
      writeFile("index.liquid", initLiquid);
      writeFile("data.json", initData);
    }
  }, [isLoading]);

  function render() {
    if (isRunning) {
      interruptExecution();
    }
    if (isReady) {
      runPython(main);
    }
  }

  let timer;
  const timerInterval = 1000;

  function _onLiquidChange(value) {
    writeFile("index.liquid", value);
    render();
  }
  function onLiquidChange(value) {
    clearTimeout(timer);
    timer = setTimeout(() => _onLiquidChange(value), timerInterval);
  }

  function _onDataChange(value) {
    writeFile("data.json", value);
    render();
  }

  function onDataChange(value) {
    clearTimeout(timer);
    timer = setTimeout(() => _onDataChange(value), timerInterval);
  }

  return (
    <div className={clsx("container", styles.container)}>
      <div className="row">
        <div className="col">
          <h1 className={styles.heading}>Python Liquid Playground</h1>
          <hr className={styles.headingRule} />
        </div>
      </div>
      <div className="row">
        <div className={clsx("col", styles.editorCol)}>
          <Allotment className={styles.splitView} minSize={200}>
            <Allotment.Pane>
              <Allotment vertical>
                <Allotment.Pane snap>
                  <LiquidEditor
                    defaultValue={initLiquid}
                    theme={initTheme}
                    onChange={onLiquidChange}
                  />
                </Allotment.Pane>
                <Allotment.Pane snap>
                  <DataEditor
                    defaultValue={initData}
                    theme={initTheme}
                    onChange={onDataChange}
                  />
                </Allotment.Pane>
              </Allotment>
            </Allotment.Pane>

            <Allotment.Pane>
              <ResultEditor result={stdout} theme={initTheme} />
            </Allotment.Pane>
          </Allotment>
        </div>
      </div>
      <div className="row">
        <div className={clsx("col", styles.infoCol)}>
          <p>
            JSON data is on the left and results are on the right.
            <br />
            Drag out the extra pane on the right to see a normalized path for
            each result.
            <br />
            Results are updated automatically after one second of inactivity.
          </p>
        </div>
      </div>
    </div>
  );
}
