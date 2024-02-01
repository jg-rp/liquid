"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[1393],{6339:(e,i,n)=>{n.r(i),n.d(i,{assets:()=>s,contentTitle:()=>a,default:()=>h,frontMatter:()=>c,metadata:()=>d,toc:()=>t});var o=n(5893),r=n(1151);const c={},a="liquid.loaders.CachingChoiceLoader",d={id:"api/cachingchoiceloader",title:"liquid.loaders.CachingChoiceLoader",description:"A template loader inherits from ChoiceLoader and caches parsed templates in memory.",source:"@site/docs/api/cachingchoiceloader.md",sourceDirName:"api",slug:"/api/cachingchoiceloader",permalink:"/liquid/api/cachingchoiceloader",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/cachingchoiceloader.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.ChoiceLoader",permalink:"/liquid/api/choiceloader"},next:{title:"liquid.loaders.DictLoader",permalink:"/liquid/api/dictloader"}},s={},t=[{value:"<code>CachingChoiceLoader</code>",id:"cachingchoiceloader",level:2}];function l(e){const i={a:"a",code:"code",h1:"h1",h2:"h2",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,r.useMDXComponents)(),...e.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(i.h1,{id:"liquidloaderscachingchoiceloader",children:"liquid.loaders.CachingChoiceLoader"}),"\n",(0,o.jsxs)(i.p,{children:["A template loader inherits from ",(0,o.jsx)(i.a,{href:"/liquid/api/choiceloader",children:(0,o.jsx)(i.code,{children:"ChoiceLoader"})})," and caches parsed templates in memory."]}),"\n",(0,o.jsx)(i.h2,{id:"cachingchoiceloader",children:(0,o.jsx)(i.code,{children:"CachingChoiceLoader"})}),"\n",(0,o.jsx)(i.pre,{children:(0,o.jsx)(i.code,{className:"language-python",children:'CachingChoiceLoader(\n    loaders: List[BaseLoader],\n    *,\n    auto_reload: bool = True,\n    namespace_key: str = "",\n    cache_size: int = 300\n)\n'})}),"\n",(0,o.jsxs)(i.p,{children:[(0,o.jsx)(i.strong,{children:"Parameters"}),":"]}),"\n",(0,o.jsxs)(i.ul,{children:["\n",(0,o.jsxs)(i.li,{children:["\n",(0,o.jsxs)(i.p,{children:[(0,o.jsx)(i.code,{children:"loaders: List[BaseLoader]"})," - A list of template loaders implementing ",(0,o.jsx)(i.code,{children:"liquid.loaders.BaseLoader"}),"."]}),"\n"]}),"\n",(0,o.jsxs)(i.li,{children:["\n",(0,o.jsxs)(i.p,{children:[(0,o.jsx)(i.code,{children:"auto_reload: bool = True"})," - If ",(0,o.jsx)(i.code,{children:"True"}),", automatically reload a cached template if it has been updated."]}),"\n"]}),"\n",(0,o.jsxs)(i.li,{children:["\n",(0,o.jsxs)(i.p,{children:[(0,o.jsx)(i.code,{children:'namespace_key: str = ""'}),' - The name of a global render context variable or loader keyword argument that resolves to the current loader "namespace" or "scope".']}),"\n"]}),"\n",(0,o.jsxs)(i.li,{children:["\n",(0,o.jsxs)(i.p,{children:[(0,o.jsx)(i.code,{children:"cache_size: int: 300"})," - The maximum number of templates to hold in the cache before removing the least recently used template."]}),"\n"]}),"\n"]})]})}function h(e={}){const{wrapper:i}={...(0,r.useMDXComponents)(),...e.components};return i?(0,o.jsx)(i,{...e,children:(0,o.jsx)(l,{...e})}):l(e)}},1151:(e,i,n)=>{n.r(i),n.d(i,{MDXProvider:()=>d,useMDXComponents:()=>a});var o=n(7294);const r={},c=o.createContext(r);function a(e){const i=o.useContext(c);return o.useMemo((function(){return"function"==typeof e?e(i):{...i,...e}}),[i,e])}function d(e){let i;return i=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:a(e.components),o.createElement(c.Provider,{value:i},e.children)}}}]);