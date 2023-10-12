import React, { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { Allotment } from "allotment";
import "allotment/dist/style.css";
import { usePython } from "react-py";
import Editor from "@monaco-editor/react";
import { useColorMode } from "@docusaurus/theme-common";
import Link from "@docusaurus/Link";

import { DocumentIcon } from "@heroicons/react/24/solid";
import Loader from "../Loader";

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

function EditorTab({ fileName, file, setFileName }) {
  return (
    <button
      className={clsx(
        "flex cursor-pointer items-center border-none px-4 py-1 text-sm font-medium",
        fileName === file.name
          ? "bg-[#F8F8FF] text-slate-700 dark:bg-[#1E1E1E] dark:text-neutral-300"
          : "bg-slate-200 text-slate-500 hover:bg-[#F8F8FF] hover:text-slate-700 dark:bg-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-600"
      )}
      onClick={() => setFileName(fileName)}
    >
      {fileName}
    </button>
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

  const editorRef = useRef(null);

  function handleEditorDidMount(editor, monaco) {
    editorRef.current = editor;
    import("monaco-themes/themes/GitHub.json")
      .then((themeData) => {
        monaco.editor.defineTheme("GitHub", themeData);
      })
      .then((_) => {
        if (colorMode === "light") monaco.editor.setTheme("GitHub");
      });
  }

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

  const files = {
    "index.liquid": {
      name: "index.liquid",
      language: "liquid",
      value: indexLiquid,
      setter: setIndex,
    },
    "snippet.liquid": {
      name: "snippet.liquid",
      language: "liquid",
      value: snippetLiquid,
      setter: setSnippet,
    },
    "data.json": {
      name: "data.json",
      language: "json",
      value: initData,
      setter: setData,
    },
  };

  const [fileName, setFileName] = useState("index.liquid");
  const file = files[fileName];

  useEffect(() => {
    editorRef.current?.focus();
  }, [file.name]);

  // TODO: default HTML template
  // TODO: set default result
  // TODO: add note about extra tags and filters
  // TODO: add links to footer, homepage github README

  return (
    <div className={clsx("container", "--ifm-container-width-xl: 1536px;")}>
      <div className="row">
        <div className="col">
          <h1 className="mt-5 text-xl font-light">
            Playground <sup className="text-sm">BETA</sup>
          </h1>
          <hr className="mt-1" />
        </div>
      </div>
      <div className="row row--no-gutters">
        <div className="col relative h-[75vh]">
          {isLoading && <Loader />}
          <Allotment
            className="border border-solid border-[var(--ifm-hr-background-color)]"
            minSize={200}
          >
            <Allotment.Pane className="relative flex flex-col bg-[#F8F8FF] dark:bg-[#1E1E1E]">
              <RenderButton
                onClick={render}
                disabled={isLoading || isRunning}
              />

              <div className="flex h-10 space-x-0.5 border-0 bg-slate-300 dark:bg-neutral-800">
                <EditorTab
                  fileName="index.liquid"
                  file={file}
                  setFileName={setFileName}
                />
                <EditorTab
                  fileName="snippet.liquid"
                  file={file}
                  setFileName={setFileName}
                />
                <EditorTab
                  fileName="data.json"
                  file={file}
                  setFileName={setFileName}
                />
              </div>

              <div className="flex-1">
                <Editor
                  height="100%"
                  defaultLanguage={file.language}
                  theme={initTheme}
                  path={file.name}
                  defaultValue={file.value}
                  onMount={handleEditorDidMount}
                  onChange={(value) => file.setter(value)}
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
              </div>
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
                    <path d="M3.646 9.146a.5.5 0 0 1 .708 0L8 12.793l3.646-3.647a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 0-.708zm0-2.292a.5.5 0 0 0 .708 0L8 3.207l3.646 3.647a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 0 0 0 .708z" />
                  </svg>
                  result.html
                </div>
              </div>
              <Editor
                height="100%"
                language="html"
                theme={initTheme}
                value={stderr || stdout}
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
            </Allotment.Pane>
          </Allotment>
        </div>
      </div>
      <div className="row">
        <div className="col mt-1 text-center">
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
