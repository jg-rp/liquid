// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

// const lightCodeTheme = require("./src/theme/prismLight.js");
const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/vsDark");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Python Liquid",
  tagline: "Safe, customer-facing template engine",
  url: "https://jg-rp.github.io/",
  baseUrl: "/liquid/", // /liquid/ for gh-pages?
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",
  organizationName: "jg-rp", // Usually your GitHub org/user name.
  projectName: "liquid", // Usually your repo name.
  trailingSlash: false,

  presets: [
    [
      "@docusaurus/preset-classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          editUrl: "https://github.com/jg-rp/liquid/tree/docs",
          routeBasePath: "/",
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl: "https://github.com/jg-rp/liquid/tree/gh-pages/blog/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
        sitemap: {
          changefreq: "weekly",
          priority: 0.5,
        },
      }),
    ],
  ],

  plugins: [
    async function tailwind() {
      return {
        name: "tailwindcss",
        configurePostCss(postcssOptions) {
          // Appends TailwindCSS and AutoPrefixer.
          postcssOptions.plugins.push(require("tailwindcss"));
          postcssOptions.plugins.push(require("autoprefixer"));
          return postcssOptions;
        },
      };
    },
    async function disableUsedExports() {
      return {
        name: "disable-used-exports",
        configureWebpack() {
          return {
            optimization: {
              usedExports: false,
            },
          };
        },
      };
    },
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "Python Liquid",
        logo: {
          alt: "Python Liquid Logo",
          src: "img/droplet_blue_with_yellow_liquid.svg",
          srcDark: "img/droplet_yellow_with_blue_liquid.svg",
        },
        items: [
          {
            type: "doc",
            docId: "introduction/getting-started",
            position: "left",
            label: "Docs",
          },
          {
            type: "doc",
            docId: "language/filters",
            position: "left",
            label: "Filters",
          },
          {
            type: "doc",
            docId: "language/tags",
            position: "left",
            label: "Tags",
          },
          {
            type: "doc",
            docId: "api/Environment",
            position: "left",
            label: "API",
          },
          {
            to: "/playground/",
            label: "Try It",
            position: "left",
          },
          // {to: '/blog', label: 'Blog', position: 'right'},
          {
            href: "https://github.com/jg-rp/liquid/",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              {
                label: "Introduction",
                to: "/introduction/getting-started",
              },
              {
                label: "Installation",
                to: "/introduction/getting-started#install",
              },
              {
                label: "Filter Reference",
                to: "/language/filters",
              },
              {
                label: "Tag Reference",
                to: "/language/tags",
              },
            ],
          },
          {
            title: "Features",
            items: [
              {
                label: "HTML Auto-Escape",
                to: "/introduction/auto-escape",
              },
              {
                label: "Async Support",
                to: "/introduction/async-support",
              },
              {
                label: "Caching",
                to: "/introduction/caching",
              },
              {
                label: "Static Template Analysis",
                to: "/guides/static-template-analysis",
              },
              {
                label: "Resource Limits",
                to: "/guides/resource-limits",
              },
            ],
          },
          {
            title: "Extra Tags",
            items: [
              {
                label: "Template Inheritance",
                to: "/extra/tags#extends--block",
              },
              {
                label: "Macros",
                to: "/extra/tags#macro--call",
              },
              {
                label: "Inline Conditional Expressions",
                to: "extra/tags#inline-if--else",
              },
              {
                label: "Logical Negation",
                to: "/extra/tags#if-not",
              },
              {
                label: "Block Scoped Variables",
                to: "/extra/tags#with",
              },
            ],
          },
          {
            title: "Links",
            items: [
              {
                label: "GitHub",
                href: "https://github.com/jg-rp/liquid",
              },
              {
                label: "Change Log",
                href: "https://github.com/jg-rp/liquid/blob/main/CHANGES.md",
              },
              {
                label: "PyPi",
                href: "https://pypi.org/project/python-liquid/",
              },
            ],
          },
          {
            title: "Related Projects",
            items: [
              {
                label: "LiquidScript",
                href: "https://github.com/jg-rp/liquidscript",
              },
              {
                label: "Django Liquid",
                href: "https://github.com/jg-rp/django-liquid",
              },
              {
                label: "Flask Liquid",
                href: "https://github.com/jg-rp/Flask-Liquid",
              },
              {
                label: "Python Liquid Babel",
                href: "https://github.com/jg-rp/liquid-babel",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} James Prior. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: [],
      },
      algolia: {
        appId: "SY0LPESLUP",
        apiKey: "5f0c1de3dad3648085c7bcd9fd6c4997",
        indexName: "jg-rp",
        contextualSearch: false,
      },
    }),
};

module.exports = config;
