"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[5465],{3905:(e,t,r)=>{r.r(t),r.d(t,{MDXContext:()=>c,MDXProvider:()=>u,mdx:()=>x,useMDXComponents:()=>m,withMDXComponents:()=>p});var n=r(7294);function o(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function a(){return a=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n])}return e},a.apply(this,arguments)}function i(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,n)}return r}function l(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?i(Object(r),!0).forEach((function(t){o(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):i(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function d(e,t){if(null==e)return{};var r,n,o=function(e,t){if(null==e)return{};var r,n,o={},a=Object.keys(e);for(n=0;n<a.length;n++)r=a[n],t.indexOf(r)>=0||(o[r]=e[r]);return o}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(n=0;n<a.length;n++)r=a[n],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(o[r]=e[r])}return o}var c=n.createContext({}),p=function(e){return function(t){var r=m(t.components);return n.createElement(e,a({},t,{components:r}))}},m=function(e){var t=n.useContext(c),r=t;return e&&(r="function"==typeof e?e(t):l(l({},t),e)),r},u=function(e){var t=m(e.components);return n.createElement(c.Provider,{value:t},e.children)},s="mdxType",f={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},h=n.forwardRef((function(e,t){var r=e.components,o=e.mdxType,a=e.originalType,i=e.parentName,c=d(e,["components","mdxType","originalType","parentName"]),p=m(r),u=o,s=p["".concat(i,".").concat(u)]||p[u]||f[u]||a;return r?n.createElement(s,l(l({ref:t},c),{},{components:r})):n.createElement(s,l({ref:t},c))}));function x(e,t){var r=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var a=r.length,i=new Array(a);i[0]=h;var l={};for(var d in t)hasOwnProperty.call(t,d)&&(l[d]=t[d]);l.originalType=e,l[s]="string"==typeof e?e:o,i[1]=l;for(var c=2;c<a;c++)i[c]=r[c];return n.createElement.apply(null,i)}return n.createElement.apply(null,r)}h.displayName="MDXCreateElement"},8073:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>d,contentTitle:()=>i,default:()=>u,frontMatter:()=>a,metadata:()=>l,toc:()=>c});var n=r(7462),o=(r(7294),r(3905));const a={},i="liquid.loaders.ChoiceLoader",l={unversionedId:"api/choiceloader",id:"api/choiceloader",title:"liquid.loaders.ChoiceLoader",description:"A template loader that will try each of a list of loaders until a template is found.",source:"@site/docs/api/choiceloader.md",sourceDirName:"api",slug:"/api/choiceloader",permalink:"/liquid/api/choiceloader",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/choiceloader.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.FileExtensionLoader",permalink:"/liquid/api/fileextensionloader"},next:{title:"liquid.loaders.DictLoader",permalink:"/liquid/api/dictloader"}},d={},c=[{value:"<code>ChoiceLoader</code>",id:"choiceloader",level:2},{value:"Methods",id:"methods",level:2},{value:"<code>get_source</code>",id:"get_source",level:3},{value:"<code>get_source_async</code>",id:"get_source_async",level:3}],p={toc:c},m="wrapper";function u(e){let{components:t,...r}=e;return(0,o.mdx)(m,(0,n.default)({},p,r,{components:t,mdxType:"MDXLayout"}),(0,o.mdx)("h1",{id:"liquidloaderschoiceloader"},"liquid.loaders.ChoiceLoader"),(0,o.mdx)("p",null,"A template loader that will try each of a list of loaders until a template is found."),(0,o.mdx)("h2",{id:"choiceloader"},(0,o.mdx)("inlineCode",{parentName:"h2"},"ChoiceLoader")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"class FileSystemLoader(loaders)")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Parameters"),":"),(0,o.mdx)("ul",null,(0,o.mdx)("li",{parentName:"ul"},(0,o.mdx)("inlineCode",{parentName:"li"},"loaders: List[liquid.loaders.BaseLoader]")," - A list of loaders to try.")),(0,o.mdx)("h2",{id:"methods"},"Methods"),(0,o.mdx)("h3",{id:"get_source"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_source")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"get_source(environment, template_name)")),(0,o.mdx)("p",null,"Calls ",(0,o.mdx)("inlineCode",{parentName:"p"},"get_source")," on each loader, returning the first template source found."),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Raises"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.TemplateNotFound")," if a template with the given name can not be\nfound.",(0,o.mdx)("br",{parentName:"p"}),"\n",(0,o.mdx)("strong",{parentName:"p"},"Returns"),": The source, filename and reload function for the named template.",(0,o.mdx)("br",{parentName:"p"}),"\n",(0,o.mdx)("strong",{parentName:"p"},"Return Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"liquid.loaders.TemplateSource")),(0,o.mdx)("h3",{id:"get_source_async"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_source_async")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"async get_source(environment, template_name)")),(0,o.mdx)("p",null,"An async version of ",(0,o.mdx)("a",{parentName:"p",href:"#get_source"},(0,o.mdx)("inlineCode",{parentName:"a"},"get_source()")),"."),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Returns"),": The source, filename and reload function for the named template.",(0,o.mdx)("br",{parentName:"p"}),"\n",(0,o.mdx)("strong",{parentName:"p"},"Return Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"liquid.loaders.TemplateSource")))}u.isMDXComponent=!0}}]);