"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4936],{7009:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>o,contentTitle:()=>d,default:()=>h,frontMatter:()=>l,metadata:()=>r,toc:()=>s});var t=i(5893),a=i(1151);const l={},d="Loading Templates",r={id:"introduction/loading-templates",title:"Loading Templates",description:"You can load templates from a file system or database, for example, by creating an Environment and configuring a template loader. You'd also need a loader if you want to use the built-in {% include %} or {% render %} tags.",source:"@site/docs/introduction/loading-templates.md",sourceDirName:"introduction",slug:"/introduction/loading-templates",permalink:"/liquid/introduction/loading-templates",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/introduction/loading-templates.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Getting Started",permalink:"/liquid/introduction/getting-started"},next:{title:"Render Context",permalink:"/liquid/introduction/render-context"}},o={},s=[{value:"Caching File System Loader",id:"caching-file-system-loader",level:2}];function c(e){const n={a:"a",admonition:"admonition",code:"code",em:"em",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...(0,a.useMDXComponents)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h1,{id:"loading-templates",children:"Loading Templates"}),"\n",(0,t.jsxs)(n.p,{children:["You can load templates from a file system or database, for example, by creating an ",(0,t.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,t.jsx)(n.code,{children:"Environment"})})," and configuring a template ",(0,t.jsx)(n.em,{children:"loader"}),". You'd also need a loader if you want to use the built-in ",(0,t.jsx)(n.a,{href:"/liquid/language/tags#include",children:(0,t.jsx)(n.code,{children:"{% include %}"})})," or ",(0,t.jsx)(n.a,{href:"/liquid/language/tags#render",children:(0,t.jsx)(n.code,{children:"{% render %}"})})," tags."]}),"\n",(0,t.jsxs)(n.p,{children:[(0,t.jsx)(n.a,{href:"/liquid/api/Environment#get_template",children:(0,t.jsx)(n.code,{children:"Environment.get_template()"})})," and ",(0,t.jsx)(n.a,{href:"/liquid/api/Environment#get_template_async",children:(0,t.jsx)(n.code,{children:"Environment.get_template_async()"})})," accept a template name and return a ",(0,t.jsx)(n.a,{href:"/liquid/api/BoundTemplate",children:(0,t.jsx)(n.code,{children:"BoundTemplate"})}),". That is a template bound to the environment, ready to be rendered. It is up to the loader to interpret a template name. In the case of ",(0,t.jsx)(n.a,{href:"/liquid/api/filesystemloader",children:(0,t.jsx)(n.code,{children:"FileSystemLoader"})}),", the name would be a file name, possibly preceded by a path relative to the configured search path."]}),"\n",(0,t.jsxs)(n.p,{children:["Built-in loaders include ",(0,t.jsx)(n.a,{href:"/liquid/api/cachingfilesystemloader",children:(0,t.jsx)(n.code,{children:"CachingFileSystemLoader"})}),", ",(0,t.jsx)(n.a,{href:"/liquid/api/filesystemloader",children:(0,t.jsx)(n.code,{children:"FileSystemLoader"})}),", ",(0,t.jsx)(n.a,{href:"/liquid/api/fileextensionloader",children:(0,t.jsx)(n.code,{children:"FileExtensionLoader"})}),", ",(0,t.jsx)(n.a,{href:"/liquid/api/dictloader",children:(0,t.jsx)(n.code,{children:"DictLoader"})}),", ",(0,t.jsx)(n.a,{href:"/liquid/api/choiceloader",children:(0,t.jsx)(n.code,{children:"ChoiceLoader"})}),", ",(0,t.jsx)(n.a,{href:"/liquid/api/cachingchoiceloader",children:(0,t.jsx)(n.code,{children:"CachingChoiceLoader"})})," and ",(0,t.jsx)(n.a,{href:"/liquid/api/packageloader",children:(0,t.jsx)(n.code,{children:"PackageLoader"})}),". See also ",(0,t.jsx)(n.a,{href:"/liquid/guides/custom-loaders",children:"custom loaders"}),", and examples of a ",(0,t.jsx)(n.a,{href:"/liquid/guides/custom-loaders#front-matter-loader",children:(0,t.jsx)(n.code,{children:"FrontMatterFileSystemLoader"})})," and an ",(0,t.jsx)(n.a,{href:"/liquid/guides/custom-loaders#async-database-loader",children:(0,t.jsx)(n.code,{children:"AsyncDatabaseLoader"})}),"."]}),"\n",(0,t.jsxs)(n.p,{children:["This ",(0,t.jsx)(n.code,{children:"FileSystemLoader"})," example assumes a folder called ",(0,t.jsx)(n.code,{children:"templates"})," exists in the current working directory, and that template files ",(0,t.jsx)(n.code,{children:"index.html"})," and ",(0,t.jsx)(n.code,{children:"some-list.html"})," exist within it."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-html",metastring:'title="templates/index.html"',children:"<!doctype html>\n<html lang=\"en\">\n  <head>\n    <title>{{ page_title }}</title>\n  </head>\n  <body>\n    <h1>{{ heading }}</h1>\n    {% render 'some-list.html' with people %}\n  </body>\n</html>\n"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-html",metastring:'title="templates/some-list.html"',children:"<ul>\n  {% for person in people %}\n  <li>{{ person.name }}</li>\n  {% endfor %}\n</ul>\n"})}),"\n",(0,t.jsxs)(n.p,{children:["By default, every ",(0,t.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,t.jsx)(n.code,{children:"Environment"})})," is created with an empty ",(0,t.jsx)(n.a,{href:"/liquid/api/dictloader",children:(0,t.jsx)(n.code,{children:"DictLoader"})}),". Specify an alternative template loader using the ",(0,t.jsx)(n.code,{children:"loader"})," argument."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'from liquid import Environment\nfrom liquid import FileSystemLoader\n\nenv = Environment(loader=FileSystemLoader("templates/"))\n\npeople = [\n    {"name": "John"},\n    {"name": "Sally"},\n]\n\ntemplate = env.get_template("index.html")\n\nprint(template.render(\n    heading="Some List",\n    page_title="Awesome Title",\n    people=people,\n))\n'})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-html",metastring:'title="output"',children:'<!doctype html>\n<html lang="en">\n  <head>\n    <title>Awesome Title</title>\n  </head>\n  <body>\n    <h1>Some List</h1>\n    <ul>\n      <li>John</li>\n\n      <li>Sally</li>\n    </ul>\n  </body>\n</html>\n'})}),"\n",(0,t.jsx)(n.admonition,{type:"info",children:(0,t.jsxs)(n.p,{children:["Notice how whitespace is output unchanged. See ",(0,t.jsx)(n.a,{href:"/liquid/language/introduction#whitespace-control",children:(0,t.jsx)(n.code,{children:"whitespace control"})})," for more information."]})}),"\n",(0,t.jsx)(n.h2,{id:"caching-file-system-loader",children:"Caching File System Loader"}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:(0,t.jsx)(n.em,{children:"New in version 1.9.0"})})}),"\n",(0,t.jsxs)(n.p,{children:["When rendering partial templates with ",(0,t.jsx)(n.a,{href:"/liquid/language/tags#include",children:(0,t.jsx)(n.code,{children:"{% include %}"})})," or ",(0,t.jsx)(n.a,{href:"/liquid/language/tags#render",children:(0,t.jsx)(n.code,{children:"{% render %}"})}),", or making use of Python Liquid's ",(0,t.jsx)(n.a,{href:"/liquid/extra/tags#extends--block",children:"template inheritance features"}),", it is recommended to use a ",(0,t.jsx)(n.em,{children:"caching loader"})," such as ",(0,t.jsx)(n.a,{href:"/liquid/api/cachingfilesystemloader",children:(0,t.jsx)(n.code,{children:"CachingFileSystemLoader"})})," or ",(0,t.jsx)(n.a,{href:"/liquid/api/cachingchoiceloader",children:(0,t.jsx)(n.code,{children:"CachingChoiceLoader"})})," or a custom loader that handles its own cache."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'from liquid import CachingFileSystemLoader\nfrom liquid import Environment\n\nloader = CachingFileSystemLoader("templates/", cache_size=500)\nenv = Environment(loader=loader)\n\n# ...\n'})})]})}function h(e={}){const{wrapper:n}={...(0,a.useMDXComponents)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(c,{...e})}):c(e)}},1151:(e,n,i)=>{i.r(n),i.d(n,{MDXProvider:()=>r,useMDXComponents:()=>d});var t=i(7294);const a={},l=t.createContext(a);function d(e){const n=t.useContext(l);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:d(e.components),t.createElement(l.Provider,{value:n},e.children)}}}]);