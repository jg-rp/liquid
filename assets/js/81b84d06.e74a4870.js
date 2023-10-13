"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[7444],{3905:(e,n,a)=>{a.r(n),a.d(n,{MDXContext:()=>d,MDXProvider:()=>u,mdx:()=>y,useMDXComponents:()=>p,withMDXComponents:()=>m});var t=a(7294);function l(e,n,a){return n in e?Object.defineProperty(e,n,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[n]=a,e}function i(){return i=Object.assign||function(e){for(var n=1;n<arguments.length;n++){var a=arguments[n];for(var t in a)Object.prototype.hasOwnProperty.call(a,t)&&(e[t]=a[t])}return e},i.apply(this,arguments)}function r(e,n){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var t=Object.getOwnPropertySymbols(e);n&&(t=t.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),a.push.apply(a,t)}return a}function s(e){for(var n=1;n<arguments.length;n++){var a=null!=arguments[n]?arguments[n]:{};n%2?r(Object(a),!0).forEach((function(n){l(e,n,a[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):r(Object(a)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(a,n))}))}return e}function o(e,n){if(null==e)return{};var a,t,l=function(e,n){if(null==e)return{};var a,t,l={},i=Object.keys(e);for(t=0;t<i.length;t++)a=i[t],n.indexOf(a)>=0||(l[a]=e[a]);return l}(e,n);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(t=0;t<i.length;t++)a=i[t],n.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(l[a]=e[a])}return l}var d=t.createContext({}),m=function(e){return function(n){var a=p(n.components);return t.createElement(e,i({},n,{components:a}))}},p=function(e){var n=t.useContext(d),a=n;return e&&(a="function"==typeof e?e(n):s(s({},n),e)),a},u=function(e){var n=p(e.components);return t.createElement(d.Provider,{value:n},e.children)},c="mdxType",f={inlineCode:"code",wrapper:function(e){var n=e.children;return t.createElement(t.Fragment,{},n)}},x=t.forwardRef((function(e,n){var a=e.components,l=e.mdxType,i=e.originalType,r=e.parentName,d=o(e,["components","mdxType","originalType","parentName"]),m=p(a),u=l,c=m["".concat(r,".").concat(u)]||m[u]||f[u]||i;return a?t.createElement(c,s(s({ref:n},d),{},{components:a})):t.createElement(c,s({ref:n},d))}));function y(e,n){var a=arguments,l=n&&n.mdxType;if("string"==typeof e||l){var i=a.length,r=new Array(i);r[0]=x;var s={};for(var o in n)hasOwnProperty.call(n,o)&&(s[o]=n[o]);s.originalType=e,s[c]="string"==typeof e?e:l,r[1]=s;for(var d=2;d<i;d++)r[d]=a[d];return t.createElement.apply(null,r)}return t.createElement.apply(null,a)}x.displayName="MDXCreateElement"},4539:(e,n,a)=>{a.r(n),a.d(n,{assets:()=>o,contentTitle:()=>r,default:()=>u,frontMatter:()=>i,metadata:()=>s,toc:()=>d});var t=a(7462),l=(a(7294),a(3905));const i={},r="Contextual Template Analysis",s={unversionedId:"guides/contextual-template-analysis",id:"guides/contextual-template-analysis",title:"Contextual Template Analysis",description:"_New in version 1.3.0_",source:"@site/docs/guides/contextual-template-analysis.md",sourceDirName:"guides",slug:"/guides/contextual-template-analysis",permalink:"/liquid/guides/contextual-template-analysis",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/contextual-template-analysis.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Static Template Analysis",permalink:"/liquid/guides/static-template-analysis"},next:{title:"Tag Analysis",permalink:"/liquid/guides/tag-analysis"}},o={},d=[{value:"Limitations",id:"limitations",level:2},{value:"Usage",id:"usage",level:2},{value:"Local Variables",id:"local-variables",level:2},{value:"Undefined variables",id:"undefined-variables",level:2},{value:"Filters",id:"filters",level:2}],m={toc:d},p="wrapper";function u(e){let{components:n,...a}=e;return(0,l.mdx)(p,(0,t.default)({},m,a,{components:n,mdxType:"MDXLayout"}),(0,l.mdx)("h1",{id:"contextual-template-analysis"},"Contextual Template Analysis"),(0,l.mdx)("p",null,(0,l.mdx)("strong",{parentName:"p"},(0,l.mdx)("em",{parentName:"strong"},"New in version 1.3.0"))),(0,l.mdx)("p",null,"Complementing ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/guides/static-template-analysis"},"static template analysis"),", added in Python Liquid version 1.2.0, contextual template analysis renders a template and captures information about template variable and filter usage as it goes."),(0,l.mdx)("p",null,"Given some ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/introduction/render-context"},"render context")," data, ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#analyze_with_context"},(0,l.mdx)("inlineCode",{parentName:"a"},"BoundTemplate.analyze_with_context()"))," will visit nodes in a template's syntax tree as if it were being rendered, excluding those nodes that are not reachable using the current render context."),(0,l.mdx)("h2",{id:"limitations"},"Limitations"),(0,l.mdx)("p",null,"Due to some unfortunate design decisions, Python Liquid does not support template introspection from within a render context or ",(0,l.mdx)("inlineCode",{parentName:"p"},"Expression")," object. Meaning line numbers and template names are not available when using contextual template analysis. Only variable names are reported along with the number of times they were referenced. This is not the case with ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/guides/static-template-analysis"},"static template analysis"),"."),(0,l.mdx)("p",null,"It's also not currently possible to detect names added to a block's scope. For example, ",(0,l.mdx)("inlineCode",{parentName:"p"},"forloop.index")," will be included in the results object if referenced within a for loop block."),(0,l.mdx)("h2",{id:"usage"},"Usage"),(0,l.mdx)("p",null,(0,l.mdx)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#analyze_with_context"},(0,l.mdx)("inlineCode",{parentName:"a"},"BoundTemplate.analyze_with_context()"))," and ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#analyze_with_context_async"},(0,l.mdx)("inlineCode",{parentName:"a"},"BoundTemplate.analyze_with_context_async()"))," accept the same arguments as ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#render"},(0,l.mdx)("inlineCode",{parentName:"a"},"BoundTemplate.render()")),". The returned object is an instance of ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/api/contextual-template-analysis"},(0,l.mdx)("inlineCode",{parentName:"a"},"ContextualTemplateAnalysis")),". Each of its properties is a dictionary mapping template variable name to the number of times that name was referenced."),(0,l.mdx)("p",null,(0,l.mdx)("inlineCode",{parentName:"p"},"ContextualTemplateAnalysis.all_variables")," includes all variable names discovered while rendering a template given some render context data. It will not include variables from blocks that would not have been rendered."),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.all_variables))\n\n\n# `user` is defined\nanalysis = template.analyze_with_context(user={"name": "Sally"})\nprint(list(analysis.all_variables))\n')),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"['user', 'fallback']\n['user', 'user.name']\n")),(0,l.mdx)("h2",{id:"local-variables"},"Local Variables"),(0,l.mdx)("p",null,(0,l.mdx)("inlineCode",{parentName:"p"},"ContextualTemplateAnalysis.local_variables")," includes variable names that have been assigned with the ",(0,l.mdx)("inlineCode",{parentName:"p"},"assign"),", ",(0,l.mdx)("inlineCode",{parentName:"p"},"capture"),", ",(0,l.mdx)("inlineCode",{parentName:"p"},"increment")," or ",(0,l.mdx)("inlineCode",{parentName:"p"},"decrement")," tags, or any custom tag that uses ",(0,l.mdx)("inlineCode",{parentName:"p"},"Context.assign()"),"."),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.local_variables))\n')),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"['fallback']\n")),(0,l.mdx)("h2",{id:"undefined-variables"},"Undefined variables"),(0,l.mdx)("p",null,(0,l.mdx)("inlineCode",{parentName:"p"},"ContextualTemplateAnalysis.undefined_variables")," includes variable names that could not be resolved in the current render context. If a name is referenced before it is assigned, it will appear in ",(0,l.mdx)("inlineCode",{parentName:"p"},"undefined_variables")," and ",(0,l.mdx)("inlineCode",{parentName:"p"},"local_variables"),"."),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template("""\\\n{% assign fallback = \'anonymous\' %}\n{{ nosuchthing }}\n\n{% if user %}\n  Hello, {{ user.name }}.\n{% else %}\n  Hello, {{ fallback }}\n{% endif %}\n""")\n\n# `user` is undefined\nanalysis = template.analyze_with_context()\nprint(list(analysis.undefined_variables))\n')),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"['nosuchthing', 'user']\n")),(0,l.mdx)("h2",{id:"filters"},"Filters"),(0,l.mdx)("p",null,(0,l.mdx)("strong",{parentName:"p"},(0,l.mdx)("em",{parentName:"strong"},"New in version 1.7.0"))),(0,l.mdx)("p",null,(0,l.mdx)("inlineCode",{parentName:"p"},"ContextualTemplateAnalysis.filters")," includes the names of filters used in a template, including those found in ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/language/tags#include"},"included")," or ",(0,l.mdx)("a",{parentName:"p",href:"/liquid/language/tags#render"},"rendered")," templates."),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template(\n    """\\\n{% assign fallback = \'anonymous\' %}\n{{ nosuchthing }}\n\n{% if user %}\n  Hello, {{ user.name | upcase }}.\n{% else %}\n  Hello, {{ fallback | downcase }}\n{% endif %}\n"""\n)\n\nanalysis = template.analyze_with_context(user="Sue")\nprint(list(analysis.filters))\n')),(0,l.mdx)("pre",null,(0,l.mdx)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"['upcase']\n")))}u.isMDXComponent=!0}}]);