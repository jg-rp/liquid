"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[5465],{3905:(e,t,r)=>{r.d(t,{Zo:()=>d,kt:()=>f});var n=r(7294);function a(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function o(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,n)}return r}function i(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?o(Object(r),!0).forEach((function(t){a(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function l(e,t){if(null==e)return{};var r,n,a=function(e,t){if(null==e)return{};var r,n,a={},o=Object.keys(e);for(n=0;n<o.length;n++)r=o[n],t.indexOf(r)>=0||(a[r]=e[r]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(n=0;n<o.length;n++)r=o[n],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(a[r]=e[r])}return a}var c=n.createContext({}),p=function(e){var t=n.useContext(c),r=t;return e&&(r="function"==typeof e?e(t):i(i({},t),e)),r},d=function(e){var t=p(e.components);return n.createElement(c.Provider,{value:t},e.children)},u="mdxType",s={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},m=n.forwardRef((function(e,t){var r=e.components,a=e.mdxType,o=e.originalType,c=e.parentName,d=l(e,["components","mdxType","originalType","parentName"]),u=p(r),m=a,f=u["".concat(c,".").concat(m)]||u[m]||s[m]||o;return r?n.createElement(f,i(i({ref:t},d),{},{components:r})):n.createElement(f,i({ref:t},d))}));function f(e,t){var r=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var o=r.length,i=new Array(o);i[0]=m;var l={};for(var c in t)hasOwnProperty.call(t,c)&&(l[c]=t[c]);l.originalType=e,l[u]="string"==typeof e?e:a,i[1]=l;for(var p=2;p<o;p++)i[p]=r[p];return n.createElement.apply(null,i)}return n.createElement.apply(null,r)}m.displayName="MDXCreateElement"},8073:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>c,contentTitle:()=>i,default:()=>s,frontMatter:()=>o,metadata:()=>l,toc:()=>p});var n=r(7462),a=(r(7294),r(3905));const o={},i="liquid.loaders.ChoiceLoader",l={unversionedId:"api/choiceloader",id:"api/choiceloader",title:"liquid.loaders.ChoiceLoader",description:"A template loader that will try each of a list of loaders until a template is found.",source:"@site/docs/api/choiceloader.md",sourceDirName:"api",slug:"/api/choiceloader",permalink:"/liquid/api/choiceloader",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/choiceloader.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.FileExtensionLoader",permalink:"/liquid/api/fileextensionloader"},next:{title:"liquid.loaders.DictLoader",permalink:"/liquid/api/dictloader"}},c={},p=[{value:"<code>ChoiceLoader</code>",id:"choiceloader",level:2},{value:"Methods",id:"methods",level:2},{value:"<code>get_source</code>",id:"get_source",level:3},{value:"<code>get_source_async</code>",id:"get_source_async",level:3}],d={toc:p},u="wrapper";function s(e){let{components:t,...r}=e;return(0,a.kt)(u,(0,n.Z)({},d,r,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"liquidloaderschoiceloader"},"liquid.loaders.ChoiceLoader"),(0,a.kt)("p",null,"A template loader that will try each of a list of loaders until a template is found."),(0,a.kt)("h2",{id:"choiceloader"},(0,a.kt)("inlineCode",{parentName:"h2"},"ChoiceLoader")),(0,a.kt)("p",null,(0,a.kt)("inlineCode",{parentName:"p"},"class FileSystemLoader(loaders)")),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Parameters"),":"),(0,a.kt)("ul",null,(0,a.kt)("li",{parentName:"ul"},(0,a.kt)("inlineCode",{parentName:"li"},"loaders: List[liquid.loaders.BaseLoader]")," - A list of loaders to try.")),(0,a.kt)("h2",{id:"methods"},"Methods"),(0,a.kt)("h3",{id:"get_source"},(0,a.kt)("inlineCode",{parentName:"h3"},"get_source")),(0,a.kt)("p",null,(0,a.kt)("inlineCode",{parentName:"p"},"get_source(environment, template_name)")),(0,a.kt)("p",null,"Calls ",(0,a.kt)("inlineCode",{parentName:"p"},"get_source")," on each loader, returning the first template source found."),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Raises"),": ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid.exceptions.TemplateNotFound")," if a template with the given name can not be\nfound.",(0,a.kt)("br",{parentName:"p"}),"\n",(0,a.kt)("strong",{parentName:"p"},"Returns"),": The source, filename and reload function for the named template.",(0,a.kt)("br",{parentName:"p"}),"\n",(0,a.kt)("strong",{parentName:"p"},"Return Type"),": ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid.loaders.TemplateSource")),(0,a.kt)("h3",{id:"get_source_async"},(0,a.kt)("inlineCode",{parentName:"h3"},"get_source_async")),(0,a.kt)("p",null,(0,a.kt)("inlineCode",{parentName:"p"},"async get_source(environment, template_name)")),(0,a.kt)("p",null,"An async version of ",(0,a.kt)("a",{parentName:"p",href:"#get_source"},(0,a.kt)("inlineCode",{parentName:"a"},"get_source()")),"."),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Returns"),": The source, filename and reload function for the named template.",(0,a.kt)("br",{parentName:"p"}),"\n",(0,a.kt)("strong",{parentName:"p"},"Return Type"),": ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid.loaders.TemplateSource")))}s.isMDXComponent=!0}}]);