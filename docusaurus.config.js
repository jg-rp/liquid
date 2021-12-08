// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/vsDark');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Python Liquid',
  tagline: 'Python Liquid Template Engine',
  url: 'https://jg-rp.github.io/',
  baseUrl: '/liquid/',  // /liquid/ for gh-pages?
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'jg-rp', // Usually your GitHub org/user name.
  projectName: 'liquid', // Usually your repo name.
  trailingSlash: false,

  presets: [
    [
      '@docusaurus/preset-classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl: 'https://github.com/jg-rp/liquid/tree/gh-pages/docs/',
          routeBasePath: '/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl:
            'https://github.com/jg-rp/liquid/tree/gh-pages/blog/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Python Liquid',
        logo: {
          alt: 'Python Liquid Logo',
          src: 'img/droplet_blue_with_yellow_liquid.svg',
          srcDark: 'img/droplet_yellow_with_blue_liquid.svg',
        },
        items: [
          {
            type: 'doc',
            docId: 'introduction/getting-started',
            position: 'left',
            label: 'Docs',
          },
          {
            type: 'doc',
            docId: 'language/filters',
            position: 'left',
            label: 'Filters',
          },
          {
            type: 'doc',
            docId: 'language/tags',
            position: 'left',
            label: 'Tags',
          },
          {
            type: 'doc',
            docId: 'api/Environment',
            position: 'left',
            label: 'API',
          },
          // {to: '/blog', label: 'Blog', position: 'right'},
          {
            href: 'https://github.com/jg-rp/liquid/',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `Copyright © ${new Date().getFullYear()} James Prior. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['liquid']
      },
    }),
};

module.exports = config;
