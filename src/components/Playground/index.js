import Link from "@docusaurus/Link";
import { useColorMode } from "@docusaurus/theme-common";
import Editor from "@monaco-editor/react";
import { Allotment } from "allotment";
import "allotment/dist/style.css";
import clsx from "clsx";
import React, { useEffect, useRef, useState } from "react";
import { usePython } from "react-py";
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
  {
    site: {
      posts: [
        {
          title: "Sample Post 1",
          date: "2023-03-12",
          likes: 42,
          excerpt:
            "This is the content of the first sample blog post. It contains some information and details about a particular topic. Feel free to like this post if you found it interesting.",
        },
        {
          title: "Sample Post 2",
          date: "2023-03-10",
          likes: 29,
          excerpt:
            "Here's another example blog post. We hope you enjoy reading it as much as we enjoyed writing it. Don't forget to hit the like button if you find this post helpful!",
        },
        {
          title: "Sample Post 3",
          date: "2023-03-08",
          likes: 17,
          excerpt:
            "Our third blog post is all about a fascinating topic. We've put together some great content for you. If you like what you read, give us a thumbs up!",
        },
      ],
    },
  },
  undefined,
  "  "
);

const indexLiquid = `\
<div class="flex flex-col">
{% for post in site.posts %}
  {%- render 'snippet' with post as post %}
{%- endfor %}
</div>

<!-- Rendered with Python Liquid version {{ __version__ }} -->
`;

const snippetLiquid = `\
  <article>
    <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%b %d, %Y" }}</p>
    {{ post.excerpt }}
    <p>{{ post.likes }} likes</p>
  </article>
`;

const initResult = `\
<div class="flex flex-col">
  <article>
    <h2><a href="">Sample Post 1</a></h2>
    <p class="post-meta">Mar 12, 2023</p>
    This is the content of the first sample blog post. It contains some information and details about a particular topic. Feel free to like this post if you found it interesting.
    <p>42 likes</p>
  </article>
  <article>
    <h2><a href="">Sample Post 2</a></h2>
    <p class="post-meta">Mar 10, 2023</p>
    Here's another example blog post. We hope you enjoy reading it as much as we enjoyed writing it. Don't forget to hit the like button if you find this post helpful!
    <p>29 likes</p>
  </article>
  <article>
    <h2><a href="">Sample Post 3</a></h2>
    <p class="post-meta">Mar 08, 2023</p>
    Our third blog post is all about a fascinating topic. We've put together some great content for you. If you like what you read, give us a thumbs up!
    <p>17 likes</p>
  </article>

</div>

<!-- Rendered with Python Liquid version 1.10.0 -->

`;

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
      {fileName.endsWith(".json") ? (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-braces mr-1 h-4 w-4"
          viewBox="0 0 16 16"
        >
          <path d="M2.114 8.063V7.9c1.005-.102 1.497-.615 1.497-1.6V4.503c0-1.094.39-1.538 1.354-1.538h.273V2h-.376C3.25 2 2.49 2.759 2.49 4.352v1.524c0 1.094-.376 1.456-1.49 1.456v1.299c1.114 0 1.49.362 1.49 1.456v1.524c0 1.593.759 2.352 2.372 2.352h.376v-.964h-.273c-.964 0-1.354-.444-1.354-1.538V9.663c0-.984-.492-1.497-1.497-1.6zM13.886 7.9v.163c-1.005.103-1.497.616-1.497 1.6v1.798c0 1.094-.39 1.538-1.354 1.538h-.273v.964h.376c1.613 0 2.372-.759 2.372-2.352v-1.524c0-1.094.376-1.456 1.49-1.456V7.332c-1.114 0-1.49-.362-1.49-1.456V4.352C13.51 2.759 12.75 2 11.138 2h-.376v.964h.273c.964 0 1.354.444 1.354 1.538V6.3c0 .984.492 1.497 1.497 1.6z" />
        </svg>
      ) : (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-file-earmark-code mr-1 h-4 w-4"
          viewBox="0 0 16 16"
        >
          <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z" />
          <path d="M8.646 6.646a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-2 2a.5.5 0 0 1-.708-.708L10.293 9 8.646 7.354a.5.5 0 0 1 0-.708zm-1.292 0a.5.5 0 0 0-.708 0l-2 2a.5.5 0 0 0 0 .708l2 2a.5.5 0 0 0 .708-.708L5.707 9l1.647-1.646a.5.5 0 0 0 0-.708z" />
        </svg>
      )}
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
      console.log(editorRef.current?.getModel());
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
            <Allotment.Pane className="flex flex-col bg-[#F8F8FF] dark:bg-[#1E1E1E]">
              <div className="flex h-10 justify-between space-x-0 border-0 bg-slate-300 dark:bg-neutral-800">
                <div className="flex cursor-pointer items-center border-none bg-[#F8F8FF] px-4 py-1 text-sm font-medium text-slate-700 dark:bg-[#1E1E1E] dark:text-neutral-300">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    className="bi bi-code mr-1 h-5 w-5"
                    viewBox="0 0 16 16"
                  >
                    <path d="M5.854 4.854a.5.5 0 1 0-.708-.708l-3.5 3.5a.5.5 0 0 0 0 .708l3.5 3.5a.5.5 0 0 0 .708-.708L2.707 8l3.147-3.146zm4.292 0a.5.5 0 0 1 .708-.708l3.5 3.5a.5.5 0 0 1 0 .708l-3.5 3.5a.5.5 0 0 1-.708-.708L13.293 8l-3.147-3.146z" />
                  </svg>
                  result.html
                </div>
              </div>
              <div className="flex-1">
                <Editor
                  height="100%"
                  language="html"
                  theme={initTheme}
                  defaultValue={initResult}
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
                    readOnly: true,
                  }}
                />
              </div>
            </Allotment.Pane>
          </Allotment>
        </div>
      </div>
      <div className="row">
        <div className="col mt-1 text-center">
          <p className="text-sm">
            Click the green button to render.
            <br />
            All <Link to="/extra/introduction">extra tags and filters</Link> are
            enabled.
            <br />
            Templates are rendered in-browser thanks to{" "}
            <Link to="https://pyodide.org/en/stable/index.html">Pyodide</Link>.
          </p>
        </div>
      </div>
    </div>
  );
}
