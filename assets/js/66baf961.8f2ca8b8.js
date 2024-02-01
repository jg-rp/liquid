"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4157],{9368:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>l,contentTitle:()=>d,default:()=>h,frontMatter:()=>s,metadata:()=>r,toc:()=>a});var t=i(5893),o=i(1151);const s={},d="liquid.loaders.FileExtensionLoader",r={id:"api/fileextensionloader",title:"liquid.loaders.FileExtensionLoader",description:"A loader that inherits from FileSystemLoader and adds a file name extension to any template_name that does not have one.",source:"@site/docs/api/fileextensionloader.md",sourceDirName:"api",slug:"/api/fileextensionloader",permalink:"/liquid/api/fileextensionloader",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/fileextensionloader.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.FileSystemLoader",permalink:"/liquid/api/filesystemloader"},next:{title:"liquid.loaders.ChoiceLoader",permalink:"/liquid/api/choiceloader"}},l={},a=[{value:"FileExtensionLoader",id:"fileextensionloader",level:2}];function c(e){const n={a:"a",code:"code",h1:"h1",h2:"h2",li:"li",p:"p",strong:"strong",ul:"ul",...(0,o.useMDXComponents)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h1,{id:"liquidloadersfileextensionloader",children:"liquid.loaders.FileExtensionLoader"}),"\n",(0,t.jsxs)(n.p,{children:["A loader that inherits from ",(0,t.jsx)(n.a,{href:"/liquid/api/filesystemloader",children:(0,t.jsx)(n.code,{children:"FileSystemLoader"})})," and adds a file name extension to any ",(0,t.jsx)(n.code,{children:"template_name"})," that does not have one."]}),"\n",(0,t.jsxs)(n.p,{children:["When rendering from an environment configured with a ",(0,t.jsx)(n.code,{children:"FileExtensionLoader"}),", templates can, for example, use ",(0,t.jsx)(n.code,{children:"{% render 'somesnippet' %}"})," and ",(0,t.jsx)(n.code,{children:"{% include 'mysection' %}"})," instead of ",(0,t.jsx)(n.code,{children:"{% render 'somesnippet.liquid' %}"})," or ",(0,t.jsx)(n.code,{children:"{% include 'mysection.html' %}"}),"."]}),"\n",(0,t.jsx)(n.h2,{id:"fileextensionloader",children:"FileExtensionLoader"}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.code,{children:'class FileExtensionLoader(search_path, encoding="utf-8", ext=".liquid")'})}),"\n",(0,t.jsxs)(n.p,{children:[(0,t.jsx)(n.strong,{children:"Parameters"}),":"]}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:[(0,t.jsx)(n.code,{children:"search_path: Union[str, Path, Iterable[Union[str, Path]]]"})," - One or more paths to search."]}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:[(0,t.jsx)(n.code,{children:'encoding: str = "utf-8"'})," - Open template files with the given encoding. Defaults to ",(0,t.jsx)(n.code,{children:'"utf-8"'}),"."]}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:[(0,t.jsx)(n.code,{children:'ext: str = ".liquid"'})," - A default file extension. Should include a leading period. Defaults to ",(0,t.jsx)(n.code,{children:".liquid"}),"."]}),"\n"]}),"\n"]})]})}function h(e={}){const{wrapper:n}={...(0,o.useMDXComponents)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(c,{...e})}):c(e)}},1151:(e,n,i)=>{i.r(n),i.d(n,{MDXProvider:()=>r,useMDXComponents:()=>d});var t=i(7294);const o={},s=t.createContext(o);function d(e){const n=t.useContext(s);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:d(e.components),t.createElement(s.Provider,{value:n},e.children)}}}]);