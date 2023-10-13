"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[7313],{3905:(e,a,t)=>{t.r(a),t.d(a,{MDXContext:()=>p,MDXProvider:()=>u,mdx:()=>v,useMDXComponents:()=>m,withMDXComponents:()=>s});var l=t(7294);function n(e,a,t){return a in e?Object.defineProperty(e,a,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[a]=t,e}function i(){return i=Object.assign||function(e){for(var a=1;a<arguments.length;a++){var t=arguments[a];for(var l in t)Object.prototype.hasOwnProperty.call(t,l)&&(e[l]=t[l])}return e},i.apply(this,arguments)}function r(e,a){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);a&&(l=l.filter((function(a){return Object.getOwnPropertyDescriptor(e,a).enumerable}))),t.push.apply(t,l)}return t}function o(e){for(var a=1;a<arguments.length;a++){var t=null!=arguments[a]?arguments[a]:{};a%2?r(Object(t),!0).forEach((function(a){n(e,a,t[a])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):r(Object(t)).forEach((function(a){Object.defineProperty(e,a,Object.getOwnPropertyDescriptor(t,a))}))}return e}function d(e,a){if(null==e)return{};var t,l,n=function(e,a){if(null==e)return{};var t,l,n={},i=Object.keys(e);for(l=0;l<i.length;l++)t=i[l],a.indexOf(t)>=0||(n[t]=e[t]);return n}(e,a);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(l=0;l<i.length;l++)t=i[l],a.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(n[t]=e[t])}return n}var p=l.createContext({}),s=function(e){return function(a){var t=m(a.components);return l.createElement(e,i({},a,{components:t}))}},m=function(e){var a=l.useContext(p),t=a;return e&&(t="function"==typeof e?e(a):o(o({},a),e)),t},u=function(e){var a=m(e.components);return l.createElement(p.Provider,{value:a},e.children)},c="mdxType",f={inlineCode:"code",wrapper:function(e){var a=e.children;return l.createElement(l.Fragment,{},a)}},b=l.forwardRef((function(e,a){var t=e.components,n=e.mdxType,i=e.originalType,r=e.parentName,p=d(e,["components","mdxType","originalType","parentName"]),s=m(t),u=n,c=s["".concat(r,".").concat(u)]||s[u]||f[u]||i;return t?l.createElement(c,o(o({ref:a},p),{},{components:t})):l.createElement(c,o({ref:a},p))}));function v(e,a){var t=arguments,n=a&&a.mdxType;if("string"==typeof e||n){var i=t.length,r=new Array(i);r[0]=b;var o={};for(var d in a)hasOwnProperty.call(a,d)&&(o[d]=a[d]);o.originalType=e,o[c]="string"==typeof e?e:n,r[1]=o;for(var p=2;p<i;p++)r[p]=t[p];return l.createElement.apply(null,r)}return l.createElement.apply(null,t)}b.displayName="MDXCreateElement"},9728:(e,a,t)=>{t.r(a),t.d(a,{assets:()=>d,contentTitle:()=>r,default:()=>u,frontMatter:()=>i,metadata:()=>o,toc:()=>p});var l=t(7462),n=(t(7294),t(3905));const i={},r="liquid.template.TemplateAnalysis",o={unversionedId:"api/template-analysis",id:"api/template-analysis",title:"liquid.template.TemplateAnalysis",description:"The result of analyzing a Liquid template using BoundTemplate.analyze().",source:"@site/docs/api/template-analysis.md",sourceDirName:"api",slug:"/api/template-analysis",permalink:"/liquid/api/template-analysis",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/template-analysis.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.ast.Node",permalink:"/liquid/api/node"},next:{title:"liquid.template.ContextualTemplateAnalysis",permalink:"/liquid/api/contextual-template-analysis"}},d={},p=[{value:"<code>TemplateAnalysis</code>",id:"templateanalysis",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>variables</code>",id:"variables",level:3},{value:"<code>local_variables</code>",id:"local_variables",level:3},{value:"<code>global_variables</code>",id:"global_variables",level:3},{value:"<code>filters</code>",id:"filters",level:3},{value:"<code>tags</code>",id:"tags",level:3},{value:"<code>failed_visits</code>",id:"failed_visits",level:3},{value:"<code>unloadable_partials</code>",id:"unloadable_partials",level:3}],s={toc:p},m="wrapper";function u(e){let{components:a,...t}=e;return(0,n.mdx)(m,(0,l.default)({},s,t,{components:a,mdxType:"MDXLayout"}),(0,n.mdx)("h1",{id:"liquidtemplatetemplateanalysis"},"liquid.template.TemplateAnalysis"),(0,n.mdx)("p",null,"The result of analyzing a Liquid template using ",(0,n.mdx)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#analyze"},(0,n.mdx)("inlineCode",{parentName:"a"},"BoundTemplate.analyze()")),"."),(0,n.mdx)("h2",{id:"templateanalysis"},(0,n.mdx)("inlineCode",{parentName:"h2"},"TemplateAnalysis")),(0,n.mdx)("p",null,(0,n.mdx)("inlineCode",{parentName:"p"},"class TemplateAnalysis(*, variables, local_variables, global_variables, failed_visits, unloadable_partials, filters)")),(0,n.mdx)("p",null,"Each of the following properties is a dictionary mapping variable names to a list of two-tuples. Each tuple holds the location of a reference to the name as ",(0,n.mdx)("inlineCode",{parentName:"p"},"(<template name>, <line number>)"),'. If a name is referenced multiple times, it will appear multiple times in the list. If a name is referenced before it is "assigned", it will appear in ',(0,n.mdx)("inlineCode",{parentName:"p"},"local_variables")," and ",(0,n.mdx)("inlineCode",{parentName:"p"},"global_variables"),"."),(0,n.mdx)("h2",{id:"properties"},"Properties"),(0,n.mdx)("h3",{id:"variables"},(0,n.mdx)("inlineCode",{parentName:"h3"},"variables")),(0,n.mdx)("p",null,"All referenced variables, whether they are in scope or not. Including references to names such as ",(0,n.mdx)("inlineCode",{parentName:"p"},"forloop")," from the ",(0,n.mdx)("inlineCode",{parentName:"p"},"for")," tag."),(0,n.mdx)("h3",{id:"local_variables"},(0,n.mdx)("inlineCode",{parentName:"h3"},"local_variables")),(0,n.mdx)("p",null,"Template variables that are added to the template local scope, whether they are subsequently used or not."),(0,n.mdx)("h3",{id:"global_variables"},(0,n.mdx)("inlineCode",{parentName:"h3"},"global_variables")),(0,n.mdx)("p",null,'Template variables that, on the given line number and "file", are out of scope or are assumed to be "global". That is, expected to be included by the application developer rather than a template author.'),(0,n.mdx)("h3",{id:"filters"},(0,n.mdx)("inlineCode",{parentName:"h3"},"filters")),(0,n.mdx)("p",null,"The name and locations of ",(0,n.mdx)("a",{parentName:"p",href:"/liquid/language/introduction#filters"},"filters")," used the template."),(0,n.mdx)("h3",{id:"tags"},(0,n.mdx)("inlineCode",{parentName:"h3"},"tags")),(0,n.mdx)("p",null,"The name and locations of ",(0,n.mdx)("a",{parentName:"p",href:"/liquid/language/introduction#tags"},"tags")," used the template."),(0,n.mdx)("h3",{id:"failed_visits"},(0,n.mdx)("inlineCode",{parentName:"h3"},"failed_visits")),(0,n.mdx)("p",null,"Names of AST ",(0,n.mdx)("inlineCode",{parentName:"p"},"Node")," and ",(0,n.mdx)("inlineCode",{parentName:"p"},"Expression")," objects that could not be visited, probably because they do not implement a ",(0,n.mdx)("inlineCode",{parentName:"p"},"children")," method."),(0,n.mdx)("h3",{id:"unloadable_partials"},(0,n.mdx)("inlineCode",{parentName:"h3"},"unloadable_partials")),(0,n.mdx)("p",null,"Names or identifiers of partial templates that could not be loaded. This will be empty if ",(0,n.mdx)("inlineCode",{parentName:"p"},"follow_partials")," is ",(0,n.mdx)("inlineCode",{parentName:"p"},"False"),"."))}u.isMDXComponent=!0}}]);