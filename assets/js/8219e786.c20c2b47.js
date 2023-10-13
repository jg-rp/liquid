"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[6474],{3905:(e,n,t)=>{t.r(n),t.d(n,{MDXContext:()=>p,MDXProvider:()=>c,mdx:()=>g,useMDXComponents:()=>s,withMDXComponents:()=>m});var a=t(7294);function o(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function i(){return i=Object.assign||function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var a in t)Object.prototype.hasOwnProperty.call(t,a)&&(e[a]=t[a])}return e},i.apply(this,arguments)}function l(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);n&&(a=a.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,a)}return t}function r(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?l(Object(t),!0).forEach((function(n){o(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):l(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function d(e,n){if(null==e)return{};var t,a,o=function(e,n){if(null==e)return{};var t,a,o={},i=Object.keys(e);for(a=0;a<i.length;a++)t=i[a],n.indexOf(t)>=0||(o[t]=e[t]);return o}(e,n);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)t=i[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(o[t]=e[t])}return o}var p=a.createContext({}),m=function(e){return function(n){var t=s(n.components);return a.createElement(e,i({},n,{components:t}))}},s=function(e){var n=a.useContext(p),t=n;return e&&(t="function"==typeof e?e(n):r(r({},n),e)),t},c=function(e){var n=s(e.components);return a.createElement(p.Provider,{value:n},e.children)},x="mdxType",u={inlineCode:"code",wrapper:function(e){var n=e.children;return a.createElement(a.Fragment,{},n)}},h=a.forwardRef((function(e,n){var t=e.components,o=e.mdxType,i=e.originalType,l=e.parentName,p=d(e,["components","mdxType","originalType","parentName"]),m=s(t),c=o,x=m["".concat(l,".").concat(c)]||m[c]||u[c]||i;return t?a.createElement(x,r(r({ref:n},p),{},{components:t})):a.createElement(x,r({ref:n},p))}));function g(e,n){var t=arguments,o=n&&n.mdxType;if("string"==typeof e||o){var i=t.length,l=new Array(i);l[0]=h;var r={};for(var d in n)hasOwnProperty.call(n,d)&&(r[d]=n[d]);r.originalType=e,r[x]="string"==typeof e?e:o,l[1]=r;for(var p=2;p<i;p++)l[p]=t[p];return a.createElement.apply(null,l)}return a.createElement.apply(null,t)}h.displayName="MDXCreateElement"},452:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>d,contentTitle:()=>l,default:()=>c,frontMatter:()=>i,metadata:()=>r,toc:()=>p});var a=t(7462),o=(t(7294),t(3905));const i={},l="liquid.Context",r={unversionedId:"api/context",id:"api/context",title:"liquid.Context",description:"A render context, containing namespaces for template variables and a references to the bound environment.",source:"@site/docs/api/context.md",sourceDirName:"api",slug:"/api/context",permalink:"/liquid/api/context",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/context.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.exceptions",permalink:"/liquid/api/exceptions"},next:{title:"liquid.tag.Tag",permalink:"/liquid/api/Tag"}},d={},p=[{value:"<code>Context</code>",id:"context",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>env</code>",id:"env",level:3},{value:"<code>locals</code>",id:"locals",level:3},{value:"<code>globals</code>",id:"globals",level:3},{value:"<code>counters</code>",id:"counters",level:3},{value:"<code>scope</code>",id:"scope",level:3},{value:"<code>loops</code>",id:"loops",level:3},{value:"<code>disabled_tags</code>",id:"disabled_tags",level:3},{value:"<code>autoescape</code>",id:"autoescape",level:3},{value:"Methods",id:"methods",level:2},{value:"<code>assign</code>",id:"assign",level:3},{value:"<code>get</code>",id:"get",level:3},{value:"<code>get_async</code>",id:"get_async",level:3},{value:"<code>resolve</code>",id:"resolve",level:3},{value:"<code>filter</code>",id:"filter",level:3},{value:"<code>get_size_of_locals</code>",id:"get_size_of_locals",level:3},{value:"<code>get_template</code>",id:"get_template",level:3},{value:"<code>get_template_async</code>",id:"get_template_async",level:3},{value:"<code>extend</code>",id:"extend",level:3},{value:"<code>copy</code>",id:"copy",level:3},{value:"<code>error</code>",id:"error",level:3}],m={toc:p},s="wrapper";function c(e){let{components:n,...t}=e;return(0,o.mdx)(s,(0,a.default)({},m,t,{components:n,mdxType:"MDXLayout"}),(0,o.mdx)("h1",{id:"liquidcontext"},"liquid.Context"),(0,o.mdx)("p",null,"A render context, containing namespaces for template variables and a references to the bound environment."),(0,o.mdx)("p",null,"You probably don't want to instantiate a context directly. A new one is created automatically every time a template is rendered. If you're writing custom tags, consider ",(0,o.mdx)("a",{parentName:"p",href:"#copy"},"copying")," or ",(0,o.mdx)("a",{parentName:"p",href:"#extend"},"extending")," an existing context."),(0,o.mdx)("h2",{id:"context"},(0,o.mdx)("inlineCode",{parentName:"h2"},"Context")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"class Context(env, [options])")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Parameters"),":"),(0,o.mdx)("ul",null,(0,o.mdx)("li",{parentName:"ul"},(0,o.mdx)("p",{parentName:"li"},(0,o.mdx)("inlineCode",{parentName:"p"},"env: liquid.Environment")," - The ",(0,o.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,o.mdx)("inlineCode",{parentName:"a"},"Environment"))," associated with this context.")),(0,o.mdx)("li",{parentName:"ul"},(0,o.mdx)("p",{parentName:"li"},(0,o.mdx)("inlineCode",{parentName:"p"},"globals: Optional[Mapping[str, object]]")," - Template global variables.")),(0,o.mdx)("li",{parentName:"ul"},(0,o.mdx)("p",{parentName:"li"},(0,o.mdx)("inlineCode",{parentName:"p"},"disabled_tags: Optional[List[str]]"),' - A list of tags names that are disallowed in this context.\nFor example, partial templates rendered using the "render" tag are not allowed to use "include"\ntags.')),(0,o.mdx)("li",{parentName:"ul"},(0,o.mdx)("p",{parentName:"li"},(0,o.mdx)("inlineCode",{parentName:"p"},"copy_depth: int = 0")," - The number times a context was copied to create this one."))),(0,o.mdx)("h2",{id:"properties"},"Properties"),(0,o.mdx)("h3",{id:"env"},(0,o.mdx)("inlineCode",{parentName:"h3"},"env")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"liquid.Environment")),(0,o.mdx)("p",null,"The ",(0,o.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,o.mdx)("inlineCode",{parentName:"a"},"Environment"))," associated with this context."),(0,o.mdx)("h3",{id:"locals"},(0,o.mdx)("inlineCode",{parentName:"h3"},"locals")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"Dict[str, Any]")),(0,o.mdx)("p",null,"A namespace for template local variables. Those that are bound with ",(0,o.mdx)("inlineCode",{parentName:"p"},"assign")," or ",(0,o.mdx)("inlineCode",{parentName:"p"},"capture"),"."),(0,o.mdx)("h3",{id:"globals"},(0,o.mdx)("inlineCode",{parentName:"h3"},"globals")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"Mapping[str, object]")),(0,o.mdx)("p",null,"A read-only namespace containing globally available variables. Usually passed down from the\nenvironment."),(0,o.mdx)("h3",{id:"counters"},(0,o.mdx)("inlineCode",{parentName:"h3"},"counters")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"Dict[str, int]")),(0,o.mdx)("p",null,"A namespace for ",(0,o.mdx)("inlineCode",{parentName:"p"},"increment")," and ",(0,o.mdx)("inlineCode",{parentName:"p"},"decrement")," counters."),(0,o.mdx)("h3",{id:"scope"},(0,o.mdx)("inlineCode",{parentName:"h3"},"scope")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"ReadOnlyChainMap")),(0,o.mdx)("p",null,"Namespaces are searched using this chain map. When a context is extended, the temporary namespace is\npushed to the front of this chain."),(0,o.mdx)("h3",{id:"loops"},(0,o.mdx)("inlineCode",{parentName:"h3"},"loops")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"List[object]")),(0,o.mdx)("p",null,"As stack of ",(0,o.mdx)("inlineCode",{parentName:"p"},"forloop")," objects. Used for populating ",(0,o.mdx)("inlineCode",{parentName:"p"},"forloop.parentloop"),"."),(0,o.mdx)("h3",{id:"disabled_tags"},(0,o.mdx)("inlineCode",{parentName:"h3"},"disabled_tags")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"List[str]")),(0,o.mdx)("p",null,'A list of tags names that are disallowed in this context. For example, partial templates rendered\nusing the "render" tag are not allowed to use "include" tags.'),(0,o.mdx)("h3",{id:"autoescape"},(0,o.mdx)("inlineCode",{parentName:"h3"},"autoescape")),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Type"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"bool")),(0,o.mdx)("p",null,"Indicates if HTML auto-escaping is enabled."),(0,o.mdx)("h2",{id:"methods"},"Methods"),(0,o.mdx)("h3",{id:"assign"},(0,o.mdx)("inlineCode",{parentName:"h3"},"assign")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"assign(key: str, val: Any) -> None")),(0,o.mdx)("p",null,"Add ",(0,o.mdx)("inlineCode",{parentName:"p"},"val")," to the local namespace with key ",(0,o.mdx)("inlineCode",{parentName:"p"},"key"),"."),(0,o.mdx)("h3",{id:"get"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"get(path: Union[str, Sequence[Union[str, int]]], default: object = _undefined) -> object:")),(0,o.mdx)("p",null,"Return the value at path ",(0,o.mdx)("inlineCode",{parentName:"p"},"path")," if it is in scope, else default."),(0,o.mdx)("h3",{id:"get_async"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_async")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"async get_async(key: str, val: Any) -> None")),(0,o.mdx)("p",null,"An async version of ",(0,o.mdx)("a",{parentName:"p",href:"#get"},(0,o.mdx)("inlineCode",{parentName:"a"},"get()")),"."),(0,o.mdx)("h3",{id:"resolve"},(0,o.mdx)("inlineCode",{parentName:"h3"},"resolve")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"resolve(name: str, default: object = _undefined) -> Any")),(0,o.mdx)("p",null,"Return the object at ",(0,o.mdx)("inlineCode",{parentName:"p"},"name")," in the current scope. This is like ",(0,o.mdx)("a",{parentName:"p",href:"#get"},(0,o.mdx)("inlineCode",{parentName:"a"},"get()")),", but does a single, top-level lookup rather than a chained lookup from a sequence of keys.`"),(0,o.mdx)("h3",{id:"filter"},(0,o.mdx)("inlineCode",{parentName:"h3"},"filter")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"filter(name: str) -> Callable[..., object]")),(0,o.mdx)("p",null,"Return the filter function with given name."),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Raises"),": NoSuchFilterFunc if a filter with the given name does not exist."),(0,o.mdx)("h3",{id:"get_size_of_locals"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_size_of_locals")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"get_size_of_locals(self) -> int")),(0,o.mdx)("p",null,'Return the "size" or a "score" for the current local namespace.'),(0,o.mdx)("p",null,"This is used by the optional local namespace resource limit. Override ",(0,o.mdx)("inlineCode",{parentName:"p"},"get_size_of_locals")," to customize how the limit is calculated. Be sure to consider ",(0,o.mdx)("inlineCode",{parentName:"p"},"self.local_namespace_size_carry")," when writing a custom implementation of ",(0,o.mdx)("inlineCode",{parentName:"p"},"get_size_of_locals"),"."),(0,o.mdx)("p",null,"The default implementation uses ",(0,o.mdx)("inlineCode",{parentName:"p"},"sys.getsizeof()")," on each of the local namespace's values. It is not a reliable measure of size in bytes."),(0,o.mdx)("h3",{id:"get_template"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_template")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"get_template(name: str) -> BoundTemplate")),(0,o.mdx)("p",null,"Load a template from the environment."),(0,o.mdx)("h3",{id:"get_template_async"},(0,o.mdx)("inlineCode",{parentName:"h3"},"get_template_async")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"async get_template_async(name: str) -> BoundTemplate")),(0,o.mdx)("p",null,"Load a template from the environment asynchronously."),(0,o.mdx)("h3",{id:"extend"},(0,o.mdx)("inlineCode",{parentName:"h3"},"extend")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"extend(namespace: Mapping[str, object]) -> Iterator[Context]")),(0,o.mdx)("p",null,"A context manager that extends this context with the given read-only namespace."),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Raises"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"ContextDepthError")," if the context has been extended too many times."),(0,o.mdx)("h3",{id:"copy"},(0,o.mdx)("inlineCode",{parentName:"h3"},"copy")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"copy( self, namespace: Dict[str, object], disabled_tags: Optional[List[str]] = None) -> Context:")),(0,o.mdx)("p",null,"Return a copy of this context without any local variables or other state for stateful tags."),(0,o.mdx)("p",null,(0,o.mdx)("strong",{parentName:"p"},"Raises"),": ",(0,o.mdx)("inlineCode",{parentName:"p"},"ContextDepthError")," if the context has been copied too many times."),(0,o.mdx)("h3",{id:"error"},(0,o.mdx)("inlineCode",{parentName:"h3"},"error")),(0,o.mdx)("p",null,(0,o.mdx)("inlineCode",{parentName:"p"},"error(exc: Error) -> None:")),(0,o.mdx)("p",null,"Ignore, raise or convert the given exception to a warning, according to the current tolerance mode."))}c.isMDXComponent=!0}}]);