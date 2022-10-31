"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[6474],{9475:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>i,default:()=>c,frontMatter:()=>l,metadata:()=>r,toc:()=>s});var a=n(3117),o=(n(7294),n(3905));const l={},i="liquid.Context",r={unversionedId:"api/context",id:"api/context",title:"liquid.Context",description:"A render context, containing namespaces for template variables and a references to the bound environment.",source:"@site/docs/api/context.md",sourceDirName:"api",slug:"/api/context",permalink:"/liquid/api/context",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/api/context.md",tags:[],version:"current",frontMatter:{},sidebar:"apiSidebar",previous:{title:"liquid.loaders.DictLoader",permalink:"/liquid/api/dictloader"},next:{title:"liquid.tag.Tag",permalink:"/liquid/api/Tag"}},p={},s=[{value:"<code>Context</code>",id:"context",level:2},{value:"Properties",id:"properties",level:2},{value:"<code>env</code>",id:"env",level:3},{value:"<code>locals</code>",id:"locals",level:3},{value:"<code>globals</code>",id:"globals",level:3},{value:"<code>counters</code>",id:"counters",level:3},{value:"<code>scope</code>",id:"scope",level:3},{value:"<code>loops</code>",id:"loops",level:3},{value:"<code>disabled_tags</code>",id:"disabled_tags",level:3},{value:"<code>autoescape</code>",id:"autoescape",level:3},{value:"Methods",id:"methods",level:2},{value:"<code>assign</code>",id:"assign",level:3},{value:"<code>get</code>",id:"get",level:3},{value:"<code>get_async</code>",id:"get_async",level:3},{value:"<code>resolve</code>",id:"resolve",level:3},{value:"<code>filter</code>",id:"filter",level:3},{value:"<code>get_size_of_locals</code>",id:"get_size_of_locals",level:3},{value:"<code>get_template</code>",id:"get_template",level:3},{value:"<code>get_template_async</code>",id:"get_template_async",level:3},{value:"<code>extend</code>",id:"extend",level:3},{value:"<code>copy</code>",id:"copy",level:3},{value:"<code>error</code>",id:"error",level:3}],d={toc:s};function c(e){let{components:t,...n}=e;return(0,o.kt)("wrapper",(0,a.Z)({},d,n,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("h1",{id:"liquidcontext"},"liquid.Context"),(0,o.kt)("p",null,"A render context, containing namespaces for template variables and a references to the bound environment."),(0,o.kt)("p",null,"You probably don't want to instantiate a context directly. A new one is created automatically every time a template is rendered. If you're writing custom tags, consider ",(0,o.kt)("a",{parentName:"p",href:"#copy"},"copying")," or ",(0,o.kt)("a",{parentName:"p",href:"#extend"},"extending")," an existing context."),(0,o.kt)("h2",{id:"context"},(0,o.kt)("inlineCode",{parentName:"h2"},"Context")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"class Context(env, [options])")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Parameters"),":"),(0,o.kt)("ul",null,(0,o.kt)("li",{parentName:"ul"},(0,o.kt)("p",{parentName:"li"},(0,o.kt)("inlineCode",{parentName:"p"},"env: liquid.Environment")," - The ",(0,o.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,o.kt)("inlineCode",{parentName:"a"},"Environment"))," associated with this context.")),(0,o.kt)("li",{parentName:"ul"},(0,o.kt)("p",{parentName:"li"},(0,o.kt)("inlineCode",{parentName:"p"},"globals: Optional[Mapping[str, object]]")," - Template global variables.")),(0,o.kt)("li",{parentName:"ul"},(0,o.kt)("p",{parentName:"li"},(0,o.kt)("inlineCode",{parentName:"p"},"disabled_tags: Optional[List[str]]"),' - A list of tags names that are disallowed in this context.\nFor example, partial templates rendered using the "render" tag are not allowed to use "include"\ntags.')),(0,o.kt)("li",{parentName:"ul"},(0,o.kt)("p",{parentName:"li"},(0,o.kt)("inlineCode",{parentName:"p"},"copy_depth: int = 0")," - The number times a context was copied to create this one."))),(0,o.kt)("h2",{id:"properties"},"Properties"),(0,o.kt)("h3",{id:"env"},(0,o.kt)("inlineCode",{parentName:"h3"},"env")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"liquid.Environment")),(0,o.kt)("p",null,"The ",(0,o.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,o.kt)("inlineCode",{parentName:"a"},"Environment"))," associated with this context."),(0,o.kt)("h3",{id:"locals"},(0,o.kt)("inlineCode",{parentName:"h3"},"locals")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"Dict[str, Any]")),(0,o.kt)("p",null,"A namespace for template local variables. Those that are bound with ",(0,o.kt)("inlineCode",{parentName:"p"},"assign")," or ",(0,o.kt)("inlineCode",{parentName:"p"},"capture"),"."),(0,o.kt)("h3",{id:"globals"},(0,o.kt)("inlineCode",{parentName:"h3"},"globals")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"Mapping[str, object]")),(0,o.kt)("p",null,"A read-only namespace containing globally available variables. Usually passed down from the\nenvironment."),(0,o.kt)("h3",{id:"counters"},(0,o.kt)("inlineCode",{parentName:"h3"},"counters")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"Dict[str, int]")),(0,o.kt)("p",null,"A namespace for ",(0,o.kt)("inlineCode",{parentName:"p"},"increment")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"decrement")," counters."),(0,o.kt)("h3",{id:"scope"},(0,o.kt)("inlineCode",{parentName:"h3"},"scope")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"ReadOnlyChainMap")),(0,o.kt)("p",null,"Namespaces are searched using this chain map. When a context is extended, the temporary namespace is\npushed to the front of this chain."),(0,o.kt)("h3",{id:"loops"},(0,o.kt)("inlineCode",{parentName:"h3"},"loops")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"List[object]")),(0,o.kt)("p",null,"As stack of ",(0,o.kt)("inlineCode",{parentName:"p"},"forloop")," objects. Used for populating ",(0,o.kt)("inlineCode",{parentName:"p"},"forloop.parentloop"),"."),(0,o.kt)("h3",{id:"disabled_tags"},(0,o.kt)("inlineCode",{parentName:"h3"},"disabled_tags")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"List[str]")),(0,o.kt)("p",null,'A list of tags names that are disallowed in this context. For example, partial templates rendered\nusing the "render" tag are not allowed to use "include" tags.'),(0,o.kt)("h3",{id:"autoescape"},(0,o.kt)("inlineCode",{parentName:"h3"},"autoescape")),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Type"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"bool")),(0,o.kt)("p",null,"Indicates if HTML auto-escaping is enabled."),(0,o.kt)("h2",{id:"methods"},"Methods"),(0,o.kt)("h3",{id:"assign"},(0,o.kt)("inlineCode",{parentName:"h3"},"assign")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"assign(key: str, val: Any) -> None")),(0,o.kt)("p",null,"Add ",(0,o.kt)("inlineCode",{parentName:"p"},"val")," to the local namespace with key ",(0,o.kt)("inlineCode",{parentName:"p"},"key"),"."),(0,o.kt)("h3",{id:"get"},(0,o.kt)("inlineCode",{parentName:"h3"},"get")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"get(path: Union[str, Sequence[Union[str, int]]], default: object = _undefined) -> object:")),(0,o.kt)("p",null,"Return the value at path ",(0,o.kt)("inlineCode",{parentName:"p"},"path")," if it is in scope, else default."),(0,o.kt)("h3",{id:"get_async"},(0,o.kt)("inlineCode",{parentName:"h3"},"get_async")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"async get_async(key: str, val: Any) -> None")),(0,o.kt)("p",null,"An async version of ",(0,o.kt)("a",{parentName:"p",href:"#get"},(0,o.kt)("inlineCode",{parentName:"a"},"get()")),"."),(0,o.kt)("h3",{id:"resolve"},(0,o.kt)("inlineCode",{parentName:"h3"},"resolve")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"resolve(name: str, default: object = _undefined) -> Any")),(0,o.kt)("p",null,"Return the object at ",(0,o.kt)("inlineCode",{parentName:"p"},"name")," in the current scope. This is like ",(0,o.kt)("a",{parentName:"p",href:"#get"},(0,o.kt)("inlineCode",{parentName:"a"},"get()")),", but does a single, top-level lookup rather than a chained lookup from a sequence of keys.`"),(0,o.kt)("h3",{id:"filter"},(0,o.kt)("inlineCode",{parentName:"h3"},"filter")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"filter(name: str) -> Callable[..., object]")),(0,o.kt)("p",null,"Return the filter function with given name."),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Raises"),": NoSuchFilterFunc if a filter with the given name does not exist."),(0,o.kt)("h3",{id:"get_size_of_locals"},(0,o.kt)("inlineCode",{parentName:"h3"},"get_size_of_locals")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"get_size_of_locals(self) -> int")),(0,o.kt)("p",null,'Return the "size" or a "score" for the current local namespace.'),(0,o.kt)("p",null,"This is used by the optional local namespace resource limit. Override ",(0,o.kt)("inlineCode",{parentName:"p"},"get_size_of_locals")," to customize how the limit is calculated. Be sure to consider ",(0,o.kt)("inlineCode",{parentName:"p"},"self.local_namespace_size_carry")," when writing a custom implementation of ",(0,o.kt)("inlineCode",{parentName:"p"},"get_size_of_locals"),"."),(0,o.kt)("p",null,"The default implementation uses ",(0,o.kt)("inlineCode",{parentName:"p"},"sys.getsizeof()")," on each of the local namespace's values. It is not a reliable measure of size in bytes."),(0,o.kt)("h3",{id:"get_template"},(0,o.kt)("inlineCode",{parentName:"h3"},"get_template")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"get_template(name: str) -> BoundTemplate")),(0,o.kt)("p",null,"Load a template from the environment."),(0,o.kt)("h3",{id:"get_template_async"},(0,o.kt)("inlineCode",{parentName:"h3"},"get_template_async")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"async get_template_async(name: str) -> BoundTemplate")),(0,o.kt)("p",null,"Load a template from the environment asynchronously."),(0,o.kt)("h3",{id:"extend"},(0,o.kt)("inlineCode",{parentName:"h3"},"extend")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"extend(namespace: Mapping[str, object]) -> Iterator[Context]")),(0,o.kt)("p",null,"A context manager that extends this context with the given read-only namespace."),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Raises"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"ContextDepthError")," if the context has been extended too many times."),(0,o.kt)("h3",{id:"copy"},(0,o.kt)("inlineCode",{parentName:"h3"},"copy")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"copy( self, namespace: Dict[str, object], disabled_tags: Optional[List[str]] = None) -> Context:")),(0,o.kt)("p",null,"Return a copy of this context without any local variables or other state for stateful tags."),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Raises"),": ",(0,o.kt)("inlineCode",{parentName:"p"},"ContextDepthError")," if the context has been copied too many times."),(0,o.kt)("h3",{id:"error"},(0,o.kt)("inlineCode",{parentName:"h3"},"error")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"error(exc: Error) -> None:")),(0,o.kt)("p",null,"Ignore, raise or convert the given exception to a warning, according to the current tolerance mode."))}c.isMDXComponent=!0},3905:(e,t,n)=>{n.d(t,{Zo:()=>d,kt:()=>u});var a=n(7294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function r(e,t){if(null==e)return{};var n,a,o=function(e,t){if(null==e)return{};var n,a,o={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var p=a.createContext({}),s=function(e){var t=a.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},d=function(e){var t=s(e.components);return a.createElement(p.Provider,{value:t},e.children)},c={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},m=a.forwardRef((function(e,t){var n=e.components,o=e.mdxType,l=e.originalType,p=e.parentName,d=r(e,["components","mdxType","originalType","parentName"]),m=s(n),u=o,k=m["".concat(p,".").concat(u)]||m[u]||c[u]||l;return n?a.createElement(k,i(i({ref:t},d),{},{components:n})):a.createElement(k,i({ref:t},d))}));function u(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var l=n.length,i=new Array(l);i[0]=m;var r={};for(var p in t)hasOwnProperty.call(t,p)&&(r[p]=t[p]);r.originalType=e,r.mdxType="string"==typeof e?e:o,i[1]=r;for(var s=2;s<l;s++)i[s]=n[s];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}m.displayName="MDXCreateElement"}}]);