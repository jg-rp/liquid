"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[3625],{1141:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>a,contentTitle:()=>s,default:()=>u,frontMatter:()=>d,metadata:()=>o,toc:()=>c});var r=i(5893),t=i(1151);const d={},s="Strictness",o={id:"introduction/strictness",title:"Strictness",description:"Templates are parsed and rendered in strict mode by default. Where syntax and render-time type errors raise an exception as soon as possible. You can change the error tolerance mode with the tolerance argument to Environment or Template.",source:"@site/docs/introduction/strictness.md",sourceDirName:"introduction",slug:"/introduction/strictness",permalink:"/liquid/introduction/strictness",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/introduction/strictness.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Objects and Drops",permalink:"/liquid/introduction/objects-and-drops"},next:{title:"Comments",permalink:"/liquid/introduction/comments"}},a={},c=[{value:"Undefined Variables",id:"undefined-variables",level:2},{value:"Undefined Filters",id:"undefined-filters",level:2}];function l(e){const n={a:"a",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",...(0,t.useMDXComponents)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(n.h1,{id:"strictness",children:"Strictness"}),"\n",(0,r.jsxs)(n.p,{children:["Templates are parsed and rendered in strict mode by default. Where syntax and render-time type errors raise an exception as soon as possible. You can change the error tolerance mode with the ",(0,r.jsx)(n.code,{children:"tolerance"})," argument to ",(0,r.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,r.jsx)(n.code,{children:"Environment"})})," or ",(0,r.jsx)(n.a,{href:"/liquid/api/Template",children:(0,r.jsx)(n.code,{children:"Template"})}),"."]}),"\n",(0,r.jsxs)(n.p,{children:["Available modes are ",(0,r.jsx)(n.code,{children:"Mode.STRICT"}),", ",(0,r.jsx)(n.code,{children:"Mode.WARN"})," and ",(0,r.jsx)(n.code,{children:"Mode.LAX"}),"."]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'from liquid import Environment, FileSystemLoader, Mode\n\nenv = Environment(\n    loader=FileSystemLoader("templates/"),\n    tolerance=Mode.LAX,\n)\n'})}),"\n",(0,r.jsx)(n.h2,{id:"undefined-variables",children:"Undefined Variables"}),"\n",(0,r.jsxs)(n.p,{children:["By default, references to undefined variables are silently ignored. Pass ",(0,r.jsx)(n.code,{children:"StrictUndefined"})," as the ",(0,r.jsx)(n.code,{children:"undefined"})," argument to ",(0,r.jsx)(n.a,{href:"/liquid/api/Template",children:(0,r.jsx)(n.code,{children:"Template"})})," or ",(0,r.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,r.jsx)(n.code,{children:"Environment"})}),", and any operation on an undefined variable will raise an ",(0,r.jsx)(n.code,{children:"UndefinedError"}),"."]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:"from liquid import Environment, StrictUndefined\nenv = Environment(undefined=StrictUndefined)\n"})}),"\n",(0,r.jsxs)(n.p,{children:["See ",(0,r.jsx)(n.a,{href:"/liquid/guides/undefined-variables",children:"Undefined Variables"})," for more information and example of how to customize undefined variable handling."]}),"\n",(0,r.jsx)(n.h2,{id:"undefined-filters",children:"Undefined Filters"}),"\n",(0,r.jsxs)(n.p,{children:["Undefined filters raise a ",(0,r.jsx)(n.code,{children:"NoSuchFilterFunc"})," exception by default. Set the ",(0,r.jsx)(n.code,{children:"strict_filters"})," argument to ",(0,r.jsx)(n.a,{href:"/liquid/api/Template",children:(0,r.jsx)(n.code,{children:"Template"})})," or ",(0,r.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,r.jsx)(n.code,{children:"Environment"})})," to ",(0,r.jsx)(n.code,{children:"False"})," and undefined filters will be silently ignored."]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:"from liquid import Environment\nenv = Environment(strict_filters=False)\n"})})]})}function u(e={}){const{wrapper:n}={...(0,t.useMDXComponents)(),...e.components};return n?(0,r.jsx)(n,{...e,children:(0,r.jsx)(l,{...e})}):l(e)}},1151:(e,n,i)=>{i.r(n),i.d(n,{MDXProvider:()=>o,useMDXComponents:()=>s});var r=i(7294);const t={},d=r.createContext(t);function s(e){const n=r.useContext(d);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function o(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(t):e.components||t:s(e.components),r.createElement(d.Provider,{value:n},e.children)}}}]);