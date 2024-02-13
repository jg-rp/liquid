"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[5465],{162:(e,o,n)=>{n.r(o),n.d(o,{assets:()=>c,contentTitle:()=>t,default:()=>h,frontMatter:()=>s,metadata:()=>d,toc:()=>l});var r=n(5893),i=n(1151);const s={},t="liquid.loaders.ChoiceLoader",d={id:"api/choiceloader",title:"liquid.loaders.ChoiceLoader",description:"A template loader that will try each of a list of loaders until a template is found.",source:"@site/docs/api/choiceloader.md",sourceDirName:"api",slug:"/api/choiceloader",permalink:"/liquid/api/choiceloader",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/choiceloader.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.FileExtensionLoader",permalink:"/liquid/api/fileextensionloader"},next:{title:"liquid.loaders.CachingChoiceLoader",permalink:"/liquid/api/cachingchoiceloader"}},c={},l=[{value:"<code>ChoiceLoader</code>",id:"choiceloader",level:2},{value:"Methods",id:"methods",level:2},{value:"<code>get_source</code>",id:"get_source",level:3},{value:"<code>get_source_async</code>",id:"get_source_async",level:3}];function a(e){const o={a:"a",br:"br",code:"code",h1:"h1",h2:"h2",h3:"h3",li:"li",p:"p",strong:"strong",ul:"ul",...(0,i.useMDXComponents)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(o.h1,{id:"liquidloaderschoiceloader",children:"liquid.loaders.ChoiceLoader"}),"\n",(0,r.jsx)(o.p,{children:"A template loader that will try each of a list of loaders until a template is found."}),"\n",(0,r.jsx)(o.h2,{id:"choiceloader",children:(0,r.jsx)(o.code,{children:"ChoiceLoader"})}),"\n",(0,r.jsx)(o.p,{children:(0,r.jsx)(o.code,{children:"class FileSystemLoader(loaders)"})}),"\n",(0,r.jsxs)(o.p,{children:[(0,r.jsx)(o.strong,{children:"Parameters"}),":"]}),"\n",(0,r.jsxs)(o.ul,{children:["\n",(0,r.jsxs)(o.li,{children:[(0,r.jsx)(o.code,{children:"loaders: List[liquid.loaders.BaseLoader]"})," - A list of loaders to try."]}),"\n"]}),"\n",(0,r.jsx)(o.h2,{id:"methods",children:"Methods"}),"\n",(0,r.jsx)(o.h3,{id:"get_source",children:(0,r.jsx)(o.code,{children:"get_source"})}),"\n",(0,r.jsx)(o.p,{children:(0,r.jsx)(o.code,{children:"get_source(environment, template_name)"})}),"\n",(0,r.jsxs)(o.p,{children:["Calls ",(0,r.jsx)(o.code,{children:"get_source"})," on each loader, returning the first template source found."]}),"\n",(0,r.jsxs)(o.p,{children:[(0,r.jsx)(o.strong,{children:"Raises"}),": ",(0,r.jsx)(o.code,{children:"liquid.exceptions.TemplateNotFound"})," if a template with the given name can not be\nfound.",(0,r.jsx)(o.br,{}),"\n",(0,r.jsx)(o.strong,{children:"Returns"}),": The source, filename and reload function for the named template.",(0,r.jsx)(o.br,{}),"\n",(0,r.jsx)(o.strong,{children:"Return Type"}),": ",(0,r.jsx)(o.code,{children:"liquid.loaders.TemplateSource"})]}),"\n",(0,r.jsx)(o.h3,{id:"get_source_async",children:(0,r.jsx)(o.code,{children:"get_source_async"})}),"\n",(0,r.jsx)(o.p,{children:(0,r.jsx)(o.code,{children:"async get_source(environment, template_name)"})}),"\n",(0,r.jsxs)(o.p,{children:["An async version of ",(0,r.jsx)(o.a,{href:"#get_source",children:(0,r.jsx)(o.code,{children:"get_source()"})}),"."]}),"\n",(0,r.jsxs)(o.p,{children:[(0,r.jsx)(o.strong,{children:"Returns"}),": The source, filename and reload function for the named template.",(0,r.jsx)(o.br,{}),"\n",(0,r.jsx)(o.strong,{children:"Return Type"}),": ",(0,r.jsx)(o.code,{children:"liquid.loaders.TemplateSource"})]})]})}function h(e={}){const{wrapper:o}={...(0,i.useMDXComponents)(),...e.components};return o?(0,r.jsx)(o,{...e,children:(0,r.jsx)(a,{...e})}):a(e)}},1151:(e,o,n)=>{n.r(o),n.d(o,{MDXProvider:()=>d,useMDXComponents:()=>t});var r=n(7294);const i={},s=r.createContext(i);function t(e){const o=r.useContext(s);return r.useMemo((function(){return"function"==typeof e?e(o):{...o,...e}}),[o,e])}function d(e){let o;return o=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:t(e.components),r.createElement(s.Provider,{value:o},e.children)}}}]);