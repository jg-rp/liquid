"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[3915],{3905:(e,t,n)=>{n.d(t,{Zo:()=>s,kt:()=>k});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function l(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},i=Object.keys(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var p=a.createContext({}),d=function(e){var t=a.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):l(l({},t),e)),n},s=function(e){var t=d(e.components);return a.createElement(p.Provider,{value:t},e.children)},u="mdxType",c={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},m=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,i=e.originalType,p=e.parentName,s=o(e,["components","mdxType","originalType","parentName"]),u=d(n),m=r,k=u["".concat(p,".").concat(m)]||u[m]||c[m]||i;return n?a.createElement(k,l(l({ref:t},s),{},{components:n})):a.createElement(k,l({ref:t},s))}));function k(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=n.length,l=new Array(i);l[0]=m;var o={};for(var p in t)hasOwnProperty.call(t,p)&&(o[p]=t[p]);o.originalType=e,o[u]="string"==typeof e?e:r,l[1]=o;for(var d=2;d<i;d++)l[d]=n[d];return a.createElement.apply(null,l)}return a.createElement.apply(null,n)}m.displayName="MDXCreateElement"},9117:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>l,default:()=>c,frontMatter:()=>i,metadata:()=>o,toc:()=>d});var a=n(7462),r=(n(7294),n(3905));const i={id:"Tag"},l="liquid.tag.Tag",o={unversionedId:"api/Tag",id:"api/Tag",title:"liquid.tag.Tag",description:"Base class for all built-in and custom template tags.",source:"@site/docs/api/tag.md",sourceDirName:"api",slug:"/api/Tag",permalink:"/liquid/api/Tag",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/tag.md",tags:[],version:"current",frontMatter:{id:"Tag"},sidebar:"apiSidebar",previous:{title:"liquid.Context",permalink:"/liquid/api/context"},next:{title:"liquid.ast.Node",permalink:"/liquid/api/node"}},p={},d=[{value:"<code>Tag</code>",id:"tag",level:2},{value:"Class Attributes",id:"class-attributes",level:2},{value:"<code>block</code>",id:"block",level:3},{value:"<code>name</code>",id:"name",level:3},{value:"<code>end</code>",id:"end",level:3},{value:"Properties",id:"properties",level:2},{value:"<code>env</code>",id:"env",level:3},{value:"Methods",id:"methods",level:2},{value:"<code>get_node</code>",id:"get_node",level:3},{value:"<code>parse</code>",id:"parse",level:3}],s={toc:d},u="wrapper";function c(e){let{components:t,...n}=e;return(0,r.kt)(u,(0,a.Z)({},s,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"liquidtagtag"},"liquid.tag.Tag"),(0,r.kt)("p",null,"Base class for all built-in and ",(0,r.kt)("a",{parentName:"p",href:"/liquid/guides/custom-tags"},"custom template tags"),"."),(0,r.kt)("h2",{id:"tag"},(0,r.kt)("inlineCode",{parentName:"h2"},"Tag")),(0,r.kt)("p",null,(0,r.kt)("inlineCode",{parentName:"p"},"class Tag(env)")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Parameters"),":"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"env: liquid.Environment")," - The ",(0,r.kt)("a",{parentName:"li",href:"/liquid/api/Environment"},(0,r.kt)("inlineCode",{parentName:"a"},"Environment"))," that manages this tag.")),(0,r.kt)("h2",{id:"class-attributes"},"Class Attributes"),(0,r.kt)("h3",{id:"block"},(0,r.kt)("inlineCode",{parentName:"h3"},"block")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Type"),": ",(0,r.kt)("inlineCode",{parentName:"p"},"bool = True")),(0,r.kt)("p",null,"Indicates if the tag is a block tag."),(0,r.kt)("h3",{id:"name"},(0,r.kt)("inlineCode",{parentName:"h3"},"name")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Type"),": ",(0,r.kt)("inlineCode",{parentName:"p"},'str = ""')),(0,r.kt)("p",null,"The name of the tag. Like ",(0,r.kt)("inlineCode",{parentName:"p"},'"if"')," or ",(0,r.kt)("inlineCode",{parentName:"p"},'"for"'),"."),(0,r.kt)("h3",{id:"end"},(0,r.kt)("inlineCode",{parentName:"h3"},"end")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Type"),": ",(0,r.kt)("inlineCode",{parentName:"p"},'str = ""')),(0,r.kt)("p",null,"The end or closing tag name. If ",(0,r.kt)("inlineCode",{parentName:"p"},"block")," is ",(0,r.kt)("inlineCode",{parentName:"p"},"True"),", ",(0,r.kt)("inlineCode",{parentName:"p"},"end")," must be set. By convention it is\n",(0,r.kt)("inlineCode",{parentName:"p"},'"end<tag.name>"'),"."),(0,r.kt)("h2",{id:"properties"},"Properties"),(0,r.kt)("h3",{id:"env"},(0,r.kt)("inlineCode",{parentName:"h3"},"env")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Type"),": ",(0,r.kt)("inlineCode",{parentName:"p"},"liquid.Environment")),(0,r.kt)("p",null,"The ",(0,r.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.kt)("inlineCode",{parentName:"a"},"Environment"))," that manages this tag."),(0,r.kt)("h2",{id:"methods"},"Methods"),(0,r.kt)("h3",{id:"get_node"},(0,r.kt)("inlineCode",{parentName:"h3"},"get_node")),(0,r.kt)("p",null,(0,r.kt)("inlineCode",{parentName:"p"},"get_node(self, stream: TokenStream) -> Node")),(0,r.kt)("p",null,"Used internally to delegate to ",(0,r.kt)("inlineCode",{parentName:"p"},"Tag.parse"),"."),(0,r.kt)("h3",{id:"parse"},(0,r.kt)("inlineCode",{parentName:"h3"},"parse")),(0,r.kt)("p",null,(0,r.kt)("inlineCode",{parentName:"p"},"parse(self, stream: TokenStream) -> Node:")),(0,r.kt)("p",null,"Abstract method. Return a parse tree node by parsing tokens from the given stream. Every tag must implement ",(0,r.kt)("inlineCode",{parentName:"p"},"parse"),"."))}c.isMDXComponent=!0}}]);