import React, { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { Allotment } from "allotment";
import "allotment/dist/style.css";
import { usePython } from "react-py";
import Editor from "@monaco-editor/react";
import { useColorMode } from "@docusaurus/theme-common";
import Link from "@docusaurus/Link";

import { Tab } from "@headlessui/react";
import { DocumentIcon } from "@heroicons/react/24/solid";

import Loader from "../Loader";
import styles from "./styles.module.css";

const mainCode = `\
import json
import sys
import liquid
from liquid import Environment, FileExtensionLoader
from liquid.extra import add_tags_and_filters

with open("data.json") as fd:
    data = json.load(fd)

data["__version__"] = liquid.__version__

env = Environment(loader=FileExtensionLoader("."))
add_tags_and_filters(env)
template = env.get_template("index.liquid")
print(template.render(**data))`;

const initData = JSON.stringify(
  { foo: "bar", baz: [1, 2, 3] },
  undefined,
  "  "
);

const indexLiquid = `\
Python Liquid version {{ __version__ }}

{%- assign names = 'bob,sue' | split: ',' %}

{% for name in names %}
  {%- include 'snippet' %}
{% endfor %}

{% for n in baz %}
  {{- n }} * 2 == {{ n | times: 2 }}
{% endfor %}`;

const snippetLiquid = "Hello, {{ name }}!";

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
      loading=""
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
      loading=""
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

function ResultEditor({ result, theme, onMount }) {
  return (
    <Editor
      height="100%"
      language="html"
      theme={theme}
      value={result}
      onMount={onMount}
      loading=""
      options={{
        codeLens: false,
        minimap: { enabled: false },
        tabSize: 2,
        renderLineHighlight: "none",
        scrollBeyondLastLine: false,
        scrollbar: { alwaysConsumeMouseWheel: false },
        padding: { bottom: 10, top: 10 },
        wordWrap: "off",
        readOnly: true,
      }}
    />
  );
}

function RenderButton({ onClick, disabled }) {
  return (
    <div className="absolute right-6 top-4 z-10">
      <button
        className={clsx(
          "flex h-12 w-12 items-center justify-center rounded-full border-none bg-lime-300 text-lime-700 shadow",
          !disabled
            ? "opacity-75 hover:cursor-pointer hover:bg-lime-500 hover:text-lime-900 hover:opacity-100"
            : "opacity-50 hover:cursor-not-allowed"
        )}
        type="button"
        onClick={onClick}
        disabled={disabled}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          viewBox="0 0 16 16"
          className="bi bi-play-fil h-8 w-8"
          aria-hidden="true"
        >
          <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z" />
        </svg>
      </button>
    </div>
  );
}

export default function Playground() {
  const [index, setIndex] = useState(indexLiquid);
  const [snippet, setSnippet] = useState(snippetLiquid);
  const [data, setData] = useState(initData);

  const { colorMode } = useColorMode();
  const initTheme = colorMode === "light" ? "GitHub" : "vs-dark";

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

  useEffect(() => {
    if (!isLoading) {
      writeFile("index.liquid", indexLiquid);
      writeFile("snippet.liquid", snippetLiquid);
      writeFile("data.json", initData);
    }
  }, [isLoading]);

  function render() {
    if (isRunning) {
      interruptExecution();
    }
    if (isReady) {
      writeFile("index.liquid", index);
      writeFile("snippet.liquid", snippet);
      writeFile("data.json", data);
      runPython(mainCode);
    }
  }

  function handleEditorDidMount(_, monaco) {
    import("monaco-themes/themes/GitHub.json")
      .then((themeData) => {
        monaco.editor.defineTheme("GitHub", themeData);
      })
      .then((_) => {
        if (colorMode === "light") monaco.editor.setTheme("GitHub");
      });
  }

  const tabs = [
    {
      name: "index.liquid",
      code: index,
      setter: setIndex,
    },
    {
      name: "snippet.liquid",
      code: snippet,
      setter: setSnippet,
    },
    {
      name: "data.json",
      code: data,
      setter: setData,
    },
  ];

  return (
    <div className={clsx("container", styles.container)}>
      <div className="row">
        <div className="col">
          <h1 className="mt-5 text-xl font-light">
            Playground <sup className="text-sm">BETA</sup>
          </h1>
          <hr className={styles.headingRule} />
        </div>
      </div>
      <div className="row row--no-gutters">
        <div className={clsx("col relative", styles.editorCol)}>
          {isLoading && <Loader />}
          <Allotment className={styles.splitView} minSize={200}>
            <Allotment.Pane className="relative flex flex-col bg-[#F8F8FF] dark:bg-[#1E1E1E]">
              <RenderButton
                onClick={render}
                disabled={isLoading || isRunning}
              />
              <Tab.Group>
                <Tab.List className="min-h-10 flex h-10 space-x-0.5 bg-slate-300 dark:bg-neutral-800">
                  {tabs.map(({ name }) => (
                    <Tab
                      key={name}
                      className={({ selected }) =>
                        clsx(
                          "flex cursor-pointer items-center border-none px-4 py-1 text-sm font-medium",
                          selected
                            ? "bg-[#F8F8FF] text-slate-700 dark:bg-[#1E1E1E] dark:text-neutral-300"
                            : "bg-slate-200 text-slate-500 hover:bg-[#F8F8FF] hover:text-slate-700 dark:bg-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-600"
                        )
                      }
                    >
                      {name.endsWith(".json") ? (
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-braces mr-1 h-5 w-5"
                          viewBox="0 0 16 16"
                        >
                          <path d="M2.114 8.063V7.9c1.005-.102 1.497-.615 1.497-1.6V4.503c0-1.094.39-1.538 1.354-1.538h.273V2h-.376C3.25 2 2.49 2.759 2.49 4.352v1.524c0 1.094-.376 1.456-1.49 1.456v1.299c1.114 0 1.49.362 1.49 1.456v1.524c0 1.593.759 2.352 2.372 2.352h.376v-.964h-.273c-.964 0-1.354-.444-1.354-1.538V9.663c0-.984-.492-1.497-1.497-1.6zM13.886 7.9v.163c-1.005.103-1.497.616-1.497 1.6v1.798c0 1.094-.39 1.538-1.354 1.538h-.273v.964h.376c1.613 0 2.372-.759 2.372-2.352v-1.524c0-1.094.376-1.456 1.49-1.456V7.332c-1.114 0-1.49-.362-1.49-1.456V4.352C13.51 2.759 12.75 2 11.138 2h-.376v.964h.273c.964 0 1.354.444 1.354 1.538V6.3c0 .984.492 1.497 1.497 1.6z" />
                        </svg>
                      ) : (
                        <DocumentIcon className="mr-1 h-4 w-4" />
                      )}
                      {name}
                    </Tab>
                  ))}
                </Tab.List>

                <Tab.Panels className="flex-1">
                  {tabs.map(({ name, code, setter }) => (
                    <Tab.Panel className="h-full" key={name}>
                      {name.endsWith(".json") ? (
                        <DataEditor
                          defaultValue={code}
                          theme={initTheme}
                          onChange={(value) => setter(value)}
                        />
                      ) : (
                        <LiquidEditor
                          defaultValue={code}
                          theme={initTheme}
                          onChange={(value) => setter(value)}
                        />
                      )}
                    </Tab.Panel>
                  ))}
                </Tab.Panels>
              </Tab.Group>
            </Allotment.Pane>
            <Allotment.Pane className="bg-[#F8F8FF] dark:bg-[#1E1E1E]">
              <div className="flex h-10 justify-between space-x-0 border-0 bg-slate-300 dark:bg-neutral-800">
                <div className="flex cursor-pointer items-center border-none bg-[#F8F8FF] px-4 py-1 text-sm font-medium text-slate-700 dark:bg-[#1E1E1E] dark:text-neutral-300">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    className="bi bi-chevron-expand mr-1 h-5 w-5 rotate-90"
                    viewBox="0 0 16 16"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M3.646 9.146a.5.5 0 0 1 .708 0L8 12.793l3.646-3.647a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 0-.708zm0-2.292a.5.5 0 0 0 .708 0L8 3.207l3.646 3.647a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 0 0 0 .708z"
                    />
                  </svg>
                  result.html
                </div>
              </div>
              <ResultEditor
                result={stderr || stdout}
                theme={initTheme}
                onMount={handleEditorDidMount}
              />
            </Allotment.Pane>
          </Allotment>
        </div>
      </div>
      <div className="row">
        <div className={clsx("col", styles.infoCol)}>
          <p>
            Templates are rendered in-browser thanks to{" "}
            <Link to="https://pyodide.org/en/stable/index.html">Pyodide</Link>,
            a port of CPython to WebAssembly.
          </p>
        </div>
      </div>
    </div>
  );
}
