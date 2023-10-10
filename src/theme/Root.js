import React from "react";
import { PythonProvider } from "react-py";

export default function Root({ children }) {
  const packages = { micropip: ["python-liquid"] };
  return <PythonProvider packages={packages}>{children}</PythonProvider>;
}
