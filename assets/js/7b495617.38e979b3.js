"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[533],{3905:(e,t,n)=>{n.d(t,{Zo:()=>u,kt:()=>f});var r=n(7294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,r,o=function(e,t){if(null==e)return{};var n,r,o={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var d=r.createContext({}),p=function(e){var t=r.useContext(d),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},u=function(e){var t=p(e.components);return r.createElement(d.Provider,{value:t},e.children)},c="mdxType",s={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},k=r.forwardRef((function(e,t){var n=e.components,o=e.mdxType,a=e.originalType,d=e.parentName,u=l(e,["components","mdxType","originalType","parentName"]),c=p(n),k=o,f=c["".concat(d,".").concat(k)]||c[k]||s[k]||a;return n?r.createElement(f,i(i({ref:t},u),{},{components:n})):r.createElement(f,i({ref:t},u))}));function f(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var a=n.length,i=new Array(a);i[0]=k;var l={};for(var d in t)hasOwnProperty.call(t,d)&&(l[d]=t[d]);l.originalType=e,l[c]="string"==typeof e?e:o,i[1]=l;for(var p=2;p<a;p++)i[p]=n[p];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}k.displayName="MDXCreateElement"},8314:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>d,contentTitle:()=>i,default:()=>s,frontMatter:()=>a,metadata:()=>l,toc:()=>p});var r=n(7462),o=(n(7294),n(3905));const a={},i="liquid.ast.Node",l={unversionedId:"api/node",id:"api/node",title:"liquid.ast.Node",description:"Abstract base class for all nodes in a parse tree.",source:"@site/docs/api/node.md",sourceDirName:"api",slug:"/api/node",permalink:"/liquid/api/node",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/node.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.tag.Tag",permalink:"/liquid/api/Tag"},next:{title:"liquid.template.TemplateAnalysis",permalink:"/liquid/api/template-analysis"}},d={},p=[{value:"<code>Node</code>",id:"node",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>tok</code>",id:"tok",level:3},{value:"Methods",id:"methods",level:2},{value:"<code>token</code>",id:"token",level:3},{value:"<code>render</code>",id:"render",level:3},{value:"<code>render_async</code>",id:"render_async",level:3},{value:"<code>render_to_output</code>",id:"render_to_output",level:3},{value:"<code>render_to_output_async</code>",id:"render_to_output_async",level:3}],u={toc:p},c="wrapper";function s(e){let{components:t,...n}=e;return(0,o.kt)(c,(0,r.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("h1",{id:"liquidastnode"},"liquid.ast.Node"),(0,o.kt)("p",null,"Abstract base class for all nodes in a parse tree."),(0,o.kt)("h2",{id:"node"},(0,o.kt)("inlineCode",{parentName:"h2"},"Node")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"class Node()")),(0,o.kt)("h2",{id:"properties"},"Properties"),(0,o.kt)("h3",{id:"tok"},(0,o.kt)("inlineCode",{parentName:"h3"},"tok")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"liquid.token.Token")),(0,o.kt)("p",null,"The token that started this node. All subclasses of include a ",(0,o.kt)("inlineCode",{parentName:"p"},"tok")," property or override ",(0,o.kt)("a",{parentName:"p",href:"#token"},(0,o.kt)("inlineCode",{parentName:"a"},"token()")),"."),(0,o.kt)("h2",{id:"methods"},"Methods"),(0,o.kt)("h3",{id:"token"},(0,o.kt)("inlineCode",{parentName:"h3"},"token")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"token() -> liquid.token.Token")),(0,o.kt)("p",null,"Return the token that started this node. Looks for ",(0,o.kt)("a",{parentName:"p",href:"#tok"},(0,o.kt)("inlineCode",{parentName:"a"},"self.tok")),"."),(0,o.kt)("h3",{id:"render"},(0,o.kt)("inlineCode",{parentName:"h3"},"render")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"render(context: Context, buffer: TextIO) -> Optional[bool]")),(0,o.kt)("p",null,"Check disabled tags before delegating to ",(0,o.kt)("a",{parentName:"p",href:"#render-to-output"},(0,o.kt)("inlineCode",{parentName:"a"},"render_to_output()")),"."),(0,o.kt)("h3",{id:"render_async"},(0,o.kt)("inlineCode",{parentName:"h3"},"render_async")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"async render_async(context: Context, buffer: TextIO) -> Optional[bool]")),(0,o.kt)("p",null,"An async version of ",(0,o.kt)("a",{parentName:"p",href:"#render"},(0,o.kt)("inlineCode",{parentName:"a"},"render()"))),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Raises"),": DisabledTagError if ",(0,o.kt)("inlineCode",{parentName:"p"},"self.token()")," is disabled in the current context."),(0,o.kt)("h3",{id:"render_to_output"},(0,o.kt)("inlineCode",{parentName:"h3"},"render_to_output")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"render_to_output(context: Context, buffer: TextIO) -> Optional[bool]")),(0,o.kt)("p",null,"Abstract method. Render this node to the output buffer with the given context."),(0,o.kt)("h3",{id:"render_to_output_async"},(0,o.kt)("inlineCode",{parentName:"h3"},"render_to_output_async")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"async render_to_output_async(context: Context, buffer: TextIO) -> Optional[bool]")),(0,o.kt)("p",null,"An async version of ",(0,o.kt)("a",{parentName:"p",href:"#render-to-output"},(0,o.kt)("inlineCode",{parentName:"a"},"render_to_output()")),". Delegates to ",(0,o.kt)("inlineCode",{parentName:"p"},"render_to_output")," by default."))}s.isMDXComponent=!0}}]);