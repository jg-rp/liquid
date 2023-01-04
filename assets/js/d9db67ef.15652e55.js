"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[3639],{3414:(e,i,t)=>{t.r(i),t.d(i,{assets:()=>p,contentTitle:()=>o,default:()=>d,frontMatter:()=>l,metadata:()=>a,toc:()=>u});var r=t(3117),n=(t(7294),t(3905));const l={},o="liquid.exceptions",a={unversionedId:"api/exceptions",id:"api/exceptions",title:"liquid.exceptions",description:"liquid.exceptions.Error",source:"@site/docs/api/exceptions.md",sourceDirName:"api",slug:"/api/exceptions",permalink:"/liquid/api/exceptions",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/exceptions.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.DictLoader",permalink:"/liquid/api/dictloader"},next:{title:"liquid.Context",permalink:"/liquid/api/context"}},p={},u=[{value:"liquid.exceptions.Error",id:"liquidexceptionserror",level:2},{value:"liquid.exceptions.LiquidSyntaxError",id:"liquidexceptionsliquidsyntaxerror",level:2},{value:"liquid.exceptions.LiquidTypeError",id:"liquidexceptionsliquidtypeerror",level:2},{value:"liquid.exceptions.DisabledTagError",id:"liquidexceptionsdisabledtagerror",level:2},{value:"liquid.exceptions.NoSuchFilterFunc",id:"liquidexceptionsnosuchfilterfunc",level:2},{value:"liquid.exceptions.FilterError",id:"liquidexceptionsfiltererror",level:2},{value:"liquid.exceptions.FilterArgumentError",id:"liquidexceptionsfilterargumenterror",level:2},{value:"liquid.exceptions.FilterValueError",id:"liquidexceptionsfiltervalueerror",level:2},{value:"liquid.exceptions.TemplateNotFound",id:"liquidexceptionstemplatenotfound",level:2},{value:"liquid.exceptions.ContextDepthError",id:"liquidexceptionscontextdeptherror",level:2},{value:"liquid.exceptions.LocalNamespaceLimitError",id:"liquidexceptionslocalnamespacelimiterror",level:2},{value:"liquid.exceptions.LoopIterationLimitError",id:"liquidexceptionsloopiterationlimiterror",level:2},{value:"liquid.exceptions.OutputStreamLimitError",id:"liquidexceptionsoutputstreamlimiterror",level:2},{value:"liquid.exceptions.TemplateTraversalError",id:"liquidexceptionstemplatetraversalerror",level:2},{value:"liquid.exceptions.UndefinedError",id:"liquidexceptionsundefinederror",level:2}],s={toc:u};function d(e){let{components:i,...t}=e;return(0,n.kt)("wrapper",(0,r.Z)({},s,t,{components:i,mdxType:"MDXLayout"}),(0,n.kt)("h1",{id:"liquidexceptions"},"liquid.exceptions"),(0,n.kt)("h2",{id:"liquidexceptionserror"},"liquid.exceptions.Error"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.Error(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Base class for all Liquid exceptions."),(0,n.kt)("h2",{id:"liquidexceptionsliquidsyntaxerror"},"liquid.exceptions.LiquidSyntaxError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.LiquidSyntaxError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when there is a parser error."),(0,n.kt)("h2",{id:"liquidexceptionsliquidtypeerror"},"liquid.exceptions.LiquidTypeError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.LiquidTypeError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when an error occurs at render time."),(0,n.kt)("h2",{id:"liquidexceptionsdisabledtagerror"},"liquid.exceptions.DisabledTagError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.DisabledTagError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when an attempt is made to render a disabled tag."),(0,n.kt)("h2",{id:"liquidexceptionsnosuchfilterfunc"},"liquid.exceptions.NoSuchFilterFunc"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.NoSuchFilterFunc(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when a filter lookup fails."),(0,n.kt)("h2",{id:"liquidexceptionsfiltererror"},"liquid.exceptions.FilterError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.FilterError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Base class of all filter related errors."),(0,n.kt)("h2",{id:"liquidexceptionsfilterargumenterror"},"liquid.exceptions.FilterArgumentError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.FilterArgumentError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when a filter's arguments are invalid."),(0,n.kt)("h2",{id:"liquidexceptionsfiltervalueerror"},"liquid.exceptions.FilterValueError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.FilterValueError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when a filter'ss value is invalid."),(0,n.kt)("h2",{id:"liquidexceptionstemplatenotfound"},"liquid.exceptions.TemplateNotFound"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.TemplateNotFound(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when a template could not be found."),(0,n.kt)("h2",{id:"liquidexceptionscontextdeptherror"},"liquid.exceptions.ContextDepthError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.ContextDepthError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when the maximum context depth is reached."),(0,n.kt)("p",null,"Usually indicates recursive use of render or include tags."),(0,n.kt)("h2",{id:"liquidexceptionslocalnamespacelimiterror"},"liquid.exceptions.LocalNamespaceLimitError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.LocalNamespaceLimitError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when the maximum size of a render context's local namespace has been exceeded."),(0,n.kt)("h2",{id:"liquidexceptionsloopiterationlimiterror"},"liquid.exceptions.LoopIterationLimitError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.LoopIterationLimitError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when the maximum number of loop iterations has been exceeded."),(0,n.kt)("h2",{id:"liquidexceptionsoutputstreamlimiterror"},"liquid.exceptions.OutputStreamLimitError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.OutputStreamLimitError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when an output stream limit has been exceeded."),(0,n.kt)("h2",{id:"liquidexceptionstemplatetraversalerror"},"liquid.exceptions.TemplateTraversalError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.TemplateTraversalError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised when an AST node or expression can not be visited.."),(0,n.kt)("h2",{id:"liquidexceptionsundefinederror"},"liquid.exceptions.UndefinedError"),(0,n.kt)("p",null,(0,n.kt)("inlineCode",{parentName:"p"},"class liquid.exceptions.UndefinedError(*args, linenum=None, filename=None)")),(0,n.kt)("p",null,"Exception raised by the StrictUndefined type."))}d.isMDXComponent=!0},3905:(e,i,t)=>{t.d(i,{Zo:()=>s,kt:()=>m});var r=t(7294);function n(e,i,t){return i in e?Object.defineProperty(e,i,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[i]=t,e}function l(e,i){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);i&&(r=r.filter((function(i){return Object.getOwnPropertyDescriptor(e,i).enumerable}))),t.push.apply(t,r)}return t}function o(e){for(var i=1;i<arguments.length;i++){var t=null!=arguments[i]?arguments[i]:{};i%2?l(Object(t),!0).forEach((function(i){n(e,i,t[i])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):l(Object(t)).forEach((function(i){Object.defineProperty(e,i,Object.getOwnPropertyDescriptor(t,i))}))}return e}function a(e,i){if(null==e)return{};var t,r,n=function(e,i){if(null==e)return{};var t,r,n={},l=Object.keys(e);for(r=0;r<l.length;r++)t=l[r],i.indexOf(t)>=0||(n[t]=e[t]);return n}(e,i);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(r=0;r<l.length;r++)t=l[r],i.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(n[t]=e[t])}return n}var p=r.createContext({}),u=function(e){var i=r.useContext(p),t=i;return e&&(t="function"==typeof e?e(i):o(o({},i),e)),t},s=function(e){var i=u(e.components);return r.createElement(p.Provider,{value:i},e.children)},d={inlineCode:"code",wrapper:function(e){var i=e.children;return r.createElement(r.Fragment,{},i)}},c=r.forwardRef((function(e,i){var t=e.components,n=e.mdxType,l=e.originalType,p=e.parentName,s=a(e,["components","mdxType","originalType","parentName"]),c=u(t),m=n,x=c["".concat(p,".").concat(m)]||c[m]||d[m]||l;return t?r.createElement(x,o(o({ref:i},s),{},{components:t})):r.createElement(x,o({ref:i},s))}));function m(e,i){var t=arguments,n=i&&i.mdxType;if("string"==typeof e||n){var l=t.length,o=new Array(l);o[0]=c;var a={};for(var p in i)hasOwnProperty.call(i,p)&&(a[p]=i[p]);a.originalType=e,a.mdxType="string"==typeof e?e:n,o[1]=a;for(var u=2;u<l;u++)o[u]=t[u];return r.createElement.apply(null,o)}return r.createElement.apply(null,t)}c.displayName="MDXCreateElement"}}]);