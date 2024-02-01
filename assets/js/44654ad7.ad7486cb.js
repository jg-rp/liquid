"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[7313],{232:(e,l,a)=>{a.r(l),a.d(l,{assets:()=>o,contentTitle:()=>n,default:()=>p,frontMatter:()=>s,metadata:()=>d,toc:()=>r});var i=a(5893),t=a(1151);const s={},n="liquid.template.TemplateAnalysis",d={id:"api/template-analysis",title:"liquid.template.TemplateAnalysis",description:"The result of analyzing a Liquid template using BoundTemplate.analyze().",source:"@site/docs/api/template-analysis.md",sourceDirName:"api",slug:"/api/template-analysis",permalink:"/liquid/api/template-analysis",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/template-analysis.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.ast.Node",permalink:"/liquid/api/node"},next:{title:"liquid.template.ContextualTemplateAnalysis",permalink:"/liquid/api/contextual-template-analysis"}},o={},r=[{value:"<code>TemplateAnalysis</code>",id:"templateanalysis",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>variables</code>",id:"variables",level:3},{value:"<code>local_variables</code>",id:"local_variables",level:3},{value:"<code>global_variables</code>",id:"global_variables",level:3},{value:"<code>filters</code>",id:"filters",level:3},{value:"<code>tags</code>",id:"tags",level:3},{value:"<code>failed_visits</code>",id:"failed_visits",level:3},{value:"<code>unloadable_partials</code>",id:"unloadable_partials",level:3}];function c(e){const l={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",p:"p",...(0,t.useMDXComponents)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(l.h1,{id:"liquidtemplatetemplateanalysis",children:"liquid.template.TemplateAnalysis"}),"\n",(0,i.jsxs)(l.p,{children:["The result of analyzing a Liquid template using ",(0,i.jsx)(l.a,{href:"/liquid/api/BoundTemplate#analyze",children:(0,i.jsx)(l.code,{children:"BoundTemplate.analyze()"})}),"."]}),"\n",(0,i.jsx)(l.h2,{id:"templateanalysis",children:(0,i.jsx)(l.code,{children:"TemplateAnalysis"})}),"\n",(0,i.jsx)(l.p,{children:(0,i.jsx)(l.code,{children:"class TemplateAnalysis(*, variables, local_variables, global_variables, failed_visits, unloadable_partials, filters)"})}),"\n",(0,i.jsxs)(l.p,{children:["Each of the following properties is a dictionary mapping variable names to a list of two-tuples. Each tuple holds the location of a reference to the name as ",(0,i.jsx)(l.code,{children:"(<template name>, <line number>)"}),'. If a name is referenced multiple times, it will appear multiple times in the list. If a name is referenced before it is "assigned", it will appear in ',(0,i.jsx)(l.code,{children:"local_variables"})," and ",(0,i.jsx)(l.code,{children:"global_variables"}),"."]}),"\n",(0,i.jsx)(l.h2,{id:"properties",children:"Properties"}),"\n",(0,i.jsx)(l.h3,{id:"variables",children:(0,i.jsx)(l.code,{children:"variables"})}),"\n",(0,i.jsxs)(l.p,{children:["All referenced variables, whether they are in scope or not. Including references to names such as ",(0,i.jsx)(l.code,{children:"forloop"})," from the ",(0,i.jsx)(l.code,{children:"for"})," tag."]}),"\n",(0,i.jsx)(l.h3,{id:"local_variables",children:(0,i.jsx)(l.code,{children:"local_variables"})}),"\n",(0,i.jsx)(l.p,{children:"Template variables that are added to the template local scope, whether they are subsequently used or not."}),"\n",(0,i.jsx)(l.h3,{id:"global_variables",children:(0,i.jsx)(l.code,{children:"global_variables"})}),"\n",(0,i.jsx)(l.p,{children:'Template variables that, on the given line number and "file", are out of scope or are assumed to be "global". That is, expected to be included by the application developer rather than a template author.'}),"\n",(0,i.jsx)(l.h3,{id:"filters",children:(0,i.jsx)(l.code,{children:"filters"})}),"\n",(0,i.jsxs)(l.p,{children:["The name and locations of ",(0,i.jsx)(l.a,{href:"/liquid/language/introduction#filters",children:"filters"})," used the template."]}),"\n",(0,i.jsx)(l.h3,{id:"tags",children:(0,i.jsx)(l.code,{children:"tags"})}),"\n",(0,i.jsxs)(l.p,{children:["The name and locations of ",(0,i.jsx)(l.a,{href:"/liquid/language/introduction#tags",children:"tags"})," used the template."]}),"\n",(0,i.jsx)(l.h3,{id:"failed_visits",children:(0,i.jsx)(l.code,{children:"failed_visits"})}),"\n",(0,i.jsxs)(l.p,{children:["Names of AST ",(0,i.jsx)(l.code,{children:"Node"})," and ",(0,i.jsx)(l.code,{children:"Expression"})," objects that could not be visited, probably because they do not implement a ",(0,i.jsx)(l.code,{children:"children"})," method."]}),"\n",(0,i.jsx)(l.h3,{id:"unloadable_partials",children:(0,i.jsx)(l.code,{children:"unloadable_partials"})}),"\n",(0,i.jsxs)(l.p,{children:["Names or identifiers of partial templates that could not be loaded. This will be empty if ",(0,i.jsx)(l.code,{children:"follow_partials"})," is ",(0,i.jsx)(l.code,{children:"False"}),"."]})]})}function p(e={}){const{wrapper:l}={...(0,t.useMDXComponents)(),...e.components};return l?(0,i.jsx)(l,{...e,children:(0,i.jsx)(c,{...e})}):c(e)}},1151:(e,l,a)=>{a.r(l),a.d(l,{MDXProvider:()=>d,useMDXComponents:()=>n});var i=a(7294);const t={},s=i.createContext(t);function n(e){const l=i.useContext(s);return i.useMemo((function(){return"function"==typeof e?e(l):{...l,...e}}),[l,e])}function d(e){let l;return l=e.disableParentContext?"function"==typeof e.components?e.components(t):e.components||t:n(e.components),i.createElement(s.Provider,{value:l},e.children)}}}]);