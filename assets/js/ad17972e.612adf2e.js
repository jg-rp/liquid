"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4507],{8464:(e,t,s)=>{s.r(t),s.d(t,{assets:()=>d,contentTitle:()=>o,default:()=>c,frontMatter:()=>a,metadata:()=>i,toc:()=>l});const i=JSON.parse('{"id":"guides/security","title":"Security","description":"Designed for situations where template authors are untrusted and, perhaps, not software developers, Liquid has security goals that are distinct from many other template languages. Most notably:","source":"@site/docs/guides/security.md","sourceDirName":"guides","slug":"/guides/security","permalink":"/liquid/guides/security","draft":false,"unlisted":false,"editUrl":"https://github.com/jg-rp/liquid/tree/docs/docs/guides/security.md","tags":[],"version":"current","frontMatter":{},"sidebar":"docsSidebar","previous":{"title":"Custom Loaders","permalink":"/liquid/guides/custom-loaders"},"next":{"title":"Static Template Analysis","permalink":"/liquid/guides/static-template-analysis"}}');var n=s(4848),r=s(8453);const a={},o="Security",d={},l=[{value:"Guidelines",id:"guidelines",level:2}];function u(e){const t={a:"a",code:"code",h1:"h1",h2:"h2",header:"header",li:"li",p:"p",ul:"ul",...(0,r.useMDXComponents)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(t.header,{children:(0,n.jsx)(t.h1,{id:"security",children:"Security"})}),"\n",(0,n.jsx)(t.p,{children:"Designed for situations where template authors are untrusted and, perhaps, not software developers, Liquid has security goals that are distinct from many other template languages. Most notably:"}),"\n",(0,n.jsxs)(t.ul,{children:["\n",(0,n.jsx)(t.li,{children:"Liquid is non-evaling. User (template authors) submitted code must not be executed on the server."}),"\n",(0,n.jsxs)(t.li,{children:["Liquid must not leak arbitrary properties and methods of objects added to a template's render context without being explicitly whitelisted. See ",(0,n.jsx)(t.a,{href:"/liquid/introduction/objects-and-drops",children:"Objects and Drops"}),"."]}),"\n",(0,n.jsxs)(t.li,{children:["Tags and filters must not mutate global context variables. See ",(0,n.jsx)(t.a,{href:"/liquid/introduction/render-context",children:"Render Context"}),"."]}),"\n"]}),"\n",(0,n.jsx)(t.h2,{id:"guidelines",children:"Guidelines"}),"\n",(0,n.jsxs)(t.p,{children:["When developing custom ",(0,n.jsx)(t.a,{href:"/liquid/guides/custom-tags",children:"tags"}),", ",(0,n.jsx)(t.a,{href:"/liquid/guides/custom-filters",children:"filters"})," and ",(0,n.jsx)(t.a,{href:"/liquid/guides/custom-loaders",children:"loaders"}),", the following recommendations apply."]}),"\n",(0,n.jsxs)(t.ul,{children:["\n",(0,n.jsxs)(t.li,{children:["Don't use ",(0,n.jsx)(t.a,{href:"https://docs.python.org/3/library/functions.html#eval",children:(0,n.jsx)(t.code,{children:"eval"})})," to evaluate tag expressions."]}),"\n",(0,n.jsxs)(t.li,{children:["Respect the global namespace by using ",(0,n.jsx)(t.a,{href:"/liquid/api/context#assign",children:(0,n.jsx)(t.code,{children:"context.assign()"})})," rather than updating a namespace directly."]}),"\n",(0,n.jsx)(t.li,{children:"Implement filters as pure functions, without side effects."}),"\n",(0,n.jsx)(t.li,{children:"Actively guard against loading templates from outside the search path when implementing loaders that deal with a filesystem."}),"\n"]})]})}function c(e={}){const{wrapper:t}={...(0,r.useMDXComponents)(),...e.components};return t?(0,n.jsx)(t,{...e,children:(0,n.jsx)(u,{...e})}):u(e)}},8453:(e,t,s)=>{s.r(t),s.d(t,{MDXProvider:()=>o,useMDXComponents:()=>a});var i=s(6540);const n={},r=i.createContext(n);function a(e){const t=i.useContext(r);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(n):e.components||n:a(e.components),i.createElement(r.Provider,{value:t},e.children)}}}]);