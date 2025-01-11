"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4486],{4726:(e,n,a)=>{a.r(n),a.d(n,{assets:()=>d,contentTitle:()=>r,default:()=>u,frontMatter:()=>s,metadata:()=>t,toc:()=>o});const t=JSON.parse('{"id":"guides/contextual-template-analysis","title":"Contextual Template Analysis","description":"_New in version 1.3.0_","source":"@site/docs/guides/contextual-template-analysis.md","sourceDirName":"guides","slug":"/guides/contextual-template-analysis","permalink":"/liquid/guides/contextual-template-analysis","draft":false,"unlisted":false,"editUrl":"https://github.com/jg-rp/liquid/tree/docs/docs/guides/contextual-template-analysis.md","tags":[],"version":"current","frontMatter":{},"sidebar":"docsSidebar","previous":{"title":"Static Template Analysis","permalink":"/liquid/guides/static-template-analysis"},"next":{"title":"Tag Analysis","permalink":"/liquid/guides/tag-analysis"}}');var l=a(4848),i=a(8453);const s={},r="Contextual Template Analysis",d={},o=[{value:"Limitations",id:"limitations",level:2},{value:"Usage",id:"usage",level:2},{value:"Local Variables",id:"local-variables",level:2},{value:"Undefined variables",id:"undefined-variables",level:2},{value:"Filters",id:"filters",level:2}];function c(e){const n={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",header:"header",p:"p",pre:"pre",strong:"strong",...(0,i.useMDXComponents)(),...e.components};return(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(n.header,{children:(0,l.jsx)(n.h1,{id:"contextual-template-analysis",children:"Contextual Template Analysis"})}),"\n",(0,l.jsx)(n.p,{children:(0,l.jsx)(n.strong,{children:(0,l.jsx)(n.em,{children:"New in version 1.3.0"})})}),"\n",(0,l.jsxs)(n.p,{children:["Complementing ",(0,l.jsx)(n.a,{href:"/liquid/guides/static-template-analysis",children:"static template analysis"}),", added in Python Liquid version 1.2.0, contextual template analysis renders a template and captures information about template variable and filter usage as it goes."]}),"\n",(0,l.jsxs)(n.p,{children:["Given some ",(0,l.jsx)(n.a,{href:"/liquid/introduction/render-context",children:"render context"})," data, ",(0,l.jsx)(n.a,{href:"/liquid/api/BoundTemplate#analyze_with_context",children:(0,l.jsx)(n.code,{children:"BoundTemplate.analyze_with_context()"})})," will visit nodes in a template's syntax tree as if it were being rendered, excluding those nodes that are not reachable using the current render context."]}),"\n",(0,l.jsx)(n.h2,{id:"limitations",children:"Limitations"}),"\n",(0,l.jsxs)(n.p,{children:["Due to some unfortunate design decisions, Python Liquid does not support template introspection from within a render context or ",(0,l.jsx)(n.code,{children:"Expression"})," object. Meaning line numbers and template names are not available when using contextual template analysis. Only variable names are reported along with the number of times they were referenced. This is not the case with ",(0,l.jsx)(n.a,{href:"/liquid/guides/static-template-analysis",children:"static template analysis"}),"."]}),"\n",(0,l.jsxs)(n.p,{children:["It's also not currently possible to detect names added to a block's scope. For example, ",(0,l.jsx)(n.code,{children:"forloop.index"})," will be included in the results object if referenced within a for loop block."]}),"\n",(0,l.jsx)(n.h2,{id:"usage",children:"Usage"}),"\n",(0,l.jsxs)(n.p,{children:[(0,l.jsx)(n.a,{href:"/liquid/api/BoundTemplate#analyze_with_context",children:(0,l.jsx)(n.code,{children:"BoundTemplate.analyze_with_context()"})})," and ",(0,l.jsx)(n.a,{href:"/liquid/api/BoundTemplate#analyze_with_context_async",children:(0,l.jsx)(n.code,{children:"BoundTemplate.analyze_with_context_async()"})})," accept the same arguments as ",(0,l.jsx)(n.a,{href:"/liquid/api/BoundTemplate#render",children:(0,l.jsx)(n.code,{children:"BoundTemplate.render()"})}),". The returned object is an instance of ",(0,l.jsx)(n.a,{href:"/liquid/api/contextual-template-analysis",children:(0,l.jsx)(n.code,{children:"ContextualTemplateAnalysis"})}),". Each of its properties is a dictionary mapping template variable name to the number of times that name was referenced."]}),"\n",(0,l.jsxs)(n.p,{children:[(0,l.jsx)(n.code,{children:"ContextualTemplateAnalysis.all_variables"})," includes all variable names discovered while rendering a template given some render context data. It will not include variables from blocks that would not have been rendered."]}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-python",children:'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.all_variables))\n\n\n# `user` is defined\nanalysis = template.analyze_with_context(user={"name": "Sally"})\nprint(list(analysis.all_variables))\n'})}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"['user', 'fallback']\n['user', 'user.name']\n"})}),"\n",(0,l.jsx)(n.h2,{id:"local-variables",children:"Local Variables"}),"\n",(0,l.jsxs)(n.p,{children:[(0,l.jsx)(n.code,{children:"ContextualTemplateAnalysis.local_variables"})," includes variable names that have been assigned with the ",(0,l.jsx)(n.code,{children:"assign"}),", ",(0,l.jsx)(n.code,{children:"capture"}),", ",(0,l.jsx)(n.code,{children:"increment"})," or ",(0,l.jsx)(n.code,{children:"decrement"})," tags, or any custom tag that uses ",(0,l.jsx)(n.code,{children:"Context.assign()"}),"."]}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-python",children:'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.local_variables))\n'})}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"['fallback']\n"})}),"\n",(0,l.jsx)(n.h2,{id:"undefined-variables",children:"Undefined variables"}),"\n",(0,l.jsxs)(n.p,{children:[(0,l.jsx)(n.code,{children:"ContextualTemplateAnalysis.undefined_variables"})," includes variable names that could not be resolved in the current render context. If a name is referenced before it is assigned, it will appear in ",(0,l.jsx)(n.code,{children:"undefined_variables"})," and ",(0,l.jsx)(n.code,{children:"local_variables"}),"."]}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-python",children:'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{{ nosuchthing }}\n\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.undefined_variables))\n'})}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"['nosuchthing', 'user']\n"})}),"\n",(0,l.jsx)(n.h2,{id:"filters",children:"Filters"}),"\n",(0,l.jsx)(n.p,{children:(0,l.jsx)(n.strong,{children:(0,l.jsx)(n.em,{children:"New in version 1.7.0"})})}),"\n",(0,l.jsxs)(n.p,{children:[(0,l.jsx)(n.code,{children:"ContextualTemplateAnalysis.filters"})," includes the names of filters used in a template, including those found in ",(0,l.jsx)(n.a,{href:"/liquid/language/tags#include",children:"included"})," or ",(0,l.jsx)(n.a,{href:"/liquid/language/tags#render",children:"rendered"})," templates."]}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-python",children:'from liquid import Template\n\ntemplate = Template(\n    """\\\n{% assign fallback = \'anonymous\' %}\n{{ nosuchthing }}\n\n{% if user %}\n  Hello, {{ user.name | upcase }}.\n{% else %}\n  Hello, {{ fallback | downcase }}\n{% endif %}\n"""\n)\n\nanalysis = template.analyze_with_context(user="Sue")\nprint(list(analysis.filters))\n'})}),"\n",(0,l.jsx)(n.pre,{children:(0,l.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"['upcase']\n"})})]})}function u(e={}){const{wrapper:n}={...(0,i.useMDXComponents)(),...e.components};return n?(0,l.jsx)(n,{...e,children:(0,l.jsx)(c,{...e})}):c(e)}},8453:(e,n,a)=>{a.r(n),a.d(n,{MDXProvider:()=>r,useMDXComponents:()=>s});var t=a(6540);const l={},i=t.createContext(l);function s(e){const n=t.useContext(i);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(l):e.components||l:s(e.components),t.createElement(i.Provider,{value:n},e.children)}}}]);