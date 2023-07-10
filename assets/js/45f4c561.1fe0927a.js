"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[5768],{3905:(e,t,a)=>{a.d(t,{Zo:()=>u,kt:()=>f});var n=a(7294);function l(e,t,a){return t in e?Object.defineProperty(e,t,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[t]=a,e}function i(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,n)}return a}function r(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?i(Object(a),!0).forEach((function(t){l(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):i(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}function o(e,t){if(null==e)return{};var a,n,l=function(e,t){if(null==e)return{};var a,n,l={},i=Object.keys(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||(l[a]=e[a]);return l}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(l[a]=e[a])}return l}var s=n.createContext({}),p=function(e){var t=n.useContext(s),a=t;return e&&(a="function"==typeof e?e(t):r(r({},t),e)),a},u=function(e){var t=p(e.components);return n.createElement(s.Provider,{value:t},e.children)},d="mdxType",c={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},m=n.forwardRef((function(e,t){var a=e.components,l=e.mdxType,i=e.originalType,s=e.parentName,u=o(e,["components","mdxType","originalType","parentName"]),d=p(a),m=l,f=d["".concat(s,".").concat(m)]||d[m]||c[m]||i;return a?n.createElement(f,r(r({ref:t},u),{},{components:a})):n.createElement(f,r({ref:t},u))}));function f(e,t){var a=arguments,l=t&&t.mdxType;if("string"==typeof e||l){var i=a.length,r=new Array(i);r[0]=m;var o={};for(var s in t)hasOwnProperty.call(t,s)&&(o[s]=t[s]);o.originalType=e,o[d]="string"==typeof e?e:l,r[1]=o;for(var p=2;p<i;p++)r[p]=a[p];return n.createElement.apply(null,r)}return n.createElement.apply(null,a)}m.displayName="MDXCreateElement"},3705:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>s,contentTitle:()=>r,default:()=>c,frontMatter:()=>i,metadata:()=>o,toc:()=>p});var n=a(7462),l=(a(7294),a(3905));const i={},r="liquid.template.ContextualTemplateAnalysis",o={unversionedId:"api/contextual-template-analysis",id:"api/contextual-template-analysis",title:"liquid.template.ContextualTemplateAnalysis",description:"The result of analyzing a Liquid template using BoundTemplate.analyzewithcontext().",source:"@site/docs/api/contextual-template-analysis.md",sourceDirName:"api",slug:"/api/contextual-template-analysis",permalink:"/liquid/api/contextual-template-analysis",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/contextual-template-analysis.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.template.TemplateAnalysis",permalink:"/liquid/api/template-analysis"},next:{title:"liquid.TagAnalysis",permalink:"/liquid/api/tag-analysis"}},s={},p=[{value:"<code>ContextualTemplateAnalysis</code>",id:"contextualtemplateanalysis",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>all_variables</code>",id:"all_variables",level:3},{value:"<code>local_variables</code>",id:"local_variables",level:3},{value:"<code>undefined_variables</code>",id:"undefined_variables",level:3},{value:"<code>filters</code>",id:"filters",level:3}],u={toc:p},d="wrapper";function c(e){let{components:t,...a}=e;return(0,l.kt)(d,(0,n.Z)({},u,a,{components:t,mdxType:"MDXLayout"}),(0,l.kt)("h1",{id:"liquidtemplatecontextualtemplateanalysis"},"liquid.template.ContextualTemplateAnalysis"),(0,l.kt)("p",null,"The result of analyzing a Liquid template using ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#analyze_with_context"},(0,l.kt)("inlineCode",{parentName:"a"},"BoundTemplate.analyze_with_context()")),"."),(0,l.kt)("h2",{id:"contextualtemplateanalysis"},(0,l.kt)("inlineCode",{parentName:"h2"},"ContextualTemplateAnalysis")),(0,l.kt)("p",null,(0,l.kt)("inlineCode",{parentName:"p"},"class ContextualTemplateAnalysis(*, all_variables, local_variables, undefined_variables, filters)")),(0,l.kt)("p",null,"Each of the following properties is a dictionary mapping variable or filter names to the number of times that variable was referenced."),(0,l.kt)("h2",{id:"properties"},"Properties"),(0,l.kt)("h3",{id:"all_variables"},(0,l.kt)("inlineCode",{parentName:"h3"},"all_variables")),(0,l.kt)("p",null,"All variables references along a path through the template's syntax tree."),(0,l.kt)("h3",{id:"local_variables"},(0,l.kt)("inlineCode",{parentName:"h3"},"local_variables")),(0,l.kt)("p",null,"The names of variables assigned using the built-in ",(0,l.kt)("inlineCode",{parentName:"p"},"assign"),", ",(0,l.kt)("inlineCode",{parentName:"p"},"capture"),", ",(0,l.kt)("inlineCode",{parentName:"p"},"increment")," or ",(0,l.kt)("inlineCode",{parentName:"p"},"decrement")," tags, or any custom tag that uses ",(0,l.kt)("inlineCode",{parentName:"p"},"Context.assign()"),"."),(0,l.kt)("h3",{id:"undefined_variables"},(0,l.kt)("inlineCode",{parentName:"h3"},"undefined_variables")),(0,l.kt)("p",null,"The names of variables that could not be resolved. If a name is referenced before it is assigned, it will appear in ",(0,l.kt)("inlineCode",{parentName:"p"},"undefined_variables")," and ",(0,l.kt)("inlineCode",{parentName:"p"},"local_variables"),"."),(0,l.kt)("h3",{id:"filters"},(0,l.kt)("inlineCode",{parentName:"h3"},"filters")),(0,l.kt)("p",null,"The names of ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/introduction#filters"},"filters")," found in the template and any ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/tags#include"},"included")," or ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/tags#render"},"rendered")," templates."))}c.isMDXComponent=!0}}]);