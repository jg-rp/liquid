import React, { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { Allotment } from "allotment";
import "allotment/dist/style.css";
import { usePython } from "react-py";
import Editor from "@monaco-editor/react";
import { useColorMode } from "@docusaurus/theme-common";
import Link from "@docusaurus/Link";

import { Tab } from "@headlessui/react";
import { DocumentIcon, PlayIcon } from "@heroicons/react/24/solid";

import Loader from "../Loader";
import Controls from "../Controls";
import styles from "./styles.module.css";

const mainCode = `\
import json
import sys
import liquid
from liquid import Environment, FileExtensionLoader

try:
    with open("data.json") as fd:
        data = json.load(fd)
except (json.error, FileNotFoundError) as err:
    sys.stdout.write(str(err))
    data = {}

data["__version__"] = liquid.__version__

env = Environment(loader=FileExtensionLoader("."))

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
      language="plain"
      theme={theme}
      value={result}
      onMount={onMount}
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
      .then((_) => monaco.editor.setTheme("GitHub"));
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
          <h1 className={styles.heading}>Python Liquid Playground</h1>
          <hr className={styles.headingRule} />
        </div>
      </div>
      <div className="row">
        <div className={clsx("col relative", styles.editorCol)}>
          {isLoading && <Loader />}
          <Allotment className={styles.splitView} minSize={200}>
            <Allotment.Pane className="bg-[#F8F8FF]">
              <Tab.Group>
                <Tab.List className="flex h-10 space-x-0 border-0 bg-neutral-700">
                  {tabs.map(({ name }) => (
                    <Tab
                      key={name}
                      className={({ selected }) =>
                        clsx(
                          "flex cursor-pointer items-center border-none px-4 py-1 text-sm font-medium",
                          selected
                            ? "bg-[#F8F8FF] text-neutral-700"
                            : "bg-neutral-500 text-gray-50 hover:bg-[#F8F8FF] hover:text-neutral-700"
                        )
                      }
                    >
                      <DocumentIcon className="-mb-1 mr-1 h-4 w-4" />
                      {name}
                    </Tab>
                  ))}
                </Tab.List>

                <Tab.Panels className="h-full">
                  {tabs.map(({ name, code, setter }) => (
                    <Tab.Panel className="h-full" key={name}>
                      <div className="h-full flex-1">
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
                      </div>
                    </Tab.Panel>
                  ))}
                </Tab.Panels>
              </Tab.Group>
            </Allotment.Pane>
            <Allotment.Pane>
              <div className="flex h-10 justify-between space-x-0 border-0 bg-neutral-700">
                <div className="flex cursor-pointer items-center border-none bg-[#F8F8FF] px-4 py-1 text-sm font-medium text-neutral-700">
                  <DocumentIcon className="-mb-1 mr-1 h-4 w-4" />
                  results
                </div>
                <Controls
                  items={[
                    {
                      label: "Render",
                      icon: PlayIcon,
                      onClick: render,
                      disabled: isLoading || isRunning,
                    },
                  ]}
                />
              </div>
              <ResultEditor
                result={stdout}
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
            a port of Python to WebAssembly.
          </p>
        </div>
      </div>
    </div>
  );
}
