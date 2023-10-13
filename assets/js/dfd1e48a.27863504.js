"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[3915],{3905:(e,n,t)=>{t.r(n),t.d(n,{MDXContext:()=>p,MDXProvider:()=>u,mdx:()=>f,useMDXComponents:()=>s,withMDXComponents:()=>m});var a=t(7294);function r(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function i(){return i=Object.assign||function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var a in t)Object.prototype.hasOwnProperty.call(t,a)&&(e[a]=t[a])}return e},i.apply(this,arguments)}function o(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);n&&(a=a.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,a)}return t}function d(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?o(Object(t),!0).forEach((function(n){r(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):o(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function l(e,n){if(null==e)return{};var t,a,r=function(e,n){if(null==e)return{};var t,a,r={},i=Object.keys(e);for(a=0;a<i.length;a++)t=i[a],n.indexOf(t)>=0||(r[t]=e[t]);return r}(e,n);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)t=i[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(r[t]=e[t])}return r}var p=a.createContext({}),m=function(e){return function(n){var t=s(n.components);return a.createElement(e,i({},n,{components:t}))}},s=function(e){var n=a.useContext(p),t=n;return e&&(t="function"==typeof e?e(n):d(d({},n),e)),t},u=function(e){var n=s(e.components);return a.createElement(p.Provider,{value:n},e.children)},c="mdxType",x={inlineCode:"code",wrapper:function(e){var n=e.children;return a.createElement(a.Fragment,{},n)}},g=a.forwardRef((function(e,n){var t=e.components,r=e.mdxType,i=e.originalType,o=e.parentName,p=l(e,["components","mdxType","originalType","parentName"]),m=s(t),u=r,c=m["".concat(o,".").concat(u)]||m[u]||x[u]||i;return t?a.createElement(c,d(d({ref:n},p),{},{components:t})):a.createElement(c,d({ref:n},p))}));function f(e,n){var t=arguments,r=n&&n.mdxType;if("string"==typeof e||r){var i=t.length,o=new Array(i);o[0]=g;var d={};for(var l in n)hasOwnProperty.call(n,l)&&(d[l]=n[l]);d.originalType=e,d[c]="string"==typeof e?e:r,o[1]=d;for(var p=2;p<i;p++)o[p]=t[p];return a.createElement.apply(null,o)}return a.createElement.apply(null,t)}g.displayName="MDXCreateElement"},9117:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>o,default:()=>u,frontMatter:()=>i,metadata:()=>d,toc:()=>p});var a=t(7462),r=(t(7294),t(3905));const i={id:"Tag"},o="liquid.tag.Tag",d={unversionedId:"api/Tag",id:"api/Tag",title:"liquid.tag.Tag",description:"Base class for all built-in and custom template tags.",source:"@site/docs/api/tag.md",sourceDirName:"api",slug:"/api/Tag",permalink:"/liquid/api/Tag",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/tag.md",tags:[],version:"current",frontMatter:{id:"Tag"},sidebar:"apiSidebar",previous:{title:"liquid.Context",permalink:"/liquid/api/context"},next:{title:"liquid.ast.Node",permalink:"/liquid/api/node"}},l={},p=[{value:"<code>Tag</code>",id:"tag",level:2},{value:"Class Attributes",id:"class-attributes",level:2},{value:"<code>block</code>",id:"block",level:3},{value:"<code>name</code>",id:"name",level:3},{value:"<code>end</code>",id:"end",level:3},{value:"Properties",id:"properties",level:2},{value:"<code>env</code>",id:"env",level:3},{value:"Methods",id:"methods",level:2},{value:"<code>get_node</code>",id:"get_node",level:3},{value:"<code>parse</code>",id:"parse",level:3}],m={toc:p},s="wrapper";function u(e){let{components:n,...t}=e;return(0,r.mdx)(s,(0,a.default)({},m,t,{components:n,mdxType:"MDXLayout"}),(0,r.mdx)("h1",{id:"liquidtagtag"},"liquid.tag.Tag"),(0,r.mdx)("p",null,"Base class for all built-in and ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/guides/custom-tags"},"custom template tags"),"."),(0,r.mdx)("h2",{id:"tag"},(0,r.mdx)("inlineCode",{parentName:"h2"},"Tag")),(0,r.mdx)("p",null,(0,r.mdx)("inlineCode",{parentName:"p"},"class Tag(env)")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},"Parameters"),":"),(0,r.mdx)("ul",null,(0,r.mdx)("li",{parentName:"ul"},(0,r.mdx)("inlineCode",{parentName:"li"},"env: liquid.Environment")," - The ",(0,r.mdx)("a",{parentName:"li",href:"/liquid/api/Environment"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment"))," that manages this tag.")),(0,r.mdx)("h2",{id:"class-attributes"},"Class Attributes"),(0,r.mdx)("h3",{id:"block"},(0,r.mdx)("inlineCode",{parentName:"h3"},"block")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},"Type"),": ",(0,r.mdx)("inlineCode",{parentName:"p"},"bool = True")),(0,r.mdx)("p",null,"Indicates if the tag is a block tag."),(0,r.mdx)("h3",{id:"name"},(0,r.mdx)("inlineCode",{parentName:"h3"},"name")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},"Type"),": ",(0,r.mdx)("inlineCode",{parentName:"p"},'str = ""')),(0,r.mdx)("p",null,"The name of the tag. Like ",(0,r.mdx)("inlineCode",{parentName:"p"},'"if"')," or ",(0,r.mdx)("inlineCode",{parentName:"p"},'"for"'),"."),(0,r.mdx)("h3",{id:"end"},(0,r.mdx)("inlineCode",{parentName:"h3"},"end")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},"Type"),": ",(0,r.mdx)("inlineCode",{parentName:"p"},'str = ""')),(0,r.mdx)("p",null,"The end or closing tag name. If ",(0,r.mdx)("inlineCode",{parentName:"p"},"block")," is ",(0,r.mdx)("inlineCode",{parentName:"p"},"True"),", ",(0,r.mdx)("inlineCode",{parentName:"p"},"end")," must be set. By convention it is\n",(0,r.mdx)("inlineCode",{parentName:"p"},'"end<tag.name>"'),"."),(0,r.mdx)("h2",{id:"properties"},"Properties"),(0,r.mdx)("h3",{id:"env"},(0,r.mdx)("inlineCode",{parentName:"h3"},"env")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},"Type"),": ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.Environment")),(0,r.mdx)("p",null,"The ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment"))," that manages this tag."),(0,r.mdx)("h2",{id:"methods"},"Methods"),(0,r.mdx)("h3",{id:"get_node"},(0,r.mdx)("inlineCode",{parentName:"h3"},"get_node")),(0,r.mdx)("p",null,(0,r.mdx)("inlineCode",{parentName:"p"},"get_node(self, stream: TokenStream) -> Node")),(0,r.mdx)("p",null,"Used internally to delegate to ",(0,r.mdx)("inlineCode",{parentName:"p"},"Tag.parse"),"."),(0,r.mdx)("h3",{id:"parse"},(0,r.mdx)("inlineCode",{parentName:"h3"},"parse")),(0,r.mdx)("p",null,(0,r.mdx)("inlineCode",{parentName:"p"},"parse(self, stream: TokenStream) -> Node:")),(0,r.mdx)("p",null,"Abstract method. Return a parse tree node by parsing tokens from the given stream. Every tag must implement ",(0,r.mdx)("inlineCode",{parentName:"p"},"parse"),"."))}u.isMDXComponent=!0}}]);