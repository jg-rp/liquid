import React from "react";
import Layout from "@theme/Layout";
import Playground from "../components/Playground";

export default function PlaygroundPage() {
  return (
    <Layout title="Playground" description="JSONPath playground">
      <Playground />
    </Layout>
  );
}
